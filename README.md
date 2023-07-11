# Description
OSC-Generator is a collection of Python tools to generate [ASAM OpenSCENARIO](https://www.asam.net/standards/detail/openscenario/) files from vehicle data and an [ASAM OpenDRIVE](https://www.asam.net/standards/detail/opendrive/) file.

![OSC-Workflow](docs/images/OSC-Generator_Interfaces.png)

The generated openSCENARIO file (.xosc) can then be used for purposes such as scenario re-simulations, or in further applications, for example, visualised in a tool like [esmini](https://github.com/esmini/esmini).

![openSCENARIO_visualisation_demo](docs/images/OSC-Generator_Demo.gif)

## Scope of Application
Currently, OpenSCENARIO V1.2 and OpenDRIVE V1.4 are supported.
Intersections may currently cause trouble but will be supported in a future release.
All features are tested in Python 3.7 on Windows 10.

## Installation
### PyPI
- OSC-Generator can be installed using pip
  ```
  pip install osc-generator
  ```

### Testing
- Additional dependencies for testing are required.
  - Required Python packages can be installed via pip:
    ```
    pip install -r requirements_dev.txt
    ```
  - For testing, an ASAM OpenDRIVE file is needed. The file '_2017-04-04_Testfeld_A9_Nord_offset.xodr_' from [here](https://service.mdm-portal.de/mdm-portal-application/publDetail.do?publicationId=2594000) can be used by downloading a copy to the _tests/test_data_ folder. This file uses ASAM OpenDRIVE V1.4 format.
- Run pytest in the _tests_ folder or a parent folder thereof.
- When everything is set up correctly, all tests should run successfully without raising any warnings.

## Usage
- Class: OSC-Generator provides a Python class which can be used to generate a scenario in the OpenSCENARIO format from trajectories and an OpenDRIVE file. The file example.py contains runnable example code for usage of this class.
- CLI: 
  - OSC-Generator can use arguments provided via Python's commandline interface. For information on how to use this feature, see the output of the help function:
  
  - When installed via pip, OSC-Generator can directly be called in the console:
    ```
    osc_generator -h 
    ```
  - To use the OSC-Generator through the command line (without installation via pip), navigate to the main project directory and from there the help function can be called:
    ```
    python -m osc_generator.osc_generator -h 
    ```  

- CLI arguments
  - the following table outlines the available input arguments
      
   | Argument | Type     | Default Value | Description | 
   |----------|----------|--------------|--------------------------------------------------------------------|
   | "-t", "--trajectories" | required | N/A | Path to the file containing the object trajectories used as input |
   | "-d", "--opendrive" | required | N/A | Path to the opendrive file which describes the road net which the objects are using |
   | "-s", "--openscenario" | optional | "None" | Output file path and name. If not specified, a directory and name will be chosen. If the file already exists , it will be overwritten |
   | "-v", "--version"| optional | N/A | Show program's version number and exit |
   | "-c", "--catalog" | optional | "None" | Catalog file path and name. If not specified, a default catalog path is used |
   | "-oscv", "--oscversion" | optional | "None" | Desired version of the output OpenScenario file. If not specified, default is OSC V1.0 |


## Expected Input Data and Formats
### Trajectories file
- the input trajectories file can currently be provided in two formats 
  - .csv
  - .osi (Open Simulation Interface - see below)


- the following data is required in a .csv for an OpenSCENARIO file to be generated (especially when using lane data relative to the ego vehicle):
  - **timestamp** [seconds] - time of each data point, from the beginning of the "scenario"
  - **lat** [decimal degree (WGS84)] - latitude of the ego vehicle in the scenario
  - **lon** [decimal degree (WGS84)] - longitude of the ego vehicle in the scenario
  - **heading** [degrees (starting North, increasing clockwise)] - heading of the ego vehicle in the scenario
  - **speed** [kilometers/hour] - speed of the ego vehicle in the scenario
  - **lin_left_typ** [-] - lane type of left lane
  - **lin_left_beginn_x** [meters] - beginning left lane detection point, relative to the ego vehicle, in the x direction 
  - **lin_left_y_abstand** [meters] - distance between the ego vehicle and the left lane, in the y direction
  - **lin_left_kruemm** [-] - the curvature of the left lane
  - **lin_left_ende_x** [meters] - end left lane detection point, relative to the ego vehicle, in the x direction
  - **lin_left_breite** [meters] - width of the lane marking 
  - **lin_right_typ** [-] - lane type of left lane
  - **lin_right_beginn_x** [meters] - beginning right lane detection point, relative to the ego vehicle, in the x direction
  - **lin_right_y_abstand** [meters] - distance between the ego vehicle and the right lane, in the y direction
  - **lin_right_kruemm** [-] - the curvature of the right lane
  - **lin_right_ende_x** [meters] - end right lane detection point, relative to the ego vehicle, in the x direction
  - **lin_right_breite** [meters] - lane type of right lane


- the following data is optional, depending on how many object vehicles are in the scenario - "#" represents the object number, starting at 1
  - **pos_x_#** [meters] - distance between object vehicle and ego vehicle in x direction
  - **pos_y_#** [meters] - distance between object vehicle and ego vehicle in y direction
  - **speed_x_#** [kilometers/hour] - speed of object vehicle in x direction
  - **speed_y_#** [kilometers/hour] - speed of object vehicle in y direction
  - **class_#** [-] - class/type of object, e.g. 7 = car class 

- for an example of an input trajectory .csv file, see "tests/test_data/trajectories_file.csv"
  

### OpenDRIVE file
- the OpenDRIVE file should be compliant with ASAM's standard
  - ideally matching the trajectory data too


## Open Simulation Interface (OSI) Format Input 
- In order to use OSI format (.osi) input trajectory files with the OSC-Generator, the following steps are required:
  - install the Open Simulation Interface (OSI):
    - follow the installation instructions: https://github.com/OpenSimulationInterface/open-simulation-interface
  - copy the file 'OSITrace.py':
    - from "$PATH_TO_OSI_DIRECTORY\open-simulation-interface\format"
    - to "$PATH_TO_OSC-GENERATOR_DIRECTORY\OSC-Generator\osc_generator\tools\OSI"
  - run tests
  

- Usage of this feature functions as described above.   
- if OSI is not installed, the OSC-Generator can still be used with .csv input trajectory files.

## Citation
An associated [paper](https://ieeexplore.ieee.org/document/9575441) describes the original use case for which the OSC-Generator was created. 
When using this software, please cite the following: 
```
@software{OSC-Generator,
author = {{Montanari, Francesco}, {Akkaya, Yigit Ali}, {Boßmann, Nils}, {Sichermann, Jörg}, {Müller, Marcel}, {Aigner, Axel Jeronimo}, {D'Sa, Dave}},
license = {Apache-2.0},
title = {{OSC-Generator}},
url = {https://github.com/EFS-OpenSource/OSC-Generator},
version = {0.2.0}
}
```

## Acknowledgment
This work is supported by the German Federal Ministry for Digital and Transport (BMDV) within the *Automated and Connected Driving* funding program under grant No. 01MM20012F ([SAVeNoW](https://savenow.de)).

@copyright 2022 e:fs TechHub GmbH and Audi AG. All rights reserved.
https://www.efs-techhub.com/
https://www.audi.com/de/company.html

@license Apache v2.0

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
