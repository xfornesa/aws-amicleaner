#!/usr/bin/env python
import boto3
import argparse
import sys

from prettytable import PrettyTable
from resources.config import MAPPING_KEY, MAPPING_VALUES, KEEP_PREVIOUS
from resources.config import TERM
from resources.models import AMI, AWSEC2Instance


class AMICleaner:

    def __init__(self):
        self.ec2 = boto3.client('ec2')

    @staticmethod
    def get_ami_sorting_key(ami):

        """ return a key for sorting array of AMIs """

        return ami.creation_date

    def remove_amis(self, amis):

        """
        deregister AMIs (array) and removes related snapshots
        :param amis: array of AMI objects
        """

        amis = amis or []
        for ami in amis:
            print ami
            self.ec2.deregister_image(ImageId=ami.id)
            print "{0} deregistered".format(ami.id)
            for block_device in ami.block_device_mappings:
                self.ec2.delete_snapshot(SnapshotId=block_device.snapshot_id)
                print "snapshot {0} / {1} deleted".format(
                    ami.id,
                    block_device.snapshot_id
                )

        return True

    def remove_amis_from_ids(self, ami_ids):

        """
        takes a list of AMI ids, verify on aws and removes them
        :param ami_ids: array of AMI ids
        """

        if not ami_ids:
            return False

        my_custom_images = self.ec2.describe_images(
            Owners=['self'],
            ImageIds=ami_ids
        )
        amis = []
        for image_json in my_custom_images.get('Images'):
            ami = AMI.object_with_json(image_json)
            amis.append(ami)

        self.remove_amis(amis)

        return True

    def fetch_available_amis(self):

        """ Retrieve from your aws account your custom AMIs using dry run """

        available_amis = dict()

        my_custom_images = self.ec2.describe_images(Owners=['self'])
        for image_json in my_custom_images.get('Images'):
            ami = AMI.object_with_json(image_json)
            available_amis[ami.id] = ami

        return available_amis

    def fetch_instances(self):

        """ Retrieve from your aws account your running ec2 instances """

        ec2_instances = dict()

        my_instances = self.ec2.describe_instances()
        for reservation in my_instances.get("Reservations", []):
            for instance_json in reservation.get("Instances", []):
                ec2_instance = AWSEC2Instance.object_with_json(instance_json)
                ec2_instances[ec2_instance.image_id] = ec2_instance

        return ec2_instances

    def fetch_candidates(self, amis_dict=None, instances_dict=None):

        """
        Collects AMIs and ec2 instances (as dicts) and returns AMIs not holded
        by instances. Both dicts have as keys an ami-id
        """

        amis_dict = amis_dict or self.fetch_available_amis()
        instances_dict = instances_dict or self.fetch_instances()

        for instance_image_id, ec2_instance in instances_dict.iteritems():
            amis_dict.pop(instance_image_id, None)

        return amis_dict.values()

    def map_candidates(self, candidates_ami=None, mapping_strategy=None):

        """
        Given a dict of AMIs to clean, and a mapping strategy (see config.py),
        this function returns a dict of grouped amis with the mapping strategy
        name as a key.

        example :
        mapping_strategy = {"key": "name", "values": ["ubuntu", "debian"]}
        or
        mapping_strategy = {"key": "tags", "values": ["env", "role"]}

        print map_candidates(candidates_ami, mapping_strategy)
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

        mapping_strategy = mapping_strategy or {}

        if not mapping_strategy:
            return candidates_ami

        candidates_ami = candidates_ami or self.fetch_candidates()

        candidates_map = dict()
        for ami in candidates_ami:
            # case : grouping on name
            if mapping_strategy.get("key") == "name":
                for mapping_value in mapping_strategy.get("values"):
                    if mapping_value in ami.name:
                        mapping_list = candidates_map.get(mapping_value) or []
                        mapping_list.append(ami)
                        candidates_map[mapping_value] = mapping_list
            # case : grouping on tags
            elif mapping_strategy.get("key") == "tags":
                mapping_value = self.tags_values_to_string(
                    ami.tags,
                    mapping_strategy.get("values")
                )
                mapping_list = candidates_map.get(mapping_value) or []
                mapping_list.append(ami)
                candidates_map[mapping_value] = mapping_list

        return candidates_map

    @staticmethod
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

    def reduce_candidates(self, mapped_candidates_ami, keep_previous=0):

        """
        Given a array of AMIs to clean this function return a subsequent
        list by preserving a given number of them (history) based on creation
        time and rotation_strategy param
        """

        if not keep_previous:
            return mapped_candidates_ami

        if not mapped_candidates_ami:
            return mapped_candidates_ami

        amis = sorted(
            mapped_candidates_ami,
            key=self.get_ami_sorting_key,
            reverse=True
        )

        return amis[keep_previous:]


def parse_args(args):
    parser = argparse.ArgumentParser(description='Clean your AMI on your '
                                                 'AWS account. Your AWS '
                                                 'credentials must be sourced')

    parser.add_argument("--from-ids",
                        dest='from_ids',
                        nargs='+',
                        help="AMI id you simply want to remove")

    parser.add_argument("--full-report",
                        dest='full_report',
                        action="store_true",
                        help="Prints a full report of what to be cleaned")

    parser.add_argument("--mapping-key",
                        dest='mapping_key',
                        help="How to regroup AMIs : [name|tags]")

    parser.add_argument("--mapping-values",
                        dest='mapping_values',
                        nargs='+',
                        help="List of values for tags or name")

    parser.add_argument("--keep-previous",
                        dest='keep_previous',
                        type=int,
                        help="Number of previous AMI to keep excluding those"
                             "currently being running")

    parser.add_argument("-f", "--force-delete",
                        dest='force_delete',
                        action="store_true",
                        help="Skip confirmation")

    parsed_args = parser.parse_args(args)
    if parsed_args.mapping_key and not parsed_args.mapping_values:
        print "missing mapping-values\n"
        parser.print_help()
        return None

    return parsed_args


def fetch_and_prepare(mapping_strategy, keep_previous, full_report=False):

    """ Uses AMICleaner to retrieve candidates AMI, map and reduce """

    cleaner = AMICleaner()

    print TERM.bold("\nRetrieving AMIs to clean ...")
    mapped_amis = cleaner.map_candidates(mapping_strategy=mapping_strategy)

    if not mapped_amis:
        return None

    candidates = []
    report = dict()

    for group_name, amis in mapped_amis.iteritems():
        group_name = group_name or ""

        if not group_name:
            report["no-tags (excluded)"] = amis
        else:
            reduced = cleaner.reduce_candidates(amis, keep_previous)
            if reduced:
                report[group_name] = reduced
                candidates.extend(reduced)

    print_report(report, full_report)

    return candidates


def print_report(candidates, full_report=False):
    # print results

    if not candidates:
        return

    groups_table = PrettyTable(["Group name", "candidates"])

    for group_name, amis in candidates.iteritems():
        groups_table.add_row([group_name, len(amis)])
        eligible_amis_table = PrettyTable(
            ["AMI ID", "AMI Name", "Creation Date"]
        )
        for ami in amis:
            eligible_amis_table.add_row([
                ami.id,
                ami.name,
                ami.creation_date
            ])
        if full_report:
            print group_name
            print eligible_amis_table.get_string(sortby="AMI Name"), "\n\n"

    print "\nAMIs to be removed:"
    print groups_table.get_string(sortby="Group name")


def delete_amis(candidates, from_ids=False):

    """ delete candidates AMIs and related snapshots """

    if from_ids:
        print TERM.bold("\nCleaning from {} AMI id(s) ...".format(
            len(candidates))
        )
        AMICleaner().remove_amis_from_ids(candidates)
    else:
        print TERM.bold("\nCleaning {} AMIs ...".format(len(candidates)))
        AMICleaner().remove_amis(candidates)


def main():

    """ main entry point for cli """

    args = parse_args(sys.argv[1:])

    if not args:
        sys.exit(1)

    # defaults
    mapping_key = args.mapping_key or MAPPING_KEY
    mapping_values = args.mapping_values or MAPPING_VALUES
    keep_previous = args.keep_previous or KEEP_PREVIOUS

    if args.from_ids:
        delete_amis(args.from_ids, True)
    else:
        # print defaults
        print TERM.bold("Default values : ==>")
        print TERM.green("mapping_key : {0}".format(mapping_key))
        print TERM.green("mapping_values : {0}".format(mapping_values))
        print TERM.green("keep_previous : {0}".format(keep_previous))

        mapping_strategy = {"key": mapping_key, "values": mapping_values}

        candidates = fetch_and_prepare(
            mapping_strategy,
            keep_previous,
            args.full_report
        )

        delete = False

        if not args.force_delete:
            answer = raw_input("Do you want to continue and remove {} AMIs "
                               "[y/N] ? : ".format(len(candidates)))
            delete = (answer.lower() == "y")
        else:
            delete = True

        if delete:
            delete_amis(candidates)


if __name__ == "__main__":
    main()
