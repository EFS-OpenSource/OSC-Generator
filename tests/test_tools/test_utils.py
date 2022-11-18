#  ****************************************************************************
#  @test_utils.py
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
from osc_generator.tools import utils
import pytest
import os


@pytest.fixture
def test_data_dir():
    return os.path.join(os.path.dirname(__file__), '../test_data')


@pytest.fixture
def df(test_data_dir):
    return pd.read_csv(os.path.join(test_data_dir, 'trajectories_file.csv'))


@pytest.fixture
def cleaned_df(test_data_dir):
    return pd.read_csv(os.path.join(test_data_dir, 'cleaned_df.csv'))


@pytest.fixture
def cols():
    cols = [['pos_x_1', 'pos_y_1', 'speed_x_1', 'speed_y_1', 'class_1'],
            ['pos_x_2', 'pos_y_2', 'speed_x_2', 'speed_y_2', 'class_2'],
            ['pos_x_3', 'pos_y_3', 'speed_x_3', 'speed_y_3', 'class_3'],
            ['pos_x_4', 'pos_y_4', 'speed_x_4', 'speed_y_4', 'class_4'],
            ['pos_x_5', 'pos_y_5', 'speed_x_5', 'speed_y_5', 'class_5'],
            ['pos_x_6', 'pos_y_6', 'speed_x_6', 'speed_y_6', 'class_6'],
            ['pos_x_7', 'pos_y_7', 'speed_x_7', 'speed_y_7', 'class_7']]
    return cols


class TestUtils:
    def test_delete_not_relevant_objects(self, df, cleaned_df, cols):
        actual, _ = utils.delete_irrelevant_objects(df, cols)
        expected = cleaned_df
        pd.testing.assert_frame_equal(actual, expected)

    def test_new_coordinate_heading(self, df, cleaned_df):
        p = ['pos_x_6', 'pos_y_6', 'speed_x_6']
        k = 64
        actual = utils.calc_new_geopos_from_2d_vector_on_spheric_earth(curr_coords=df.loc[k, ["lat", "long"]],
                                                                       heading=df.loc[k, "heading"],
                                                                       dist_x=df.loc[k, p[0]], dist_y=df.loc[k, p[1]])
        expected = [1, 2]
        assert actual is not None
        assert len(actual) == len(expected)

    def test_flatten(self):
        cols_1 = [['pos_x_1', 'pos_y_1', 'speed_x_1', 'speed_y_1', 'class_1'],
                  ['pos_x_2', 'pos_y_2', 'speed_x_2', 'speed_y_2', 'class_2']]
        expected_1 = ['pos_x_1', 'pos_y_1', 'speed_x_1', 'speed_y_1', 'class_1',
                      'pos_x_2', 'pos_y_2', 'speed_x_2', 'speed_y_2', 'class_2']
        cols_2 = ['pos_x_1', 'pos_y_1', 'speed_x_1', 'speed_y_1', 'class_1',
                  'pos_x_2', 'pos_y_2', 'speed_x_2', 'speed_y_2', 'class_2']
        expected_2 = ['pos_x_1', 'pos_y_1', 'speed_x_1', 'speed_y_1', 'class_1',
                      'pos_x_2', 'pos_y_2', 'speed_x_2', 'speed_y_2', 'class_2']

        cols_3 = [[], []]
        expected_3 = []
        assert utils.flatten(cols_1) == expected_1
        assert utils.flatten(cols_2) == expected_2
        assert utils.flatten(cols_3) == expected_3

    def test_find_vars(self, df, cols):
        actual = utils.find_vars('pos_x_|pos_y_|speed_x_|speed_y_|class_', df.columns, reshape=True)
        expected = np.asarray(cols)
        assert actual is not None
        assert isinstance(actual, np.ndarray)
        assert actual[2, 3] == expected[2, 3]

    def test_convert_heading(self):
        assert round(utils.convert_heading(0.0), 2) != 0
        assert round(utils.convert_heading(0), 2) != 0
        assert round(utils.convert_heading(360), 2) == 1.57
        assert round(utils.convert_heading(-270), 2) == 12.57
        assert round(utils.convert_heading(-735), 2) == 20.68

    def test_get_heading(self, df, cols):
        actual = utils.calc_heading_from_two_geo_positions(48.80437693633773, 48.80440442405007, 11.465818732551098, 11.465823006918304)
        assert round(actual, 2) == -127.32
        assert utils.calc_heading_from_two_geo_positions(0, 0, 0, 0) == 180
