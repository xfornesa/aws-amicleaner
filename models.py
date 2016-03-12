#!/usr/bin/env python

from config import T


class AMI:

    def __init__(self):
        self.id = None
        self.architecture = None
        self.block_device_mappings = []
        self.creation_date = None
        self.hypervisor = None
        self.image_type = None
        self.location = None
        self.name = None
        self.owner_id = None
        self.public = None
        self.root_device_name = None
        self.root_device_type = None
        self.state = None
        self.tags = []
        self.virtualization_type = None

    @staticmethod
    def object_with_json(json):
        if json is None:
            return None

        o = AMI()
        o.id = json.get('ImageId')
        o.architecture = json.get('Architecture')
        o.creation_date = json.get('CreationDate')
        o.hypervisor = json.get('Hypervisor')
        o.image_type = json.get('ImageType')
        o.location = json.get('ImageLocation')
        o.owner_id = json.get('OwnerId')
        o.public = json.get('ImageLocation')
        o.root_device_name = json.get('RootDeviceName')
        o.root_device_type = json.get('RootDeviceType')
        o.state = json.get('State')
        o.virtualization_type = json.get('VirtualizationType')

        o.tags = []
        o.virtualization_type = None


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
            print T.red("Failed to retrieve instance details")
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


class AWSBlockDevice:

    def __init__(self):
        self.device_name = None
        self.snapshot_id = None
        self.volume_size = None
        self.volume_type = None
        self.encrypted = None

    @staticmethod
    def object_with_json(json):
        if json is None:
            return None

        o = AWSBlockDevice()
        o.device_name = json.get('DeviceName')
        o.snapshot_id = json.get('Ebs').get('SnapshotId')
        o.volume_size = json.get('Ebs').get('VolumeSize')
        o.volume_type = json.get('Ebs').get('VolumeType')
        o.volume_type = json.get('Ebs').get('Encrypted')


class AWSTag:
    def __init__(self):
        self.key = None
        self.value = None

    @staticmethod
    def object_with_json(json):
        if json is None:
            return None

        o = AWSTag()
        o.key = json.get('Key')
        o.value = json.get('Value')
        return o
