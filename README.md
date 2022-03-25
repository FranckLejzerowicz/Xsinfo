# Xsinfo

Collect info about the current nodes and cores usage so that it can help one
choosing where and how much resources can be allocated for a job on SLURM.
     
 # Install

```
git clone https://github.com/FranckLejzerowicz/Xsinfo.git
cd Xsinfo
pip install -e .
```
*_Note that python should be python3_


## Outputs

A _Torque_'s or _Slurm_'s script (if GPU are queried), including directives for
resources querying (the file extension shall be .pbs).

The would then needs to:
1. Check the written `.pbs` script for modified paths or errors (**strongly**
advised)
    * especially if option `-l` is used (copy job input files and execute
on the given "/localscratch" folder, as in this case some existing path may be copied that should not be, as for example program executatble paths...) 
    * **attention**: if option `--run` is used, it is impossible to check
(use with caution) 
3. Run `qsub <path>.pbs` (for Torque), or `sbatch <path>.sh` (for Slurm)
  
## Usage

```
Xsinfo -i <input_path> -o <output_path> -j <job_name> [OPTIONS]
```

It is not very necessary to set values for the options `-q` and `-d`, as well 
as for option `-N` unless you ```

### Bug Reports

contact `franck.lejzerowicz@gmail.com`