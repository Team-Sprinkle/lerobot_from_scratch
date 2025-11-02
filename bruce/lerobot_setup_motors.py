"""
Helper to set motor id and baudrate.

I wrote line-by-line the original code to understand it.
You need to look into utils.py to understand how motors are set for a different device.


```shell
lerobot-setup-motors \
    --teleop.type=so100_leader \
    --teleop.port=/dev/tty.usbmodem575E0031751
```
"""

from dataclasses import dataclass
import draccus

from lerobot.robots import (
    RobotConfig,
    koch_follower,
    lekiwi,
    make_robot_from_config,
    so100_follower,
    so101_follower,
)

from lerobot.teleoperators import (
    TeleoperatorConfig,
    koch_leader,
    make_teleoperator_from_config,
    so100_leader,
    so101_leader,
)


COMPATIBLE_DEVICES = [
    "koch_follower",
    "koch_leader",
    "so100_follower",
    "so100_leader",
    "so101_follower",
    "so101_leader",
    "lekiwi",
]


@dataclass
class SetupConfig:
    teleop: TeleoperatorConfig | None = None
    robot: RobotConfig | None = None

    def __post__init__(self):
        if bool(self.teleop) == bool(self.robot):
            raise ValueError("Either robot or teleop needs to be chosen.")
        self.device = self.robot if self.robot else self.teleop


@draccus.wrap()  # Uses Draccus - Slightly Less Simple Configuration with Dataclasses
def setup_motors(cfg: SetupConfig):
    if cfg.device.type not in COMPATIBLE_DEVICES:
        raise NotImplementedError
    if isinstance(cfg.device, RobotConfig):
        device = make_robot_from_config(cfg.device)
    else:
        device = make_teleoperator_from_config(cfg.device)

    device.setup_motors()


def main():
    setup_motors()


if __name__ == "__main__":
    main()
