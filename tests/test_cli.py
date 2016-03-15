import boto
from moto import mock_ec2

from amicleaner.cli import fetch_available_amis, fetch_running_instances


@mock_ec2
def test_fetch_available_amis():
    assert fetch_available_amis() == {}


@mock_ec2
def test_fetch_running_instances():
    assert fetch_running_instances() == {}
