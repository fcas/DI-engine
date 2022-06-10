import os
from re import L
import shutil
import argparse

from distar.ctools.utils import read_config, deep_merge_dicts
from distar.actor import Actor
import torch
import random
import time
from ding.envs import BaseEnvManager
from dizoo.distar.envs import DIStarEnv
import traceback

from easydict import EasyDict
env_cfg = EasyDict(
    {
        'env': {
            'manager': {
                'episode_num': 100000,
                'max_retry': 1,
                'retry_type': 'reset',
                'auto_reset': True,
                'step_timeout': None,
                'reset_timeout': None,
                'retry_waiting_time': 0.1,
                'cfg_type': 'BaseEnvManagerDict',
                'shared_memory': False
            }
        }
    }
)

class TestDIstarEnv:
    def __init__(self):

        cfg = read_config('./test_distar_config.yaml')
        self._whole_cfg = cfg
        self._whole_cfg.env.map_name = 'KingsCove'
        self._agent_env = DIStarEnv(self._whole_cfg)

    def _inference_loop(self, job={}):


        torch.set_num_threads(1)

        # self._env = DIStarEnv(self._whole_cfg)
        self._env = BaseEnvManager(
            env_fn=[lambda: DIStarEnv(self._whole_cfg) for _ in range(1)], cfg=env_cfg.env.manager
        )
        self._env.seed(1)

        with torch.no_grad():
            for episode in range(2):
                self._env.launch()
                try:
                    for env_step in range(10):
                        obs = self._env.ready_obs
                        # print(obs)
                        obs = {env_id: obs[env_id] for env_id in range(1)}
                        actions = {}
                        for env_id in range(1):
                            observations = obs[env_id]
                            actions[env_id] = self._agent_env.random_action(observations)
                            # print(actions)
                        timesteps = self._env.step(actions)
                        print(actions)
                        
                except Exception as e:
                    print('[EPISODE LOOP ERROR]', e, flush=True)
                    print(''.join(traceback.format_tb(e.__traceback__)), flush=True)
                    self._env.close()
                
                self._env.close()

if __name__ == '__main__':

    ## main
    if os.path.exists(r'C:\Program Files (x86)\StarCraft II'):
        sc2path = r'C:\Program Files (x86)\StarCraft II'
    elif os.path.exists('/Applications/StarCraft II'):
        sc2path = '/Applications/StarCraft II'
    else:
        assert 'SC2PATH' in os.environ.keys(), 'please add StarCraft2 installation path to your environment variables!'
        sc2path = os.environ['SC2PATH']
        assert os.path.exists(sc2path), 'SC2PATH: {} does not exist!'.format(sc2path)
    if not os.path.exists(os.path.join(sc2path, 'Maps/Ladder2019Season2')):
        shutil.copytree(os.path.join(os.path.dirname(__file__), '../envs/maps/Ladder2019Season2'), os.path.join(sc2path, 'Maps/Ladder2019Season2'))

    ## actor_run
    actor = TestDIstarEnv()
    actor._inference_loop()