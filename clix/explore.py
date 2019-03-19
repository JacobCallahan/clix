import asyncio
import sys
import time
from pathlib import Path

import attr
import yaml

import asyncssh
from clix import helpers
from clix.parsers import argparse, hammer, subman
from logzero import logger


@attr.s()
class AsyncExplorer:
    name = attr.ib(default=None)
    version = attr.ib(default=None)
    host = attr.ib(default=None)
    user = attr.ib(default=None)
    password = attr.ib(default=None)
    max_sessions = attr.ib(default=10)
    adjust_max = attr.ib(default=True)
    parser = attr.ib(default=None)
    compact = attr.ib(default=False)
    _data = attr.ib(default={}, repr=False)

    def __attrs_post_init__(self):
        """do some things"""
        if not self.version:
            self.version = time.strftime("%Y-%m-%d", time.localtime())
        # choose the correct parser class from known parsers
        if self.parser.lower() == "hammer":
            self.parser = hammer.Hammer()
        elif self.parser.lower() == "argparse":
            self.parser = argparse.ArgParse()
        elif self.parser.lower() == "subscription-manager":
            self.parser = subman.SubMan()
        if not self.parser or isinstance(self.parser, str):
            logger.warning("No known parser specified! Please review documentation.")
        logger.debug(f"Using parser {self.parser.__class__.__name__}")

        self.conn_args = {
            "host": self.host,
            "username": self.user,
            "password": self.password,
            "known_hosts": None,
        }
        self.sema = asyncio.Semaphore(value=self.max_sessions)

    async def scrape_help(self, prefix, sub=""):
        prefix = "{} {}".format(prefix, sub) if sub else prefix
        command = " ".join([prefix, self.parser.suffix])
        logger.debug(prefix)
        await self.sema.acquire()
        async with asyncssh.connect(**self.conn_args) as conn:
            result = await conn.run(command, check=False)
        self.sema.release()
        if result.exit_status != 0:
            logger.warning(
                f"""Recieved non-zero exit code: {result.exit_status}
                 for command {command}. Result {result.stderr}"""
            )
        help_text = result.stdout
        logger.debug(help_text)
        sub_commands, options = self.parser.process_help_text(help_text)
        # create and run a scrape for each sub command n
        tasks = [
            asyncio.ensure_future(self.scrape_help(prefix, sub_command))
            for sub_command in sub_commands
        ]
        completed = await asyncio.gather(*tasks)
        sorted(completed)
        # loop over the results and pass them up
        subs = {sub_command: results for sub_command, results in completed}
        # put everything together and return the results
        results = {}
        if subs:
            results["sub_commands"] = subs
        if options:
            results["options"] = options
        if len(prefix.split()) == 1:
            self._data = results
        else:
            return sub, results

    def save_results(self):
        """convert the stored data into yaml-friendly dict and save"""
        yaml_data = self.parser.yaml_format(self._data)
        if not yaml_data:
            logger.warning("No data to be saved. Exiting.")
            return
        if self.compact:
            from clix.diff import VersionDiff

            yaml_data = VersionDiff._truncate(yaml_data["sub_commands"])
            fpath = Path(f"CLIs/{self.name}/{self.version}-comp.yaml")
        else:
            fpath = Path(f"CLIs/{self.name}/{self.version}.yaml")
        if fpath.exists():
            logger.warning(f"{fpath} already exists. Deleting..")
            fpath.unlink()
        # create the directory, if it doesn't exist
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fpath.touch()
        logger.info(f"Saving results to {fpath}")
        with fpath.open("w+") as outfile:
            yaml.dump({self.name: yaml_data}, outfile, default_flow_style=False)
        return fpath

    def explore(self):
        """Main function for the explore module"""
        # raise the number of max sessions, if necessary and desired
        if self.adjust_max:
            logger.debug("Attempting to determine the max session count")
            curr_vals = helpers.get_max_connections(self.host, self.user, self.password)
            if not curr_vals:
                logger.warning("Unable to get max connections. Exiting.")
            max_sess = int(curr_vals[0].split()[-1])
            logger.debug(f"Current max sessions {max_sess}")
            if max_sess < self.max_sessions:
                logger.debug(
                    "Current max sessions are lower than desired. Attempting to expand..."
                )
                new_sess_val = helpers.set_max_sessions(
                    curr_vals[0], self.max_sessions, self.host, self.user, self.password
                )
                new_start_val = helpers.set_max_starts(
                    curr_vals[1], self.max_sessions, self.host, self.user, self.password
                )
                if not new_sess_val or not new_start_val:
                    logger.warning(
                        f"Unable to set session values. Reverting to {max_sess}."
                    )
                    self.max_sessions = max_sess
                    self.sema = asyncio.Semaphore(value=self.max_sessions)
                    self.adjust_max = False
                else:
                    helpers.restart_sshd(self.host, self.user, self.password)
            else:
                self.adjust_max = False
        # run the loop to explore the cli
        try:
            asyncio.get_event_loop().run_until_complete(
                self.scrape_help(prefix=self.name)
            )
        except (OSError, asyncssh.Error) as exc:
            logger.warning(f"SSH connection failed: {exc}")
        # revert the session changes, if applied
        if self.adjust_max:
            new_sess_val = helpers.set_max_sessions(
                new_sess_val, curr_vals[0], self.host, self.user, self.password
            )
            new_start_val = helpers.set_max_starts(
                new_start_val, curr_vals[1], self.host, self.user, self.password
            )
