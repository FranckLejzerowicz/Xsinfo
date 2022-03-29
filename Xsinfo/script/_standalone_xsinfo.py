# ----------------------------------------------------------------------------
# Copyright (c) 2022, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
# ----------------------------------------------------------------------------

import click
from Xsinfo.xsinfo import run_xsinfo
from Xsinfo import __version__


@click.command()
@click.option(
	"--torque/--no-torque", default=False, show_default=True,
	help="Switch from Slurm to Torque."
)
@click.option(
	"--refresh", "--no-refresh", default=False, show_default=True,
	help="Update any sinfo snapshot file written today in ~/.slurm."
)
@click.option(
	"--show", "--no-show", default=False, show_default=True,
	help="Show available cpu and memory per node on top of summaries."
)
@click.version_option(__version__, prog_name="Xsinfo")


def standalone_xsinfo(torque, refresh, show):
	run_xsinfo(torque, refresh, show)


if __name__ == "__main__":
	standalone_xsinfo()
