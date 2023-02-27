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

    # Write Parameters
    param = xosc.ParameterDeclarations()

    # Write catalogs
    catalog_path = "../Catalogs/Vehicles"
    catalog = xosc.Catalog()
    catalog.add_catalog("VehicleCatalog", catalog_path)

    # Write road network
    road = xosc.RoadNetwork(
        roadfile=opendrive_name, scenegraph=osgb_name
    )

    # Write entities
    entities = xosc.Entities()
    # Entity - ego
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

    # Entities - objects
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

    # Write Init
    init = xosc.Init()
    step_time = xosc.TransitionDynamics(
        xosc.DynamicsShapes.step, xosc.DynamicsDimension.rate, 0
    )
    # Start (init) conditions - Ego
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
        objstart = xosc.TeleportAction(xosc.WorldPosition(x=f'{obj[0]}', y=f'{obj[1]}',
                                                          z='0', h=f'{obj[3]}', p='0', r='0'))
        init.add_init_action(objname, objstart)
        init.add_init_action(objname, objspeed)

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
        man = xosc.Maneuver(f'New Maneuver {key + 1}', parameters=param)
        man_lat = xosc.Maneuver(f'New Maneuver {key + 1}', parameters=param)
        mangroup = xosc.ManeuverGroup(f'New Sequence {key + 1}')
        mangroup.add_actor(name)
        # Start trigger for Act
        act_trig_cond = xosc.SimulationTimeCondition(value=0, rule=xosc.Rule.greaterThan)
        act_starttrigger = xosc.ValueTrigger(name=f'Start Condition of Act {key + 1}', delay=0,
                                    conditionedge=xosc.ConditionEdge.rising, valuecondition=act_trig_cond)
        act = xosc.Act(f'New Act {key + 1}', starttrigger=act_starttrigger)

        long_event = False
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
                    long_event = True
                    # Time based trigger
                    trig_cond = xosc.SimulationTimeCondition(value=float(ego_maneuver[0]) / 10, rule=xosc.Rule.greaterThan)
                    trigger = xosc.ValueTrigger(name=f'Start Condition of Event {eventcounter}', delay=0,
                                                conditionedge=xosc.ConditionEdge.rising, valuecondition=trig_cond)

                elif not timebased_lon:
                    long_event = True
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

                man.add_event(event)

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

        lateral_event = False
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
                lateral_event = True

            elif not timebased_lat:
                # Position based absolute position trigger
                worldpos = xosc.WorldPosition(x=inf_maneuver[3], y=inf_maneuver[4],
                                              z='0', h='0', p='0', r='0')
                trig_cond = xosc.DistanceCondition(value=f'{radius_pos_trigger}', rule=xosc.Rule.lessThan,
                                                   position=worldpos, alongroute="0", freespace="0")
                trigger = xosc.EntityTrigger(name=f'Start Condition of Event {eventcounter}', delay=0,
                                             conditionedge=xosc.ConditionEdge.rising, entitycondition=trig_cond,
                                             triggerentity=f'{name}')
                lateral_event = True

            event.add_trigger(trigger)
            dyn = xosc.TransitionDynamics(shape=xosc.DynamicsShapes.sinusoidal,
                                          dimension=xosc.DynamicsDimension.time, value=inf_maneuver[5])
            action = xosc.RelativeLaneChangeAction(lane=lane_change, entity=f'{name}', transition_dynamics=dyn,
                                                   target_lane_offset=4.26961e-316)
            event.add_action(actionname=f"{inf_maneuver[2]}", action=action)

            man_lat.add_event(event)

        # Add maneuver events to act and story
        if long_event:
            mangroup.add_maneuver(man)
        if lateral_event:
            mangroup.add_maneuver(man_lat)
        act.add_maneuver_group(mangroup)
        story.add_act(act)

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

    # Create Output Path
    if output_path is not None:
        path = output_path

    else:
        if use_folder:
            if timebased_lon and timebased_lat:
                path = os.path.join(dir_name, 'man_export_' + os.path.basename(section_name) + '_time_lon_lat.xosc')
            elif timebased_lon and not timebased_lat:
                path = os.path.join(dir_name,
                                    'man_export_' + os.path.basename(section_name) + '_time_lon_pos_lat_' + str(
                                        radius_pos_trigger) + '_m.xosc')
            elif not timebased_lon and timebased_lat:
                path = os.path.join(dir_name, 'man_export_' + os.path.basename(section_name) + '_pos_lon_time_lat.xosc')

            else:
                path = os.path.join(dir_name, 'man_export_' + os.path.basename(section_name) + '_pos_lon_lat_' +
                                    str(radius_pos_trigger) + '_m.xosc')

        else:
            raise NotImplementedError("use_folder flag is going to be removed")
    # Write Scenario to xml
    scenario.write_xml(path)

    return path
