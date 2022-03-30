#  ****************************************************************************
#  @rulebased.py
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
import matplotlib.pyplot as plt
from shapely.geometry import MultiPoint, LineString, Point
from scipy.signal import find_peaks


def create_longitudinal_maneuver_vectors(speed: pd.Series, acceleration_definition_threshold: float = 0.2,
                                         acceleration_definition_min_length: float = 2.0,
                                         speed_threshold_no_more_start: float = 20.0, plot: bool = False) -> tuple:
    """
    Creates vectors for the longitudinal vehicle maneuvers.

    Args:
        speed: Vehicle speed information
        acceleration_definition_threshold: Due to noise, if acc is bigger --> ego is accelerating
        acceleration_definition_min_length: Minimum number in frames, if ego vehicle state is shorter --> ignore
        speed_threshold_no_more_start: In kmh, if start is labeled and this velocity is surpassed --> finish labeling
        plot: Plotting option

    Returns:
        object (tuple): Vectors with vehicle speed maneuvers:
            accelerate_array,
            start_array,
            keep_velocity_array,
            standstill_array,
            decelerate_array,
            stop_array,
            reversing_array
    """
    if not isinstance(speed, pd.Series):
        raise TypeError("input must be a pd.Series")
    if not isinstance(acceleration_definition_threshold, float):
        raise TypeError("input must be a float")
    if not isinstance(acceleration_definition_min_length, float):
        raise TypeError("input must be a float")
    if not isinstance(speed_threshold_no_more_start, float):
        raise TypeError("input must be a float")
    if not isinstance(plot, bool):
        raise TypeError("input must be a bool")

    new_speed = speed / 3.6  # Conversion km/h --> m/s
    speed_gradient = new_speed.diff(periods=1) / 0.1  # Delta_ay/delta_t
    speed_gradient = speed_gradient.rolling(window=5, min_periods=0).mean()
    speed_gradient = speed_gradient.shift(periods=-2, fill_value=speed_gradient[speed_gradient.shape[0] - 1])
    speed_gradient[speed.isnull()] = np.NaN
    acceleration_x = speed_gradient

    accelerate_array = np.zeros(speed.shape[0])
    start_array = np.zeros(speed.shape[0])
    keep_velocity_array = np.zeros(speed.shape[0])
    standstill_array = np.zeros(speed.shape[0])
    decelerate_array = np.zeros(speed.shape[0])
    stop_array = np.zeros(speed.shape[0])
    reversing_array = np.zeros(speed.shape[0])

    # Initializations
    counter_acceleration = 0
    acceleration_start = False

    counter_deceleration = 0
    deceleration_start = False

    counter_keep = 0
    keep_start = False

    counter_start = -1
    counter_stop = 0

    counter_buffer = 0

    length_speed_rows = 0

    for i in range(speed.shape[0]):
        # Future proofing if breaks are introduced in the loop
        length_speed_rows = i

        # Get acceleration ego
        if acceleration_x[i] > acceleration_definition_threshold:
            acceleration_start = True
            counter_acceleration += 1
        else:
            if acceleration_start & (counter_acceleration >= acceleration_definition_min_length):
                if counter_buffer > 0:
                    counter_acceleration += counter_buffer
                accelerate_array[i - counter_acceleration: i] = 1
                counter_buffer = 0
            else:
                counter_buffer += counter_acceleration
            counter_acceleration = 0
            acceleration_start = False

        # Get deceleration ego
        if acceleration_x[i] < -acceleration_definition_threshold:
            deceleration_start = True
            counter_deceleration += 1
        else:
            if deceleration_start & (counter_deceleration >= acceleration_definition_min_length):
                if counter_buffer > 0:
                    counter_deceleration += counter_buffer
                decelerate_array[i - counter_deceleration: i] = 1
                counter_buffer = 0
            else:
                counter_buffer += counter_deceleration
            counter_deceleration = 0
            deceleration_start = False

        # Get keep velocity ego
        if (acceleration_x[i] < acceleration_definition_threshold) & (
                acceleration_x[i] > -acceleration_definition_threshold) & (speed[i] != 0):
            keep_start = True
            counter_keep += 1
        else:
            if keep_start & (counter_keep > acceleration_definition_min_length):
                if counter_buffer > 0:
                    counter_keep += counter_buffer
                keep_velocity_array[i - counter_keep: i] = 1
                counter_buffer = 0
            else:
                counter_buffer += counter_keep
            counter_keep = 0
            keep_start = False

        # Get reversing
        if speed[i] < 0:
            reversing_array[i] = 1

        # Get standstill
        if speed[i] == 0:
            standstill_array[i] = 1

        # Get start
        # If counter > 0, counter increment (works only after start detection in next if statement)
        if (speed[i] > 0) & (counter_start > 0):
            counter_start += 1
            start_array[(i - counter_start): i] = 1
            # Break criteria:
            if speed[i] > speed_threshold_no_more_start:
                counter_start = -1
            if deceleration_start:
                counter_start = -1
        # If start detected set counter to 1
        if (speed[i] == 0) & (counter_start <= 1):
            counter_start = 1
        if (speed[i] > 0) & (counter_start <= 1):
            counter_start = 0

        # Get stop
        if (counter_stop > 0) & (speed[i] == 0):
            stop_array[i - counter_stop: i] = 1
            counter_stop = 0

        if (speed[i] < speed_threshold_no_more_start) & (speed[i] != 0):
            counter_stop += 1
        else:
            counter_stop = 0

        if acceleration_start:
            counter_stop = 0
        if keep_start:
            counter_stop = 0

    counter_acceleration += counter_buffer
    counter_deceleration += counter_buffer
    counter_keep += counter_buffer

    # Make sure that last maneuver is labeled
    if acceleration_start:
        accelerate_array[length_speed_rows - counter_acceleration: length_speed_rows] = 1
    if deceleration_start:
        decelerate_array[length_speed_rows - counter_deceleration: length_speed_rows] = 1
    if keep_start:
        keep_velocity_array[length_speed_rows - counter_keep: length_speed_rows] = 1

    if plot:
        fill_array = accelerate_array.astype('bool') | decelerate_array.astype('bool') | \
                     keep_velocity_array.astype('bool') | reversing_array.astype('bool') | \
                     standstill_array.astype('bool') | start_array.astype('bool') | stop_array.astype('bool')
        plt.subplot(10, 1, 1)
        plt.plot(speed)
        plt.subplot(10, 1, 2)
        plt.plot(acceleration_x)
        plt.subplot(10, 1, 3)
        plt.plot(accelerate_array)
        plt.subplot(10, 1, 4)
        plt.plot(decelerate_array)
        plt.subplot(10, 1, 5)
        plt.plot(keep_velocity_array)
        plt.subplot(10, 1, 6)
        plt.plot(reversing_array)
        plt.subplot(10, 1, 7)
        plt.plot(standstill_array)
        plt.subplot(10, 1, 8)
        plt.plot(start_array)
        plt.subplot(10, 1, 9)
        plt.plot(stop_array)
        plt.subplot(10, 1, 10)
        plt.plot(fill_array)
        plt.show()

    return accelerate_array, start_array, keep_velocity_array, standstill_array, decelerate_array, stop_array, \
        reversing_array


