# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import math
import itertools
import subprocess

import pandas as pd


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
    sinfo = pd.DataFrame(sinfo, columns=[
        'node', 'partition', 'status', 'cpu_load', 'cpus',
        'socket', 'cores', 'threads', 'mem', 'free_mem'
    ])
    return sinfo


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
    expanded = sinfo.cpus.apply(lambda x: pd.Series(x.split('/')[:2]))
    expanded = expanded.rename(columns={0: 'allocated', 1: 'cpus_avail'})
    sinfo_cpu = pd.concat([sinfo, expanded], axis=1)
    return sinfo_cpu


def subset_it(sinfo: pd.DataFrame, it: tuple, idx: int) -> pd.DataFrame:
    """Subset the sinfo data frame to either one of two partitions.

    Parameters
    ----------
    sinfo : pd.DataFrame
        Main data frame from which two data frames are compared.
    it : tuple
        Names of the two partitions corresponding to the two
        compared data frames.
    idx : int
        Either 0 or 1 for the first of second of the two
        compared data frames.

    Returns
    -------
    tab : pd.DataFrame
        sinfo data frame corresponding to one of two partitions.
    """
    tab = pd.DataFrame()
    if it[idx] in set(sinfo.partition):
        tab = sinfo.loc[sinfo.partition == it[idx]]
        tab = tab.drop(columns='partition')
        tab.index = range(tab.shape[0])
    return tab


def get_nodes_info(sinfo: pd.DataFrame) -> dict:
    """
    Reduce the sinfo table already reduced to the nodes having available cores
    in order to only keep the nodes available for one of the partitions across
    which they are assigned.

    Parameters
    ----------
    sinfo : pd.DataFrame
        sinfo about the nodes with available cores.

    Returns
    -------
    shared : dict
        List of partitions (value) having the same nodes as one partition (key).
    """
    shared = {}
    for it in itertools.combinations(sorted(sinfo.partition.unique()), 2):
        it1, it2 = subset_it(sinfo, it, 0), subset_it(sinfo, it, 1)
        if it1.shape[0] and it1.shape[1] and it1.equals(it2):
            order = it
            if it[1].endswith('*'):
                order = (it[0], it[1][:-1])
            elif it[0].endswith('*'):
                order = (it[1], it[0][:-1])
            rm_index = sinfo[sinfo.partition == order[0]].index
            sinfo.drop(index=rm_index, inplace=True)
            shared.setdefault(order[-1], []).append(order[0])
    return shared


def keep_avail_nodes(sinfo_cpu: pd.DataFrame):
    """Filter nodes that are either idle but reserved, or that are allocated,
    i.e. that do not have a single available cpu.

    Parameters
    ----------
    sinfo_cpu : pd.DataFrame
        sinfo about the nodes with available cores expanded per current usage.
    """
    avail_cpus = sinfo_cpu.loc[(sinfo_cpu.status == 'reserved') |
                               (sinfo_cpu.cpus_avail == 0)]
    sinfo_cpu.drop(index=avail_cpus.index, inplace=True)


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
    sinfo_cpu['mem_load'] = sinfo_cpu['mem_load'].clip(0)
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


def get_nodes(load_pd: pd.DataFrame) -> dict:
    """
    Collect all the cores of each node that have the current amount of
    memory load, cpu load or other criteria for resource.

    Parameters
    ----------
    load_pd : pd.DataFrame
        subset of the relevant sinfo for the current memory load,
        cpu load or other criteria for resource.

    Returns
    -------
    nodes : dict
        core per nodes.
    """
    nodes = {}
    for node in load_pd.node:
        node_split = node.split('-')
        nodes.setdefault(node_split[0], []).append(node_split[1])
    return nodes


def format_nodes(nodes: dict) -> str:
    """
    Get a string representing a series of nodes. This format can be
    passed to the `--nodelist` option in Slurm.

    Parameters
    ----------
    nodes : dict
        cores per node.

    Returns
    -------
    cpus_per_node_str : str
        cores per node separated by commas and hyphens, as taken in by Slurm.
    """
    cpus_per_node = ['%s-[%s]' % (n, ','.join(cs)) for n, cs in nodes.items()]
    cpus_per_node_str = ','.join(cpus_per_node)
    return cpus_per_node_str


def summarize(sinfo_cpus: pd.DataFrame):
    """
    Show some node usage stats in order for the use to select nodes
    with enough resources in terms of cpu and memory availability.

    Parameters
    ----------
    sinfo_cpus : pd.DataFrame
        sinfo about the nodes with available cores.
    """
    sinfo_cpus.sort_values('cpus_avail', ascending=False, inplace=True)
    for cpu_mem in ['cpu', 'mem']:
        print('# Showing nodes per %s of %s load:' % ('%', cpu_mem))
        print('%s\tcpus\tmem\tav \t±\tpart\tnodes')
        for load, load_pd in sinfo_cpus.groupby('%s_load_bin' % cpu_mem):
            if not load_pd.shape[0]:
                continue
            nodes = format_nodes(get_nodes(load_pd))
            parts = ','.join([x.strip('*') for x in set(load_pd.partition)])
            ncpus = load_pd.cpus_avail.sum()
            mem = load_pd.free_mem.sum()
            mem_av = round(load_pd.free_mem.mean(), 2)
            mem_sd = round(load_pd.free_mem.std(), 2)
            print('%s%s\t%s\t%s\t%s\t%s\t%s\t%s' % (
                load, '%', ncpus, mem, mem_av, mem_sd, parts, nodes))


def show_shared(shared: dict):
    """
    Just shows the partitions sharing the same nodes.

    Parameters
    ----------
    shared : dict
        partitions sharing the same nodes.
    """
    for k, vs in shared.items():
        print('\n%s\nSame nodes between partitions:' % ('-' * 35))
        for v in vs:
            print('-> "%s" and "%s"' % (k, v))
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
    sinfo_cpu.set_index('node', inplace=True)
    sinfo_cpu.index.name = None
    print('##')
    print(sinfo_cpu[['cpu_load', 'cpus_avail', 'free_mem',
                     'mem_load', 'partition']])


def write_sinfo_cpu(output: str, sinfo_cpu: pd.DataFrame) -> None:
    """

    Parameters
    ----------
    output : str
        A file path to output nodes summary, or empty string to only print.
    sinfo_cpu : pd.DataFrame

    """
    if output:
        sinfo_cpu.to_csv(output, index=False, sep='\t')
        print('\n# sinfo written in "%s' % output)


def run_xsinfo(output: str, torque: bool) -> None:
    """Run the routine of collecting the nodes/cpus information and summarize it
    for different dimension, or get possible usage solutions for a users need.

    Parameters
    ----------
    output : str
        A file path to output nodes summary, or empty string to only print.
    torque : bool
        Whether the scheduler is PBS/Torque
    """
    if torque:
        print('No node collection mechanism yet for PBS/Torque!')
    else:
        # if subprocess.getstatusoutput('sinfo')[0]:
        #     raise IOError('No SLURM scheduler ("sinfo" not available)')
        sinfo = get_sinfo()
        shared = get_nodes_info(sinfo)

        sinfo_cpu = expand_cpus(sinfo)
        change_dtypes(sinfo_cpu)
        keep_avail_nodes(sinfo_cpu)
        bin_loads(sinfo_cpu)
        summarize(sinfo_cpu)

        write_sinfo_cpu(output, sinfo_cpu)

        show_shared(shared)
        show_sinfo_cpu(sinfo_cpu)
