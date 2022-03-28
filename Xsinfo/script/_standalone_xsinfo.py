# ----------------------------------------------------------------------------
# Copyright (c) 2022, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import click
from Xsinfo.xsinfo import run_xsinfo
from Xsinfo import __version__


@click.command()
@click.option(
	"--torque/--no-torque", default=False, show_default=True,
	help="Switch from Slurm to Torque"
)
@click.option(
	"--refresh", "--no-refresh", default='', type=str,
	help="Whether to update any sinfo snapshot file written today in ~/.slurm."
)
@click.version_option(__version__, prog_name="Xsinfo")


def standalone_xsinfo(torque, refresh):
	run_xsinfo(torque, refresh)


if __name__ == "__main__":
	standalone_xsinfo()
