# -*- coding: utf-8 -*-

import json

from amicleaner.resources.models import AMI, AWSBlockDevice, AWSEC2Instance
from amicleaner.resources.models import AWSTag


def test_get_awstag_from_none():
    aws_tag = AWSTag.object_with_json(None)
    assert aws_tag is None


def test_get_awstag_from_json():
    json_to_parse = {"Key": "Name", "Value": "Test"}
    aws_tag = AWSTag.object_with_json(json_to_parse)
    assert aws_tag.value == "Test"
    assert aws_tag.key == "Name"


def test_get_awsblockdevice_from_none():
    aws_block_device = AWSBlockDevice.object_with_json(None)
    assert aws_block_device is None


def test_get_awsblockdevice_from_json():
    with open("tests/mocks/block_device.json") as mock_file:
        json_to_parse = json.load(mock_file)
        aws_block_device = AWSBlockDevice.object_with_json(json_to_parse)
        assert aws_block_device.device_name == "/dev/xvda"
        assert aws_block_device.snapshot_id == "snap-4e8fae6b"
        assert aws_block_device.volume_size == 8
        assert aws_block_device.encrypted is False


def test_get_awsec2instance_from_none():
    aws_ec2_instance = AWSEC2Instance.object_with_json(None)
    assert aws_ec2_instance is None


def test_get_awsec2instance_from_json():
    with open("tests/mocks/ec2instance.json") as mock_file:
        json_to_parse = json.load(mock_file)
        aws_ec2_instance = AWSEC2Instance.object_with_json(json_to_parse)
        assert aws_ec2_instance.image_id == "ami-05cf2541"
        assert aws_ec2_instance.tags[0].key == "Name"
        assert aws_ec2_instance.tags[0].value == "test"
        assert aws_ec2_instance.id == "i-096266cb"
        assert aws_ec2_instance.launch_time is not None
        assert aws_ec2_instance.key_name == "test"
        assert aws_ec2_instance.vpc_id == "vpc-6add9f00"


def test_get_ami_from_none():
    ami = AMI.object_with_json(None)
    assert ami is None


def test_get_ami_from_json():
    with open("tests/mocks/ami.json") as mock_file:
        json_to_parse = json.load(mock_file)
        ami = AMI.object_with_json(json_to_parse)
        assert ami.id == "ami-02197662"
        assert ami.virtualization_type == "hvm"
        assert ami.name == "custom-debian-201511040131"
        assert repr(ami) == "AMI: ami-02197662 2015-11-04T01:35:31.000Z"
        assert ami.tags[0].value is not None
        assert ami.tags[0].value is not None
        assert len(ami.tags) == 2
        assert len(ami.block_device_mappings) == 2


def test_models_to_tring():
    assert str(AMI()) is not None
    assert str(AWSBlockDevice()) is not None
    assert str(AWSEC2Instance()) is not None
    assert str(AWSTag()) is not None
