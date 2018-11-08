# -*- encoding: utf-8 -*-
"""Main module for rizza's interface."""
import argparse
import pytest
import sys
from clix.explore import AsyncExplorer
from clix.diff import VersionDiff

from clix.libtools.libmaker import LibMaker
from clix.helpers import get_cli_list, get_ver_list
from clix import logger


class Main(object):
    """This main class will allow for better nested arguments (git stlye)"""

    def __init__(self):
        # self.conf = Config()
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "action",
            type=str,
            choices=["explore", "diff", "makelib", "list", "test"],
            help="The action to perform.",
        )
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.action):
            logger.warning(f"Action {args.action} is not supported.")
            parser.print_help()
            exit(1)
        getattr(self, args.action)()

    def explore(self):
        """Explore a target cli and export the findings"""
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-n",
            "--cli-name",
            type=str,
            required=True,
            help="The name of the command (satellite6).",
        )
        parser.add_argument(
            "-t",
            "--target-host",
            type=str,
            required=True,
            help="The target host's name (my.host.domain.com).",
        )
        parser.add_argument(
            "-a",
            "--auth",
            type=str,
            required=True,
            help="The username/password for the host, sepatated by '/' (root/toor).",
        )
        parser.add_argument(
            "-v",
            "--version",
            type=str,
            default=None,
            help="The cli version we're exploring (6.3).",
        )
        parser.add_argument(
            "-p",
            "--parser",
            type=str,
            default="hammer",
            help="The name of the parser to use when pulling data (hammer).",
        )
        parser.add_argument(
            "--max-sessions",
            type=int,
            default=10,
            help=(
                "The maximum number of concurrent sessions to open. "
                "Note that CLIx will manually set the system's current value higher, if needed."
            ),
        )
        parser.add_argument(
            "--compact",
            action="store_true",
            help="Strip all the extra information from the results.",
        )
        parser.add_argument(
            "--debug", action="store_true", help="Enable debug loggin level."
        )

        args = parser.parse_args(sys.argv[2:])
        if args.debug:
            logger.setup_logzero(level="debug")
        user, pword = args.auth.split("/")
        explorer = AsyncExplorer(
            name=args.cli_name,
            version=args.version,
            host=args.target_host,
            user=user,
            password=pword,
            parser=args.parser,
            max_sessions=args.max_sessions,
            compact=args.compact,
        )
        explorer.explore()
        explorer.save_results()

    def diff(self):
        """Determine the changes between two cli versions"""
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-n",
            "--cli-name",
            type=str,
            default=None,
            help="The name of the cli (satellite6).",
        )
        parser.add_argument(
            "-l",
            "--latest-version",
            type=str,
            default=None,
            help="The latest version of the cli",
        )
        parser.add_argument(
            "-p",
            "--previous-version",
            type=str,
            default=None,
            help="A previous version of the cli",
        )
        parser.add_argument(
            "--compact",
            action="store_true",
            help="Strip all the extra information from the diff.",
        )
        parser.add_argument(
            "--debug", action="store_true", help="Enable debug loggin level."
        )

        args = parser.parse_args(sys.argv[2:])
        if args.debug:
            logger.setup_logzero(level="debug")
        vdiff = VersionDiff(
            cli_name=args.cli_name,
            ver1=args.latest_version,
            ver2=args.previous_version,
            compact=args.compact,
        )
        vdiff.diff()
        vdiff.save_diff()

    def makelib(self):
        """Create a library to interact with a specific cli version"""
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-n",
            "--cli-name",
            type=str,
            default=None,
            help="The name of the cli (satellite6).",
        )
        parser.add_argument(
            "-v",
            "--version",
            type=str,
            default=None,
            help="The cli version we're creating a library for (6.3).",
        )
        parser.add_argument(
            "--debug", action="store_true", help="Enable debug loggin level."
        )

        args = parser.parse_args(sys.argv[2:])
        if args.debug:
            logger.setup_logzero(level="debug")
        libmaker = LibMaker(cli_name=args.cli_name, cli_version=args.version)
        libmaker.make_lib()

    def list(self):
        """List out the cli information we have stored"""
        parser = argparse.ArgumentParser()
        parser.add_argument("subject", type=str, choices=["clis", "versions"])
        parser.add_argument(
            "-n",
            "--cli-name",
            type=str,
            default=None,
            help="The name of the cli you want to list versions of.",
        )

        args = parser.parse_args(sys.argv[2:])

        if args.subject == "clis":
            results = get_cli_list()
            if results:
                print("\n".join(results))
            else:
                print("No CLIs have been explored.")
        elif args.subject == "versions" and args.cli_name:
            results = get_ver_list(args.cli_name)
            if results:
                print("\n".join(results))
            else:
                print(f"No versions have been explored for {args.cli_name}.")

    def test(self):
        """List out some information about our entities and inputs."""
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--args",
            type=str,
            nargs="+",
            help='pytest args to pass in. (--args="-r a")',
        )
        args = parser.parse_args(sys.argv[2:])
        if args.args:
            pyargs = args.args
        else:
            pyargs = ["-q"]
        pytest.cmdline.main(args=pyargs)

    def __repr__(self):
        return None


if __name__ == "__main__":
    Main()
