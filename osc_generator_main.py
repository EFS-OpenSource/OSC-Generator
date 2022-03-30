#  ****************************************************************************
#  @osc_generator_main.py
#  
#  @copyright 2022 Elektronische Fahrwerksysteme GmbH and Audi AG. All rights reserved.
#
#  @license Apache v2.0
#  
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  
#      http://www.apache.org/licenses/LICENSE-2.0
#  
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#  ****************************************************************************


import sys
from argparse import ArgumentParser
from osc_generator.osc_generator import OSCGenerator


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.0.0',
                        help="Show program's version number and exit.")
    parser.add_argument("-t", "--trajectories", dest="trajectories_path",
                        help="path to the file containing the object trajectories used as input",
                        metavar="TRAJECTORIES_PATH")
    parser.add_argument("-d", "--opendrive", dest="opendrive_path",
                        help="path to the opendrive file which describes the road net which the objects are using",
                        metavar="TRAJECTORIES_PATH")
    parser.add_argument("-s", "--openscenario", dest="output_scenario_path", default=None,
                        help="output file path and name. If not specified, a directory and name will be chosen. "
                             "If the file already exists , it will be overwritten.")
    try:
        args = parser.parse_args()
    except SystemExit as err: 
        if err.code == 2: 
            parser.print_help()
        sys.exit(0)
    OSG = OSCGenerator()
    OSG.generate_osc(args.trajectories_path, args.opendrive_path, args.output_scenario_path)
