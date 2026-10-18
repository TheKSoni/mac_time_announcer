#!/usr/bin/env python3
#
# Copyright (c) 2026 Kunal Soni (theksoni)
# SPDX-License-Identifier: MIT
#

import os
import sys
import json
import time
from datetime import datetime

CONFIG_PATH = os.path.expanduser('~/.config/time_announcer.json')

DEFAULT_CONFIG = {
    "enabled": True,
    "interval_minutes": 15,
    "type": "clock", # "clock" (e.g. 15th min) or "relative" (every 15m from now)
    "mode": "only",  # "only" (run between A and B) or "except" (do NOT run between A and B)
    "start_time": "18:00",
    "end_time": "10:30",
    "last_run": 0
}

def load_config():
    if not os.path.exists(os.path.dirname(CONFIG_PATH)):
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)

def parse_time_to_minutes(time_str):
    h, m = map(int, time_str.split(':'))
    return h * 60 + m

def is_time_allowed(config):
    now = datetime.now()
    current_minutes = now.hour * 60 + now.minute
    start_min = parse_time_to_minutes(config["start_time"])
    end_min = parse_time_to_minutes(config["end_time"])
    
    if start_min <= end_min:
        in_window = start_min <= current_minutes <= end_min
    else:
        in_window = current_minutes >= start_min or current_minutes <= end_min

    if config["mode"] == "only":
        return in_window
    elif config["mode"] == "except":
        return not in_window
    return True

def should_run(config):
    if not config["enabled"]:
        return False
        
    now = datetime.now()
    interval = config["interval_minutes"]
    
    if config["type"] == "clock":
        return now.minute % interval == 0
    else:
        last_run = config.get("last_run", 0)
        return (time.time() - last_run) >= (interval * 60) - 2

def announce():
    speech_time = datetime.now().strftime("%l:%M %p")
    os.system(f'osascript -e "say \"The time is {speech_time}\""')

if __name__ == "__main__":
    cfg = load_config()
    if should_run(cfg):
        if is_time_allowed(cfg):
            announce()
        cfg["last_run"] = time.time()
        save_config(cfg)
