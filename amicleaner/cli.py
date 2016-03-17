#!/usr/bin/env python
import boto3
import argparse
import sys

from prettytable import PrettyTable
from resources.config import GROUPING_KEY, GROUPING_VALUES, KEEP_PREVIOUS
from resources.config import TERM
from resources.models import AMI, AWSEC2Instance


def fetch_available_amis():
    """ Retrieve from your aws account your custom AMIs using dry run """

    client = boto3.client('ec2')
    amis = dict()

    my_custom_images = client.describe_images(Owners=['self'])
    for image_json in my_custom_images.get('Images'):
        ami = AMI.object_with_json(image_json)
        amis[ami.id] = ami

    return amis


def fetch_running_instances():
    """ Retrieve from your aws account your running ec2 instances """

    client = boto3.client('ec2')
    ec2_instances = dict()

    '''
    using dict and instances id as key will make unique values of
    available instances
    '''

    my_running_instances = client.describe_instances()
    for reservation in my_running_instances.get("Reservations", []):
        for instance_json in reservation.get("Instances", []):
            ec2_instance = AWSEC2Instance.object_with_json(instance_json)
            ec2_instances[ec2_instance.image_id] = ec2_instance

    return ec2_instances


def filter_unused_amis(amis_dict=None, instances_dict=None):
    """
    Giving a dict of amis and ec2 instances, this function will apply a filter
    and return a dict of unused amis. Both dicts have as keys an ami-id
    """

    amis_dict = amis_dict or {}
    instances_dict = instances_dict or {}

    for instance_image_id, ec2_instance in instances_dict.iteritems():
        amis_dict.pop(instance_image_id, None)

    return amis_dict


def get_ami_sorting_key(ami):
    """ return a key for sorting array of AMIs """

    return ami.creation_date


def apply_rotation_strategy(amis_array, rotation_strategy=0):
    """
    Given a array of AMIs to clean, this function return a subsequent list by
    preserving a given number of them (history) based on creation time and
    rotation_strategy param
    """

    if not rotation_strategy:
        return amis_array

    if not amis_array:
        return amis_array

    amis_array = sorted(amis_array, key=get_ami_sorting_key, reverse=True)

    return amis_array[rotation_strategy:]


def apply_grouping_strategy(unused_amis, grouping_strategy):
    """
    Given a dict of AMIs to clean, and a grouping strategy (see config.py),
    this function returns a dict of grouped amis with the grouping strategy
    name as a key.

    example :
    grouping_strategy = {"key": "name", "values": ["ubuntu", "debian"]}
    or
    grouping_strategy = {"key": "tags", "values": ["env", "role"]}

    print apply_grouping_strategy(unused_amis, grouping_strategy)
    ==>
    {
        "ubuntu": [obj1, obj3],
        "debian": [obj2, obj5]
    }

    or
    ==>
    {
        "prod.nginx": [obj1, obj3],
        "prod.tomcat": [obj2, obj5],
        "test.nginx": [obj6, obj7],
    }
    """

    grouping_strategy = grouping_strategy or {}
    unused_amis = unused_amis or {}

    if not grouping_strategy:
        return unused_amis

    groups = dict()
    for ami in unused_amis.itervalues():
        # case : grouping on name
        if grouping_strategy.get("key") == "name":
            for grouping_value in grouping_strategy.get("values"):
                if grouping_value in ami.name:
                    grouping_list = groups.get(grouping_value) or []
                    grouping_list.append(ami)
                    groups[grouping_value] = grouping_list
        # case : grouping on tags
        elif grouping_strategy.get("key") == "tags":
            grouping_value = tags_values_to_string(
                ami.tags,
                grouping_strategy.get("values")
            )
            grouping_list = groups.get(grouping_value) or []
            grouping_list.append(ami)
            groups[grouping_value] = grouping_list

    return groups


def tags_values_to_string(tags, filters=None):
    """
    filters tags(key,value) array and return a string with tags values
    :tags is an array of AWSTag objects
    """

    if tags is None:
        return None

    tag_values = []

    filters = filters or []
    filters_to_string = ".".join(filters)

    for tag in tags:
        if not filters:
            tag_values.append(tag.value)
        elif tag.key in filters_to_string:
            tag_values.append(tag.value)

    return ".".join(sorted(tag_values))


def report_only():
    pass


def configure_args_parser():
    parser = argparse.ArgumentParser(description='Clean your AMI on your '
                                                 'AWS account. Your AWS '
                                                 'credentials must be sourced')

    parser.add_argument("--report-only", dest='report_only',
                        action="store_true",
                        help="Just print a report of what to be cleaned")

    parser.add_argument("--grouping-key", dest='grouping_key',
                        help="How to regroup AMIs : [name|tags]")

    parser.add_argument("--grouping-values",
                        dest='grouping_values',
                        nargs='+',
                        help="List of values for tags or name")

    parser.add_argument("--keep-previous", dest='keep_previous',
                        help="Number of previous AMI to keep excluding those"
                             "currently being running")

    args = parser.parse_args()
    if args.grouping_key and not args.grouping_values:
        print "missing grouping-values"
        parser.print_help()
        sys.exit()

    return args


def main():
    """ main entry point for cli """

    args = configure_args_parser()


    # defaults
    grouping_key = args.grouping_key or GROUPING_KEY
    grouping_values = args.grouping_values or GROUPING_VALUES
    keep_previous = int(args.keep_previous) or KEEP_PREVIOUS

    # print defaults
    print TERM.bold("Default values : ==>")
    print TERM.green("grouping_key : {0}".format(grouping_key))
    print TERM.green("grouping_values : {0}".format(grouping_values))
    print TERM.green("keep_previous : {0}".format(keep_previous))

    print TERM.bold("\nRetrieving AMIs to clean ...")
    # retrieving unused amis
    unused_amis = filter_unused_amis(
        fetch_available_amis(),
        fetch_running_instances()
    )

    # map
    mapped_amis = apply_grouping_strategy(
        unused_amis,
        {"key": grouping_key, "values": grouping_values}
    )
    reduced_amis = dict()

    # reduce
    for group_name, amis in mapped_amis.iteritems():

        group_name = group_name or ""
        if not group_name:
            reduced_amis["no-tags"] = amis
        else:
            filtered = apply_rotation_strategy(amis, keep_previous)
            if filtered:
                reduced_amis[group_name] = filtered

    # print results
    groups_table = PrettyTable(["Group name", "AMI count"])

    for group_name, amis in reduced_amis.iteritems():
        groups_table.add_row([group_name, len(amis)])
        eligible_amis_table = PrettyTable(["AMI ID", "AMI Name", "Creation Date"])
        for ami in amis:
            eligible_amis_table.add_row([
                ami.id,
                ami.name,
                ami.creation_date
            ])
        print group_name
        print eligible_amis_table.get_string(sortby="AMI Name"), "\n\n"

    print "summary"
    print groups_table.get_string(sortby="Group name")

    if args.report_only:
        report_only()


if __name__ == "__main__":
    main()
