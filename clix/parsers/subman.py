"""
Provides a class with methods that parse the cli correctly.

Parser classes must currently implement the following methods:
    process_help_text - Returns a list of sub command and a list of options.
    yaml_format - Returns yaml-friendly dict of the compiled data.

Additionally, each parser class must have a suffix
"""
import attr
from logzero import logger


@attr.s()
class SubMan:
    """Parser class for subscription-manager"""

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
        for line in help_text.splitlines():
            line = line.strip()  # noqa: PLW2901 - want to clean extra spaces
            if "help" in line or not line:
                continue
            if " Modules:" in line:
                logger.debug("Changing category to subcommands.")
                category = "sub commands"
            elif line and category == "sub commands":
                sub_commands.append(line.split()[0])
            elif "--" in line and category == "options":
                line = line.split("--")[1]  # noqa: PLW2901 - not used downstream
                options.append(line.split()[0])
            elif line == "Options:":
                logger.debug("Changing category to options.")
                category = "options"
            elif category == "options":
                continue  # handle the case of multi-line helps
            else:
                category = "skip"
        logger.debug(f"sub Commands: {sub_commands}, Options: {options}")
        return sub_commands, options
