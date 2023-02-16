#  ****************************************************************************
#  @scenario_writer.py
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
import os
import numpy as np
from xml.etree.ElementTree import Element, SubElement
from xml.etree import ElementTree
from xml.dom import minidom
from scenariogeneration import xosc

def write_pretty(elem: Element, output: str, use_folder: bool, timebased_lon: bool, timebased_lat: bool,
                 dir_name: str, section_name: str, radius_pos_trigger: float, output_path: str = None):
    """
    Write a pretty-printed XML string for the Element.

    Args:
        elem: Root of the Element tree
        output: Output file type xosc
        use_folder: Option to use folder structure
        timebased_lon: Option to use time based trigger for longitudinal maneuvers
        timebased_lat: Option to use time based trigger for lateral maneuvers
        dir_name: Name of the directory
        section_name: Name of the scenario section
        radius_pos_trigger: Radius of the position based trigger
        output_path: Path to scenario file

    Returns:
        object (str): Path to scenario file
    """
    if not isinstance(elem, Element):
        raise TypeError("input must be a Element")
    if not isinstance(output, str):
        raise TypeError("input must be a str")
    if not isinstance(use_folder, bool):
        raise TypeError("input must be a bool")
    if not isinstance(timebased_lon, bool):
        raise TypeError("input must be a bool")
    if not isinstance(timebased_lat, bool):
        raise TypeError("input must be a bool")
    if not isinstance(dir_name, str):
        raise TypeError("input must be a str")
    if not isinstance(section_name, str):
        raise TypeError("input must be a str")

    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    xmlstr = reparsed.toprettyxml(indent="\t")

    if output == 'xosc':
        if output_path is not None:
            path = output_path
            
        else:
            if use_folder:
                if timebased_lon and timebased_lat:
                    path = os.path.join(dir_name, 'man_export_' + os.path.basename(section_name) + '_time_lon_lat.xosc')
                elif timebased_lon and not timebased_lat:
                    path = os.path.join(dir_name, 'man_export_' + os.path.basename(section_name) + '_time_lon_pos_lat_' + str(
                        radius_pos_trigger) + '_m.xosc')
                elif not timebased_lon and timebased_lat:
                    path = os.path.join(dir_name, 'man_export_' + os.path.basename(section_name) + '_pos_lon_time_lat.xosc')

                else:
                    path = os.path.join(dir_name, 'man_export_' + os.path.basename(section_name) + '_pos_lon_lat_' +
                                        str(radius_pos_trigger) + '_m.xosc')

            else:
                raise NotImplementedError("use_folder flag is going to be removed")

    else:
        raise NotImplementedError("Only xosc output is currently implemented.")

    with open(path, 'w') as f:
        f.write(xmlstr)

    return path


