#  ****************************************************************************
#  @coord_calculations.py
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

import pandas as pd
import math
import pyproj
from pyproj import Geod
import numpy as np
import warnings


def transform_lanes_rel2abs(df: pd.DataFrame, data_type: str) -> pd.DataFrame:
    """
    Transforms lane coordinates in absolut coordinate system

    Args:
        df: Input dataframe
        data_type: Input file type (csv or osi)

    Returns:
        object (pd.DataFrame): Transformed dataframe
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("input must be a pd.DataFrame")
    if not isinstance(data_type, str):
        raise TypeError("input must be a str")

    def find_curve(begin_x: float, begin_y: float, k: float, end_x: float) -> np.ndarray:
        """
        Helper function for rel2abs. Creates an array containing a 2D curve represented by x and y values.

        Args:
            begin_x: x coordinate of the curve starting point
            begin_y: y coordinate of the curve starting point
            k: curvature of the curve
            end_x: x coordinate of the curve ending point (may not be represented with a point of the array)

        Returns:
            object (np.ndarray): array containing a 2D curve represented by x and y values
        """
        points = []
        x = 0
        x_increment = 2
        while x <= end_x:
            if k == 0:
                points.append((x, begin_y))
            else:
                y = (k * begin_y + 1 - math.sqrt(1 - (k ** 2) * ((x - begin_x) ** 2))) / k
                points.append((x, y))
            x += x_increment
        return np.array(points)

    def calc_new_geopos_from_2d_vector(lat: float, lon: float, head: float, x: float, y: float, g: Geod) -> tuple:
        """
        Helper function for rel2abs. calculates a new geo position based on a start position, heading and a 2d movement
        vector from object perspective

        Args:
            lat: Latitude of starting position
            lon: Longitude of starting position
            head: Starting heading
            x: X component of movement vector from object starting perspective
            y: Y component of movement vector from object starting perspective
            g (pyproj.geod): Geodetic

        Returns:
            object (tuple): Latitude and longitude of new geo position
        """
        d = math.sqrt(x ** 2 + y ** 2)
        # When Azimuth to calculate, it is important to consider heading of ego vehicle
        q = head - math.degrees(math.atan2(y, x))

        endlon, endlat, backaz = g.fwd(lon, lat, q, d, radians=False)
        return endlat, endlon

    length = len(df.index) - 1
    df_crv = df.dropna(subset=['lin_right_beginn_x', 'lin_left_beginn_x'])
    length_crv = len(df_crv.index) - 1
    if data_type == 'csv':
        points_right = find_curve(df_crv['lin_right_beginn_x'][length_crv],
                                df_crv['lin_right_y_abstand'][length_crv],
                                df_crv['lin_right_kruemm'][length_crv],
                                df_crv['lin_right_ende_x'][length_crv])

        points_left = find_curve(df_crv['lin_left_beginn_x'][length_crv],
                               df_crv['lin_left_y_abstand'][length_crv],
                               df_crv['lin_left_kruemm'][length_crv],
                               df_crv['lin_left_ende_x'][length_crv])
        df_temp_1 = pd.DataFrame(columns=['lin_right_beginn_x'])
        df_temp_1['lin_right_beginn_x'] = points_right[:, 0]
        df_temp_1['lin_right_y_abstand'] = points_right[:, 1]
        df_temp_2 = pd.DataFrame(columns=['lin_left_beginn_x'])
        df_temp_2['lin_left_beginn_x'] = points_left[:, 0]
        df_temp_2['lin_left_y_abstand'] = points_left[:, 1]
        df_temp_1 = pd.concat([df_temp_1, df_temp_2], axis=1)
        df_temp_1 = df_temp_1.dropna()

        df = pd.concat([df, df_temp_1], ignore_index=True)
    else:
        pass

    geodetic = Geod(ellps='WGS84')
    r_lane_lat_list = []
    r_lane_lon_list = []
    l_lane_lat_list = []
    l_lane_lon_list = []
    for i in range(len(df.index)):
        if i < length:
            r_lane_lat, r_lane_lon = calc_new_geopos_from_2d_vector(df['lat'][i], df['long'][i], df['heading'][i],
                                                df['lin_right_beginn_x'][i],
                                                df['lin_right_y_abstand'][i], geodetic)
            l_lane_lat, l_lane_lon = calc_new_geopos_from_2d_vector(df['lat'][i], df['long'][i], df['heading'][i],
                                                df['lin_left_beginn_x'][i],
                                                df['lin_left_y_abstand'][i], geodetic)
        else:
            r_lane_lat, r_lane_lon = calc_new_geopos_from_2d_vector(df['lat'][length], df['long'][length], df['heading'][length],
                                                df['lin_right_beginn_x'][i],
                                                df['lin_right_y_abstand'][i], geodetic)
            l_lane_lat, l_lane_lon = calc_new_geopos_from_2d_vector(df['lat'][length], df['long'][length], df['heading'][length],
                                                df['lin_left_beginn_x'][i],
                                                df['lin_left_y_abstand'][i], geodetic)

        r_lane_lat_list.append(r_lane_lat)
        r_lane_lon_list.append(r_lane_lon)
        l_lane_lat_list.append(l_lane_lat)
        l_lane_lon_list.append(l_lane_lon)

    # Give each line an ID:
    left = []
    right = []
    # Detect lane change for id change
    for i in range(length):
        index = i + 1
        if df['lin_left_y_abstand'][index] < 0:
            left.append(index)
        if df['lin_right_y_abstand'][index] > 0:
            right.append(index)

    left_index = []
    right_index = []
    # Delete consecutive values
    for i in range(len(left) - 1):
        if left[i] == left[i + 1] - 1:
            left_index.append(left[i])
    for i in range(len(left_index)):
        left.remove(left_index[i])

    for i in range(len(right) - 1):
        if right[i] == right[i + 1] - 1:
            right_index.append(right[i])
    for i in range(len(right_index)):
        right.remove(right_index[i])

    # Create single list with respective label list
    left_right = left + right
    left_right = sorted(left_right)
    left_right_label = []
    for i in range(len(left_right)):
        if left_right[i] in left:
            left_right_label.append('left')
        if left_right[i] in right:
            left_right_label.append('right')

    df_out = pd.DataFrame()
    if len(left_right) == 0:
        df_out['right_lane_lat'] = r_lane_lat_list
        df_out['right_lane_lon'] = r_lane_lon_list
        df_out['left_lane_lat'] = l_lane_lat_list
        df_out['left_lane_lon'] = l_lane_lon_list
    else:
        array = np.empty(len(r_lane_lat_list))
        array[:] = np.NaN
        df_out['0lat'] = array
        df_out['0lon'] = array
        df_out['1lat'] = array
        df_out['1lon'] = array

        for i in range(len(left_right)):
            df_out[str(i + 2) + 'lat'] = array
            df_out[str(i + 2) + 'lon'] = array

        df_out.iloc[0:left_right[0] + 1, 0] = r_lane_lat_list[0:left_right[0] + 1]
        df_out.iloc[0:left_right[0] + 1, 1] = r_lane_lon_list[0:left_right[0] + 1]
        df_out.iloc[0:left_right[0] + 1, 2] = l_lane_lat_list[0:left_right[0] + 1]
        df_out.iloc[0:left_right[0] + 1, 3] = l_lane_lon_list[0:left_right[0] + 1]

        counter = 4
        id_right = [0, 1]
        id_left = [2, 3]
        for i in range(len(left_right)):
            # Get starting and ending index of next lane slice
            current_index = left_right[i] + 1
            if len(left_right) - 1 == i:
                next_index = df.shape[0]
            else:
                next_index = left_right[i + 1] + 1

            if left_right_label[i] == 'left':
                id_right = id_left
                id_left = [counter, counter + 1]
                counter = counter + 2
            if left_right_label[i] == 'right':
                id_left = id_right
                id_right = [counter, counter + 1]
                counter = counter + 2

            df_out.iloc[current_index:next_index, id_right[0]] = r_lane_lat_list[current_index:next_index]
            df_out.iloc[current_index:next_index, id_right[1]] = r_lane_lon_list[current_index:next_index]
            df_out.iloc[current_index:next_index, id_left[0]] = l_lane_lat_list[current_index:next_index]
            df_out.iloc[current_index:next_index, id_left[1]] = l_lane_lon_list[current_index:next_index]

    return df_out


def get_proj_from_open_drive(open_drive_path: str) -> str:
    """
    Get Coordinate system infos from OpenDrive file

    Args:
        open_drive_path: Path to OpenDRIVE file

    Returns:
        object (str): Coordinate system
    """
    if not isinstance(open_drive_path, str):
        raise TypeError("input must be a str")

    open_drive = open(open_drive_path, 'r')
    proj_open_drive = 'unknown'
    for line in open_drive:
        if line.find("geoReference") >= 0:
            proj_open_drive = pyproj.Proj(line[line.find("[CDATA[") + 7:line.find("]]")])
            break
    if proj_open_drive == 'unknown':
        warnings.warn("no valid coordinate system found in OpenDRIVE -> coordinates won't be correct", UserWarning)

    open_drive.close()
    return proj_open_drive
