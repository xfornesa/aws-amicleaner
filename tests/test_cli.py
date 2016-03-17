from datetime import datetime, date
from moto import mock_ec2

from amicleaner.cli import fetch_available_amis, fetch_running_instances
from amicleaner.cli import filter_unused_amis, apply_grouping_strategy
from amicleaner.cli import tags_values_to_string, apply_rotation_strategy
from amicleaner.resources.models import AMI, AWSEC2Instance, AWSTag


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


def test_apply_grouping_strategy_with_null_arguments():
    assert apply_grouping_strategy({}, {}) == {}


def test_tags_values_to_string():
    first_tag = AWSTag()
    first_tag.key = "Key1"
    first_tag.value = "Value1"

    second_tag = AWSTag()
    second_tag.key = "Key2"
    second_tag.value = "Value2"

    third_tag = AWSTag()
    third_tag.key = "Key3"
    third_tag.value = "Value3"

    fourth_tag = AWSTag()
    fourth_tag.key = "Key4"
    fourth_tag.value = "Value4"

    tags = [first_tag, third_tag, second_tag, fourth_tag]
    filters = ["Key2", "Key3"]

    tags_values_string = tags_values_to_string(tags, filters)
    assert tags_values_string is not None
    assert tags_values_string == "Value2.Value3"


def test_tags_values_to_string_without_filters():
    first_tag = AWSTag()
    first_tag.key = "Key1"
    first_tag.value = "Value1"

    second_tag = AWSTag()
    second_tag.key = "Key2"
    second_tag.value = "Value2"

    third_tag = AWSTag()
    third_tag.key = "Key3"
    third_tag.value = "Value3"

    tags = [first_tag, third_tag, second_tag]
    filters = []

    tags_values_string = tags_values_to_string(tags, filters)
    assert tags_values_string is not None
    assert tags_values_string == "Value1.Value2.Value3"


def test_apply_grouping_strategy_with_names():

    # creating tests objects
    first_ami = AMI()
    first_ami.id = 'ami-28c2b348'
    first_ami.name = "ubuntu-20160102"
    first_ami.creation_date = datetime.now()

    second_ami = AMI()
    second_ami.id = 'ami-28c2b349'
    second_ami.name = "ubuntu-20160103"
    second_ami.creation_date = datetime.now()

    third_ami = AMI()
    third_ami.id = 'ami-28c2b350'
    third_ami.name = "debian-20160104"
    third_ami.creation_date = datetime.now()

    # creating amis to drop dict
    unused_ami = dict()
    unused_ami[first_ami.id] = first_ami
    unused_ami[second_ami.id] = second_ami
    unused_ami[third_ami.id] = third_ami

    # grouping strategy
    grouping_strategy = {"key": "name", "values": ["ubuntu", "debian"]}
    grouped_amis = apply_grouping_strategy(unused_ami, grouping_strategy)
    assert grouped_amis is not None
    assert len(grouped_amis.get('ubuntu')) == 2
    assert len(grouped_amis.get('debian')) == 1


def test_apply_grouping_strategy_with_tags():

    # tags
    stack_tag = AWSTag()
    stack_tag.key = "stack"
    stack_tag.value = "web-server"

    env_tag = AWSTag()
    env_tag.key = "env"
    env_tag.value = "prod"

    # creating tests objects
    # prod and web-server
    first_ami = AMI()
    first_ami.id = 'ami-28c2b348'
    first_ami.name = "ubuntu-20160102"
    first_ami.tags.append(stack_tag)
    first_ami.tags.append(env_tag)
    first_ami.creation_date = datetime.now()

    # just prod
    second_ami = AMI()
    second_ami.id = 'ami-28c2b349'
    second_ami.name = "ubuntu-20160103"
    second_ami.tags.append(env_tag)
    second_ami.creation_date = datetime.now()

    # prod and web-server
    third_ami = AMI()
    third_ami.id = 'ami-28c2b350'
    third_ami.name = "debian-20160104"
    third_ami.tags.append(stack_tag)
    third_ami.tags.append(env_tag)
    third_ami.creation_date = datetime.now()

    # creating amis to drop dict
    unused_ami = dict()
    unused_ami[first_ami.id] = first_ami
    unused_ami[second_ami.id] = second_ami
    unused_ami[third_ami.id] = third_ami

    # grouping strategy
    grouping_strategy = {"key": "tags", "values": ["stack", "env"]}
    grouped_amis = apply_grouping_strategy(unused_ami, grouping_strategy)
    assert grouped_amis is not None
    assert len(grouped_amis.get("prod")) == 1
    assert len(grouped_amis.get("prod.web-server")) == 2


def test_apply_rotation_strategy_without_rotation_number():
    # creating tests objects
    first_ami = AMI()
    first_ami.id = 'ami-28c2b348'
    first_ami.name = "ubuntu-20160102"
    first_ami.creation_date = datetime(2016, 1, 10)

    # just prod
    second_ami = AMI()
    second_ami.id = 'ami-28c2b349'
    second_ami.name = "ubuntu-20160103"
    second_ami.creation_date = datetime(2016, 1, 11)

    # prod and web-server
    third_ami = AMI()
    third_ami.id = 'ami-28c2b350'
    third_ami.name = "debian-20160104"
    third_ami.creation_date = datetime(2016, 1, 12)

    # creating amis to drop dict
    unused_ami = [second_ami, third_ami, first_ami]

    assert apply_rotation_strategy(unused_ami) == unused_ami


def test_apply_rotation_strategy():
    # creating tests objects
    first_ami = AMI()
    first_ami.id = 'ami-28c2b348'
    first_ami.name = "ubuntu-20160102"
    first_ami.creation_date = datetime(2016, 1, 10)

    # just prod
    second_ami = AMI()
    second_ami.id = 'ami-28c2b349'
    second_ami.name = "ubuntu-20160103"
    second_ami.creation_date = datetime(2016, 1, 11)

    # prod and web-server
    third_ami = AMI()
    third_ami.id = 'ami-28c2b350'
    third_ami.name = "debian-20160104"
    third_ami.creation_date = datetime(2016, 1, 12)

    # keep 2 recent amis
    unused_ami = [second_ami, third_ami, first_ami]
    rotation_number = 2
    left = apply_rotation_strategy(unused_ami, rotation_number)
    assert len(left) == 1
    assert left[0].id == first_ami.id

    # keep 1 recent ami
    rotation_number = 1
    left = apply_rotation_strategy(unused_ami, rotation_number)
    assert len(left) == 2
    assert left[0].id == second_ami.id

    # keep 5 recent amis
    rotation_number = 5
    left = apply_rotation_strategy(unused_ami, rotation_number)
    assert len(left) == 0