def convert_to_osc(df: pd.DataFrame, ego: list, objects: dict, ego_maneuver_array: dict, inf_maneuver_array: dict,
                   movobj_grps_coord: np.ndarray, objlist: list,
                   plot: bool, opendrive_path: str, use_folder: bool, timebased_lon: bool, timebased_lat: bool,
                   section_name: str, radius_pos_trigger: float,
                   dir_name: str, osc_version: str, output_path: str = None) -> str:
    """
    Converter for OpenScenario

    Args:
        df: Dataframe containing trajectories
        ego: Ego position
        objects: Object positions
        ego_maneuver_array: Dict containing array of ego maneuvers
        inf_maneuver_array: Ict containing array of infrastructure specific maneuvers
        movobj_grps_coord: Coordinates of groups of detected objects
        objlist: Object list
        plot: Flag for graphical plotting
        opendrive_path: Path to the OpenDRIVE file
        use_folder: Iption to use folder structure
        timebased_lon: Option to use time based trigger for long maneuvers
        timebased_lat: Option to use time based trigger for lat maneuvers
        section_name: Name of the scenario section
        radius_pos_trigger: Radius of the position based trigger
        dir_name: Name of the directory
        osc_version: OpenSCENARIO version
        output_path: Path to OpenSCENARIO file

    Returns:
        object (str): Path to scenario file
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("input must be a pd.DataFrame")
    if not isinstance(ego, list):
        raise TypeError("input must be a list")
    if not isinstance(objects, dict):
        raise TypeError("input must be a dict")
    if not isinstance(ego_maneuver_array, dict):
        raise TypeError("input must be a dict")
    if not isinstance(inf_maneuver_array, dict):
        raise TypeError("input must be a dict")
    if not isinstance(movobj_grps_coord, np.ndarray):
        raise TypeError("input must be a np.ndarray")
    if not isinstance(objlist, list):
        raise TypeError("input must be a list")
    if not isinstance(plot, bool):
        raise TypeError("input must be a bool")
    if not isinstance(opendrive_path, str):
        raise TypeError("input must be a str")
    if not isinstance(use_folder, bool):
        raise TypeError("input must be a bool")
    if not isinstance(timebased_lon, bool):
        raise TypeError("input must be a bool")
    if not isinstance(timebased_lat, bool):
        raise TypeError("input must be a bool")
    if not isinstance(section_name, str):
        raise TypeError("input must be a str")
    if not isinstance(radius_pos_trigger, float):
        raise TypeError("input must be a float")
    if not isinstance(dir_name, str):
        raise TypeError("input must be a str")
    if not isinstance(osc_version, str):
        raise TypeError("input must be a str")

    opendrive_name = opendrive_path.split(os.path.sep)[-1]
    osgb_name = opendrive_name[:-4] + 'opt.osgb'

    # Write head
    root = Element("OpenSCENARIO")
    SubElement(root, "FileHeader", revMajor=osc_version.split('.')[0], revMinor=osc_version.split('.')[1], date=" ",
               description="", author="OSC GENERATOR")
    # SubElement(root, 'ParameterDeclaration')

    # Write Parameters
    param = xosc.ParameterDeclarations()

    # Write catalogs
    catalog_path = "../Catalogs/Vehicles"
    catalog = xosc.Catalog()
    catalog.add_catalog("VehicleCatalog", catalog_path)
    # catalogs = SubElement(root, 'Catalogs')
    # SubElement(SubElement(catalogs, 'VehicleCatalog'), 'Directory',
    #            output_path="Distros/Current/Config/Players/Vehicles")
    # SubElement(SubElement(catalogs, 'DriverCatalog'), 'Directory',
    #            output_path="Distros/Current/Config/Players/driverCfg.xml")
    # SubElement(SubElement(catalogs, 'PedestrianCatalog'), 'Directory',
    #            output_path="Distros/Current/Config/Players/Pedestrians")
    # SubElement(SubElement(catalogs, 'PedestrianControllerCatalog'), 'Directory', output_path="")
    # SubElement(SubElement(catalogs, 'MiscObjectCatalog'), 'Directory',
    #            output_path="Distros/Current/Config/Players/Objects")
    # SubElement(SubElement(catalogs, 'EnvironmentCatalog'), 'Directory', output_path="")
    # SubElement(SubElement(catalogs, 'ManeuverCatalog'), 'Directory', output_path="")
    # SubElement(SubElement(catalogs, 'TrajectoryCatalog'), 'Directory', output_path="")
    # SubElement(SubElement(catalogs, 'RouteCatalog'), 'Directory', output_path="")

    ## Write road network
    road = xosc.RoadNetwork(
        roadfile=opendrive_name, scenegraph=osgb_name
    )
    # road = SubElement(root, 'RoadNetwork')
    # SubElement(road, 'Logics', filepath=opendrive_name)
    # SubElement(road, 'SceneGraph', filepath=osgb_name)
    # SubElement(road, 'Signals', name="Signals")

    # Write entities
    entities = xosc.Entities()
    # ent = SubElement(root, 'Entities')

    # Entity ego
    egoname = "Ego"

    # vehicle
    bb = xosc.BoundingBox(1.872, 4.924, 1.444, 1.376, 0, 0.722)  # dim(w, l, h), centre(x, y, z)
    fa = xosc.Axle(0.48, 0.684, 1.672, 2.91, 0.342)
    ra = xosc.Axle(0, 0.684, 1.672, 0, 0.342)
    ego_veh = xosc.Vehicle("car_white", xosc.VehicleCategory.car, bb, fa, ra, 67, 10, 9.5, 1700)
    ego_veh.add_property(name="control", value="external")
    ego_veh.add_property_file("")
    # entity controller
    prop = xosc.Properties()
    prop.add_property(name="weight", value="60")
    prop.add_property(name="height", value="1.8")
    prop.add_property(name="eyeDistance", value="0.065")
    prop.add_property(name="age", value="28")
    prop.add_property(name="sex", value="male")
    cont = xosc.Controller("DefaultDriver", prop)

    entities.add_scenario_object(egoname, ego_veh, cont)

    # ent_obj = SubElement(ent, 'Object', name="EGO")
    # ent_obj_vehicle = SubElement(ent_obj, 'Vehicle', name="Audi_A6_2010_blue", category="car")
    #
    # SubElement(ent_obj_vehicle, 'ParameterDeclaration')
    # ent_obj_vehicle_bb = SubElement(ent_obj_vehicle, 'BoundingBox')
    # ent_obj_vehicle_ax = SubElement(ent_obj_vehicle, 'Axles')
    # ent_obj_vehicle_pr = SubElement(ent_obj_vehicle, 'Properties')
    #
    # SubElement(ent_obj_vehicle_bb, 'Center', x="1.376", y="0", z="0.722")
    # SubElement(ent_obj_vehicle_bb, 'Dimension', width="1.872", length="4.924", height="1.444")
    # SubElement(ent_obj_vehicle, 'Performance', maxSpeed="67", maxDeceleration="9.5", mass="1700")
    # SubElement(ent_obj_vehicle_ax, 'Front', maxSteering="0.48", wheelDiameter="0.684", trackWidth="1.672",
    #            positionX="2.91", positionZ="0.342")
    # SubElement(ent_obj_vehicle_ax, 'Rear', maxSteering="0", wheelDiameter="0.684", trackWidth="1.672", positionX="0",
    #            positionZ="0.342")
    # SubElement(ent_obj_vehicle_pr, 'Property', name="control", value="external")
    # SubElement(ent_obj_vehicle_pr, 'File', filepath="")
    #
    # ent_obj_crl = SubElement(ent_obj, 'Controller')
    # ent_obj_crl_dr = SubElement(ent_obj_crl, 'Driver', name="DefaultDriver")
    # SubElement(ent_obj_crl_dr, 'ParameterDeclaration')
    # ent_obj_crl_dr_de = SubElement(ent_obj_crl_dr, 'Description', weight="60", height="1.8", eyeDistance="0.065",
    #                                age="28", sex="male")
    # SubElement(ent_obj_crl_dr_de, 'Properties')

    # Entities objects
    for idx, obj in objects.items():
        object_count = idx + 1
        objname = f"Player{object_count}"
        # vehicle
        bb = xosc.BoundingBox(1.872, 4.924, 1.444, 1.376, 0, 0.722)  # dim(w, l, h), centre(x, y, z)
        fa = xosc.Axle(0.48, 0.684, 1.672, 2.91, 0.342)
        ra = xosc.Axle(0, 0.684, 1.672, 0, 0.342)
        obj_veh = xosc.Vehicle(objlist[idx], xosc.VehicleCategory.car, bb, fa, ra, 67, 10, 9.5, 1700)
        obj_veh.add_property(name="control", value="internal")
        obj_veh.add_property_file("")

        entities.add_scenario_object(objname, obj_veh, cont)
    # for idx, obj in objects.items():
    #     object_count = idx + 1
    #     ent_obj = SubElement(ent, 'Object', name=f"Player{object_count}")
    #     ent_obj_vehicle = SubElement(ent_obj, 'Vehicle', name=objlist[idx], category="car")
    #
    #     SubElement(ent_obj_vehicle, 'ParameterDeclaration')
    #     ent_obj_vehicle_bb = SubElement(ent_obj_vehicle, 'BoundingBox')
    #     ent_obj_vehicle_ax = SubElement(ent_obj_vehicle, 'Axles')
    #     ent_obj_vehicle_pr = SubElement(ent_obj_vehicle, 'Properties')
    #
    #     SubElement(ent_obj_vehicle_bb, 'Center', x="1.376", y="0", z="0.722")
    #     SubElement(ent_obj_vehicle_bb, 'Dimension', width="1.872", length="4.924", height="1.444")
    #     SubElement(ent_obj_vehicle, 'Performance', maxSpeed="67", maxDeceleration="9.5", mass="1700")
    #     SubElement(ent_obj_vehicle_ax, 'Front', maxSteering="0.48", wheelDiameter="0.684", trackWidth="1.672",
    #                positionX="2.91", positionZ="0.342")
    #     SubElement(ent_obj_vehicle_ax, 'Rear', maxSteering="0", wheelDiameter="0.684", trackWidth="1.672",
    #                positionX="0", positionZ="0.342")
    #     SubElement(ent_obj_vehicle_pr, 'Property', name="control", value="internal")
    #     SubElement(ent_obj_vehicle_pr, 'File', filepath="")
    #
    #     ent_obj_crl = SubElement(ent_obj, 'Controller')
    #     ent_obj_crl_dr = SubElement(ent_obj_crl, 'Driver', name="DefaultDriver")
    #     SubElement(ent_obj_crl_dr, 'ParameterDeclaration')
    #     ent_obj_crl_dr_de = SubElement(ent_obj_crl_dr, 'Description', weight="60", height="1.8", eyeDistance="0.065",
    #                                    age="28", sex="male")
    #     SubElement(ent_obj_crl_dr_de, 'Properties')

#####################################################

    # Write Init
    init = xosc.Init()
    step_time = xosc.TransitionDynamics(
        xosc.DynamicsShapes.step, xosc.DynamicsDimension.rate, 0
    )
    # Start conditions - Ego
    egospeed = xosc.AbsoluteSpeedAction(float(f'{ego[2]}'), step_time)
    egostart = xosc.TeleportAction(xosc.WorldPosition(x=f'{ego[0]}', y=f'{ego[1]}', z='0', h=f'{ego[3]}', p='0', r='0'))
    init.add_init_action(egoname, egostart)
    init.add_init_action(egoname, egospeed)

    # init storyboard object
    sb = xosc.StoryBoard(init)

    # Start (init) conditions objects
    for idx, obj in objects.items():
        object_count = idx + 1
        objname = f"Player{object_count}"
        objspeed = xosc.AbsoluteSpeedAction(float(f'{obj[2]}'), step_time)
        objstart = xosc.TeleportAction(xosc.WorldPosition(x=f'{obj[0]}', y=f'{obj[1]}', z='0', h=f'{obj[3]}', p='0', r='0'))
        init.add_init_action(objname, objstart)
        init.add_init_action(objname, objspeed)

    # # Write storyboard
    # stb = SubElement(root, 'Storyboard')
    #
    # # Init
    # init = SubElement(stb, 'Init')
    # init_act = SubElement(init, 'Actions')
    #
    # # Start condition ego
    # init_act_obj = SubElement(init_act, 'Private', object='EGO')
    # init_act_obj_pos = SubElement(SubElement(init_act_obj, 'Action'), 'Position')
    # SubElement(init_act_obj_pos, 'World', x=f'{ego[0]}', y=f'{ego[1]}', z='0', h=f'{ego[3]}', p='0', r='0')
    # init_act_obj_v = SubElement(SubElement(SubElement(init_act_obj, 'Action'), 'Longitudinal'), 'Speed')
    # SubElement(init_act_obj_v, 'Dynamics', shape="step", rate="0")
    # SubElement(SubElement(init_act_obj_v, 'Target'), 'Absolute', value=f'{ego[2]}')
    #
    # # Start conditions objects
    # for idx, obj in objects.items():
    #     object_count = idx + 1
    #     init_act_obj = SubElement(init_act, 'Private', object=f'Player{object_count}')
    #     init_act_obj_pos = SubElement(SubElement(init_act_obj, 'Action'), 'Position')
    #     SubElement(init_act_obj_pos, 'World', x=f'{obj[0]}', y=f'{obj[1]}', z='0', h=f'{obj[3]}', p='0', r='0')
    #     init_act_obj_v = SubElement(SubElement(SubElement(init_act_obj, 'Action'), 'Longitudinal'), 'Speed')
    #     SubElement(init_act_obj_v, 'Dynamics', shape="step", rate="0")
    #     SubElement(SubElement(init_act_obj_v, 'Target'), 'Absolute', value=f'{obj[2]}')

    #####################################################

    # Write Story
    story = xosc.Story("New Story")

    # For each vehicle write a separate Act
    # (Act --> for each vehicle; Events inside of Act --> for each of vehicles maneuvers)
    for key, maneuver_list in ego_maneuver_array.items():
        if key == 0:
            name = 'Ego'
        else:
            name = 'Player' + str(key)

        eventcounter = 0
        standstill = False

        # Create necessary Story Element Objects
        man = xosc.Maneuver(f'New Maneuver 1', parameters=param)
        mangroup = xosc.ManeuverGroup(f'New Sequence 1')
        mangroup.add_actor(name)
        # Start trigger for Act
        act_trig_cond = xosc.SimulationTimeCondition(value=0, rule=xosc.Rule.greaterThan)
        act_starttrigger = xosc.ValueTrigger(name=f'Start Condition of Act {key + 1}', delay=0,
                                    conditionedge=xosc.ConditionEdge.rising, valuecondition=act_trig_cond)
        act = xosc.Act(f'New Act {key + 1}', starttrigger=act_starttrigger)

        # Loop ego specific maneuvers (accelerate, decelerate, standstill, ...)
        for idx, ego_maneuver in enumerate(maneuver_list):
            if str(ego_maneuver[2]) != 'FM_EGO_standstill':
                eventcounter += 1

            if standstill & (str(ego_maneuver[2]) == 'FM_EGO_standstill'):
                standstill = True

            if not standstill:
                ## Long maneuvers without move_in, move_out
                event = xosc.Event(f'New Event {eventcounter}', xosc.Priority.overwrite)

                # Starting Condition of long maneuvers
                if timebased_lon:
                    # Time based trigger
                    trig_cond = xosc.SimulationTimeCondition(value=float(ego_maneuver[0]) / 10, rule=xosc.Rule.greaterThan)
                    trigger = xosc.ValueTrigger(name=f'Start Condition of Event {eventcounter}', delay=0,
                                                conditionedge=xosc.ConditionEdge.rising, valuecondition=trig_cond)

                elif not timebased_lon:
                    # Position based absolute position trigger
                    worldpos = xosc.WorldPosition(x=ego_maneuver[3], y=ego_maneuver[4],
                                                  z='0', h='0', p='0', r='0')
                    trig_cond = xosc.DistanceCondition(value=f'{radius_pos_trigger}', rule=xosc.Rule.lessThan,
                                                       position=worldpos, alongroute="0", freespace="0")
                    trigger = xosc.EntityTrigger(name=f'Start Condition of Event {eventcounter}', delay=0,
                                                 conditionedge=xosc.ConditionEdge.rising, entitycondition=trig_cond,
                                                 triggerentity=f'{name}')

                event.add_trigger(trigger)
                dyn = xosc.TransitionDynamics(shape=xosc.DynamicsShapes.linear,
                                              dimension=xosc.DynamicsDimension.rate, value=ego_maneuver[6])
                action = xosc.AbsoluteSpeedAction(speed=ego_maneuver[5], transition_dynamics=dyn)
                event.add_action(actionname=f"{ego_maneuver[2]}", action=action)

            # Progress test
            #     man = xosc.Maneuver("TestMan")
                man.add_event(event)
    #         # mangroup = xosc.ManeuverGroup("TestManGroup")
    #         # mangroup.add_actor(name)
    #     mangroup.add_maneuver(man)
    #     # act = xosc.Act("TestAct")
    #     act.add_maneuver_group(mangroup)
    # # story = xosc.Story("TestStory")
    #     story.add_act(act)
            # sb.add_story(story)

            if standstill & (str(ego_maneuver[2]) != 'FM_EGO_standstill'):
                standstill = False

                # Maneuver: change speed by absolute elapsed simulation time trigger
                event = xosc.Event(f'New Event {eventcounter}', priority=xosc.Priority.overwrite)

                trig_cond = xosc.SimulationTimeCondition(value=float(ego_maneuver[0]) / 10, rule=xosc.Rule.greaterThan)
                trigger = xosc.ValueTrigger(name=f'Start Condition of Event {eventcounter}', delay=0,
                                            conditionedge=xosc.ConditionEdge.rising, valuecondition=trig_cond)

                event.add_trigger(trigger)
                dyn = xosc.TransitionDynamics(shape=xosc.DynamicsShapes.linear,
                                              dimension=xosc.DynamicsDimension.rate, value=ego_maneuver[6])
                action = xosc.AbsoluteSpeedAction(speed=ego_maneuver[5], transition_dynamics=dyn)
                event.add_action(actionname=f"{ego_maneuver[2]}", action=action)

                man.add_event(event)

        # # Progress test
        # mangroup.add_maneuver(man)
        # act.add_maneuver_group(mangroup)
        # story.add_act(act)

        # Loop infrastructure specific maneuvers
        current_inf_maneuver_array = inf_maneuver_array[key]
        for idx, inf_maneuver in enumerate(current_inf_maneuver_array):
            eventcounter += 1

            if inf_maneuver[2] == 'FM_INF_lane_change_left':
                lane_change = 1
            elif inf_maneuver[2] == 'FM_INF_lane_change_right':
                lane_change = -1
            else:
                raise ValueError('Lane change maneuver name is wrong')

            # Lane Change
            event = xosc.Event(f'New Event {eventcounter}', xosc.Priority.overwrite)

            # Starting Condition of lane change
            if timebased_lat:
                # Time based_lat trigger
                trig_cond = xosc.SimulationTimeCondition(value=float(inf_maneuver[0]) / 10,
                                                         rule=xosc.Rule.greaterThan)
                trigger = xosc.ValueTrigger(name=f'Start Condition of Event {eventcounter}', delay=0,
                                            conditionedge=xosc.ConditionEdge.rising, valuecondition=trig_cond)

            elif not timebased_lat:
                # Position based absolute position trigger
                worldpos = xosc.WorldPosition(x=inf_maneuver[3], y=inf_maneuver[4],
                                              z='0', h='0', p='0', r='0')
                trig_cond = xosc.DistanceCondition(value=f'{radius_pos_trigger}', rule=xosc.Rule.lessThan,
                                                   position=worldpos, alongroute="0", freespace="0")
                trigger = xosc.EntityTrigger(name=f'Start Condition of Event {eventcounter}', delay=0,
                                             conditionedge=xosc.ConditionEdge.rising, entitycondition=trig_cond,
                                             triggerentity=f'{name}')

            event.add_trigger(trigger)
            dyn = xosc.TransitionDynamics(shape=xosc.DynamicsShapes.sinusoidal,
                                          dimension=xosc.DynamicsDimension.time, value=inf_maneuver[5])
            action = xosc.RelativeLaneChangeAction(lane=lane_change, entity=f'{name}', transition_dynamics=dyn,
                                                   target_lane_offset=4.26961e-316)
            event.add_action(actionname=f"{inf_maneuver[2]}", action=action)

            man.add_event(event)

        # Progress test
        mangroup.add_maneuver(man)
        act.add_maneuver_group(mangroup)
        story.add_act(act)

    #####################################################
    # # Write story
    # sry = SubElement(stb, 'Story', name="New Story", owner="")
    #
    # # For each vehicle write a separate Act
    # # (Act --> for each vehicle; Events inside of Act --> for each of vehicles maneuvers)
    # for key, maneuver_list in ego_maneuver_array.items():
    #     if key == 0:
    #         name = 'EGO'
    #     else:
    #         name = 'Player' + str(key)
    #
    #     act = SubElement(sry, 'Act', name=f"New Act {key + 1}")
    #     sqc = SubElement(act, 'Sequence', name="New Sequence 1", numberOfExecutions="1")
    #     SubElement(SubElement(sqc, 'Actors'), 'Entity', name=f"{name}")
    #     man = SubElement(sqc, 'Maneuver', name="New Maneuver 1")
    #     SubElement(man, 'ParameterDeclaration')
    #
    #     eventcounter = 0
    #     standstill = False
    #     # Loop ego specific maneuvers (accelerate, decelerate, standstill, ...)
    #     for idx, ego_maneuver in enumerate(maneuver_list):
    #         if str(ego_maneuver[2]) != 'FM_EGO_standstill':
    #             eventcounter += 1
    #
    #         if standstill & (str(ego_maneuver[2]) == 'FM_EGO_standstill'):
    #             standstill = True
    #
    #         if not standstill:
    #             # Long maneuvers without move_in, move_out
    #             man_evt = SubElement(man, 'Event', name=f'New Event {eventcounter}', priority="overwrite")
    #
    #             man_evt_ac = SubElement(man_evt, 'Action', name=f"{ego_maneuver[2]}")
    #             man_evt_ac_v = SubElement(SubElement(SubElement(man_evt_ac, 'Private'), 'Longitudinal'), 'Speed')
    #             SubElement(man_evt_ac_v, 'Dynamics', shape="linear", rate=f"{ego_maneuver[6]}")
    #             SubElement(SubElement(man_evt_ac_v, 'Target'), 'Absolute', value=f'{ego_maneuver[5]}')
    #
    #             # Starting Condition of long maneuvers
    #             man_evt_cond = SubElement(SubElement(SubElement(man_evt,
    #                                                             'StartConditions'),
    #                                                  'ConditionGroup'),
    #                                       'Condition', name=f'Start Condition of Event {eventcounter}',
    #                                       delay="0", edge="rising")
    #
    #             if timebased_lon:
    #                 # Time based trigger
    #                 SubElement(SubElement(man_evt_cond, 'ByValue'), 'SimulationTime',
    #                            value=f'{int(ego_maneuver[0]) / 10}', rule="greater_than")
    #
    #             elif not timebased_lon:
    #                 # Position based absolute position trigger
    #                 man_evt_cond_by = SubElement(man_evt_cond, 'ByEntity')
    #                 SubElement(SubElement(man_evt_cond_by, 'TriggeringEntities', rule="any"), 'Entity', name=f'{name}')
    #                 SubElement(SubElement(SubElement(SubElement(man_evt_cond_by,
    #                                                             'EntityCondition'),
    #                                                  'Distance', value=f'{radius_pos_trigger}', freespace="0",
    #                                                  alongRoute="0", rule="less_than"),
    #                                       'Position'),
    #                            'World', x=f'{ego_maneuver[3]}', y=f'{ego_maneuver[4]}', z='0', h='0', p='0', r='0')
    #
    #         if standstill & (str(ego_maneuver[2]) != 'FM_EGO_standstill'):
    #             standstill = False
    #
    #             # Maneuver: change speed by absolute elapsed simulation time trigger
    #             man_evt = SubElement(man, 'Event', name=f'New Event {eventcounter}', priority="overwrite")
    #
    #             man_evt_ac = SubElement(man_evt, 'Action', name=f"{ego_maneuver[2]}")
    #             man_evt_ac_v = SubElement(SubElement(SubElement(man_evt_ac, 'Private'), 'Longitudinal'), 'Speed')
    #             SubElement(man_evt_ac_v, 'Dynamics', shape="linear", rate=f"{ego_maneuver[6]}")
    #             SubElement(SubElement(man_evt_ac_v, 'Target'), 'Absolute', value=f'{ego_maneuver[5]}')
    #
    #             man_evt_cond = SubElement(SubElement(SubElement(man_evt,
    #                                                             'StartConditions'),
    #                                                  'ConditionGroup'),
    #                                       'Condition', name=f'Start Condition of Event {eventcounter}',
    #                                       delay="0", edge="rising")
    #             SubElement(SubElement(man_evt_cond, 'ByValue'), 'SimulationTime',
    #                        value=f'{int(ego_maneuver[0]) / 10}', rule="greater_than")
    #                                                                                       ######################
    #     # Loop infrastructure specific maneuvers
    #     current_inf_maneuver_array = inf_maneuver_array[key]
    #     for idx, inf_maneuver in enumerate(current_inf_maneuver_array):
    #         eventcounter += 1
    #
    #         if inf_maneuver[2] == 'FM_INF_lane_change_left':
    #             lane_change = 1
    #         elif inf_maneuver[2] == 'FM_INF_lane_change_right':
    #             lane_change = -1
    #         else:
    #             raise ValueError('Lane change maneuver name is wrong')
    #
    #         # Lane Change
    #         man_evt = SubElement(man, 'Event', name=f'New Event {eventcounter}', priority="overwrite")
    #         man_evt_ac = SubElement(man_evt, 'Action', name=f"{inf_maneuver[2]}")
    #         man_evt_ac_lane = SubElement(SubElement(SubElement(man_evt_ac, 'Private'), 'Lateral'), 'LaneChange',
    #                                      targetLaneOffset="4.26961e-316")
    #         SubElement(man_evt_ac_lane, 'Dynamics', time=f"{inf_maneuver[5]}", shape="sinusoidal")
    #         SubElement(SubElement(man_evt_ac_lane, 'Target'), 'Relative', object=f'{name}', value=f'{lane_change}')
    #
    #         # Starting Condition of lane change
    #         man_evt_cond = SubElement(SubElement(SubElement(man_evt,
    #                                                         'StartConditions'),
    #                                              'ConditionGroup'),
    #                                   'Condition', name=f'Start Condition of Event {eventcounter}',
    #                                   delay="0", edge="rising")
    #
    #         if timebased_lat:
    #             # Time based_lat trigger
    #             SubElement(SubElement(man_evt_cond, 'ByValue'), 'SimulationTime', value=f'{int(inf_maneuver[0]) / 10}',
    #                        rule="greater_than")
    #
    #         elif not timebased_lat:
    #             # Position based absolute position trigger
    #             man_evt_cond_by = SubElement(man_evt_cond, 'ByEntity')
    #             SubElement(SubElement(man_evt_cond_by, 'TriggeringEntities', rule="any"), 'Entity', name=f'{name}')
    #             SubElement(SubElement(SubElement(SubElement(man_evt_cond_by,
    #                                                         'EntityCondition'),
    #                                              'Distance', value=f'{radius_pos_trigger}', freespace="0",
    #                                              alongRoute="0", rule="less_than"),
    #                                   'Position'),
    #                        'World', x=f'{inf_maneuver[3]}', y=f'{inf_maneuver[4]}', z='0', h='0', p='0', r='0')
    #
    #     # Starting condition of act
    #     SubElement(SubElement(SubElement(SubElement(SubElement(SubElement(act,
    #                                                                       'Conditions'),
    #                                                            'Start'),
    #                                                 'ConditionGroup'),
    #                                      'Condition', name=f"Start Condition of Act {key + 1}", delay="0",
    #                                      edge="rising"),
    #                           'ByValue'),
    #                'SimulationTime', value="0", rule="greater_than")

    #####################################################

    # Create Scenario
    sb.add_story(story)
    scenario = xosc.Scenario(
        "",
        "OSC Generator",
        param,
        entities,
        sb,
        road,
        catalog
    )
    path = os.path.join(dir_name, 'man_export_' + os.path.basename(section_name) + '_scengen_test.xosc')
    scenario.write_xml(path)

    # path = write_pretty(root, 'xosc', use_folder, timebased_lon, timebased_lat,
    #                     dir_name, section_name, radius_pos_trigger, output_path)

    return path
