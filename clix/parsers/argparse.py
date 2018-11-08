# -*- encoding: utf-8 -*-
"""
Provides a class with methods that parse the cli correctly.

Parser classes must currently implement the following methods:
    pull_links - Returns a list of links to visit from the API's base url.
    yaml_format - Returns yaml-friendly dict of the compiled data.
    scrape_content - Returns a dict of params and paths from a single page.
"""
import attr
from logzero import logger


@attr.s()
class ArgParse:
    """Parser class for Ruby's APIPie apidoc generator"""

    _data = attr.ib(default={}, repr=False)
    suffix = "--help"

    def yaml_format(self, data):
        """compile all data into a yaml-compatible dict

        if you want to do any special processing on the data, here is the place
        """
        return data

    @staticmethod
    def process_help_text(help_text):
        """Iterate through each line of help text and pull into categories"""
        sub_commands, options, category = [], [], "skip"
        for line in help_text.split("\n"):
            if "help" in line:
                continue
            elif line and category == "sub commands":
                sub_commands.append(line.strip().split()[0])
            elif "--" in line and category == "options":
                line = line.split("--")[1]
                options.append(line.split()[0])
            elif line == "Subcommands:":
                logger.debug("Changing category to debug.")
                category = "sub commands"
            elif line == "Options:":
                logger.debug("Changing category to options.")
                category = "options"
            elif category == "options":
                continue  # handle the case of multi-line helps
            else:
                category = "skip"
        logger.debug(f"sub Commands: {sub_commands}, Options: {options}")
        return sub_commands, options
