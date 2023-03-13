#  ****************************************************************************
#  @man_helpers.py
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

"""
helper functions for maneuver abstraction.
"""
import pyproj
import simplekml
import math
import pandas as pd
import numpy as np
import os
from typing import Union

from osc_generator.tools.coord_calculations import get_proj_from_open_drive
from osc_generator.tools import rulebased, utils


def convert_maneuvers_to_kml(lat: pd.DataFrame, lon: pd.DataFrame, maneuvers: pd.DataFrame, ego: bool) -> simplekml.Kml:
    """
    Convert manuevers from pandas Dataframe to kml

    Args:
        lat: Latitude
        lon: Longitude
        maneuvers: Maneuvers of the vehicle
        ego: For the ego vehicle True

    Returns:
        object (simplekml.Kml): Kml file containing the maneuvers
    """
    if not isinstance(lat, pd.DataFrame):
        raise TypeError("input must be a pd.DataFrame")
    if not isinstance(lon, pd.DataFrame):
        raise TypeError("input must be a pd.DataFrame")
    if not isinstance(maneuvers, pd.DataFrame):
        raise TypeError("input must be a pd.DataFrame")
    if not isinstance(ego, bool):
        raise TypeError("input must be a bool")

    kml = simplekml.Kml()
    overview_doc = kml.newdocument(name='Overview')
    old_lon = 0
    old_lat = 0

    accelerate = maneuvers['FM_EGO_accelerate']
    accelerate_doc = kml.newdocument(name='accelerate')
    velocity = maneuvers['FM_EGO_keep_velocity']
    velocity_doc = kml.newdocument(name='velocity')
    standstill = maneuvers['FM_EGO_standstill']
    standstill_doc = kml.newdocument(name='standstill')
    decelerate = maneuvers['FM_EGO_decelerate']
    decelerate_doc = kml.newdocument(name='decelerate')

    lane_change_left = None
    lane_change_left_doc = None
    lane_change_right = None
    lane_change_right_doc = None
    if ego is True:
        lane_change_left = maneuvers['FM_INF_lane_change_left']
        lane_change_left_doc = kml.newdocument(name='lane_change_left')
        lane_change_right = maneuvers['FM_INF_lane_change_right']
        lane_change_right_doc = kml.newdocument(name='lane_change_right')

    for row in range(lat.shape[0]):
        if not (pd.isna(lat.loc[row])) or not (pd.isna(lon.loc[row])):
            if old_lat != 0 and old_lon != 0:
                pathway = overview_doc.newlinestring()
                pathway.coords = [(old_lon, old_lat), (lon.loc[row], lat.loc[row])]
                pathway.style.linestyle.width = 8
                pathway.style.linestyle.color = simplekml.Color.rgb(0, 0, 0)
                if accelerate[row] == 1:
                    pathway = accelerate_doc.newlinestring()
                    pathway.coords = [(old_lon, old_lat), (lon.loc[row], lat.loc[row])]
                    pathway.style.linestyle.width = 4
                    pathway.style.linestyle.color = simplekml.Color.rgb(0, 255, 251)
                if velocity[row] == 1:
                    pathway = velocity_doc.newlinestring()
                    pathway.coords = [(old_lon, old_lat), (lon.loc[row], lat.loc[row])]
                    pathway.style.linestyle.width = 4
                    pathway.style.linestyle.color = simplekml.Color.rgb(0, 143, 255)
                if standstill[row] == 1:
                    pathway = standstill_doc.newlinestring()
                    pathway.coords = [(old_lon, old_lat), (lon.loc[row], lat.loc[row])]
                    pathway.style.linestyle.width = 4
                    pathway.style.linestyle.color = simplekml.Color.rgb(0, 0, 0)
                if decelerate[row] == 1:
                    pathway = decelerate_doc.newlinestring()
                    pathway.coords = [(old_lon, old_lat), (lon.loc[row], lat.loc[row])]
                    pathway.style.linestyle.width = 4
                    pathway.style.linestyle.color = simplekml.Color.rgb(0, 23, 255)
                if ego is True:
                    if lane_change_left[row] == 1:
                        pathway = lane_change_left_doc.newlinestring()
                        pathway.coords = [(old_lon, old_lat), (lon.loc[row], lat.loc[row])]
                        pathway.style.linestyle.width = 4
                        pathway.style.linestyle.color = simplekml.Color.rgb(255, 169, 59)
                    if lane_change_right[row] == 1:
                        pathway = lane_change_right_doc.newlinestring()
                        pathway.coords = [(old_lon, old_lat), (lon.loc[row], lat.loc[row])]
                        pathway.style.linestyle.width = 4
                        pathway.style.linestyle.color = simplekml.Color.rgb(209, 126, 20)

            old_lon = lon.loc[row]
            old_lat = lat.loc[row]

    return kml


