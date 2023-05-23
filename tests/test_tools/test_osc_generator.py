#  ****************************************************************************
#  @test_osc_generator.py
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

from osc_generator.osc_generator import OSCGenerator
from xmldiff import main
import pandas as pd
import pytest
import os
import warnings


@pytest.fixture
def test_data_dir():
    return os.path.join(os.path.dirname(__file__), '../test_data')


class TestOSCGenerator:
    def test_generate_osc(self, test_data_dir):
        trajectories_path = os.path.join(test_data_dir, r'trajectories_file.csv')
        opendrive_path = os.path.join(test_data_dir, r'2017-04-04_Testfeld_A9_Nord_offset.xodr')
        output_scenario_path = os.path.join(test_data_dir, r'output_scenario.xosc')
        expected_scenario_path = os.path.join(test_data_dir, r'expected_scenario.xosc')
        system_under_test = OSCGenerator()
        system_under_test.generate_osc(trajectories_path, opendrive_path, output_scenario_path)
        diff = main.diff_files(output_scenario_path, expected_scenario_path)
        assert [] == diff
        
    def test_generate_osc_class_reuse(self, test_data_dir):
        trajectories_path = os.path.join(test_data_dir, r'trajectories_file.csv')
        opendrive_path = os.path.join(test_data_dir, r'2017-04-04_Testfeld_A9_Nord_offset.xodr')
        output_scenario_path = os.path.join(test_data_dir, r'output_scenario.xosc')
        expected_scenario_path = os.path.join(test_data_dir, r'expected_scenario.xosc')
        system_under_test = OSCGenerator()
        system_under_test.generate_osc(trajectories_path, opendrive_path, output_scenario_path)
        diff = main.diff_files(output_scenario_path, expected_scenario_path)
        assert [] == diff
        system_under_test.generate_osc(trajectories_path, opendrive_path, output_scenario_path)
        diff = main.diff_files(output_scenario_path, expected_scenario_path)
        assert [] == diff

    def test_generate_osc_class_osi(self, test_data_dir):
        try:
            trajectories_path = os.path.join(test_data_dir, r'trajectories_file.osi')
            opendrive_path = os.path.join(test_data_dir, r'2017-04-04_Testfeld_A9_Nord_offset.xodr')
            output_scenario_path = os.path.join(test_data_dir, r'output_scenario.xosc')
            expected_scenario_path = os.path.join(test_data_dir, r'expected_scenario.xosc')
            system_under_test = OSCGenerator()
            system_under_test.generate_osc(trajectories_path, opendrive_path, output_scenario_path)
            diff = main.diff_files(output_scenario_path, expected_scenario_path)
            assert [] == diff
            system_under_test.generate_osc(trajectories_path, opendrive_path, output_scenario_path)
            diff = main.diff_files(output_scenario_path, expected_scenario_path)
            assert [] == diff
        except NameError:
            warnings.warn(
                "Feature OSI Input Data is not available. Download from: https://github.com/OpenSimulationInterface/open-simulation-interface/blob/master/format/OSITrace.py",
                UserWarning)

    def test_generate_osc_class_osi_reuse(self, test_data_dir):
        try:
            trajectories_path = os.path.join(test_data_dir, r'trajectories_file.osi')
            opendrive_path = os.path.join(test_data_dir, r'2017-04-04_Testfeld_A9_Nord_offset.xodr')
            output_scenario_path = os.path.join(test_data_dir, r'output_scenario.xosc')
            expected_scenario_path = os.path.join(test_data_dir, r'expected_scenario.xosc')
            system_under_test = OSCGenerator()
            system_under_test.generate_osc(trajectories_path, opendrive_path, output_scenario_path)
            diff = main.diff_files(output_scenario_path, expected_scenario_path)
            assert [] == diff
            system_under_test.generate_osc(trajectories_path, opendrive_path, output_scenario_path)
            diff = main.diff_files(output_scenario_path, expected_scenario_path)
            assert [] == diff
        except NameError:
            warnings.warn("Feature OSI Input Data is not available. Download from: https://github.com/OpenSimulationInterface/open-simulation-interface/blob/master/format/OSITrace.py", UserWarning)


    def test_generate_osc_class_csv_reuse(self, test_data_dir):
        trajectories_path = os.path.join(test_data_dir, r'trajectories_file.csv')
        opendrive_path = os.path.join(test_data_dir, r'2017-04-04_Testfeld_A9_Nord_offset.xodr')
        output_scenario_path = os.path.join(test_data_dir, r'output_scenario.xosc')
        expected_scenario_path = os.path.join(test_data_dir, r'expected_scenario.xosc')
        system_under_test = OSCGenerator()
        system_under_test.generate_osc(trajectories_path, opendrive_path, output_scenario_path)
        diff = main.diff_files(output_scenario_path, expected_scenario_path)
        assert [] == diff
        system_under_test.generate_osc(trajectories_path, opendrive_path, output_scenario_path)
        diff = main.diff_files(output_scenario_path, expected_scenario_path)
        assert [] == diff

    def test_generate_osc_straight_csv(self, test_data_dir):
        trajectories_path = os.path.join(test_data_dir, r'testfile_straight.csv')
        opendrive_path = os.path.join(test_data_dir, r'TestTrack.xodr')
        output_scenario_path = os.path.join(test_data_dir, r'output_scenario.xosc')
        expected_scenario_path = os.path.join(test_data_dir, r'expected_straight.xosc')
        system_under_test = OSCGenerator()
        system_under_test.generate_osc(trajectories_path, opendrive_path, output_scenario_path)
        diff = main.diff_files(output_scenario_path, expected_scenario_path)
        assert [] == diff

    def test_generate_osc_straight_osi(self, test_data_dir):
        trajectories_path = os.path.join(test_data_dir, r'testfile_straight.osi')
        opendrive_path = os.path.join(test_data_dir, r'TestTrack.xodr')
        output_scenario_path = os.path.join(test_data_dir, r'output_scenario.xosc')
        expected_scenario_path = os.path.join(test_data_dir, r'expected_straight.xosc')
        try:
            system_under_test = OSCGenerator()
            system_under_test.generate_osc(trajectories_path, opendrive_path, output_scenario_path)
            diff = main.diff_files(output_scenario_path, expected_scenario_path)
            assert [] == diff
        except NameError:
            warnings.warn("Feature OSI Input Data is not available. Download from: https://github.com/OpenSimulationInterface/open-simulation-interface/blob/master/format/OSITrace.py", UserWarning)
