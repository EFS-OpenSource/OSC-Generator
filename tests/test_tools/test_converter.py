#  ****************************************************************************
#  @test_converter.py
#
#  @copyright 2023 e:fs TechHub GmbH and Audi AG. All rights reserved.
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

from osc_generator.tools.converter import Converter
from xmldiff import main
import pytest
import pandas as pd
import os
import warnings


@pytest.fixture
def test_data_dir():
    return os.path.join(os.path.dirname(__file__), '../test_data')

@pytest.fixture
def df_lanes(test_data_dir):
    return pd.read_csv(os.path.join(test_data_dir, 'df_lanes_llc.csv'))


class TestConverter:
    def test_converter_csv_relative_ego_llc(self, test_data_dir):  # left lane change scenario, from csv file
        trajectories_path = os.path.join(test_data_dir, r'testfile_llc.csv')
        opendrive_path = os.path.join(test_data_dir, r'TestTrack.xodr')
        output_scenario_path = os.path.join(test_data_dir, r'output_scenario.xosc')
        expected_scenario_path = os.path.join(test_data_dir, r'expected_llc.xosc')
        system_under_test = Converter()
        system_under_test.set_paths(trajectories_path, opendrive_path, output_scenario_path)
        system_under_test.process_trajectories(relative=True)
        system_under_test.label_maneuvers(acc_threshold=0.2, optimize_acc=False, generate_kml=False)
        system_under_test.write_scenario(plot=False,
                                 radius_pos_trigger=2.0,
                                 timebased_lon=True,
                                 timebased_lat=True,
                                 output='xosc')
        diff = main.diff_files(output_scenario_path, expected_scenario_path)
        assert [] == diff

    def test_converter_osi_relative_ego_llc(self, test_data_dir):  # left lane change scenario, from osi file
        trajectories_path = os.path.join(test_data_dir, r'testfile_llc.osi')
        opendrive_path = os.path.join(test_data_dir, r'TestTrack.xodr')
        output_scenario_path = os.path.join(test_data_dir, r'output_scenario.xosc')
        expected_scenario_path = os.path.join(test_data_dir, r'expected_llc.xosc')
        try:
            system_under_test = Converter()
            system_under_test.set_paths(trajectories_path, opendrive_path, output_scenario_path)
            system_under_test.process_trajectories(relative=True)
            system_under_test.label_maneuvers(acc_threshold=0.2, optimize_acc=False, generate_kml=False)
            system_under_test.write_scenario(plot=False,
                                     radius_pos_trigger=2.0,
                                     timebased_lon=True,
                                     timebased_lat=True,
                                     output='xosc')
            diff = main.diff_files(output_scenario_path, expected_scenario_path)
            assert [] == diff
        except NameError:
            warnings.warn("Feature OSI Input Data is not available. Download from: https://github.com/OpenSimulationInterface/open-simulation-interface/blob/master/format/OSITrace.py", UserWarning)


    def test_converter_csv_absolute_ego_llc(self, test_data_dir, df_lanes):  # left lane change, absolute co-ords
        trajectories_path = os.path.join(test_data_dir, r'testfile_llc.csv')
        opendrive_path = os.path.join(test_data_dir, r'TestTrack.xodr')
        output_scenario_path = os.path.join(test_data_dir, r'output_scenario.xosc')
        expected_scenario_path = os.path.join(test_data_dir, r'expected_llc.xosc')
        system_under_test = Converter()
        system_under_test.set_paths(trajectories_path, opendrive_path, output_scenario_path)
        system_under_test.process_trajectories(relative=False, df_lanes=df_lanes)
        system_under_test.label_maneuvers(acc_threshold=0.2, optimize_acc=False, generate_kml=False)
        system_under_test.write_scenario(plot=False,
                                 radius_pos_trigger=2.0,
                                 timebased_lon=True,
                                 timebased_lat=True,
                                 output='xosc')
        diff = main.diff_files(output_scenario_path, expected_scenario_path)
        assert [] == diff

    def test_converter_csv_relative_ego_rlc(self, test_data_dir):  # right lane change scenario, from csv file
        trajectories_path = os.path.join(test_data_dir, r'testfile_rlc.csv')
        opendrive_path = os.path.join(test_data_dir, r'TestTrack.xodr')
        output_scenario_path = os.path.join(test_data_dir, r'output_scenario.xosc')
        expected_scenario_path = os.path.join(test_data_dir, r'expected_rlc.xosc')
        system_under_test = Converter()
        system_under_test.set_paths(trajectories_path, opendrive_path, output_scenario_path)
        system_under_test.process_trajectories(relative=True)
        system_under_test.label_maneuvers(acc_threshold=0.2, optimize_acc=False, generate_kml=False)
        system_under_test.write_scenario(plot=False,
                                         radius_pos_trigger=2.0,
                                         timebased_lon=True,
                                         timebased_lat=True,
                                         output='xosc')
        diff = main.diff_files(output_scenario_path, expected_scenario_path)
        assert [] == diff

    def test_converter_osi_relative_ego_rlc(self, test_data_dir):  # right lane change scenario, from osi file
        trajectories_path = os.path.join(test_data_dir, r'testfile_rlc.osi')
        opendrive_path = os.path.join(test_data_dir, r'TestTrack.xodr')
        output_scenario_path = os.path.join(test_data_dir, r'output_scenario.xosc')
        expected_scenario_path = os.path.join(test_data_dir, r'expected_rlc.xosc')
        system_under_test = Converter()
        system_under_test.set_paths(trajectories_path, opendrive_path, output_scenario_path)
        system_under_test.process_trajectories(relative=True)
        system_under_test.label_maneuvers(acc_threshold=0.2, optimize_acc=False, generate_kml=False)
        system_under_test.write_scenario(plot=False,
                                         radius_pos_trigger=2.0,
                                         timebased_lon=True,
                                         timebased_lat=True,
                                         output='xosc')
        diff = main.diff_files(output_scenario_path, expected_scenario_path)
        assert [] == diff