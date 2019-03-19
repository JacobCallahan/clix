# -*- encoding: utf-8 -*-
"""This module provides the capability to create a new hammer version."""
import attr
import yaml
from pathlib import Path
from logzero import logger
from clix.helpers import clean_keywords, shift_text


@attr.s()
class CommandMaker:
    cli_dict = attr.ib(repr=False)
    cli_name = attr.ib()
    cli_version = attr.ib()

    @staticmethod
    def name_to_proper_name(command_name):
        """Convert an command name to a class name. cmd_name => Cmd Name"""
        if command_name[-1] == "s":  # we don't want pluralized names
            command_name = command_name[:-1]
        return " ".join(x.capitalize() for x in command_name.split("-"))

    @staticmethod
    def name_to_class(command_name):
        """Convert an command name to a class name. cmd_name => CmdName"""
        if command_name[-1] == "s":  # we don't want pluralized names
            command_name = command_name[:-1]
        return "".join(x.capitalize() for x in command_name.split("-"))

    @staticmethod
    def get_opts(options):
        """SubMan options often take the form of rhsmcertd.splay=RHSMCERTD.SPLAY
            we want to turn that into rhsmcertd_splay
        """
        if not options:
            return options
        elif isinstance(options, list):
            return [CommandMaker.get_opts(opt) for opt in options]
        else:
            return options.split("=")[0].replace(".", "_")

    def fill_subcommand_class_template(self, yaml_data, command_path=None):
        """Load and fill out a method template for every method"""
        command_path = command_path if command_path else self.cli_name
        command_name = command_path.split(" ")[-1]
        logger.debug(f"Filling class for {command_name}.")
        logger.debug(yaml_data)
        # load the template
        cmd_temp_f = Path("libs/templates/hammer/subcommand_class.template")
        if not cmd_temp_f.exists():
            logger.error(f"Unable to find {cmd_temp_f.absolute()}.")
            return
        loaded_template = None
        with cmd_temp_f.open("r+") as f_load:
            loaded_template = f_load.read()

        # fill the template for each method
        # construct the text that replaces ~~class command options~~
        class_command_options = "\n".join(
            [f"'{self.get_opts(opt)}'," for opt in yaml_data.get("options", [])]
        )
        if class_command_options:
            class_command_options = "\n".join(class_command_options)
            class_command_options = shift_text(class_command_options, 3)
        # Construct the text that replaces ~~sub classes~~
        sub_classes, sub_commands = [], []
        for sub_command, contents in yaml_data.get("sub_commands", {}).items():
            if contents.get("sub_commands"):
                sub_classes.append(
                    [
                        sub_command,
                        self.fill_subcommand_class_template(
                            contents, f"{command_path} {sub_command}"
                        ),
                    ]
                )
            else:
                sub_commands.append(
                    self.fill_method_template(
                        self.name_to_proper_name(command_name),
                        sub_command,
                        self.get_opts(contents.get("options")),
                    )
                )
        subclass_assignments = [
            f"self.{subclass[0].replace('-','_')} = self.{self.name_to_class(subclass[0])}()"
            for subclass in sub_classes
        ]
        if subclass_assignments:
            subclass_assignments = "\n".join(subclass_assignments)
            subclass_assignments = f"{shift_text(subclass_assignments, 2)}\n\n"
        else:
            subclass_assignments = ""

        sub_classes = shift_text(
            "\n".join(sub_class[1] for sub_class in sub_classes), 1
        )
        sub_commands = "\n".join(sub_commands)

        loaded_template = loaded_template.replace(
            "~~SubCommandClass~~", clean_keywords(self.name_to_class(command_name))
        )
        loaded_template = loaded_template.replace(
            "~~CLIBaseClass~~", self.name_to_class(self.cli_name)
        )
        loaded_template = loaded_template.replace(
            "~~SubCommand Name~~", self.name_to_proper_name(command_name)
        )
        loaded_template = loaded_template.replace("~~command path~~", command_path)
        loaded_template = loaded_template.replace(
            "~~class command options~~", class_command_options
        )
        loaded_template = loaded_template.replace(
            "~~subclass assignments~~", subclass_assignments
        )
        loaded_template = loaded_template.replace(
            "~~sub classes~~", f"{sub_classes}\n\n"
        )
        loaded_template = loaded_template.replace("~~sub commands~~", sub_commands)
        return loaded_template

    def fill_method_template(self, parent_name, command, options):
        """Fill out and return an method template, based on `command`"""
        logger.debug(f"Generating {parent_name}'s method: {command}")
        if options:
            compiled_options = "\n".join([f"'{opt}'," for opt in options])
        else:
            compiled_options = ""
        # load the template
        cmd_temp_f = Path("libs/templates/hammer/command_method.template")
        if not cmd_temp_f.exists():
            logger.error(f"Unable to find {cmd_temp_f.absolute()}.")
            return
        loaded_t = None
        with cmd_temp_f.open("r+") as f_load:
            loaded_t = f_load.read()

        # fill the template
        loaded_t = loaded_t.replace(
            "~~method_name~~", clean_keywords(command.replace("-", "_"))
        )
        loaded_t = loaded_t.replace("~~SubCommand Name~~", parent_name)
        loaded_t = loaded_t.replace(
            "~~method name~~", self.name_to_proper_name(command)
        )
        loaded_t = loaded_t.replace("~~options~~", shift_text(compiled_options, 3))
        loaded_t = loaded_t.replace("~~command~~", command)
        return loaded_t

    def create_library_file(self):
        """Populate a library file with filled command templates"""
        library_file = Path("libs/templates/hammer/main.py.template")
        if not library_file.exists():
            logger.error(f"Unable to find {library_file}.")
            return

        logger.debug(f"Creating {self.cli_name}.py file.")
        compiled_options = "\n".join(
            [f"'{self.get_opts(opt)}'," for opt in self.cli_dict[self.cli_name].get("options", [])]
        )

        sub_classes, sub_methods = [], []
        for command, contents in (
            self.cli_dict[self.cli_name].get("sub_commands", {}).items()
        ):
            if "sub_commands" in contents:
                sub_classes.append(
                    [
                        command,
                        self.fill_subcommand_class_template(
                            contents, f"{self.cli_name} {command}"
                        ),
                    ]
                )
            else:
                sub_methods.append(
                    self.fill_method_template(
                        self.cli_name, command, self.get_opts(contents.get("options"))
                    )
                )

        subclass_assignments = [
            f"self.{subclass[0].replace('-','_')} = self.{self.name_to_class(subclass[0])}()"
            for subclass in sub_classes
        ]
        if subclass_assignments:
            subclass_assignments = "\n".join(subclass_assignments)
            subclass_assignments = f"{shift_text(subclass_assignments, 2)}\n\n"
        else:
            subclass_assignments = ""

        loaded_cmd_f = None
        with library_file.open("r+") as cmd_file:
            loaded_cmd_f = cmd_file.read()

        loaded_cmd_f = loaded_cmd_f.replace(
            "~~Project Name~~", self.name_to_proper_name(self.cli_name)
        )
        loaded_cmd_f = loaded_cmd_f.replace(
            "~~MainCommandClass~~", self.name_to_class(self.cli_name)
        )
        loaded_cmd_f = loaded_cmd_f.replace("~~main command~~", self.cli_name)
        loaded_cmd_f = loaded_cmd_f.replace(
            "~~command options~~", shift_text(compiled_options, 3)
        )
        loaded_cmd_f = loaded_cmd_f.replace(
            "~~subclass assignments~~", subclass_assignments
        )
        loaded_cmd_f = loaded_cmd_f.replace(
            "~~sub methods~~", shift_text("\n".join(sub_methods), 1)
        )
        loaded_cmd_f = loaded_cmd_f.replace(
            "~~sub classes~~",
            shift_text("\n".join([subclass[1] for subclass in sub_classes]), 0),
        )

        save_file = Path(f"libs/generated/subscription-manager/{self.cli_version}/{self.cli_name}.py")
        if save_file.exists():
            logger.warning(f"Overwriting {save_file}")
            save_file.unlink()
        # create the directory, if it doesn't exist
        save_file.parent.mkdir(parents=True, exist_ok=True)
        save_file.touch()
        logger.info(f"Saving results to {save_file}")
        with save_file.open("w+") as outfile:
            outfile.write(loaded_cmd_f)


@attr.s()
class SubManMaker:
    cli_dict = attr.ib(repr=False)
    cli_name = attr.ib()
    cli_version = attr.ib()

    def make(self):
        """Make all the changes needed to create a hammer library version"""
        command_maker = CommandMaker(
            self.cli_dict, clean_keywords(self.cli_name), self.cli_version
        )
        command_maker.create_library_file()
