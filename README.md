# Magnetic tweezers in Brugues lab (room 426b)
Ursa Ursic & Erik Plesko, 2022
updated: November 2024

This is a GitHub repository for the magnetic tweezers setup in the Brugues lab, MPI-CBG, Dresden. 

## Introduction
This setup is built for magnetic manipulation of super-paramagnetic beads in biological samples. It consists of a current generator, connected to a solenoid with a pointed ferromagnetic core. The current generator is manipulated with an arduino Nano Every through a python script. The magnetic tip (solenoid with a pointed feromagnetic core) is attached to an Injecman for spacial manipulation of the tip. 
Detailed description and documentation of the system: 
https://cloud.mpi-cbg.de/index.php/s/AMNPCnxFofayZA8

## Code 
### Setting up
For the initial setup of the system, load .ino file to the Arduino.

### Usage
When performing experiments, use the Jupyter notebook: magnetic_tweezers_brugueslab/scripts/voltage_control/Run_VoltageControl.ipynb
You need to use the virtual environment, which can be recreated using environment_mag_tw.yml file. 
In the file magnetic_tweezers_brugueslab/scripts/voltage_control/my_functions.py, you can define different functions for voltage control. 

### Other
There are two other branches feat/inject_man and feat/two_tips. Those are branches we used to develop some additional functionalities of the setup but are currently not used for experiments. In principle, it is possible to control two separate tips. It is also possible to control the motion of inject man with the code.  