def create_lateral_maneuver_vectors(df_lanes: pd.DataFrame, lat: pd.core.series.Series,
                                    lon: pd.core.series.Series, plot: bool = False) -> tuple:
    """
    Get lane change maneuver from lanes with absolute coordinates

    Args:
        df_lanes: Lane coordinates
        lat: Latitude of the vehicle
        lon: Longitude of the vehicle
        plot: Plotting option

    Returns:
        object (tuple): Vectors with vehicle lane change maneuvers:
    """
    if not isinstance(df_lanes, pd.DataFrame):
        raise TypeError("input must be a pd.DataFrame")
    if not isinstance(lat, pd.core.series.Series):
        raise TypeError("input must be a pd.core.series.Series")
    if not isinstance(lon, pd.core.series.Series):
        raise TypeError("input must be a pd.core.series.Series")
    if not isinstance(plot, bool):
        raise TypeError("input must be a bool")

    def find_intersection(x_targ_series, y_targ_series, x_ref_series, y_ref_series):
        """
        Helper function. detects lanechange

        Args:
            x_targ_series (pd.core.series.Series): series containing x-components
            y_targ_series (pd.core.series.Series): series containing y-components
            x_ref_series (pd.core.series.Series): series containing x-components
            y_ref_series (pd.core.series.Series): series containing y-components

        Returns:
            object (np.ndarray, np.ndarray): arrays indicating lane change left and right:
                left_lane_change, right_lane_change,
                left_lane_change, right_lane_change
        """
        x_targ_arr = np.asarray(x_targ_series)
        y_targ_arr = np.asarray(y_targ_series)
        x_ref_arr = np.asarray(x_ref_series)
        y_ref_arr = np.asarray(y_ref_series)

        l1 = LineString(list(zip(x_ref_arr[~np.isnan(x_ref_arr)], y_ref_arr[~np.isnan(y_ref_arr)])))
        l2 = LineString(list(zip(x_targ_arr, y_targ_arr)))

        # Find "ideal" intersection point
        intersection = l1.intersection(l2)
        if intersection.is_empty:
            xs = []
            ys = []
        elif isinstance(intersection, MultiPoint):
            xs = [point.x for point in intersection]
            ys = [point.y for point in intersection]
        else:
            xs = [intersection.x]
            ys = [intersection.y]

        dist = []
        dist2 = []
        dist3 = []

        left_lanechange_array = np.zeros(len(x_targ_arr))
        right_lanechange_array = np.zeros(len(x_targ_arr))
        if len(xs) > 0:
            for x_targ_index in range(len(x_targ_arr)):
                # Find the nearest trajectory point to "ideal" intersection point
                dist.append((x_targ_arr[x_targ_index] - xs[0]) ** 2 + (y_targ_arr[x_targ_index] - ys[0]) ** 2)

                # Compute the distance between trajectory and crossed lane
                point = Point(x_targ_arr[x_targ_index], y_targ_arr[x_targ_index])
                dist2.append(point.distance(l1))

            for x_ref_index in range(len(x_ref_arr)):
                dist3.append((x_ref_arr[x_ref_index] - xs[0]) ** 2 + (y_ref_arr[x_ref_index] - ys[0]) ** 2)

            # Min of the nearest trajectory point is the intersection with its respective index
            index = dist.index(min(dist))
            # Min if nearest reference point is the intersection with its respective index
            index2 = dist3.index(min(dist3))

            # Find previous and next extrema for
            peaks, _ = find_peaks(dist2, height=0)
            pos = np.searchsorted(peaks, index)
            if pos == 0:
                start_index = 0
            else:
                start_index = peaks[pos - 1]

            if pos == len(peaks):
                end_index = len(x_targ_arr)
            else:
                end_index = peaks[pos]

            if index + 1 == len(x_targ_arr):
                point1 = [x_ref_arr[index2 - 1], y_ref_arr[index2 - 1]]
                point2 = [x_ref_arr[index2], y_ref_arr[index2]]
                point3 = [x_targ_arr[index - 1], y_targ_arr[index - 1]]
                point4 = [x_targ_arr[index], y_targ_arr[index]]
            elif index == 0:
                point1 = [x_ref_arr[index2], y_ref_arr[index2]]
                point2 = [x_ref_arr[index2 + 1], y_ref_arr[index2 + 1]]
                point3 = [x_targ_arr[index], y_targ_arr[index]]
                point4 = [x_targ_arr[index + 1], y_targ_arr[index + 1]]
            else:
                point1 = [x_ref_arr[index2 - 1], y_ref_arr[index2 - 1]]
                point2 = [x_ref_arr[index2 + 1], y_ref_arr[index2 + 1]]
                point3 = [x_targ_arr[index - 1], y_targ_arr[index - 1]]
                point4 = [x_targ_arr[index + 1], y_targ_arr[index + 1]]

            v0 = np.array(point2) - np.array(point1)
            v1 = np.array(point4) - np.array(point3)

            angle = np.math.atan2(np.linalg.det([v0, v1]), np.dot(v0, v1))
            deg = np.degrees(angle)

            # If left lane change
            if deg < 0:
                left_lanechange_array[start_index:end_index] = 1
            else:
                # If right lane change
                right_lanechange_array[start_index:end_index] = 1

        return left_lanechange_array, right_lanechange_array

    if plot:
        for i in range(int(df_lanes.shape[1] / 2)):
            plt.scatter(df_lanes.iloc[:, i * 2], df_lanes.iloc[:, i * 2 + 1])
        plt.scatter(lat, lon)
        plt.show()

    clean_lat = lat[~np.isnan(lat)]
    clean_lon = lon[~np.isnan(lon)]

    # Loop over all available lanes from df_lane
    number_of_lanes = int(df_lanes.shape[1] / 2)
    left_lane_change_array = np.zeros(len(clean_lat))
    right_lane_change_array = np.zeros(len(clean_lat))
    for i in range(number_of_lanes):
        x_ref = df_lanes.iloc[:, (i * 2)]  # Lat
        y_ref = df_lanes.iloc[:, (i * 2) + 1]  # Lon

        left, right = find_intersection(clean_lat, clean_lon, x_ref, y_ref)

        left_lane_change_array = np.logical_or(left_lane_change_array, left)
        right_lane_change_array = np.logical_or(right_lane_change_array, right)

    left_lane_change = np.zeros(len(lat))
    left_lane_change[~np.isnan(lat)] = left_lane_change_array
    right_lane_change = np.zeros(len(lon))
    right_lane_change[~np.isnan(lon)] = right_lane_change_array

    return left_lane_change, right_lane_change
