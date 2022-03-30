#  ****************************************************************************
#  @test_coord_calculations.py
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
from osc_generator.tools import coord_calculations
import pytest
import os


@pytest.fixture
def test_data_dir():
    return os.path.join(os.path.dirname(__file__), '../test_data')


@pytest.fixture
def df(test_data_dir):
    return pd.read_csv(os.path.join(test_data_dir, 'trajectories_file.csv'))


@pytest.fixture
def df_lanes(test_data_dir):
    return pd.read_csv(os.path.join(test_data_dir, 'df_lanes.csv'))


@pytest.fixture
def odr_path(test_data_dir):
    opendrive_path = os.path.join(test_data_dir, r'2017-04-04_Testfeld_A9_Nord_offset.xodr')
    return opendrive_path


class TestCoordCalculations:
    def test_lanes_rel2abs_from_csv(self, df, df_lanes):
        actual = coord_calculations.transform_lanes_rel2abs_from_csv(df)
        expected = df_lanes
        pd.testing.assert_frame_equal(actual, expected)

    def test_get_proj_from_open_drive(self, odr_path):
        actual = coord_calculations.get_proj_from_open_drive(open_drive_path=odr_path)
        expected = '+proj=tmerc +lat_0=0 +lon_0=9 +k=0.9996 +x_0=-177308 +y_0=-5425923 +datum=WGS84 +units=m +no_defs'
        assert actual.srs == expected
