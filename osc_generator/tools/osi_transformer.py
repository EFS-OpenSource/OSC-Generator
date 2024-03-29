import struct
import pandas as pd
import math
import warnings
from osc_generator.tools.user_config import UserConfig
import os

try:
    from osc_generator.tools.OSI.OSITrace import OSITrace
except ImportError:
    warnings.warn("Feature OSI Input Data is not available. Download from: https://github.com/OpenSimulationInterface/open-simulation-interface/blob/master/format/OSITrace.py", UserWarning)

def get_user_defined_attributes(osi_message, path):
    """
    Obtain user defined attributes from the OSI message.
    Writes to config file

    :param :
        osi_message: the initial message from the OSI file
        path: for directory in which to write config file
    """
    bb_dimension = []
    bb_center = []
    for obj in osi_message.global_ground_truth.moving_object:
        if obj.base.HasField('dimension'):
                # object bounding box dimensions
                bb_dimension.append([obj.base.dimension.width, obj.base.dimension.length, obj.base.dimension.height])
        else:
            bb_dimension.append(None)

        if obj.HasField('vehicle_attributes'):
            if obj.vehicle_attributes.HasField('bbcenter_to_rear'):
                # object bounding box center point, from rear axle
                bb_center.append([obj.vehicle_attributes.bbcenter_to_rear.x,
                                  obj.vehicle_attributes.bbcenter_to_rear.y,
                                  obj.vehicle_attributes.bbcenter_to_rear.z])
            else:
                bb_center.append(None)
        else:
            bb_center.append(None)

    dir_name = os.path.dirname(path)
    user_config = UserConfig(dir_name)
    user_config.read_config()
    user_config.object_boundingbox = bb_dimension
    user_config.bbcenter_to_rear = bb_center
    user_config.write_config()


def osi2df(path: str) -> pd.DataFrame:
    """
    Transfer osi messages into pandas dataframe.

    :param path: path to osi file
    :return: pandas dataframe
    """
    if not isinstance(path, str):
        raise TypeError("input must be a str")

    trace = OSITrace()
    trace.from_file(path=path)
    messages = trace.get_messages()
    m = trace.get_message_by_index(0)
    number_of_vehicles = len(m.global_ground_truth.moving_object)

    get_user_defined_attributes(m, path)

    lists: list = [[] for _ in range(15)]
    for i in messages:
        timestamp = i.global_ground_truth.timestamp.seconds + i.global_ground_truth.timestamp.nanos / 1000000000
        lists[0].append(timestamp)
        for v in i.global_ground_truth.moving_object:
            lists[1].append(v.base.position.x)
            lists[2].append(v.base.position.y)
            lists[3].append(v.base.velocity.x)
            lists[4].append(v.base.velocity.y)
            lists[5].append(v.base.orientation.yaw)
            lists[6].append(v.vehicle_classification.type)

        for lane in i.global_ground_truth.lane_boundary:
            if lane.id.value == 0:
                lists[7].append(lane.classification.type)
                for boundary_line in lane.boundary_line:
                    lists[8].append(boundary_line.position.x)
                    lists[9].append(boundary_line.position.y)
                    lists[10].append(boundary_line.width)
            elif lane.id.value == 1:
                lists[11].append(lane.classification.type)
                for boundary_line in lane.boundary_line:
                    lists[12].append(boundary_line.position.x)
                    lists[13].append(boundary_line.position.y)
                    lists[14].append(boundary_line.width)
            else:
                pass

    df = pd.DataFrame(lists[0], columns=['timestamp'])
    df.insert(1, 'lat', lists[1][0::number_of_vehicles])
    df.insert(2, 'long', lists[2][0::number_of_vehicles])
    df.insert(3, 'heading', lists[5][0::number_of_vehicles])
    df.insert(4, 'speed', lists[3][0::number_of_vehicles])

    df.insert(5, 'lin_right_beginn_x', lists[8])
    df.insert(6, 'lin_right_y_abstand', lists[9])
    df.insert(7, 'lin_right_breite', lists[10])
    df.insert(8, 'lin_right_typ', lists[7])
    df.insert(9, 'lin_left_beginn_x', lists[12])
    df.insert(10, 'lin_left_y_abstand', lists[13])
    df.insert(11, 'lin_left_breite', lists[14])
    df.insert(12, 'lin_left_typ', lists[11])

    for i in range(number_of_vehicles - 1):
        i += 1
        df.insert(i * 5 + 8, 'pos_x_' + str(i), lists[1][i::number_of_vehicles])
        df.insert(i * 5 + 9, 'pos_y_' + str(i), lists[2][i::number_of_vehicles])
        df.insert(i * 5 + 10, 'speed_x_' + str(i), lists[3][i::number_of_vehicles])
        df.insert(i * 5 + 11, 'speed_y_' + str(i), lists[4][i::number_of_vehicles])
        df.insert(i * 5 + 12, 'class_' + str(i), lists[6][i::number_of_vehicles])

    trace.scenario_file.close()

    return df