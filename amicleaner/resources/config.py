#!/usr/bin/env python
# set your aws env vars to production

from blessings import Terminal

# terminal colors
TERM = Terminal()

# Number of previous amis to keep based on grouping strategy
#
ROTATION_NUMBER = 5

# the way to regroup AMIs, the default filtering pattern is the creation date
# and the possible other values are :
#
# name : with a grep into the ami name
#        ex: ubuntu => ["ubuntu-20160122", "ubuntu-20160123"]
# tags : with keys provided in GROUPING_STRATEGY_TAGS_KEYS, it filters AMI tags
#        ex: ["Role", "Env"] => ["ubuntu-20160122"]
#
GROUPING_STRATEGY_TYPE = "tags"

GROUPING_STRATEGY_NAME = ""

GROUPING_STRATEGY_TAGS_KEYS = ["environment", "role"]
