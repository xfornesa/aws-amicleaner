#!/usr/bin/env python
# set your aws env vars to production

from blessings import Terminal

# =====> Global config
term = Terminal()
stack = "node"


# stack = "nginx"
# ===============


# =====> Global config
term = Terminal()
stack = "move-gateway"
tfstate_key = "frontend"
ami_param = "nginx_ami"
dns_records = [{"Name": "prd-move.aa-aws-relay.com.",
                "Alias":
                    "rest.axa-assistance.com / prd-move.aa-aws-relay.com"},
               {"Name": "sandbox.aa-aws-relay.com.",
                "Alias": "sandbox.aa-aws-relay.com"}]
acct_number = "925434450864"
# ===============