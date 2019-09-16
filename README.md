# Simulation of Field Calculus-based IoT Applications with Real-Time Guarantees

Paper published in [COORDINATION 2019: Coordination Models and Languages](https://link.springer.com/chapter/10.1007/978-3-030-22397-7_4/). For any issues with reproducing the experiments, please contact [Danilo Pianini](mailto:danilo.pianini@unibo.it).


## Description

This repository contains the source code used to perform the experiments presented in the paper, as well as instructions for reproducing it.


## Prerequisites

* Importing the repository
    - Git

* Executing the simulations
    - Java 8 JDK update 202 or above installed and set as default virtual machine, or Java 11 update 7
    - The javac and java commands must be available from the terminal

* Chrunching the generated data and producing the charts
    - Python 3.7.2
    - Matplotlib 3.0.2
    - NumPy 1.16.0
    - Xarray 0.11.3

**Notes about the supported operating systems**

All the tests have been performed under Linux, no test has been performed under any other operating system, and we only support reproducing the tests under that environment.
Due to the portable nature of the used tools, the test suite might run also on other Unix-like OSs (e.g. BSD, MacOS X), and possibly under Microsoft Windows, provided that the prerequisites are met.
The detection of the available installed memory used to fine tune the simulation batch performance requires read access to `/proc/meminfo`, and it is only available under Linux.
On other systems, 16GB of RAM are guessed, please modify `build.gradle.kts` if your system has different capabilities.
All the commands that follow in this `README.md` file are meant for being used on Linux, there is a chance they will work on other Unix-like OSs, they are not going to work under Microsoft Windows (most of them can be easily adapted though).


## Reproducing the experiment


### Importing the repository

The first step is cloning this repository. It can be easily done by using `git`. Open a terminal, move it into an empty folder of your choice, then issue the following command:

``git clone git@bitbucket.org:danysk/experiment-2019-coordination-aggregate-share.git``

This should make all the required files appear in your repository, with the latest version.

### Re-executing the simulations

The whole set of simulations can be executed by pointing the terminal in the root directory where the repository was cloned, and issuing:

``./gradlew runTests``

Results will be written in the `data` directory.
Please make sure that such directory exists.
Older files in such folder whose name matches the data export name will be overwritten without prior notice.

### Crunching data and producing the graphs

A Python 3 script is available for producing the charts.
It first merges all the data generated by simulations, then uses it to produce graphs.
To execute it, issue:

``python process.py``

Charts used in the paper will be generated as pdf files.
If executed in a interactive Python environment, such as Spyder 3, the script will also plot on console a number of other charts.

## Tested platforms

We successfully ran the experiments with the following systems:

#### Tests successfully executed, charts correctly generated

  * Intel(R) Core(TM) i7-8700 CPU @ 3.20GHz
  * 32GB RAM
  * Linux 4.20.5-arch1-1-ARCH #1 SMP PREEMPT x86_64 GNU/Linux
  * OpenJDK Runtime Environment (build 1.8.0_202-b26) OpenJDK 64-Bit Server VM (build 25.202-b26, mixed mode)
  * Python 3.7.2
