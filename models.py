#!/usr/bin/env python

class AMI:

    def __init__(self):
        self.id = None
        self.name = None
        self.launch_time = None
        self.private_ip_address = None
        self.public_ip_address = None
        self.vpc_id = None
        self.image_id = None
        self.private_dns_name = None
        self.key_name = None
        self.subnet_id = None
        self.instance_type = None
        self.availability_zone = None
        self.commit_sha = None
        self.asg_name = None
        self.tags = []


class EC2Instance:

    def __init__(self):
        self.id = None
        self.name = None
        self.launch_time = None
        self.private_ip_address = None
        self.public_ip_address = None
        self.vpc_id = None
        self.image_id = None
        self.private_dns_name = None
        self.key_name = None
        self.subnet_id = None
        self.instance_type = None
        self.availability_zone = None
        self.commit_sha = None
        self.asg_name = None
        self.tags = []

    @staticmethod
    def object_with_json(json):
        pass

    @staticmethod
    def object_with_id(id):

        if id is None:
            return None

        # request for an ec2 instance with given id
        ec2 = boto3.client('ec2')
        ec2_json = None

        try:
            ec2_json = ec2.describe_instances(InstanceIds=[id])

            ec2_json = ec2_json.get('Reservations')[0].get('Instances')[0]
        except Exception as e:
            print term.red("Failed to retrieve instance details")
            print e

        if ec2_json is None:
            return None

        i = EC2Instance()
        i.id = ec2_json.get('InstanceId')
        i.name = ec2_json.get('PrivateDnsName')
        i.launch_time = ec2_json.get('LaunchTime')
        i.private_ip_address = ec2_json.get('PrivateIpAddress')
        i.public_ip_address = ec2_json.get('PublicIpAddress')
        i.vpc_id = ec2_json.get('VpcId')
        i.image_id = ec2_json.get('ImageId')
        i.private_dns_name = ec2_json.get('PrivateDnsName')
        i.key_name = ec2_json.get('KeyName')
        i.subnet_id = ec2_json.get('SubnetId')
        i.instance_type = ec2_json.get('InstanceType')
        i.availability_zone = ec2_json.get('Placement').get('AvailabilityZone')
        i.tags = ec2_json.get('InstanceId')

        for tag in ec2_json.get('Tags'):
            tag = AWSTag.object_with_json(tag)

            if tag.key == 'Name':
                i.name = tag.value
            elif tag.key == "Commit":
                i.commit_sha = tag.value
            elif tag.key == "aws:autoscaling:groupName":
                i.asg_name = tag.value

        return i


class AWSTag:
    def __init__(self):
        self.key = None
        self.value = None

    @staticmethod
    def object_with_json(tag_json):
        if tag_json is None:
            return None

        t = AWSTag()
        t.key = tag_json.get('Key')
        t.value = tag_json.get('Value')
        return t
