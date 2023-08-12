import os
import random
import math

import numpy as np
from gym import spaces

from typing import cast

from matplotlib import pyplot as plt

from PIL import Image
import habitat_sim
from habitat_sim.utils.common import d3_40_colors_rgb

from habitat_baselines.config.default import get_config  
from habitat.sims.habitat_simulator.habitat_simulator import HabitatSim
from habitat_baselines.common.env_utils import construct_envs
from habitat_baselines.common.environments import get_env_class
from habitat.core.env_point import Env
from habitat.utils.visualizations import maps
from habitat_baselines.common.utils import quat_from_angle_axis
from utils.log_manager import LogManager
from utils.log_writer import LogWriter

def display_sample(
    rgb_obs, semantic_obs=np.array([]), depth_obs=np.array([]), red_writer=None, green_writer=None, blue_writer=None, maks_writer=None, config=None, opt=-1
):
    rgb_img = Image.fromarray(rgb_obs, mode="RGB")
    
    arr = [rgb_obs]
    titles = ["rgb"]
    
    for i in range(rgb_obs.shape[0]):
        for j in range(rgb_obs.shape[1]):
            red_writer.write(str(rgb_obs[i][j][0]))
            green_writer.write(str(rgb_obs[i][j][1]))
            blue_writer.write(str(rgb_obs[i][j][2]))
            
            if rgb_obs[i][j][0] > 200 and rgb_obs[i][j][1] < 50 and rgb_obs[i][j][2] < 50:
                mask_writer.write(str(1))
            elif rgb_obs[i][j][0] < 50 and rgb_obs[i][j][1] < 50 and rgb_obs[i][j][2] < 50:
                mask_writer.write(str(2))
            else:
                mask_writer.write(str(0))
                
        red_writer.writeLine()
        green_writer.writeLine()
        blue_writer.writeLine()
        mask_writer.writeLine()
    
    if semantic_obs.size != 0:
        semantic_img = Image.new(
            "P", (semantic_obs.shape[1], semantic_obs.shape[0])
        )

        semantic_img.putpalette(d3_40_colors_rgb.flatten())
        semantic_img.putdata((semantic_obs.flatten() % 40).astype(np.uint8))
        semantic_img = semantic_img.convert("RGBA")
        arr.append(semantic_img)
        titles.append("semantic")
        
    if depth_obs.size != 0:
        depth_obs = (depth_obs - config.SIMULATOR.DEPTH_SENSOR.MIN_DEPTH) / (
                    config.SIMULATOR.DEPTH_SENSOR.MAX_DEPTH - config.SIMULATOR.DEPTH_SENSOR.MIN_DEPTH
                )
        depth_img = Image.fromarray(
            (depth_obs / 10 * 255).astype(np.uint8), mode="L"
        )
        arr.append(depth_img)
        titles.append("depth")
        
    plt.figure(figsize=(12, 8))
    for i, data in enumerate(arr):
        ax = plt.subplot(1, 3, i + 1)
        ax.axis("off")
        ax.set_title(titles[i])
        plt.imshow(data)
    
    path = "./figures/fig.png"
    if opt !=-1:
        path = "./figures/fig" + str(opt) + ".png"
    plt.savefig(path)
    plt.show(block=False)

def add_objects(env, sim, red_writer, green_writer, blue_writer, mask_writer, config=None, num=1):    
    object_lib_size = sim._sim.get_physics_object_library_size()
    print("object_lib_size:" + str(object_lib_size))
    object_init_grid_dim = (3, 1, 3)
    object_init_grid = {}
    
    # clear the objects if we are re-running this initializer
    for old_obj_id in sim._sim.get_existing_object_ids():
        print("remove:" + str(old_obj_id))
        sim._sim.remove_object(old_obj_id)
        
    index = [0, 6]
    position = [[8.816797, 3.8141459, 7.7605705], [8.316797, 3.8141459, 6.7605705]]
    for obj_id in range(num):
        obj_index = index[obj_id]
        object_position = position[obj_id]
        object_id = sim._sim.add_object(obj_index)
        sim._sim.set_translation(object_position, object_id)
        print("added object: " + str(object_id) + " of type " + str(obj_index) + " at: " + str(object_position))
        
    observation = env.step("MOVE_FORWARD")
    display_sample(observation['rgb'], observation['semantic'], np.squeeze(observation['depth']), red_writer, green_writer, blue_writer, mask_writer, config, opt=13)
    
    
if __name__ == '__main__':
    exp_config = "./habitat/config/test.yaml"
    opts = None
    config = get_config(exp_config, opts)
    
    dataset_path = "figures/test3.json.gz"
        
    config.defrost()
    config.DATASET.DATA_PATH = dataset_path
    config.TASK_CONFIG.SIMULATOR.DEPTH_SENSOR.NORMALIZE_DEPTH = False
    config.TASK_CONFIG.SIMULATOR.DEPTH_SENSOR.MIN_DEPTH = 0.0
    config.TASK_CONFIG.SIMULATOR.DEPTH_SENSOR.MAX_DEPTH = 5.0
    config.TASK_CONFIG.SIMULATOR.AGENT_0.HEIGHT = 1.5
    config.TASK_CONFIG.SIMULATOR.SEMANTIC_SENSOR.HEIGHT = 256
    config.TASK_CONFIG.SIMULATOR.SEMANTIC_SENSOR.WIDTH = 256
    config.TASK_CONFIG.SIMULATOR.AGENT_0.SENSORS = ["RGB_SENSOR", "DEPTH_SENSOR", "SEMANTIC_SENSOR"]
    config.TASK_CONFIG.TASK.MEASUREMENTS = ['DISTANCE_TO_CURR_GOAL', 'DISTANCE_TO_MULTI_GOAL', 'SUB_SUCCESS', 'SUCCESS', 'EPISODE_LENGTH', 'MSPL', 'PERCENTAGE_SUCCESS', 'RATIO', 'PSPL', 'RAW_METRICS', 'TOP_DOWN_MAP']
    config.TASK_CONFIG.TRAINER_NAME = "oracle"
    config.TASK_CONFIG.DATASET.DATA_PATH = dataset_path
    config.TASK_CONFIG.SIMULATOR.HABITAT_SIM_V0.PHYSICS_CONFIG_FILE = ("./data/default.phys_scene_config.json")
    config.freeze()
    
    #print(config)
    #print("########################")
    log_manager = LogManager()
    log_manager.setLogDirectory("check")
    red_writer = log_manager.createLogWriter("red")
    green_writer = log_manager.createLogWriter("green")
    blue_writer = log_manager.createLogWriter("blue")
    mask_writer = log_manager.createLogWriter("mask")
    
    with Env(config=config.TASK_CONFIG) as env:
        sim = env.sim
        observation = env.reset()
        info = env.get_metrics()
        #print("OBSERVATION:")
        #print(observation)
        #print("INFO:")
        #print(info)
        #display_sample(observation['rgb'], observation['semantic'], np.squeeze(observation['depth']), opt=2)
        #print("State:")
        #print(env.sim.get_agent_state())
        
        
        add_objects(env, sim,red_writer, green_writer, blue_writer, mask_writer, config=config.TASK_CONFIG, num=2)