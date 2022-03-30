# ----------------------------------------------------------------------------
# Copyright (c) 2022, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
# ----------------------------------------------------------------------------

import os
import glob
import math
import subprocess
import pandas as pd
from datetime import datetime
from os.path import dirname, isdir, isfile
# import yaml


def get_today_output():
    """Get the path to the output file for today's node usage.

    Returns
    -------
    output : str
        path
    """
    output_dir = '%s/.xsinfo' % os.path.expanduser('~')
    if not isdir(output_dir):
        os.makedirs(output_dir)
    today = str(datetime.now().date())
    output = output_dir + '/' + today + '.tsv'
    return output


def get_sinfo() -> pd.DataFrame:
    """
    Run subprocess to collect the nodes and cores
    that are idle and available for compute.

    Returns
    -------
    sinfo : pd.DataFrame
        sinfo about the nodes with available cores.
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
    sinfo = [n.split() for n in subprocess.getoutput(cmd).split('\n')]
    # with open('/Users/franck/programs/Xsinfo/Xsinfo/test/snap.txt') as o:
    #     sinfo = yaml.load(o, Loader=yaml.Loader)
    sinfo = pd.DataFrame(sinfo, columns=[
        'node', 'partition', 'status', 'cpu_load', 'cpus',
        'socket', 'cores', 'threads', 'mem', 'free_mem'])
    return sinfo


def find_series(cs: list) -> str:
    """
    Get a condensed representation of the series of cpus numbers for a node.

    Parameters
    ----------
    cs : list
        current list of numbers corresponding to cpus nodes.

    Returns
    -------
    cpus : str
        Condensed representation of nodes number (as ranges).
    """
    mini, maxi = min(cs), max(cs)
    vals = []
    cur = [mini]
    for c in cs[:-1]:
        if not cur:
            cur.append(c)
            continue
        if c + 1 not in cs:
            cur.append(c)
            vals.append(list(cur))
            cur = []
    cur.append(cs[-1])
    vals.append(list(cur))
    cpus = ','.join(['-'.join(map(str, sorted(set(x)))) for x in vals])
    return cpus


def condense_node_cpus(names):
    d = {}
    for name in names:
        name_split = name.split('-')
        d.setdefault(name_split[0], []).append(int(name_split[1]))

    nodes = []
    for n, cs in d.items():
        nodes.append('%s-[%s]' % (n, find_series(sorted(cs))))
    return ','.join(nodes)


def expand_cpus(sinfo: pd.DataFrame) -> pd.DataFrame:
    """
    Expand the list of allocated, idles, other and unavailable cpus.

    Parameters
    ----------
    sinfo : pd.DataFrame
        sinfo about the nodes with available cores.

    Returns
    -------
    sinfo_cpus : pd.DataFrame
        sinfo about the nodes with available cores expanded per current usage.
    """
    # expand the number of allocated, idle, other and total cores
    expanded = sinfo.cpus.apply(lambda x: pd.Series(map(int, x.split('/')[:2])))
    expanded = expanded.rename(columns={0: 'allocated', 1: 'cpus_avail'})
    sinfo_cpu = pd.concat([sinfo, expanded], axis=1)
    return sinfo_cpu


def keep_avail_nodes(sinfo_cpu: pd.DataFrame):
    """Filter nodes that are either idle but reserved, or that are allocated,
    i.e. that do not have a single available cpu.

    Parameters
    ----------
    sinfo_cpu : pd.DataFrame
        sinfo about the nodes with available cores expanded per current usage.
    """
    avail = sinfo_cpu.loc[(sinfo_cpu.status == 'reserved') |
                          (sinfo_cpu.cpus_avail == 0)]
    sinfo_cpu.drop(index=avail.index, inplace=True)


def change_dtypes(sinfo_cpu: pd.DataFrame) -> None:
    """
    Change the dtypes of some variables and use them to compute new metrics,
    including the memory load and free memory in GiB.

    Parameters
    ----------
    sinfo_cpu : pd.DataFrame
        sinfo about the nodes with available cores expanded per current usage.
    """
    # reduce to nodes having cores that are idle but not reserved
    sinfo_cpu['cpus_avail'] = sinfo_cpu['cpus_avail'].astype(float)
    sinfo_cpu['cpu_load'] = sinfo_cpu['cpu_load'].astype(float)
    sinfo_cpu['mem'] = sinfo_cpu['mem'].astype(float)
    sinfo_cpu['free_mem'] = sinfo_cpu['free_mem'].astype(float)
    sinfo_cpu['mem_load'] = 100*(1-(sinfo_cpu['free_mem'] / sinfo_cpu['mem']))
    sinfo_cpu['mem_load'] = round(sinfo_cpu['mem_load'].clip(0), 4)
    sinfo_cpu['free_mem'] = (sinfo_cpu['free_mem'] / 1000).apply(math.floor)


def bin_loads(sinfo_cpus: pd.DataFrame):
    """
    Group the cpu and memory load values into 1-100 quartiles.

    Parameters
    ----------
    sinfo_cpus : pd.DataFrame
        sinfo about the nodes with available cores.
    """
    q = [-1, 25, 50, 75, 100]
    labels = ['0-25', '25-50', '50-75', '75-100']
    for load in ['cpu_load', 'mem_load']:
        sinfo_cpus['%s_bin' % load] = pd.cut(sinfo_cpus[load], q, labels=labels)


def summarize(sinfo_cpus: pd.DataFrame):
    """
    Show some node usage stats in order for the use to select nodes
    with enough resources in terms of cpu and memory availability.

    Parameters
    ----------
    sinfo_cpus : pd.DataFrame
        sinfo about the nodes with available cores.
    """
    show_sinfo_cpus = sinfo_cpus.drop(columns=['partition', 'status'])
    show_sinfo_cpus.sort_values('cpus_avail', ascending=False, inplace=True)
    show_sinfo_cpus = show_sinfo_cpus.drop_duplicates()
    for cpu_mem in ['cpu', 'mem']:
        print('\n# Showing nodes per %s of %s load:' % ('%', cpu_mem))
        print('%s\tcpus\tmem(gb)\tav\t±\tnodes\tnames' % '%')
        for load, load_pd in show_sinfo_cpus.groupby('%s_load_bin' % cpu_mem):
            if not load_pd.shape[0]:
                continue
            nnodes = load_pd.node.size
            nodes = condense_node_cpus(load_pd.node.tolist())
            ncpus = load_pd.cpus_avail.sum()
            mem = load_pd.free_mem.sum()
            mem_av = round(load_pd.free_mem.mean(), 4)
            mem_sd = round(load_pd.free_mem.std(), 4)
            print('%s%s\t%s\t%s\t%s\t%s\t%s\t%s' % (
                load, '%', ncpus, mem, mem_av, mem_sd, nnodes, nodes))


def show_shared(sinfo_cpu_per_partition: dict):
    """
    Just shows the partitions sharing the same nodes.

    Parameters
    ----------
    sinfo_cpu_per_partition : dict
        partitions sharing the same nodes.
    """
    print('\n%s\nAvailable nodes/cpus across partitions:' % ('-' * 35))
    for parts, nodes in sinfo_cpu_per_partition.items():
        print(' -', parts, '\t:\t', nodes)
    print('-' * 35, '\n')


def show_sinfo_cpu(sinfo_cpu: pd.DataFrame) -> None:
    """
    Just shows the sinfo table reduced to fields of interest.
    This can be collect from the stdout by other tools in order to help
    picking nodes if required (see https://github.com/FranckLejzerowicz/Xpbs).

    Parameters
    ----------
    sinfo_cpu : pd.DataFrame
        sinfo about the nodes with available cores.
    """
    print('##')
    sinfo_cpu = sinfo_cpu.drop(
        columns='partition'
    ).drop_duplicates().set_index(
        'node'
    ).rename(columns={
        'cpu_load': 'cpu%',
        'cpus_avail': 'freecpu',
        'free_mem': 'freemem',
        'mem_load': 'mem%'}
    )
    cols = ['cpu%', 'freecpu', 'mem%', 'freemem']
    print('\t%s' % '\t'.join(cols))
    for r, row in sinfo_cpu.iterrows():
        print('%s\t%s' % (r, '\t'.join(map(str, row[cols]))))


def write_sinfo(sinfo_cpu: pd.DataFrame, output: str, refresh: bool) -> None:
    """

    Parameters
    ----------
    sinfo_cpu : pd.DataFrame
    output : str
        A file path to output nodes summary, or empty string to only print.
    refresh: bool
    """
    today = str(datetime.now().date())
    outs = glob.glob('%s/*' % dirname(output))
    for previous in [x for x in outs if today not in x]:
        os.remove(previous)

    if not isfile(output) or refresh:
        sinfo_cpu.to_csv(output, index=False, sep='\t')
        print('\n# sinfo written in "%s' % output)


def get_shared_nodes(sinfo_cpu):
    sinfo_cpu_per_partition = sinfo_cpu.groupby(
        'node'
    ).apply(
        lambda x: ','.join(x['partition'])).reset_index(
    ).groupby(
        0
    ).node.apply(
        condense_node_cpus
    ).to_dict()
    return sinfo_cpu_per_partition


def run_xsinfo(torque: bool, refresh: bool, show: bool) -> None:
    """Run the routine of collecting the nodes/cpus information and summarize it
    for different dimension, or get possible usage solutions for a users need.

    Parameters
    ----------
    torque : bool
        Switch from Slurm to Torque
    refresh : str
        Update any sinfo snapshot file written today in ~/.slurm
    show : bool
        Show available cpu and memory per node on top of summaries
    """
    if torque:
        print('No node collection mechanism yet for PBS/Torque!')
    else:
        if subprocess.getstatusoutput('sinfo')[0]:
            raise OSError('Are you using Slurm? `sinfo` command not found')
        output = get_today_output()
        if isfile(output) and not refresh:
            print('> Read', output)
            sinfo_cpu = pd.read_table(output, sep='\t')
        else:
            print('> Run sinfo')
            sinfo = get_sinfo()
            sinfo_cpu = expand_cpus(sinfo)
            keep_avail_nodes(sinfo_cpu)
            change_dtypes(sinfo_cpu)
            bin_loads(sinfo_cpu)
            sinfo_cpu_per_partition = get_shared_nodes(sinfo_cpu)
            show_shared(sinfo_cpu_per_partition)
            write_sinfo(sinfo_cpu, output, refresh)

        summarize(sinfo_cpu)
        if show:
            show_sinfo_cpu(sinfo_cpu)
