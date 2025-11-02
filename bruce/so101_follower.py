#!/usr/bin/env python
"""
I wrote line-by-line the original code to understand it.
"""

import logging
import time
from functools import cached_property
from typing import Any

# lerobot cameras
# lerobot motors
# lerobot feetech


from lerobot.utils.errors import DeviceAlreadyConnectedError, DeviceNotConnectedError

from ..robot import Robot
from ..utils import ensure_safe_goal_position
from .config_so101_follower import SO101FollowerConfig

logger = logging.getLogger(__name__)

# src/lerobot/robots/robot.py
class SO101Follower(Robot):

