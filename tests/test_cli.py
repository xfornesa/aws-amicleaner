# -*- coding: utf-8 -*-

import json

import boto3
from moto import mock_ec2

from amicleaner.cli import App
from amicleaner.core import AMICleaner
from amicleaner.resources.models import AMI
from amicleaner.utils import parse_args, Printer


@mock_ec2
def test_fetch_and_prepare():
    parser = parse_args(['--keep-previous', '0'])
    assert App(parser).fetch_and_prepare() is None


@mock_ec2
def test_deletion():
    """ Test deletion methods """

    base_ami = "ami-1234abcd"

    parser = parse_args(
        [
            '--keep-previous', '0',
            '--mapping-key', 'name',
            '--mapping-values', 'test-ami']
    )

    conn = boto3.client('ec2')
    reservation = conn.run_instances(
        ImageId=base_ami, MinCount=1, MaxCount=1
    )
    instance = reservation["Instances"][0]

    # create amis
    images = []
    for i in xrange(5):
        image = conn.create_image(
            InstanceId=instance.get("InstanceId"),
            Name="test-ami"
        )
        images.append(image.get("ImageId"))

    # delete one by id
    app = App(parser)
    assert len(AMICleaner(conn).fetch_available_amis()) == 5
    assert app.prepare_delete_amis(
        candidates=[images[4]], from_ids=True
    ) is None
    assert len(AMICleaner(conn).fetch_available_amis()) == 4

    # delete with mapping strategy
    candidates = app.fetch_and_prepare()
    assert len(candidates) == 4
    assert app.prepare_delete_amis(candidates) is None
    assert len(AMICleaner(conn).fetch_available_amis()) == 0


def test_parse_args_no_args():
    parser = parse_args([])
    assert parser.force_delete is False
    assert parser.from_ids is None
    assert parser.from_ids is None
    assert parser.full_report is False
    assert parser.mapping_key is None
    assert parser.mapping_values is None
    assert parser.keep_previous is 4


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


def test_print_report():
    assert Printer.print_report({}) is None

    with open("tests/mocks/ami.json") as mock_file:
        json_to_parse = json.load(mock_file)
        ami = AMI.object_with_json(json_to_parse)
        candidates = {'test': [ami]}
        assert Printer.print_report(candidates) is None
        assert Printer.print_report(candidates, full_report=True) is None


def test_print_failed_snapshots():
    assert Printer.print_failed_snapshots({}) is None
    assert Printer.print_failed_snapshots(["ami-one", "ami-two"]) is None


def test_print_orphan_snapshots():
    assert Printer.print_orphan_snapshots({}) is None
    assert Printer.print_orphan_snapshots(["ami-one", "ami-two"]) is None
