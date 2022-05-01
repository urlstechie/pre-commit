from __future__ import annotations

# Copyright (c) 2022 Vanessa Sochat and Ayoub Malek
# This source code is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

import argparse
import re
import os
import sys
import logging

from urlchecker.main.github import clone_repo, delete_repo
from urlchecker.core.fileproc import remove_empty
from urlchecker.core.check import UrlChecker
from urlchecker.logger import print_failure

logger = logging.getLogger("urlchecker")


def get_parser():
    # Flatten parser to just be check command
    parser = argparse.ArgumentParser(description="urlchecker python pre-commit")
    parser.add_argument(
        "path",
        help="the local path or GitHub repository to clone and check",
    )

    parser.add_argument(
        "-b",
        "--branch",
        help="if cloning, specify a branch to use (defaults to main)",
        default="main",
    )

    parser.add_argument(
        "--subfolder",
        help="relative subfolder path within path (if not specified, we use root)",
    )

    parser.add_argument(
        "--cleanup",
        help="remove root folder after checking (defaults to False, no cleaup)",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--force-pass",
        help="force successful pass (return code 0) regardless of result",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--no-print",
        help="Skip printing results to the screen (defaults to printing to console).",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--verbose",
        help="Print file names for failed urls in addition to the urls.",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--file-types",
        dest="file_types",
        help="comma separated list of file extensions to check (defaults to .md,.py)",
        default=".md,.py",
    )

    # Here we separate out filenames (provided by pre-commit) and extra patterns
    # to filter over (--patterns) which is --files in the urlchecker
    parser.add_argument("filenames", nargs="*")
    parser.add_argument(
        "--patterns",
        dest="patterns",
        help="patterns to check.",
        default="",
    )

    parser.add_argument(
        "--exclude-urls",
        help="comma separated links to exclude (no spaces)",
        default="",
    )

    parser.add_argument(
        "--exclude-patterns",
        help="comma separated list of patterns to exclude (no spaces)",
        default="",
    )

    parser.add_argument(
        "--exclude-files",
        help="comma separated list of files and patterns to exclude (no spaces)",
        default="",
    )

    # Saving

    parser.add_argument(
        "--save",
        help="Path to a csv file to save results to.",
        default=None,
    )

    # Timeouts

    parser.add_argument(
        "--retry-count",
        help="retry count upon failure (defaults to 2, one retry).",
        type=int,
        default=2,
    )

    parser.add_argument(
        "--timeout",
        help="timeout (seconds) to provide to the requests library (defaults to 5)",
        type=int,
        default=5,
    )
    return parser


def check(args):
    """
    Main entrypoint for running a check. We expect an args object with
    arguments from the main client. From here we determine the path
    to parse (or GitHub url to clone) and call the main check function
    under main/check.py

    Args:
      - args  : the argparse ArgParser with parsed args
      - extra : extra arguments not handled by the parser
    """
    path = args.path

    # Case 1: specify present working directory
    if not path or path == ".":
        path = os.getcwd()

    # Case 2: git clone isn't supported for a pre-commit hook
    elif re.search("^(git@|http)", path):
        logging.error("Repository url %s detected, not supported for pre-commit hook.")
        return 1

    # Add subfolder to path
    if args.subfolder:
        path = os.path.join(path, args.subfolder)

    # By the time we get here, a path must exist
    if not os.path.exists(path):
        logger.error("Error %s does not exist." % path)
        return 1

    logging.debug("Path specified as present working directory, %s" % path)

    # Parse file types, and excluded urls and files (includes absolute and patterns)
    file_types = args.file_types.split(",")
    exclude_urls = remove_empty(args.exclude_urls.split(","))
    exclude_patterns = remove_empty(args.exclude_patterns.split(","))
    exclude_files = remove_empty(args.exclude_files.split(","))

    # Do we have any patterns to filter (regular expressions)?
    patterns = None
    if args.patterns:
        logger.debug("Found patterns of files to filter to.")
        patterns = "(%s)" % "|".join(args.patterns)

    # Process the files
    files = []
    for filename in args.filenames:
        if not filename or not os.path.exists(filename):
            logger.error("%s does not exist, skipping." % filename)
            continue
        if patterns and not re.search(patterns, filename):
            continue
        files.append(filename)

    # Alert user about settings
    print("           original path: %s" % args.path)
    print("              final path: %s" % path)
    print("               subfolder: %s" % args.subfolder)
    print("                  branch: %s" % args.branch)
    print("                 cleanup: %s" % args.cleanup)
    print("              file types: %s" % file_types)
    print("                   files: %s" % files)
    print("               print all: %s" % (not args.no_print))
    print("                 verbose: %s" % (args.verbose))
    print("           urls excluded: %s" % exclude_urls)
    print("   url patterns excluded: %s" % exclude_patterns)
    print("  file patterns excluded: %s" % exclude_files)
    print("              force pass: %s" % args.force_pass)
    print("             retry count: %s" % args.retry_count)
    print("                    save: %s" % args.save)
    print("                 timeout: %s" % args.timeout)

    # Instantiate a new checker with provided arguments
    checker = UrlChecker(
        path=path,
        file_types=file_types,
        include_patterns=files,
        exclude_files=exclude_files,
        print_all=not args.no_print,
    )
    check_results = checker.run(
        exclude_urls=exclude_urls,
        exclude_patterns=exclude_patterns,
        retry_count=args.retry_count,
        timeout=args.timeout,
    )

    # save results to file, if save indicated
    if args.save:
        checker.save_results(args.save)

    # Case 1: We didn't find any urls to check
    if not check_results["failed"] and not check_results["passed"]:
        print("\n\n\U0001F937. No urls were collected.")
        return 0

    # Case 2: We had errors, print them for the user
    if check_results["failed"]:
        if args.verbose:
            print("\n\U0001F914 Uh oh... The following urls did not pass:")
            for file_name, result in checker.checks.items():
                if result["failed"]:
                    print_failure(file_name + ":")
                    for url in result["failed"]:
                        print_failure("     " + url)
        else:
            print("\n\U0001F914 Uh oh... The following urls did not pass:")
            for failed_url in check_results["failed"]:
                print_failure(failed_url)

    # If we have failures and it's not a force pass, exit with 1
    if not args.force_pass and check_results["failed"]:
        return 1

    # Finally, alert user if we are passing conditionally
    if check_results["failed"]:
        print("\n\U0001F928 Conditional pass force pass True.")
    else:
        print("\n\n\U0001F389 All URLS passed!")
    return 0


def main(argv: Sequence[str] | None = None) -> int:

    parser = get_parser()
    args = parser.parse_args(argv)

    # Get the return value to return to pre-commit
    return check(args)


if __name__ == "__main__":
    raise SystemExit(main())
