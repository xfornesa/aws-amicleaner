from datetime import datetime
from moto import mock_ec2

from amicleaner.cli import fetch_available_amis, fetch_running_instances
from amicleaner.cli import filter_unused_amis
from amicleaner.resources.models import AMI, AWSEC2Instance


@mock_ec2
def test_fetch_available_amis():
    assert fetch_available_amis() == {}


@mock_ec2
def test_fetch_running_instances():
    assert fetch_running_instances() == {}


def test_filter_unused_amis_with_null_arguments():
    assert filter_unused_amis() == {}


def test_filter_unused_amis():
    # creating tests objects
    first_ami = AMI()
    first_ami.id = 'ami-28c2b348'
    first_ami.creation_date = datetime.now()

    first_instance = AWSEC2Instance()
    first_instance.id = 'i-9f9f6a2a'
    first_instance.name = "first-instance"
    first_instance.image_id = first_ami.id
    first_instance.launch_time = datetime.now()

    second_ami = AMI()
    second_ami.id = 'unused-ami'
    second_ami.creation_date = datetime.now()

    second_instance = AWSEC2Instance()
    second_instance.id = 'i-9f9f6a2a'
    second_instance.name = "second-instance"
    second_instance.image_id = first_ami.id
    second_instance.launch_time = datetime.now()

    # constructing dicts
    amis_dict = dict()
    amis_dict[first_ami.id] = first_ami
    amis_dict[second_ami.id] = second_ami

    instances_dict = dict()
    instances_dict[first_instance.image_id] = instances_dict
    instances_dict[second_instance.image_id] = second_instance

    # testing filter
    unused_ami_dict = filter_unused_amis(amis_dict, instances_dict)
    assert len(unused_ami_dict) == 1
    assert amis_dict.get('unused-ami') is not None
