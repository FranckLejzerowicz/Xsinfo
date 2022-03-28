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
	"-o", "--output", default='', type=str,
	help="Output file to write the nodes availability (or only show in stdout)."
)
@click.option(
	"--torque/--no-torque", default=False, show_default=True,
	help="Switch from Slurm to Torque"
)
@click.version_option(__version__, prog_name="Xsinfo")


def standalone_xsinfo(output, torque):
	run_xsinfo(output, torque)


if __name__ == "__main__":
	standalone_xsinfo()
