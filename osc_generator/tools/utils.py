#  ****************************************************************************
#  @utils.py
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

import math
import decimal
import re
import pandas as pd
import numpy as np
from geographiclib.geodesic import Geodesic
from typing import Union


def delete_irrelevant_objects(df: pd.DataFrame, movobj_grps: Union[list, np.ndarray],
                              min_nofcases: int = 8, max_posx_min: float = 120.0,
                              max_posx_nofcases_ratio: float = 4.0) -> tuple:
    """
    Deletes not relevant objects from input data

    Args:
        df: Input dataframe
        movobj_grps: Detected objects
        min_nofcases: Minimum number of cases (higher value means more dropping)
        max_posx_min: Maximum of minimum distance to object (lower value means more dropping)
        max_posx_nofcases_ratio: Maximum of ratio between minimum distance and number of cases
            (lower value means more dropping)

    Returns:
        df: Dataframe containing only objects
        count: Number of removed objects
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("input must be a Dataframe")
    if not (isinstance(movobj_grps, np.ndarray) or isinstance(movobj_grps, list)):
        raise TypeError("input must be a list or np.ndarray")
    if not isinstance(min_nofcases, int):
        raise TypeError("input must be a integer")
    if not isinstance(max_posx_min, float):
        print(max_posx_min)
        raise TypeError("input must be a float")
    if not isinstance(max_posx_nofcases_ratio, float):
        print(max_posx_nofcases_ratio)
        raise TypeError("input must be a float")

    end = len(df) - 1
    count = 0
    for p in movobj_grps:
        posx_min = df[p[0]].min()
        nofcases = sum(~pd.isna(df[p[0]]))
        if nofcases < min_nofcases or posx_min > max_posx_min or posx_min / nofcases > max_posx_nofcases_ratio:
            df = df.drop(columns=p)
            # count += 1
        else:
            start = True
            first_one = end
            last_one = end
            for i in range(len(df)):
                if start and not pd.isna(df.loc[i, p[0]]):
                    first_one = i
                    start = False
                elif not start and pd.isna(df.loc[i, p[0]]):
                    last_one = i - 1
                    break
            variance = sum((df.loc[first_one:last_one, "speed"] - df.loc[first_one:last_one, p[2]]) ** 2)
            if variance < 50 and nofcases < 50:
                df = df.drop(columns=p)
                count += 1
            else:
                for i in range(first_one, last_one):
                    acceleration = (abs(df.loc[i + 1, p[2]] - df.loc[i, p[2]]) / 3.6) * 10
                    if acceleration > 250:
                        df = df.drop(columns=p)
                        count += 1
                        break
    return df, count


def calc_new_geopos_from_2d_vector_on_spheric_earth(curr_coords: pd.Series, heading: float, dist_x: float, dist_y: float) -> list:
    """
    Computes the new coordinates of the traced car -- interpolation for only 200ms time intervals

    Args:
        curr_coords: Current coordinates of the ego car to get the heading of the car
        heading: Tracked heading of the ego car
        dist_x: Distances in x directions of the ego car
        dist_y: Distances in y directions of the ego car

    Returns:
        object (list): List containing latitude and longitude of new position
    """
    if not isinstance(curr_coords, pd.Series):
        raise TypeError("input must be a pd.Series")
    if not isinstance(heading, float):
        raise TypeError("input must be a float")
    if not isinstance(dist_x, float):
        raise TypeError("input must be a float")
    if not isinstance(dist_y, float):
        raise TypeError("input must be a float")

    earth_rad = 6378137  # Earth radius in meters

    # Take angle from trace
    beta = (heading * math.pi) / 180

    # Step one: in x direction (ego view) new coordinates
    x_versch = dist_x * math.cos(beta)
    y_versch = dist_x * math.sin(beta)
    d_lat = x_versch / earth_rad
    d_lon = y_versch / (earth_rad * math.cos(math.pi * curr_coords[0] / 180))
    lat_new = curr_coords[0] + d_lat * 180 / math.pi
    lon_new = curr_coords[1] + d_lon * 180 / math.pi
    first_coords = [lat_new, lon_new]

    # Step two: in y direction (ego view) new coordinates
    newbeta = beta - (math.pi / 2)  # New heading shift pi/2 for y direction
    x_versch_y = dist_y * math.cos(newbeta)
    y_versch_y = dist_y * math.sin(newbeta)
    d_lat_y = x_versch_y / earth_rad
    d_lon_y = y_versch_y / (
            earth_rad * math.cos(math.pi * first_coords[0] / 180))
    lat_new_final = first_coords[0] + d_lat_y * 180 / math.pi
    lon_new_final = first_coords[1] + d_lon_y * 180 / math.pi
    new_coords = [lat_new_final, lon_new_final]  # Final coordinates shifted in x as well as y direction
    return new_coords


def flatten(x: Union[list, tuple]) -> list:
    """
    Flattening function for nested lists and tuples

    Args:
        x: List or tuple

    Returns:
        object (list): Flat list
    """
    if not isinstance(x, list) and isinstance(x, tuple):
        raise TypeError("input must be a list or tuple")

    out: list = []
    for item in x:
        if isinstance(item, (list, tuple)):
            out.extend(flatten(item))
        else:
            out.append(item)
    return out


def find_vars(pattern: str, var_list: pd.Series.index, reshape: bool = False) -> Union[np.ndarray, list]:
    """
    Find variables for a given pattern in a list

    Args:
        pattern: Search pattern
        var_list: List to be searched
        reshape: If True pattern will be split by '|' and used to reshape output

    Returns:
        object (Union[np.ndarray, list]): Found variables
    """
    if not isinstance(pattern, str):
        raise TypeError("input must be a str")
    if not isinstance(reshape, bool):
        raise TypeError("input must be a bool")

    tmp_list: list = []
    for i in var_list:
        if len(re.findall(pattern, i)):
            tmp_list.append(i)

    if not reshape:
        return tmp_list

    else:
        order = len(pattern.split('|'))
        shape = int(len(tmp_list) / order)
        tlist_np = np.array(tmp_list).reshape(shape, order)
        return tlist_np


def convert_heading(degree: Union[int, float]) -> Union[int, float]:
    """
    Convert heading to other convention and unit

    Args:
        degree: Starting north increasing clockwise

    Returns:
        object (Union[int, float]): Heading angle in rad starting east increasing anti-clockwise and conversion
    """
    if not (isinstance(degree, float) or isinstance(degree, int)):
        raise TypeError("input must be a float or int")

    float_degree = float(degree)
    if float_degree == 0:
        temp_degree: float = 0
    else:
        temp_degree = 360 - float_degree
    temp_degree = temp_degree + 90
    return math.radians(temp_degree)


def calc_heading_from_two_geo_positions(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Get the heading of the vehicle

    Args:
        lat1: Start latitude
        lon1: Start longitude
        lat2: End latitude
        lon2: End longitude

    Returns:
        object (float): Heading in rad
    """
    if not (isinstance(lat1, float) or isinstance(lat1, int)):
        raise TypeError("input must be a float or int")
    if not (isinstance(lon1, float) or isinstance(lon1, int)):
        raise TypeError("input must be a float or int")
    if not (isinstance(lat2, float) or isinstance(lat2, int)):
        raise TypeError("input must be a float or int")
    if not (isinstance(lon2, float) or isinstance(lon2, int)):
        raise TypeError("input must be a float or int")

    brng = Geodesic.WGS84.Inverse(lat1, lon1, lat2, lon2)['azi1']
    return brng
