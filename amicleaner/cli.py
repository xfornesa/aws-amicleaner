#!/usr/bin/env python
import sys

from core import AMICleaner, OrphanSnapshotCleaner
from resources.config import MAPPING_KEY, MAPPING_VALUES
from resources.config import TERM
from utils import Printer, parse_args


class App:

    def __init__(self, args):

        self.mapping_key = args.mapping_key or MAPPING_KEY
        self.mapping_values = args.mapping_values or MAPPING_VALUES
        self.keep_previous = args.keep_previous
        self.skip_orphans = args.skip_orphans
        self.from_ids = args.from_ids
        self.full_report = args.full_report
        self.force_delete = args.force_delete

        self.mapping_strategy = {
            "key": self.mapping_key,
            "values": self.mapping_values,
        }

    def fetch_and_prepare(self):

        """ Uses AMICleaner to retrieve candidates AMI, map and reduce """

        cleaner = AMICleaner()

        mapped_amis = cleaner.map_candidates(
            mapping_strategy=self.mapping_strategy
        )

        if not mapped_amis:
            return None

        candidates = []
        report = dict()

        for group_name, amis in mapped_amis.iteritems():
            group_name = group_name or ""

            if not group_name:
                report["no-tags (excluded)"] = amis
            else:
                reduced = cleaner.reduce_candidates(amis, self.keep_previous)
                if reduced:
                    report[group_name] = reduced
                    candidates.extend(reduced)

        Printer.print_report(report, self.full_report)

        return candidates

    def prepare_delete_amis(self, candidates, from_ids=False):

        """ prepare deletion of candidates AMIs"""

        failed = []

        if from_ids:
            print TERM.bold("\nCleaning from {} AMI id(s) ...".format(
                len(candidates))
            )
            failed = AMICleaner().remove_amis_from_ids(candidates)
        else:
            print TERM.bold("\nCleaning {} AMIs ...".format(len(candidates)))
            failed = AMICleaner().remove_amis(candidates)

        if failed:
            print TERM.red("\n{0} failed snapshots".format(len(failed)))
            Printer.print_failed_snapshots(failed)

    def clean_orphans(self):

        """ Find and removes orphan snapshots """

        cleaner = OrphanSnapshotCleaner()
        snaps = cleaner.fetch()

        Printer.print_orphan_snapshots(snaps)

        answer = raw_input(
            "Do you want to continue and remove {} orphan snapshots "
            "[y/N] ? : ".format(len(snaps)))
        confirm = (answer.lower() == "y")

        if confirm:
            print "Removing orphan snapshots... "
            cleaner.clean(snaps[:2])

    def print_defaults(self):

        print TERM.bold("\nDefault values : ==>")
        print TERM.green("mapping_key : {0}".format(self.mapping_key))
        print TERM.green("mapping_values : {0}".format(self.mapping_values))
        print TERM.green("keep_previous : {0}".format(self.keep_previous))

    def run_cli(self):

        if not self.skip_orphans:
            self.clean_orphans()

        if self.from_ids:
            self.prepare_delete_amis(self.from_ids, from_ids=True)
        else:
            # print defaults
            self.print_defaults()

            print TERM.bold("\nRetrieving AMIs to clean ...")
            candidates = self.fetch_and_prepare()

            if not candidates:
                sys.exit(0)

            delete = False

            if not self.force_delete:
                answer = raw_input(
                    "Do you want to continue and remove {} AMIs "
                    "[y/N] ? : ".format(len(candidates)))
                delete = (answer.lower() == "y")
            else:
                delete = True

            if delete:
                self.prepare_delete_amis(candidates)


def main():

    args = parse_args(sys.argv[1:])
    if not args:
        sys.exit(1)

    app = App(args)
    app.run_cli()


if __name__ == "__main__":
    main()