def create_speed_model(df_maneuvers: pd.DataFrame, init_speed: float) -> Union[list, np.ndarray]:
    """
    Helper function. Extracts speed information from maneuvers.

    Args:
        df_maneuvers: Maneuvers array
        init_speed: Initial speed

    Returns:
        object (Union[list, np.ndarray]): Modelled speed
    """
    if not isinstance(df_maneuvers, pd.DataFrame):
        raise TypeError("input must be a pd.DataFrame")
    if not isinstance(init_speed, float):
        raise TypeError("input must be a float")

    speed = []
    man_type = []  # 1 for acceleration, -1 for deceleration, 0 for standstill
    num_rows, num_cols = df_maneuvers.shape
    
    for i in range(num_rows):
        if df_maneuvers.iloc[i].iloc[2] == 'FM_EGO_decelerate':
            man_type.append(-1)
        elif df_maneuvers.iloc[i].iloc[2] == 'FM_EGO_keep_velocity':
            if i == 0:
                start_speed = float(init_speed / 3.6)
            else:
                start_speed = float(df_maneuvers.iloc[i - 1].iloc[5])

            if float(df_maneuvers.iloc[i].iloc[5]) >= start_speed:
                man_type.append(1)
            else:
                man_type.append(-1)
        elif df_maneuvers.iloc[i].iloc[2] == 'FM_EGO_accelerate':
            man_type.append(1)
        elif df_maneuvers.iloc[i].iloc[2] == 'FM_EGO_standstill':
            man_type.append(0)

    accel_res = []
    maneuver_len = []
    for i in range(num_rows):
        accel_res.append(float(df_maneuvers.iloc[i].iloc[6]) * man_type[i])
        if i > 0:
            maneuver_start = int(df_maneuvers.iloc[i].iloc[0])
            maneuver_end = int(df_maneuvers.iloc[i - 1].iloc[1])
            if maneuver_end >= maneuver_start:
                maneuver_len.append(int(df_maneuvers.iloc[i].iloc[1]) - maneuver_end)
            else:
                maneuver_len.append(int(df_maneuvers.iloc[i].iloc[1]) + 1 - int(df_maneuvers.iloc[i].iloc[0]))
        else:
            maneuver_len.append(int(df_maneuvers.iloc[i].iloc[1]) + 1 - int(df_maneuvers.iloc[i].iloc[0]))

    start_time = int(df_maneuvers.iloc[0].iloc[0])
    delta_t = 0.1

    acc_full = []
    for i in range(len(maneuver_len)):
        for k in range(int(maneuver_len[i])):
            acc_full.append(accel_res[i])
    for i in range(start_time, start_time + len(acc_full)):
        if i == start_time:
            speed.append(init_speed)
        else:
            if start_time == 0:
                sub = 1
            else:
                sub = start_time + 1
            speed.append(speed[i - sub] + acc_full[i - sub] * delta_t * 3.6)
    speed_np = np.array(speed)
    return speed_np


