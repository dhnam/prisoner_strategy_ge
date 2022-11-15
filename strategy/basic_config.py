from __future__ import annotations
import json
from pathlib import Path
from .rewardtable import RewardTable

RANDOM_DETR_STATE_RATIO: float
MUTATE_RATE: float
REWARD_TABLE: RewardTable

config_path = Path(__file__).with_name('config.json')
with open(config_path, 'r') as f:
    setting = json.load(f)
    RANDOM_DETR_STATE_RATIO = setting["RANDOM_DETR_STATE_RATIO"]
    MUTATE_RATE = setting["MUTATE_RATE"]
    REWARD_TABLE = RewardTable(**setting["REWARD_TABLE"])