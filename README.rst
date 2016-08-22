aws-amicleaner
==============

Cleanup your old unused ami and related snapshots

|Circle CI| |codecov.io| |pypi|

Description
-----------

This tools permits to clean your custom `Amazon Machine Images (AMI)
<http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AMIs.html>`__ and
related `EBS Snapshots
<http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSSnapshots.html>`__.

You can either run in ``fetch and clean`` mode where the tool will
retrieve all your private **AMIs** and EC2 instances, exclude AMIs being
holded by your EC2 instances (it can be useful if you use autoscaling,
and so on ...). It applies a filter based on their **names** or **tags**
and a number of **previous AMIs** you want to keep.

It can simply remove AMIs with a list of provided ids !

Prerequisites
-------------

-  `awscli <http://docs.aws.amazon.com/cli/latest/userguide/installing.html>`__
-  `python
   2.7 <https://www.python.org/downloads/release/python-2710/>`__
-  `pyhton pip <https://pip.pypa.io/en/stable/installing/>`__

This tool assumes your AWS credentials sourced, either with aws
credentials variables :

.. code:: bash

    export AWS_DEFAULT_REGION='your region'
    export AWS_ACCESS_KEY_ID='with token Access ID'
    export AWS_SECRET_ACCESS_KEY='with token AWS Secret'

or with ``awscli`` :

.. code:: bash

    export AWS_PROFILE=profile-name

How does it work ?
------------------

To run the script properly, your ``aws`` user must have at least these
permissions in ``iam``:

.. code:: json

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

Getting help
~~~~~~~~~~~~

.. code:: bash

    amicleaner/cli.py --help

Clean a list of AMIs
~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    amicleaner/cli.py --from-ids ami-abcdef01 ami-abcdef02

Fetch and clean
~~~~~~~~~~~~~~~

Print report of groups and amis to be cleaned

.. code:: bash

    amicleaner/cli.py --full-report

Keep previous number of AMIs

.. code:: bash

    amicleaner/cli.py --full-report --keep-previous 10

Regroup by name or tags

.. code:: bash

    amicleaner/cli.py --mapping-key tags --mapping-values role env

Skip confirmation, can be useful for automation

.. code:: bash

    amicleaner/cli.py -f --keep-previous 2

Using virtual env
~~~~~~~~~~~~~~~~~

.. code:: bash

    $ virtualenv env
    $ . env/bin/activate
     (env) aws-amicleaner $ pip install -r requirements.txt
     (env) aws-amicleaner $ amicleaner/cli.py


.. |Circle CI| image:: https://circleci.com/gh/bonclay7/aws-amicleaner/tree/master.svg?style=svg
   :target: https://circleci.com/gh/bonclay7/aws-amicleaner/tree/master
.. |codecov.io| image:: https://codecov.io/github/bonclay7/aws-amicleaner/coverage.svg?branch=master
   :target: https://codecov.io/github/bonclay7/aws-amicleaner?branch=master
.. |pypi| image:: https://img.shields.io/pypi/v/aws-amicleaner.svg
   :target: https://pypi.python.org/pypi/aws-amicleaner
