#  ****************************************************************************
#  @osc_generator.py
#  
#  @copyright 2022 e:fs TechHub GmbH and Audi AG. All rights reserved.
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

import os

from .tools.converter import Converter
from .tools.user_config import UserConfig
import sys
from argparse import ArgumentParser
from .version import __version__


class OSCGenerator:
    """
    This class provides an easy-to-use API for generating scenarios.
    The API is designed with forward-compatibility in mind,
    which is the reason why many experimental features of the underlying code are not accessible here.

    """
    def __init__(self):
        self.converter: Converter = Converter()

    def generate_osc(self, trajectories_path: str, opendrive_path: str, output_scenario_path: str = None,
                     **kwargs: str):
        """
        This method generates a OpenSCENARIO file based on trajectories and an OpenDRIVE file.

        Args:
            trajectories_path: Path to the file containing the object trajectories used as input
            opendrive_path: Path to the OpenDRIVE file which describes the road net which the objects are using
            output_scenario_path: Output file path and name. If not specified, a directory and name will be chosen.
                If the file already exists, it will be overwritten.
            keyword arguments:
                catalog_path: Path to the catalog file containing vehicle catalog information for the output scenario
                osc_version: Desired version of the output OpenScenario file. Default is OSC V1.0

        """
        if "catalog_path" in kwargs:
            if kwargs["catalog_path"] is not None:
                dir_name = os.path.dirname(trajectories_path)
                user_config = UserConfig(dir_name)
                user_config.catalogs = kwargs["catalog_path"]
                user_config.write_config()

        if "osc_version" in kwargs:
            if kwargs["osc_version"] is not None:
                self.converter.osc_version = kwargs["osc_version"]

        if output_scenario_path:
            self.converter.set_paths(trajectories_path, opendrive_path, output_scenario_path)
        else:
            self.converter.set_paths(trajectories_path, opendrive_path)

        self.converter.process_trajectories(relative=True)
        self.converter.label_maneuvers(acc_threshold=0.2, optimize_acc=False, generate_kml=False)
        self.converter.write_scenario(plot=False,
                                      radius_pos_trigger=2.0,
                                      timebased_lon=True,
                                      timebased_lat=False,
                                      output='xosc')
        print('Path to OpenSCENARIO file: ' + os.path.abspath(self.converter.outfile))


def main():
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=('%(prog)s ' + str(__version__)),
                        help="Show program's version number and exit.")
    parser.add_argument("-t", "--trajectories", dest="trajectories_path",
                        help="path to the file containing the object trajectories used as input")
    parser.add_argument("-d", "--opendrive", dest="opendrive_path",
                        help="path to the opendrive file which describes the road net which the objects are using")
    parser.add_argument("-s", "--openscenario", dest="output_scenario_path", default=None,
                        help="output file path and name. If not specified, a directory and name will be chosen. "
                             "If the file already exists , it will be overwritten.")
    parser.add_argument("-cat", "--catalog", dest="catalog_path", default=None,
                        help="catalog file path and name. If not specified, a default catalog path is used. ")
    parser.add_argument("-oscv", "--oscversion", dest="osc_version", default=None,
                        help="Desired version of the output OpenScenario file. If not specified, default is OSC V1.0 ")

    try:
        args = parser.parse_args()
    except SystemExit as err:
        if err.code == 2:
            parser.print_help()
        sys.exit(0)
    if (args.trajectories_path is None) or (args.opendrive_path is None):
        parser.print_help()
        return
    oscg = OSCGenerator()
    oscg.generate_osc(args.trajectories_path, args.opendrive_path, args.output_scenario_path,
                      catalog_path=args.catalog_path,
                      osc_version=args.osc_version)


if __name__ == '__main__':
    main()
