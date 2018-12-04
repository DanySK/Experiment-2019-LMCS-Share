# Simulation of Field Calculus-based IoT Applications with Real-Time Guarantees

Demo presented in [RTSS@Work 2018, 39th IEEE Real-Time Systems Symposium](http://2018.rtss.org/rtsswork/). For any issues with reproducing the experiments, please contact [Giorgio Audrito](mailto:giorgio.audrito@gmail.com).


## Description

This repository contains all the source code used to perform the experiments presented in the paper.


## Prerequisites

* Importing the repository
    - Git

* Executing the simulations
    - Java 8 JDK installed and set as default virtual machine

* Code inspection and GUI execution
    - Eclipse Neon or Oxygen (older versions should work as well)

**Notes about the supported operating systems**

All the tests have been performed under Mac OS, CentOS Linux and Ubuntu Linux. No test has been performed under any other operating system, however, due to the portable nature of the used tools, the test suite should run on any Unix-like OSs.


## Reproducing the experiment


### Importing the repository

The first step is cloning this repository. It can be easily done by using `git`. Open a terminal, move it into an empty folder of your choice, then issue the following command:

``git clone https://gaudrito@bitbucket.org/gaudrito/rtss-experiment-potential-guarantees.git``

This should make all the required files appear in your repository, with the latest version.


### Inspecting the code and simulation GUI

Open Eclipse, click on "File > Import" and then on "Gradle > Existing Gradle Project", then select the folder of the repository donwloaded in the previous step.

To properly visualize the source files you should also install a Yaml editor (as `YEdit` in the Eclipse Marketplace) and the Protelis Parser through "Help > Install New Software" with the following address:

``http://efesto.apice.unibo.it/protelis-build/protelis-parser/protelis.parser.repository/target/repository/``

The files with the source code are in `src/main/protelis/` and contain the following:

* `utils.pt`: general utility functions
* `algorithm.pt`: distance estimation algorithm and metrics
* `statistics.pt`: statistic evaluation of density and neighbourhood size
* `isolation.pt`: distance estimation upon random walking in Vienna

The files describing the environment are in `src/main/yaml/` and contain the following:

* `statistics.yaml`: environment used for the statistic evaluation (Figure 5)
* `isolation.yaml`: environment used for the case study (Figures 4 and 6)

The two environments differ only for the set of parameters and exported values. In the `java` folder, there are files improving on the current Alchemist version (scheduled for future releases). In the `resources` folder, there are effect files for the GUI presentation together with GPS data. In order to run the simulations with a GUI, create a Run Configuration in Eclipse with the following settings.

* Main class: `it.unibo.alchemist.Alchemist`
* Program arguments: `-g src/main/resources/X.aes -y src/main/yaml/X.yml` where `X` can be either `statistics` or `isolation`
