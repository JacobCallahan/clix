# -*- encoding: utf-8 -*-
"""This module provides the capability to create a new hammer version."""
import attr
from pathlib import Path
from logzero import logger
from clix import helpers
from clix.libtools import hammer


@attr.s()
class LibMaker:
    cli_name = attr.ib(default=None)
    cli_version = attr.ib(default=None)

    def __attrs_post_init__(self):
        if not self.cli_name:
            clis = helpers.get_cli_list()
            if clis:
                self.cli_name = clis[0]
            else:
                logger.warning("No known CLIs found! Try exploring.")
                return

        if not self.cli_version:
            self.cli_version = helpers.get_latest(self.cli_name)

    def make_lib(self):
        if self.cli_name.lower() == "hammer":
            logger.info(
                f"Making a hammer library for {self.cli_version}"
                " at libs/generated/hammer/"
            )
            cli_dict = helpers.load_cli(self.cli_name, self.cli_version)
            hammer_maker = hammer.HammerMaker(
                cli_dict=cli_dict, cli_name=self.cli_name, cli_version=self.cli_version
            )
            hammer_maker.make()
        else:
            logger.warning(f"I don't know how to make a library for {self.cli_name}")
