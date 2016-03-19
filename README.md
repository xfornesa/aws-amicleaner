# aws-amicleaner
Cleanup your old unused ami and related snapshots

[![Circle CI](https://circleci.com/gh/bonclay7/aws-amicleaner/tree/master.svg?style=svg)](https://circleci.com/gh/bonclay7/aws-amicleaner/tree/master)
[![codecov.io](https://codecov.io/github/bonclay7/aws-amicleaner/coverage.svg?branch=master)](https://codecov.io/github/bonclay7/aws-amicleaner?branch=master)

## Description

This tools permits to clean your custom [Amazon Machine Images (AMI)] (http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AMIs.html) and related [EBS Snapshots] (http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSSnapshots.html).

You can either run in `fetch and clean` mode where the tool will retrieve all your private __AMIs__ and EC2 instances, exclude AMIs being holded by your EC2 instances (it can be useful if you use autoscaling, and so on ...). It applies a filter based on  their __names__ or __tags__ and a number of __previous AMIs__ you want to keep.

It can simply remove AMIs with a list of provided ids !

## Prerequisites

-   [awscli](http://docs.aws.amazon.com/cli/latest/userguide/installing.html)
-   [terraform](https://terraform.io/intro/getting-started/install.html)
-   [python 2.7](https://www.python.org/downloads/release/python-2710/)
-   [pyhton pip](https://pip.pypa.io/en/stable/installing/)

This tool assumes your AWS credentials sourced, either with aws credentials variables :

```bash
export AWS_DEFAULT_REGION='your region'
export AWS_ACCESS_KEY_ID='with token Access ID'
export AWS_SECRET_ACCESS_KEY='with token AWS Secret'
```

or with `awscli` :

```bash
export AWS_PROFILE=aa-prod
```
