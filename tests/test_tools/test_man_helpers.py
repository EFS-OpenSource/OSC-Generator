#  ****************************************************************************
#  @test_man_helpers.py
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

import pandas as pd
import numpy as np
from osc_generator.tools import man_helpers
import pytest
import os


@pytest.fixture
def test_data_dir():
    return os.path.join(os.path.dirname(__file__), '../test_data')


@pytest.fixture
def maneuver(test_data_dir):
    return pd.read_csv(os.path.join(test_data_dir, 'temp_ego_maneuver_array.csv'))


@pytest.fixture
def model_speed(test_data_dir):
    return np.load(os.path.join(test_data_dir, 'model_speed.npy'))


@pytest.fixture
def prepared_df(test_data_dir):
    return pd.read_csv(os.path.join(test_data_dir, 'prepared_df.csv'))


@pytest.fixture
def df_lanes(test_data_dir):
    return pd.read_csv(os.path.join(test_data_dir, 'df_lanes.csv'))


@pytest.fixture
def odr_path(test_data_dir):
    opendrive_path = os.path.join(test_data_dir, '2017-04-04_Testfeld_A9_Nord_offset.xodr')
    return opendrive_path


@pytest.fixture
def expected_ego_maneuver_array_0(test_data_dir):
    return np.load(os.path.join(test_data_dir, 'ego_maneuver_array_0.npy'))


class TestManHelpers:
    def test_speed_model(self, maneuver, model_speed):
        actual = man_helpers.create_speed_model(maneuver, 99.57389)
        expected = model_speed

        np.testing.assert_array_almost_equal_nulp(actual, expected)
        np.testing.assert_array_equal(actual, expected)

    def test_opt_acc(self, prepared_df, df_lanes, odr_path, test_data_dir):
        actual = man_helpers.calc_opt_acc_thresh(prepared_df,
                                                 df_lanes,
                                                 odr_path,
                                                 True,
                                                 test_data_dir)
        expected = np.array([0.05, 0.1, 0.1])

        np.testing.assert_array_almost_equal_nulp(actual, expected)
        np.testing.assert_array_equal(actual, expected)

    def test_man_labeling(self, prepared_df, df_lanes, odr_path, expected_ego_maneuver_array_0, test_data_dir):
        acc_threshold = np.array([0.05, 0.1, 0.1])
        ego_maneuver_array, inf_maneuver_array, objlist, objects, ego, movobj_grps_coord = man_helpers.label_maneuvers(
            prepared_df,
            df_lanes,
            acc_threshold,
            False,
            odr_path,
            True,
            test_data_dir)
        expected_ego = [3728.331392794964, -17465.94162228238, 27.65941358024691, 7.663740745507101]

        np.testing.assert_array_equal(ego_maneuver_array[0], expected_ego_maneuver_array_0)
        np.testing.assert_array_equal(ego, expected_ego)
