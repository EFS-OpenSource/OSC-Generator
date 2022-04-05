#  ****************************************************************************
#  @converter.py
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

import numpy as np
import pandas as pd
import os
from typing import Union

from osc_generator.tools import utils
from osc_generator.tools import man_helpers
from osc_generator.tools.coord_calculations import transform_lanes_rel2abs_from_csv
from osc_generator.tools.scenario_writer import convert_to_osc


class Converter:
    """
    Main class for converter operations
    """

    def __init__(self):
        self.osc_version: str = '1.0'
        self.trajectories_path: str = ''
        self.opendrive_path: str = ''
        self.outfile = None
        self.use_folder: bool = True

        self.dir_name: str = ''
        self.section_name: str = ''

        self.df = None
        self.df_lanes = None

        self.ego_maneuver_array = None
        self.inf_maneuver_array = None
        self.objlist = None
        self.objects = None
        self.ego = None
        self.movobj_grps_coord = None

    def set_paths(self, trajectories_path: str, opendrive_path: str, output_scenario_path: str = None):
        """
        This method should be called before calling other class methods

        Args:
            trajectories_path: Path to the file containing the object trajectories used as input
            opendrive_path: Path to the OpenDRIVE file which describes the road net which the objects are using
            output_scenario_path: Output file path and name. If not specified, a directory and name will be chosen.
                If the file already exists, it will be overwritten.

        """
        if os.path.isfile(trajectories_path):
            self.trajectories_path = trajectories_path
        else:
            raise FileNotFoundError("file not found: " + str(trajectories_path))

        if os.path.isfile(opendrive_path):
            self.opendrive_path = opendrive_path
        else:
            raise FileNotFoundError("file not found: " + str(opendrive_path))

        if output_scenario_path is not None:
            output_dir_path = os.path.dirname(os.path.abspath(output_scenario_path))
            if os.path.isdir(output_dir_path):
                self.outfile = output_scenario_path
            else:
                raise FileNotFoundError("folder not found: " + str(output_dir_path))

        if self.use_folder:
            path_name = self.trajectories_path.rsplit(os.path.sep)
            self.section_name = path_name[-1]
            self.dir_name = os.path.dirname(self.trajectories_path)
        else:
            raise NotImplementedError("use_folder flag is going to be removed")

    def process_trajectories_from_csv(self, relative: bool = True, df_lanes: pd.DataFrame = None):
        """
        Process trajectories file and convert it to cleaned main dataframe
        and a dataframe for absolute coordination of lanes

        Args:
            relative: True -> coordinates of lanes and vehicles are relative to ego.
            df_lanes: If absolute coordinates are used, the lane coordinates needs to be passed here.

        """
        df = pd.read_csv(self.trajectories_path)

        if relative:
            # Delete not relevant objects (too far away, not visible long enough, not plausible)
            movobj_grps = utils.find_vars('pos_x_|pos_y_|speed_x_|speed_y_|class_', df.columns, reshape=True)
            df, del_obj = utils.delete_irrelevant_objects(df, movobj_grps, min_nofcases=20, max_posx_min=50.0,
                                                          max_posx_nofcases_ratio=10.0)
            # Create absolute lane points from relative
            self.df_lanes = transform_lanes_rel2abs_from_csv(df)

            # Compute coordinates of Objects
            # Find posx-posy movobj_grps and define lat-lon movobj_grps
            movobj_grps = utils.find_vars('pos_x_|pos_y_|speed_x_', df.columns, reshape=True)

            movobj_grps_coord = []
            for p in movobj_grps:
                movobj_grps_coord.append([p[0].replace('pos_x', 'lat'), p[1].replace('pos_y', 'lon'),
                                          p[2].replace('speed_x', 'speed'), p[2].replace('speed_x', 'class')])

            # Compute Coordinates and absolute speed
            for p, q in zip(movobj_grps, movobj_grps_coord):
                coordx = []
                coordy = []
                for k in range(len(df[p])):
                    if not any(list(pd.isna(df.loc[k, p]))):
                        n = utils.calc_new_geopos_from_2d_vector_on_spheric_earth(curr_coords=df.loc[k, ["lat", "long"]],
                                                                                  heading=df.loc[k, "heading"],
                                                                                  dist_x=df.loc[k, p[0]], dist_y=df.loc[k, p[1]])
                        coordx.append(n[0])
                        coordy.append(n[1])
                    else:
                        coordx.append(np.nan)
                        coordy.append(np.nan)
                df[q[0]] = coordx
                df[q[1]] = coordy
                df[q[2]] = abs(df[p[2]])

            # Delete and reorder columns
            delete_vars = utils.find_vars('speed_x_|speed_y_', df.columns)
            df = df.drop(columns=delete_vars)

            reorder_vars1 = ['timestamp', 'lat', 'long', 'heading', 'speed']
            reorder_vars3 = utils.flatten(movobj_grps_coord)
            self.df = df[reorder_vars1 + reorder_vars3]
        else:
            # Delete not relevant objects (too far away, too short seen, not plausible)
            movobj_grps = utils.find_vars('lat_|lon_|speed_|class_', df.columns, reshape=True)
            df, del_obj = utils.delete_irrelevant_objects(df, movobj_grps, min_nofcases=20, max_posx_min=50.0,
                                                          max_posx_nofcases_ratio=10.0)

            if df_lanes is None:
                raise ValueError('if absolute coordinates are used, the lane coordinates needs '
                                 'to be passed in process_inter func. as a dataframe.')
            else:
                self.df_lanes = df_lanes
            self.df = df

        if self.use_folder:
            self.df.to_csv(os.path.join(self.dir_name, 'df33.csv'))
        else:
            raise NotImplementedError("use_folder flag is going to be removed")

    def label_maneuvers(self, acc_threshold: Union[float, np.ndarray] = 0.2, optimize_acc: bool = False,
                        generate_kml: bool = False):
        """
        Main dataframe and lanes dataframe will be used here to label the maneuvers.

        Args:
            acc_threshold: Acceleration threshold for labeling
            optimize_acc: Option to get optimal acceleration threshold
            generate_kml: Option to create kml files
        """
        if optimize_acc:
            acc_thres_opt = man_helpers.calc_opt_acc_thresh(self.df, self.df_lanes, self.opendrive_path,
                                                            self.use_folder, self.dir_name)
            acc_threshold = acc_thres_opt
            ego_maneuver_array, inf_maneuver_array, objlist, objects, ego, movobj_grps_coord = man_helpers.label_maneuvers(
                self.df, self.df_lanes, acc_threshold, generate_kml,
                self.opendrive_path, self.use_folder, self.dir_name)
        else:
            ego_maneuver_array, inf_maneuver_array, objlist, objects, ego, movobj_grps_coord = man_helpers.label_maneuvers(
                self.df, self.df_lanes, acc_threshold, generate_kml,
                self.opendrive_path, self.use_folder, self.dir_name)

        self.ego_maneuver_array = ego_maneuver_array
        self.inf_maneuver_array = inf_maneuver_array
        self.objlist = objlist
        self.objects = objects
        self.ego = ego
        self.movobj_grps_coord = movobj_grps_coord

    def write_scenario(self, plot: bool = False,
                       radius_pos_trigger: float = 2.0, timebased_lon: bool = True, timebased_lat: bool = False,
                       output: str = 'xosc'):
        """
        Writes the trajectories or maneuvers in selected file formats.

        Args:
            plot: Ploting option
            radius_pos_trigger: Defines the radius of position trigger
            timebased_lon: True -> timebase trigger for longitudinal maneuver will be used. False -> position base
            timebased_lat: True -> timebase trigger for latitudinal maneuver will be used. False -> position base
            output: Pption for different file formats. To write OpenScenario -> 'xosc'.
        """
        if output == 'xosc':
            outfile = convert_to_osc(self.df, self.ego, self.objects, self.ego_maneuver_array, self.inf_maneuver_array,
                                     self.movobj_grps_coord, self.objlist, plot,
                                     self.opendrive_path, self.use_folder, timebased_lon, timebased_lat,
                                     self.section_name, radius_pos_trigger, self.dir_name, self.osc_version, self.outfile)
            self.outfile = outfile

        else:
            raise NotImplementedError('selected output option is not implemented')
