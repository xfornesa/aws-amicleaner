#!/usr/bin/env python


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

        for tag in json.get('Tags', []):
            aws_tag = AWSTag.object_with_json(tag)
            o.tags.append(aws_tag)

        for block_device in json.get('BlockDeviceMappings', []):
            aws_block_device = AWSBlockDevice.object_with_json(block_device)
            o.block_device_mappings.append(aws_block_device)

        return o


class AWSEC2Instance:
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
        self.asg_name = None
        self.tags = []

    @staticmethod
    def object_with_json(json):
        if json is None:
            return None

        o = AWSEC2Instance()
        o.id = json.get('InstanceId')
        o.name = json.get('PrivateDnsName')
        o.launch_time = json.get('LaunchTime')
        o.private_ip_address = json.get('PrivateIpAddress')
        o.public_ip_address = json.get('PublicIpAddress')
        o.vpc_id = json.get('VpcId')
        o.image_id = json.get('ImageId')
        o.private_dns_name = json.get('PrivateDnsName')
        o.key_name = json.get('KeyName')
        o.subnet_id = json.get('SubnetId')
        o.instance_type = json.get('InstanceType')
        o.availability_zone = json.get('Placement').get('AvailabilityZone')

        for tag in json.get('Tags'):
            aws_tag = AWSTag.object_with_json(tag)
            o.tags.append(aws_tag)

        return o


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
        if json.get('Ebs', None) is not None:
            o.snapshot_id = json.get('Ebs').get('SnapshotId')
            o.volume_size = json.get('Ebs').get('VolumeSize')
            o.volume_type = json.get('Ebs').get('VolumeType')
            o.encrypted = json.get('Ebs').get('Encrypted')

        return o


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
