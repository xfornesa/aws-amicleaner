#!/usr/bin/env python
import boto3

from resources.config import Term
from resources.models import AMI, AWSEC2Instance


def fetch_available_amis():
    client = boto3.client('ec2')
    amis = dict()

    my_custom_images = client.describe_images(Owners=['self'])
    for image_json in my_custom_images.get('Images'):
        ami = AMI.object_with_json(image_json)
        amis[ami.id] = ami

    return amis


def fetch_running_instances():
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
    amis_dict = amis_dict or {}
    instances_dict = instances_dict or {}

    for instance_image_id, ec2_instance in instances_dict.iteritems():
        amis_dict.pop(instance_image_id, None)

    return amis_dict


def main():
    print Term.bold("\nRetrieving AMIs...")
    amis_dict = fetch_available_amis()
    print Term.green("got {} of them !".format(len(amis_dict)))

    print Term.bold("\nRetrieving instances by unique AMI ids...")
    instances_dict = fetch_running_instances()
    print Term.green("got {} of them !".format(len(instances_dict)))

    print Term.bold("\nFiltering unused AMIs...")
    unused_amis = filter_unused_amis(amis_dict, instances_dict)
    print Term.green("got {} of them !".format(len(unused_amis)))


if __name__ == "__main__":
    main()
