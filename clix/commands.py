"""Main module for CLIx's interface."""
from rich.console import Console
from rich.table import Table
import rich_click as click

from clix import helpers, logger
from clix.diff import VersionDiff
from clix.explore import AsyncExplorer
from clix.libtools.libmaker import LibMaker

NICKS = {"sat6": "hammer", "satellite": "hammer", "subman": "subscription-manager"}


def _version():
    import pkg_resources

    return pkg_resources.get_distribution("clix").version


@click.group()
@click.version_option(version=_version())
@click.option(
    "--log-level",
    type=click.Choice(["debug", "info", "warning", "error", "critical"]),
    default="info",
    help="The log level to use.",
    callback=lambda ctx, param, value: logger.setup_logzero(value),
    is_eager=True,
    expose_value=False,
)
def cli():
    """CLIx is a tool for exploring and diffing CLI tools."""
    pass


@cli.command()
@click.option(
    "-n",
    "--cli-name",
    type=str,
    required=True,
    help="The name of the command (hammer).",
)
@click.option(
    "-t",
    "--target-host",
    type=str,
    required=True,
    help="The target host's name (my.host.domain.com).",
)
@click.option(
    "-a",
    "--auth",
    type=str,
    required=True,
    help="The username/password for the host, sepatated by '/' (root/toor).",
)
@click.option(
    "-v",
    "--version",
    type=str,
    default=None,
    help="The cli version we're exploring (6.3).",
)
@click.option(
    "-p",
    "--parser",
    type=str,
    default="hammer",
    help="The name of the parser to use when pulling data (hammer).",
)
@click.option(
    "--max-sessions",
    type=int,
    default=10,
    help=(
        "The maximum number of concurrent sessions to open. "
        "Note that CLIx will manually set the system's current value higher, if needed."
    ),
)
@click.option(
    "--data-dir",
    type=str,
    default="./",
    help="The base directory in which to save exports.",
)
@click.option(
    "--compact",
    is_flag=True,
    help="Strip all the extra information from the results.",
)
def explore(cli_name, target_host, auth, version, parser, max_sessions, data_dir, compact):
    """Explore a target cli and export the findings"""

    user, pword = auth.split("/")
    explorer = AsyncExplorer(
        name=NICKS.get(cli_name, cli_name),
        version=version,
        host=target_host,
        user=user,
        password=pword,
        parser=NICKS.get(parser, parser),
        max_sessions=max_sessions,
        data_dir=data_dir,
        compact=compact,
    )
    explorer.explore()
    explorer.save_results()


@cli.command()
@click.option(
    "-n",
    "--cli-name",
    type=str,
    required=True,
    help="The name of the cli (satellite6).",
)
@click.option(
    "-v",
    "--version",
    type=str,
    required=True,
    help="The version of the cli",
)
@click.option(
    "--data-dir",
    type=str,
    default="./",
    help="The base directory in which to save exports.",
)
def compact(cli_name, version, data_dir):
    """Make a compact version of the CLI data"""
    cli_data = helpers.load_cli(cli_name, version, data_dir)
    cli_data = VersionDiff._truncate(cli_data)
    helpers.save_cli(cli_name, version, cli_data, data_dir, True)


@cli.command()
@click.option(
    "-n",
    "--cli-name",
    type=str,
    required=True,
    help="The name of the cli (satellite6).",
)
@click.option(
    "-l",
    "--latest-version",
    type=str,
    required=True,
    help="The latest version of the cli",
)
@click.option(
    "-p",
    "--previous-version",
    type=str,
    required=True,
    help="A previous version of the cli",
)
@click.option(
    "--data-dir",
    type=str,
    default="./",
    help="The base directory in which to save diffs.",
)
@click.option(
    "--compact",
    is_flag=True,
    help="Strip all the extra information from the diff.",
)
def diff(cli_name, latest_version, previous_version, data_dir, compact):
    """Determine the changes between two cli versions"""
    vdiff = VersionDiff(
        cli_name=NICKS.get(cli_name, cli_name),
        ver1=latest_version,
        ver2=previous_version,
        data_dir=data_dir,
        compact=compact,
    )
    vdiff.diff()
    vdiff.save_diff()


@cli.command()
@click.option(
    "-n",
    "--cli-name",
    type=str,
    required=True,
    help="The name of the cli (satellite6).",
)
@click.option(
    "-v",
    "--version",
    type=str,
    required=True,
    help="The cli version we're exploring (6.3).",
)
@click.option(
    "--data-dir",
    type=str,
    default="./",
    help="The base directory in which to save exports.",
)
def makelib(cli_name, version, data_dir):
    """Create a library to interact with a specific cli version"""
    libmaker = LibMaker(
        cli_name=NICKS.get(cli_name, cli_name),
        cli_version=version,
        data_dir=data_dir,
    )
    libmaker.make_lib()


@cli.command()
@click.argument("subject", type=click.Choice(["clis", "versions"]))
@click.option(
    "-n",
    "--cli-name",
    type=str,
    default=None,
    help="The name of the cli you want to list versions of.",
)
@click.option(
    "--data-dir",
    type=str,
    default="./",
    help="The base directory in which to search for saved exports.",
)
def list(subject, cli_name, data_dir):
    """List out the cli information we have stored"""
    console = Console()
    if subject == "clis":
        results = helpers.get_cli_list(data_dir)
        if results:
            table = Table(title="Available CLIs")
            table.add_column("CLI Name", style="cyan")
            for cli_name_result in results:
                table.add_row(cli_name_result)
            console.print(table)
        else:
            console.print(f"No CLIs have been found in {data_dir}.")
    elif subject == "versions" and NICKS.get(cli_name, cli_name):
        results = helpers.get_ver_list(NICKS.get(cli_name, cli_name), data_dir)
        if results:
            table = Table(title=f"Available Versions for {NICKS.get(cli_name, cli_name)}")
            table.add_column("Version", style="cyan")
            for version in results:
                table.add_row(version)
            console.print(table)
        else:
            console.print(
                "No versions have been explored for "
                f"{NICKS.get(cli_name, cli_name)} in directory {data_dir}."
            )


if __name__ == "__main__":
    cli()
