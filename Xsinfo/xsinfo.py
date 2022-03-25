# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import subprocess


def get_nodes_info(avail: list) -> dict:
    """


    Parameters
    ----------
    avail : list

    Returns
    -------
    nodes : dict
        useful info about the nodes.
    """
    nodes = {}
    for row in avail:
        mem, free_mem = map(float, row[-2:])
        mem_load = 100 - (free_mem / mem)
        nodes.setdefault(row[1], []).append((row[0], row[2], row[3], mem_load,))
    return nodes


def get_sinfo() -> dict:
    """
    Run subprocess to collect the nodes and cores
    that are idle and available for compute.

    Returns
    -------
    nodes : dict
        useful info about the nodes.
    """
    # prepare a sinfo output to know more about current system availability
    cmd = 'sinfo '
    cmd += '--Node -h -O '
    cmd += 'NodeList:10,'
    cmd += 'Partition:10,'
    cmd += 'StateLong:10,'
    cmd += 'CPUsLoad:10,'
    cmd += 'CPUsState:12,'
    cmd += 'Sockets:4,'
    cmd += 'Cores:4,'
    cmd += 'Threads:4,'
    cmd += 'Memory:12,'
    cmd += 'FreeMem:12'
    # get this rich output of sinfo
    sinfo = [node.split() for node in subprocess.getoutput(cmd).split('\n')][:20]
    print(sinfo)
    print(sinfodsa)
    # # add the number of allocated, idle, other and total cores
    # sinfo = [(node + node[4].split('/')) for node in sinfo]
    # # reduce to nodes having cores that are idle but not reserved
    # avail = [node for node in sinfo if int(node[-3]) and node[2] != 'reserved']
    # nodes = get_nodes_info(avail)
    # return nodes


def show_node_info(nodes):
    pass


def run_xsinfo(
        torque: bool,
        show_sinfo: bool) -> None:
    """

    Parameters
    ----------
    torque : bool
        Whether the scheduler is PBS/Torque
    show_sinfo : bool
        Whether to print sinfo in stdout.
    """
    if torque:
        print('No node collection mechanism yet for PBS/Torque!')
    else:
        if subprocess.getstatusoutput('sinfo')[0]:
            raise IOError('No SLURM scheduler ("sinfo" not available)')
        nodes = get_sinfo()
        if show_sinfo:
            show_node_info(nodes)
    print(sinfo)
    print(sinfodsa)
