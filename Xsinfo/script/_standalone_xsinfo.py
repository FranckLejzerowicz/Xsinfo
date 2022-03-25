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
	"--show-sinfo/--no-show-sinfo", default=False, show_default=True,
	help="Whether to print sinfo in stdout (it is always written out)"
)
@click.version_option(__version__, prog_name="Xsinfo")


def standalone_xsinfo(torque, show_sinfo):
	run_xsinfo(torque, show_sinfo)


if __name__ == "__main__":
	standalone_xsinfo()
