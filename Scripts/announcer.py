#!/usr/bin/env python3
#
# Copyright (c) 2026 Kunal Soni (theksoni)
# SPDX-License-Identifier: MIT
#

import os
import sys
import json
import time
import subprocess
from datetime import datetime

CONFIG_PATH = os.path.expanduser('~/.config/time_announcer.json')
LOG_DIR = os.path.expanduser('~/.config/time_announcer_logs')

DEFAULT_CONFIG = {
    "enabled": True,
    "interval_minutes": 15,
    "type": "clock", # "clock" (e.g. 15th min) or "relative" (every 15m from now)
    "mode": "only",  # "only" (run between A and B) or "avoid" (do NOT run between A and B)
    "start_time": "18:00",
    "end_time": "10:30",
    "last_run": 0,
    "debug": False
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

def cleanup_old_logs():
    if not os.path.exists(LOG_DIR):
        return
    log_files = sorted([f for f in os.listdir(LOG_DIR) if f.endswith(".log")])
    if len(log_files) <= 3:
        return
    for old_file in log_files[:-3]:
        try:
            os.remove(os.path.join(LOG_DIR, old_file))
        except Exception:
            pass

def log_debug(message, config):
    if not config.get("debug", False):
        return
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        cleanup_old_logs()
        today_file = os.path.join(LOG_DIR, f"{datetime.now().strftime('%Y-%m-%d')}.log")
        timestamp = datetime.now().strftime("%H:%M:%S")
        with open(today_file, "a") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass

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

    if config.get("mode") == "only":
        return in_window
    elif config.get("mode") == "avoid":
        return not in_window
    return True

def should_run(config):
    if not config.get("enabled", False):
        return False
        
    now = datetime.now()
    interval = config.get("interval_minutes", 15)
    last_run = config.get("last_run", 0)
    
    # Avoid duplicate announcements in the same 30s window
    if (time.time() - last_run) < 30:
        return False

    if config.get("type", "clock") == "clock":
        return now.minute % interval == 0
    else:
        return (time.time() - last_run) >= (interval * 60) - 2

def announce():
    speech_time = datetime.now().strftime("%I:%M %p").lstrip("0")
    subprocess.run(["say", f"The time is {speech_time}"])

if __name__ == "__main__":
    cfg = load_config()
    if should_run(cfg):
        # Record the run time before speaking so speech duration doesn't shift the schedule
        cfg["last_run"] = time.time()
        save_config(cfg)
        if is_time_allowed(cfg):
            log_debug("Trigger: Announcement spoken successfully", cfg)
            announce()
        else:
            log_debug("Trigger: Announcement suppressed by time window", cfg)
    else:
        if cfg.get("debug", False):
            log_debug("Check: Skipped (not at interval or disabled)", cfg)