def calc_opt_acc_thresh(df: pd.DataFrame, df_lanes: pd.DataFrame, opendrive_path: str, use_folder: bool,
                        dir_name: str) -> np.ndarray:
    """
    Used to get optimal acceleration threshold to label maneuvers.

    Args:
        df: Main processed dataframe
        df_lanes: Dataframe which contains absolute positions of lanes
        opendrive_path: Path to opendrive file
        use_folder: Option to create folder structure
        dir_name: Name of the folder

    Returns:
        object (np.ndarray): Optimal acceleration threshold
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("input must be a pd.DataFrame")
    if not isinstance(df_lanes, pd.DataFrame):
        raise TypeError("input must be a pd.DataFrame")
    if not isinstance(opendrive_path, str):
        raise TypeError("input must be a str")
    if not isinstance(use_folder, bool):
        raise TypeError("input must be a bool")
    if not isinstance(dir_name, str):
        raise TypeError("input must be a str")

    movobj_grps_coord = utils.find_vars('lat_|lon_|speed_|class', df.columns, reshape=True)

    # Labeling
    lane_change_left_array, lane_change_right_array = rulebased.create_lateral_maneuver_vectors(df_lanes, df['lat'], df['long'])
    # Array can be extended with more values for acceleration thresholds
    acc_thres = np.array([0.05, 0.1, 0.15, 0.2, 0.25, 0.3])
    quality_array = np.zeros((len(movobj_grps_coord) + 1, len(acc_thres)))

    for x in range(len(acc_thres)):
        curr_thres = acc_thres[x]
        print('current acceleration threshold: ' + str(curr_thres))
        speed = df['speed']
        accelerate_array, \
            start_array, \
            keep_velocity_array, \
            standstill_array, \
            decelerate_array, \
            stop_array, \
            reversing_array = rulebased.create_longitudinal_maneuver_vectors(
                speed, acceleration_definition_threshold=curr_thres)

        # Create df with maneuver info
        df_maneuvers = pd.DataFrame(data=None)
        df_maneuvers['FM_INF_lane_change_left'] = lane_change_left_array
        df_maneuvers['FM_INF_lane_change_right'] = lane_change_right_array
        df_maneuvers['FM_EGO_accelerate'] = accelerate_array
        df_maneuvers['FM_EGO_start'] = start_array
        df_maneuvers['FM_EGO_keep_velocity'] = keep_velocity_array
        df_maneuvers['FM_EGO_standstill'] = standstill_array
        df_maneuvers['FM_EGO_decelerate'] = decelerate_array
        df_maneuvers['FM_EGO_stop'] = stop_array
        df_maneuvers['FM_EGO_reversing'] = reversing_array

        df_maneuvers_objects = {}
        for i in range(len(movobj_grps_coord)):
            speed = df[movobj_grps_coord[i][2]]
            accelerate_array, \
                start_array, \
                keep_velocity_array, \
                standstill_array, \
                decelerate_array, \
                stop_array, \
                reversing_array = rulebased.create_longitudinal_maneuver_vectors(
                    speed, acceleration_definition_threshold=acc_thres[x])
            df_maneuvers_objects[i] = pd.DataFrame(data=None)
            df_maneuvers_objects[i]['FM_EGO_accelerate'] = accelerate_array
            df_maneuvers_objects[i]['FM_EGO_start'] = start_array
            df_maneuvers_objects[i]['FM_EGO_keep_velocity'] = keep_velocity_array
            df_maneuvers_objects[i]['FM_EGO_standstill'] = standstill_array
            df_maneuvers_objects[i]['FM_EGO_decelerate'] = decelerate_array
            df_maneuvers_objects[i]['FM_EGO_stop'] = stop_array
            df_maneuvers_objects[i]['FM_EGO_reversing'] = reversing_array
            left_lane_change_array, right_lane_change_array = rulebased.create_lateral_maneuver_vectors(df_lanes, df[
                movobj_grps_coord[i][0]], df[movobj_grps_coord[i][1]])  # lat lon
            df_maneuvers_objects[i]['FM_INF_lane_change_left'] = left_lane_change_array
            df_maneuvers_objects[i]['FM_INF_lane_change_right'] = right_lane_change_array

        # Init
        # Get projection coordinates of respective open drive from open drive file
        proj_in = pyproj.Proj('EPSG:4326')
        proj_out = get_proj_from_open_drive(open_drive_path=opendrive_path)
        columns = ['lat', 'long', 'speed', 'heading']

        # Get start position, speed and heading of ego
        ego = []
        lon, lat = (pyproj.Transformer.from_crs(proj_in.crs, proj_out.crs, always_xy=True)).transform(
            df[columns[1]][0],
            df[columns[0]][0])
        ego.append(lon)
        ego.append(lat)
        ego.append(df[columns[2]][0] / 3.6)  # Speed
        ego.append(utils.convert_heading(df[columns[3]][0]))  # Heading

        # Get start position, speed and heading of other objects
        objects = {}
        for i in range(len(movobj_grps_coord)):
            lon, lat = (pyproj.Transformer.from_crs(proj_in.crs, proj_out.crs, always_xy=True)).transform(
                df[movobj_grps_coord[i][1]][0],
                df[movobj_grps_coord[i][0]][0])
            obj = list()
            obj.append(lon)  # Lon
            obj.append(lat)  # Lat
            obj.append(df[movobj_grps_coord[i][2]][0] / 3.6)  # Speed

            temp_heading = utils.calc_heading_from_two_geo_positions(df[movobj_grps_coord[i][0]][0], df[movobj_grps_coord[i][1]][0],
                                                                     df[movobj_grps_coord[i][0]][1], df[movobj_grps_coord[i][1]][1])
            obj.append(utils.convert_heading(temp_heading))

            objects[i] = obj

        # Get maneuvers
        ego_maneuver_array = {}
        for j in range(len(df_maneuvers_objects) + 1):  # + 1 because of ego maneuvers
            # Ego basis maneuvers for speed & acceleration control
            acceleration_switch = -1
            keep_switch = -1
            deceleration_switch = -1
            standstill_switch = -1

            temp_ego_maneuver_array = np.empty(shape=[0, 7])
            if j == 0:  # Use ego
                maneuvers = df_maneuvers
                cols = columns
            else:  # Use objects
                maneuvers = df_maneuvers_objects[j - 1]
                cols = movobj_grps_coord[j - 1]

            # Get start and end time of each maneuver
            for i in range(len(maneuvers)):
                # Start
                if maneuvers['FM_EGO_accelerate'][i] == 1 and acceleration_switch == -1:
                    temp_lon, temp_lat = (pyproj.Transformer.from_crs(proj_in.crs, proj_out.crs, always_xy=True)).\
                        transform(
                        df[cols[1]][i],
                        df[cols[0]][i])
                    temp_ego_maneuver_array = np.append(temp_ego_maneuver_array,
                                                        [[i, i, 'FM_EGO_accelerate', temp_lon, temp_lat, 0, 0]], axis=0)
                    acceleration_switch = temp_ego_maneuver_array.shape[0] - 1
                # End
                elif maneuvers['FM_EGO_accelerate'][i] == 0 and acceleration_switch > -1:
                    temp_ego_maneuver_array[acceleration_switch][1] = i - 1
                    # Target speed
                    temp_ego_maneuver_array[acceleration_switch][5] = df[cols[2]][i - 1] / 3.6
                    # Calculate the acceleration = (target speed - start speed) / duration
                    temp_ego_maneuver_array[acceleration_switch][6] = abs(df[cols[2]][i - 1] / 3.6 - (
                            df[cols[2]][int(temp_ego_maneuver_array[acceleration_switch][0])] / 3.6)) / ((i - int(
                                temp_ego_maneuver_array[acceleration_switch][0])) / 10)
                    acceleration_switch = -1

                if maneuvers['FM_EGO_keep_velocity'][i] == 1 and keep_switch == -1:
                    temp_lon, temp_lat = (pyproj.Transformer.from_crs(proj_in.crs, proj_out.crs, always_xy=True)).\
                        transform(
                        df[cols[1]][i],
                        df[cols[0]][i])
                    temp_ego_maneuver_array = np.append(temp_ego_maneuver_array,
                                                        [[i, i, 'FM_EGO_keep_velocity', temp_lon, temp_lat, 0, 0]],
                                                        axis=0)
                    keep_switch = temp_ego_maneuver_array.shape[0] - 1
                elif maneuvers['FM_EGO_keep_velocity'][i] == 0 and keep_switch > -1:
                    temp_ego_maneuver_array[keep_switch][1] = i - 1
                    temp_ego_maneuver_array[keep_switch][5] = df[cols[2]][i - 1] / 3.6
                    temp_ego_maneuver_array[keep_switch][6] = abs(df[cols[2]][i - 1] / 3.6 - (
                            df[cols[2]][int(temp_ego_maneuver_array[keep_switch][0])] / 3.6)) / ((i - int(
                                temp_ego_maneuver_array[keep_switch][0])) / 10)
                    keep_switch = -1

                if maneuvers['FM_EGO_decelerate'][i] == 1 and deceleration_switch == -1:
                    temp_lon, temp_lat = (pyproj.Transformer.from_crs(proj_in.crs, proj_out.crs, always_xy=True)).\
                        transform(
                        df[cols[1]][i],
                        df[cols[0]][i])
                    temp_ego_maneuver_array = np.append(temp_ego_maneuver_array,
                                                        [[i, i, 'FM_EGO_decelerate', temp_lon, temp_lat, 0, 0]],
                                                        axis=0)
                    deceleration_switch = temp_ego_maneuver_array.shape[0] - 1
                elif maneuvers['FM_EGO_decelerate'][i] == 0 and deceleration_switch > -1:
                    temp_ego_maneuver_array[deceleration_switch][1] = i - 1
                    temp_ego_maneuver_array[deceleration_switch][5] = df[cols[2]][i - 1] / 3.6
                    temp_ego_maneuver_array[deceleration_switch][6] = abs(df[cols[2]][i - 1] / 3.6 - (
                            df[cols[2]][int(temp_ego_maneuver_array[deceleration_switch][0])] / 3.6)) / ((i - int(
                                temp_ego_maneuver_array[deceleration_switch][0])) / 10)
                    deceleration_switch = -1

                if maneuvers['FM_EGO_standstill'][i] == 1 and standstill_switch == -1:
                    if len(temp_ego_maneuver_array) > 0:  # Assure that last maneuver (if it exists) ends with 0 km/h
                        temp_ego_maneuver_array[len(temp_ego_maneuver_array) - 1][5] = 0.0
                    temp_lon, temp_lat = pyproj.transform(proj_in, proj_out, df[cols[1]][i], df[cols[0]][i])
                    temp_ego_maneuver_array = np.append(temp_ego_maneuver_array,
                                                        [[i, i, 'FM_EGO_standstill', temp_lon, temp_lat, 0, 0]],
                                                        axis=0)
                    standstill_switch = temp_ego_maneuver_array.shape[0] - 1
                elif maneuvers['FM_EGO_standstill'][i] == 0 and standstill_switch > -1:
                    temp_ego_maneuver_array[standstill_switch][1] = i - 1
                    temp_ego_maneuver_array[standstill_switch][5] = df[cols[2]][i - 1] / 3.6
                    temp_ego_maneuver_array[standstill_switch][6] = abs(df[cols[2]][i - 1] / 3.6 - (
                            df[cols[2]][int(temp_ego_maneuver_array[standstill_switch][0])] / 3.6)) / ((i - int(
                                temp_ego_maneuver_array[standstill_switch][0])) / 10)
                    standstill_switch = -1

            if j == 0:
                speed = df['speed']
            else:
                speed_tmp = df[movobj_grps_coord[j - 1][2]]
                speed = []
                for y in range(len(speed_tmp)):
                    if not math.isnan(speed_tmp[y]):
                        speed.append(speed_tmp[y])
            speed = np.array(speed)

            # Calculate the model speed in osc format (linear accelerations)
            if temp_ego_maneuver_array.size != 0:
                df_ego_maneuver_array = pd.DataFrame(
                    data=temp_ego_maneuver_array[0:, 0:],
                    index=temp_ego_maneuver_array[0:, 0],
                    columns=temp_ego_maneuver_array[0, 0:])
                model_speed = create_speed_model(df_ego_maneuver_array, speed[0])
                # Use RMSE Value for calculating the difference
                if len(model_speed) - len(speed) == 1:
                    rmse_speed = np.sqrt(np.square(np.subtract(model_speed[0:-1], speed)).mean())
                elif len(speed) - len(model_speed) == 1:
                    rmse_speed = np.sqrt(np.square(np.subtract(model_speed, speed[0:-1])).mean())
                elif len(model_speed) == len(speed):
                    rmse_speed = np.sqrt(np.square(np.subtract(model_speed, speed)).mean())
                else:
                    rmse_speed = 999
            else:
                rmse_speed = 999
            ego_maneuver_array[j] = temp_ego_maneuver_array
            quality_array[j][x] = rmse_speed

    # Get the minumum RMSE values for each object (EGO + Player)
    num_rows, num_cols = quality_array.shape
    df_opt_acc = pd.DataFrame()
    acc_thres_opt = []
    obj_qual = np.empty(0)
    for z in range(num_rows):
        obj_qual = quality_array[z][:]
        acc_thres_opt.append(acc_thres[np.argmin(obj_qual)])
        if z == 0:
            playername = 'EGO'
        else:
            playername = 'Player' + str(z)
        df_opt_acc[playername] = [acc_thres[np.argmin(obj_qual)]]

    if use_folder:
        if not os.path.isdir(os.path.abspath(dir_name)):
            raise FileNotFoundError("input must be a valid path.")
        if not os.path.exists(os.path.abspath(dir_name)):
            raise NotADirectoryError("input must be a directory.")
        maneuver_dir = os.path.abspath(dir_name + '/maneuver_lists')
        if not os.path.exists(maneuver_dir):
            os.mkdir(maneuver_dir)
        df_opt_acc.to_csv(maneuver_dir + '/acc_thres_values.csv')
    acc_thres_opt.append(acc_thres[np.argmin(obj_qual)])

    return np.array(acc_thres_opt)


def label_maneuvers(df: pd.DataFrame, df_lanes: pd.DataFrame, acc_threshold: Union[float, np.ndarray], generate_kml: bool,
                    opendrive_path: str, use_folder: bool, dir_name: str) -> tuple:
    """
    Used for labeling the maneuvers

    Args:
        df: Main processed Dataframe
        df_lanes: Dataframe which contains absolute positions of lanes
        acc_threshold: Acceleration threshold for labeling
        generate_kml: Option to generate kml files
        opendrive_path: Path to opendrive file
        use_folder: Option to create folder structure
        dir_name: Name of the folder

    Returns:
        object (tuple): ego_maneuver_array, inf_maneuver_array, objlist, objects, ego, movobj_grps_coord
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("input must be a pd.DataFrame")
    if not isinstance(df_lanes, pd.DataFrame):
        raise TypeError("input must be a pd.DataFrame")
    if not (isinstance(acc_threshold, float) or isinstance(acc_threshold, np.ndarray)):
        raise TypeError("input must be a float or np.ndarray")
    if not isinstance(generate_kml, bool):
        raise TypeError("input must be a bool")
    if not isinstance(opendrive_path, str):
        raise TypeError("input must be a str")
    if not isinstance(use_folder, bool):
        raise TypeError("input must be a bool")
    if not isinstance(dir_name, str):
        raise TypeError("input must be a str")

    # Get signals from trajectories file
    speed = df['speed']

    # Labeling
    lane_change_left_array, lane_change_right_array = rulebased.create_lateral_maneuver_vectors(df_lanes,
                                                                                                df['lat'],
                                                                                                df['long'])
    if isinstance(acc_threshold, int) or isinstance(acc_threshold, float):
        accelerate_array, \
            start_array, \
            keep_velocity_array, \
            standstill_array, \
            decelerate_array, \
            stop_array, \
            reversing_array = rulebased.create_longitudinal_maneuver_vectors(
                            speed, acceleration_definition_threshold=acc_threshold)
    else:
        accelerate_array, \
            start_array, \
            keep_velocity_array, \
            standstill_array, \
            decelerate_array, \
            stop_array, \
            reversing_array = rulebased.create_longitudinal_maneuver_vectors(
                                speed, acceleration_definition_threshold=acc_threshold[0])

    # Create df with maneuver info
    df_maneuvers = pd.DataFrame(data=None)
    df_maneuvers['FM_INF_lane_change_left'] = lane_change_left_array
    df_maneuvers['FM_INF_lane_change_right'] = lane_change_right_array
    df_maneuvers['FM_EGO_accelerate'] = accelerate_array
    df_maneuvers['FM_EGO_start'] = start_array
    df_maneuvers['FM_EGO_keep_velocity'] = keep_velocity_array
    df_maneuvers['FM_EGO_standstill'] = standstill_array
    df_maneuvers['FM_EGO_decelerate'] = decelerate_array
    df_maneuvers['FM_EGO_stop'] = stop_array
    df_maneuvers['FM_EGO_reversing'] = reversing_array

    if use_folder:
        if not os.path.exists(dir_name + '/maneuver_lists'):
            os.mkdir(dir_name + '/maneuver_lists')
        df_maneuvers.to_excel(dir_name + '/maneuver_lists/maneuver_ego.xlsx')

    class_dict = {0: ["UnknownClass1"],
                  3: ["PedestrianClass1"],
                  5: ["BicycleClass1"],
                  6: ["MotorbikeClass1"],
                  7: ["CarClass1"],
                  8: ["VanClass1"],
                  9: ["TruckClass1"],
                  11: ["AnimalClass1"]}

    movobj_grps_coord = utils.find_vars('lat_|lon_|speed_|class', df.columns, reshape=True)
    rel_class = [int(df[movobj_grps_coord[i][3]].mode()) for i in range(len(movobj_grps_coord))]
    objlist = []
    np.random.seed(0)
    for cl in rel_class:
        objlist.append(class_dict[cl][np.random.randint(0, len(class_dict[cl]))])

    df_maneuvers_objects = {}
    for i in range(len(movobj_grps_coord)):
        speed = df[movobj_grps_coord[i][2]]
        if isinstance(acc_threshold, int) or isinstance(acc_threshold, float):
            accelerate_array, \
                start_array, \
                keep_velocity_array, \
                standstill_array, \
                decelerate_array, \
                stop_array, \
                reversing_array = rulebased.create_longitudinal_maneuver_vectors(
                                            speed, acceleration_definition_threshold=acc_threshold)
        else:
            accelerate_array, \
                start_array, \
                keep_velocity_array, \
                standstill_array, \
                decelerate_array, \
                stop_array, \
                reversing_array = rulebased.create_longitudinal_maneuver_vectors(
                    speed,
                    acceleration_definition_threshold=acc_threshold[i + 1])
        df_maneuvers_objects[i] = pd.DataFrame(data=None)
        df_maneuvers_objects[i]['FM_EGO_accelerate'] = accelerate_array
        df_maneuvers_objects[i]['FM_EGO_start'] = start_array
        df_maneuvers_objects[i]['FM_EGO_keep_velocity'] = keep_velocity_array
        df_maneuvers_objects[i]['FM_EGO_standstill'] = standstill_array
        df_maneuvers_objects[i]['FM_EGO_decelerate'] = decelerate_array
        df_maneuvers_objects[i]['FM_EGO_stop'] = stop_array
        df_maneuvers_objects[i]['FM_EGO_reversing'] = reversing_array
        left_lane_change_array, right_lane_change_array = rulebased.create_lateral_maneuver_vectors(df_lanes,
                                                                                                    df[movobj_grps_coord[i][0]],
                                                                                                    df[movobj_grps_coord[i][1]])
        df_maneuvers_objects[i]['FM_INF_lane_change_left'] = left_lane_change_array
        df_maneuvers_objects[i]['FM_INF_lane_change_right'] = right_lane_change_array
        if use_folder:
            df_maneuvers_objects[i].to_excel(dir_name + '/maneuver_lists/maneuver_object' + str(i) + '.xlsx')

    if generate_kml:
        kml = convert_maneuvers_to_kml(df['lat'], df['long'], df_maneuvers, True)
        if use_folder:
            if not os.path.exists(dir_name + '/kml_files'):
                os.mkdir(dir_name + '/kml_files')
            kml.save(dir_name + '/kml_files/ego.kml')
        else:
            kml.save(r'../files/ego.kml')
        for i in range(len(movobj_grps_coord)):
            lat = df[movobj_grps_coord[i][0]]
            lon = df[movobj_grps_coord[i][1]]
            kml = convert_maneuvers_to_kml(lat, lon, df_maneuvers_objects[i], False)
            if use_folder:
                kml.save(dir_name + '/kml_files/vehicle' + str(i) + '.kml')
            else:
                kml.save(r'../files/vehicle' + str(i) + '.kml')

    # Prepare simulation parameters
    # Get projection coordinates of respective open drive from open drive file
    proj_in = pyproj.Proj('EPSG:4326')
    proj_out = get_proj_from_open_drive(open_drive_path=opendrive_path)
    columns = ['lat', 'long', 'speed', 'heading']

    # Get start position, speed and heading of ego
    ego = []
    lon, lat = (pyproj.Transformer.from_crs(proj_in.crs, proj_out.crs, always_xy=True)).transform(df[columns[1]][0],
                                                                                                  df[columns[0]][0])
    
    ego.append(lon)
    ego.append(lat)
    ego.append(df[columns[2]][0] / 3.6)  # speed
    ego.append(utils.convert_heading(df[columns[3]][0]))  # heading

    # Get start position, speed and heading of other objects
    objects = {}
    for i in range(len(movobj_grps_coord)):
        lon, lat = (pyproj.Transformer.from_crs(proj_in.crs, proj_out.crs, always_xy=True)).transform(
            df[movobj_grps_coord[i][1]][0],
            df[movobj_grps_coord[i][0]][0])
        obj = list()
        obj.append(lon)  # Lon
        obj.append(lat)  # Lat
        obj.append(df[movobj_grps_coord[i][2]][0] / 3.6)  # speed

        temp_heading = utils.calc_heading_from_two_geo_positions(df[movobj_grps_coord[i][0]][0], df[movobj_grps_coord[i][1]][0],
                                                                 df[movobj_grps_coord[i][0]][2], df[movobj_grps_coord[i][1]][2])
        obj.append(utils.convert_heading(temp_heading))

        objects[i] = obj

    # Get maneuvers
    ego_maneuver_array = {}
    for j in range(len(df_maneuvers_objects) + 1):  # + 1 because of ego maneuvers
        # Ego basis maneuvers for speed & acceleration control
        acceleration_switch = -1
        keep_switch = -1
        deceleration_switch = -1
        standstill_switch = -1

        temp_ego_maneuver_array = np.empty(shape=[0, 7])
        if j == 0:  # Use ego
            maneuvers = df_maneuvers
            cols = columns
        else:  # Use objects
            maneuvers = df_maneuvers_objects[j - 1]
            cols = movobj_grps_coord[j - 1]

        # Get start and end time of each maneuver
        for i in range(len(maneuvers)):
            # Start
            if maneuvers['FM_EGO_accelerate'][i] == 1 and acceleration_switch == -1:
                temp_lon, temp_lat = (pyproj.Transformer.from_crs(proj_in.crs, proj_out.crs, always_xy=True)).transform(
                    df[cols[1]][i],
                    df[cols[0]][i])
                temp_ego_maneuver_array = np.append(temp_ego_maneuver_array,
                                                    [[i, i, 'FM_EGO_accelerate', temp_lon, temp_lat, 0, 0]], axis=0)
                acceleration_switch = temp_ego_maneuver_array.shape[0] - 1
            # End
            elif maneuvers['FM_EGO_accelerate'][i] == 0 and acceleration_switch > -1:
                temp_ego_maneuver_array[acceleration_switch][1] = i - 1
                # Target speed
                temp_ego_maneuver_array[acceleration_switch][5] = df[cols[2]][i - 1] / 3.6
                # Calculate the acceleration = (target speed - start speed) / duration
                temp_ego_maneuver_array[acceleration_switch][6] = abs(df[cols[2]][i - 1] / 3.6 - (
                        df[cols[2]][int(temp_ego_maneuver_array[acceleration_switch][0])] / 3.6)) / ((i - int(
                            temp_ego_maneuver_array[acceleration_switch][0])) / 10)
                acceleration_switch = -1

            if maneuvers['FM_EGO_keep_velocity'][i] == 1 and keep_switch == -1:
                temp_lon, temp_lat = (pyproj.Transformer.from_crs(proj_in.crs, proj_out.crs, always_xy=True)).transform(
                    df[cols[1]][i],
                    df[cols[0]][i])
                temp_ego_maneuver_array = np.append(temp_ego_maneuver_array,
                                                    [[i, i, 'FM_EGO_keep_velocity', temp_lon, temp_lat, 0, 0]], axis=0)
                keep_switch = temp_ego_maneuver_array.shape[0] - 1
            elif maneuvers['FM_EGO_keep_velocity'][i] == 0 and keep_switch > -1:
                temp_ego_maneuver_array[keep_switch][1] = i - 1
                temp_ego_maneuver_array[keep_switch][5] = df[cols[2]][i - 1] / 3.6
                temp_ego_maneuver_array[keep_switch][6] = abs(
                    df[cols[2]][i - 1] / 3.6 - (df[cols[2]][int(temp_ego_maneuver_array[keep_switch][0])] / 3.6)) / \
                    ((i - int(temp_ego_maneuver_array[keep_switch][0])) / 10)
                keep_switch = -1

            if maneuvers['FM_EGO_decelerate'][i] == 1 and deceleration_switch == -1:
                temp_lon, temp_lat = (pyproj.Transformer.from_crs(proj_in.crs, proj_out.crs, always_xy=True)).transform(
                    df[cols[1]][i],
                    df[cols[0]][i])
                temp_ego_maneuver_array = np.append(temp_ego_maneuver_array,
                                                    [[i, i, 'FM_EGO_decelerate', temp_lon, temp_lat, 0, 0]], axis=0)
                deceleration_switch = temp_ego_maneuver_array.shape[0] - 1
            elif maneuvers['FM_EGO_decelerate'][i] == 0 and deceleration_switch > -1:
                temp_ego_maneuver_array[deceleration_switch][1] = i - 1
                temp_ego_maneuver_array[deceleration_switch][5] = df[cols[2]][i - 1] / 3.6
                temp_ego_maneuver_array[deceleration_switch][6] = abs(df[cols[2]][i - 1] / 3.6 - (
                        df[cols[2]][int(temp_ego_maneuver_array[deceleration_switch][0])] / 3.6)) / ((i - int(
                            temp_ego_maneuver_array[deceleration_switch][0])) / 10)
                deceleration_switch = -1

            if maneuvers['FM_EGO_standstill'][i] == 1 and standstill_switch == -1:
                if len(temp_ego_maneuver_array) > 0:  # Assure that last maneuver (if it exists) ends with 0 km/h
                    temp_ego_maneuver_array[len(temp_ego_maneuver_array) - 1][5] = 0.0
                temp_lon, temp_lat = pyproj.transform(proj_in, proj_out, df[cols[1]][i], df[cols[0]][i])
                temp_ego_maneuver_array = np.append(temp_ego_maneuver_array,
                                                    [[i, i, 'FM_EGO_standstill', temp_lon, temp_lat, 0, 0]], axis=0)
                standstill_switch = temp_ego_maneuver_array.shape[0] - 1
            elif maneuvers['FM_EGO_standstill'][i] == 0 and standstill_switch > -1:
                temp_ego_maneuver_array[standstill_switch][1] = i - 1
                temp_ego_maneuver_array[standstill_switch][5] = df[cols[2]][i - 1] / 3.6
                temp_ego_maneuver_array[standstill_switch][6] = abs(df[cols[2]][i - 1] / 3.6 - (
                        df[cols[2]][int(temp_ego_maneuver_array[standstill_switch][0])] / 3.6)) / ((i - int(
                            temp_ego_maneuver_array[standstill_switch][0])) / 10)
                standstill_switch = -1

        ego_maneuver_array[j] = temp_ego_maneuver_array
        if use_folder:
            pd.DataFrame(temp_ego_maneuver_array).to_csv(
                dir_name + '/maneuver_lists/maneuver_array_lon_' + str(j) + '.csv')

    # Infrastructure maneuvers for lane change control
    inf_maneuver_array = {}
    for j in range(len(df_maneuvers_objects) + 1):  # + 1 because of ego maneuvers
        lane_change_left_switch = -1
        lane_change_right_switch = -1
        temp_inf_maneuver_array = np.empty(shape=[0, 6])
        if j == 0:  # Use ego
            maneuvers = df_maneuvers
            cols = columns
        else:  # Use objects
            maneuvers = df_maneuvers_objects[j - 1]
            cols = movobj_grps_coord[j - 1]

        # Get start and end time of each maneuver
        for i in range(len(maneuvers)):
            # Get start and end time of maneuver
            if maneuvers['FM_INF_lane_change_left'][i] == 1 and lane_change_left_switch == -1:
                temp_lon, temp_lat = pyproj.transform(proj_in, proj_out, df[cols[1]][i], df[cols[0]][i])
                temp_inf_maneuver_array = np.append(temp_inf_maneuver_array,
                                                    [[i, i, 'FM_INF_lane_change_left', temp_lon, temp_lat, 0]], axis=0)
                lane_change_left_switch = temp_inf_maneuver_array.shape[0] - 1
            elif maneuvers['FM_INF_lane_change_left'][i] == 0 and lane_change_left_switch > -1:
                temp_inf_maneuver_array[lane_change_left_switch][1] = i
                temp_inf_maneuver_array[lane_change_left_switch][5] = (i - int(
                    temp_inf_maneuver_array[lane_change_left_switch][0])) / 10
                lane_change_left_switch = -1
            elif i == len(maneuvers) - 1 and lane_change_left_switch > -1:
                temp_inf_maneuver_array[lane_change_left_switch][1] = i
                temp_inf_maneuver_array[lane_change_left_switch][5] = (i - int(
                    temp_inf_maneuver_array[lane_change_left_switch][0])) / 10
                lane_change_left_switch = -1

            if maneuvers['FM_INF_lane_change_right'][i] == 1 and lane_change_right_switch == -1:
                temp_lon, temp_lat = pyproj.transform(proj_in, proj_out, df[cols[1]][i], df[cols[0]][i])
                temp_inf_maneuver_array = np.append(temp_inf_maneuver_array,
                                                    [[i, i, 'FM_INF_lane_change_right', temp_lon, temp_lat, 0]], axis=0)
                lane_change_right_switch = temp_inf_maneuver_array.shape[0] - 1
            elif maneuvers['FM_INF_lane_change_right'][i] == 0 and lane_change_right_switch > -1:
                temp_inf_maneuver_array[lane_change_right_switch][1] = i
                temp_inf_maneuver_array[lane_change_right_switch][5] = (i - int(
                    temp_inf_maneuver_array[lane_change_right_switch][0])) / 10
                lane_change_right_switch = -1
            elif i == len(maneuvers) - 1 and lane_change_right_switch > -1:
                temp_inf_maneuver_array[lane_change_right_switch][1] = i
                temp_inf_maneuver_array[lane_change_right_switch][5] = (i - int(
                    temp_inf_maneuver_array[lane_change_right_switch][0])) / 10
                lane_change_right_switch = -1

        inf_maneuver_array[j] = temp_inf_maneuver_array
        if use_folder and temp_inf_maneuver_array.size:
            pd.DataFrame(temp_inf_maneuver_array).to_csv(
                dir_name + '/maneuver_lists/maneuver_array_lat_' + str(j) + '.csv')

    return ego_maneuver_array, inf_maneuver_array, objlist, objects, ego, movobj_grps_coord
