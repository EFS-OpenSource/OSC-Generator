#  ****************************************************************************
#  @test_rulebased.py
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

from osc_generator.tools import rulebased
import pytest
import pandas as pd
import numpy as np
import os


@pytest.fixture
def test_data_dir():
    return os.path.join(os.path.dirname(__file__), '../test_data')


@pytest.fixture
def prepared_df(test_data_dir):
    return pd.read_csv(os.path.join(test_data_dir, 'prepared_df.csv'))


@pytest.fixture
def e_accelerate_array(test_data_dir):
    return np.load(os.path.join(test_data_dir, 'accelerate_array.npy'))


@pytest.fixture
def e_decelerate_array(test_data_dir):
    return np.load(os.path.join(test_data_dir, 'decelerate_array.npy'))


@pytest.fixture
def e_keep_velocity_array(test_data_dir):
    return np.load(os.path.join(test_data_dir, 'keep_velocity_array.npy'))


@pytest.fixture
def e_lane_change_right_array(test_data_dir):
    return np.load(os.path.join(test_data_dir, 'lane_change_right_array.npy'))


@pytest.fixture
def e_lane_change_left_array(test_data_dir):
    return np.load(os.path.join(test_data_dir, 'lane_change_left_array.npy'))


@pytest.fixture
def prepared_df(test_data_dir):
    return pd.read_csv(os.path.join(test_data_dir, 'prepared_df.csv'))


@pytest.fixture
def df_lanes(test_data_dir):
    return pd.read_csv(os.path.join(test_data_dir, 'df_lanes.csv'))


class TestRulebased:
    def test_get_vehicle_state_maneuver(self, prepared_df, e_accelerate_array, e_decelerate_array,
                                        e_keep_velocity_array):
        speed = prepared_df['speed']
        accelerate_array, start_array, keep_velocity_array, standstill_array, decelerate_array, stop_array, \
            reversing_array = rulebased.create_longitudinal_maneuver_vectors(speed, acceleration_definition_threshold=0.2)

        np.testing.assert_array_equal(accelerate_array, e_accelerate_array)
        np.testing.assert_array_equal(decelerate_array, e_decelerate_array)
        np.testing.assert_array_equal(keep_velocity_array, e_keep_velocity_array)

    def test_get_lanechange_absolute(self, prepared_df, df_lanes, e_lane_change_right_array, e_lane_change_left_array):
        lane_change_left_array, lane_change_right_array = rulebased.create_lateral_maneuver_vectors(df_lanes,
                                                                                                    prepared_df['lat'],
                                                                                                    prepared_df['long'])

        np.testing.assert_array_equal(lane_change_right_array, e_lane_change_right_array)
        np.testing.assert_array_equal(lane_change_left_array, e_lane_change_left_array)
