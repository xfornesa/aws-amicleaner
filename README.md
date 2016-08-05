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
export AWS_PROFILE=profile-name
```

## How does it work ?

To run the script properly, your `aws` user must have at least
these permissions in `iam`:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Stmt1458638250000",
            "Effect": "Allow",
            "Action": [
                "ec2:DeleteSnapshot",
                "ec2:DeregisterImage",
                "ec2:DescribeImages",
                "ec2:DescribeInstances",
                "ec2:DescribeSnapshots"
            ],
            "Resource": [
                "arn:aws:ec2:::*"
            ]
        }
    ]
}
```

### Getting help

```bash
amicleaner/cli.py --help
```

### Clean a list of AMIs

```bash
amicleaner/cli.py --from-ids ami-abcdef01 ami-abcdef02
```

### Fetch and clean

Print report of groups and amis to be cleaned
```bash
amicleaner/cli.py --full-report
```

Keep previous number of AMIs
```bash
amicleaner/cli.py --full-report --keep-previous 10
```

Regroup by name or tags
```bash
amicleaner/cli.py --mapping-key tags --mapping-values role env
```

Skip confirmation, can be useful for automation
```bash
amicleaner/cli.py -f --keep-previous 2
```

### Using virtual env

```bash
$ virtualenv env
$ . env/bin/activate
 (env) aws-amicleaner $ pip install -r requirements.txt
 (env) aws-amicleaner $ amicleaner/cli.py
```

## Contributing

Issues reporting and pull requests are welcome !

## License

```
The MIT License (MIT)

Copyright (c) 2016 Guy Rodrigue Koffi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
