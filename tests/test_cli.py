import json

from datetime import datetime
from moto import mock_ec2

from amicleaner.cli import AMICleaner, parse_args, fetch_and_prepare
from amicleaner.cli import print_report
from amicleaner.resources.models import AMI, AWSEC2Instance, AWSTag


@mock_ec2
def test_fetch_available_amis():
    assert AMICleaner().fetch_available_amis() == {}


@mock_ec2
def test_fetch_instances():
    assert AMICleaner().fetch_instances() == {}


def test_fetch_candidates():
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
    unused_ami_dict = AMICleaner().fetch_candidates(amis_dict, instances_dict)
    assert len(unused_ami_dict) == 1
    assert amis_dict.get('unused-ami') is not None


def test_map_candidates_with_null_arguments():
    assert AMICleaner().map_candidates({}, {}) == {}


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

    tags_values_string = AMICleaner.tags_values_to_string(tags, filters)
    assert tags_values_string is not None
    assert tags_values_string == "Value2.Value3"


def test_tags_values_to_string_with_none():
    assert AMICleaner.tags_values_to_string(None) is None


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

    tags_values_string = AMICleaner.tags_values_to_string(tags, filters)
    assert tags_values_string is not None
    assert tags_values_string == "Value1.Value2.Value3"


def test_map_with_names():
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
    candidates = [first_ami, second_ami, third_ami]

    # grouping strategy
    grouping_strategy = {"key": "name", "values": ["ubuntu", "debian"]}

    grouped_amis = AMICleaner().map_candidates(candidates, grouping_strategy)
    assert grouped_amis is not None
    assert len(grouped_amis.get('ubuntu')) == 2
    assert len(grouped_amis.get('debian')) == 1


def test_map_with_tags():
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
    candidates = [first_ami, second_ami, third_ami]

    # grouping strategy
    grouping_strategy = {"key": "tags", "values": ["stack", "env"]}
    grouped_amis = AMICleaner().map_candidates(candidates, grouping_strategy)
    assert grouped_amis is not None
    assert len(grouped_amis.get("prod")) == 1
    assert len(grouped_amis.get("prod.web-server")) == 2


def test_reduce_without_rotation_number():
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
    candidates = [second_ami, third_ami, first_ami]

    assert AMICleaner().reduce_candidates(candidates) == candidates


def test_reduce():
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
    candidates = [second_ami, third_ami, first_ami]
    rotation_number = 2
    cleaner = AMICleaner()
    left = cleaner.reduce_candidates(candidates, rotation_number)
    assert len(left) == 1
    assert left[0].id == first_ami.id

    # keep 1 recent ami
    rotation_number = 1
    left = cleaner.reduce_candidates(candidates, rotation_number)
    assert len(left) == 2
    assert left[0].id == second_ami.id

    # keep 5 recent amis
    rotation_number = 5
    left = cleaner.reduce_candidates(candidates, rotation_number)
    assert len(left) == 0


@mock_ec2
def test_remove_ami():
    cleaner = AMICleaner()

    with open("tests/mocks/ami.json") as mock_file:
        json_to_parse = json.load(mock_file)
        ami = AMI.object_with_json(json_to_parse)

        assert cleaner.remove_amis(None) is True
        # assert cleaner.remove_amis([ami]) is True


@mock_ec2
def test_remove_ami_from_ids():
    cleaner = AMICleaner()
    assert cleaner.remove_amis_from_ids(None) is False
    # assert cleaner.remove_amis_from_ids(["ami-02197662"]) is True


def test_parse_args_no_args():
    parser = parse_args([])
    assert parser.force_delete is False
    assert parser.from_ids is None
    assert parser.from_ids is None
    assert parser.full_report is False
    assert parser.mapping_key is None
    assert parser.mapping_values is None
    assert parser.keep_previous is None


def test_parse_args():
    parser = parse_args(['--keep-previous', '10', '--full-report'])
    assert parser.keep_previous == 10
    assert parser.full_report is True

    parser = parse_args(['--mapping-key', 'name'])
    assert parser is None

    parser = parse_args(['--mapping-key', 'tags',
                         '--mapping-values', 'group1', 'group2'])
    assert parser.mapping_key == "tags"
    assert len(parser.mapping_values) == 2


@mock_ec2
def test_fetch_and_prepare():
    assert fetch_and_prepare({}, 0) is None


def test_print_report():
    assert print_report({}) is None

    with open("tests/mocks/ami.json") as mock_file:
        json_to_parse = json.load(mock_file)
        ami = AMI.object_with_json(json_to_parse)
        candidates = {'test': [ami]}
        assert print_report(candidates) is None
