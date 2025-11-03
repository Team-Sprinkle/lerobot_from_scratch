"""
Created by Indraneel on 11/03/2025

Record dataset from Lerobot

"""
from dataclasses import dataclass, field
from pathlib import Path

from lerobot.configs import parser
from lerobot.robots import RobotConfig, make_robot_from_config
from lerobot.teleoperators import TeleoperatorConfig, make_teleoperator_from_config
from lerobot.configs.policies import PreTrainedConfig
from lerobot.datasets.lerobot_dataset import LeRobotDataset
from lerobot.utils.utils import init_logging
from lerobot.utils.visualization_utils import init_rerun, log_rerun_data
from lerobot.processor import make_default_processors


@dataclass
class DatasetRecordConfig:
    # Dataset identifier
    repo_id: str
    # Description of the task
    single_task: str
    # root directory where dataset will be stored
    root: str | Path | None = None
    fps: int = 30
    # Seconds of data recording for each episode
    episode_time_s: int | float = 60
    # Number of episodes
    num_episodes: int = 50
    # Encode frames in dataset into video
    video: bool = True
    # Upload dataset to hugging face
    push_to_hub:bool = True
    private: bool = False
    tags: list[str] | None = None
    # Number of subprocesses in each thread
    num_image_writer_processes: int = 0
    # Number of threads per camera, too many threads can block main thread too few might cause low cameras fps
    num_image_writer_threads_per_camera: int = 4
    video_encoding_batch_side: int = 1
    rename_map: dict[str,str] = field(default_factory=dict)

    def __post_init__(self):
        if self.single_task is None:
            raise ValueError("You need to provide a task")


@dataclass
class RecordConfig:
    robot: RobotConfig
    dataset: DatasetRecordConfig
    teleop: TeleoperatorConfig | None = None
    policy: PreTrainedConfig| None = None
    display_data: bool = False
    play_sounds: bool = True
    # Resume recording on existing dataset
    resume:bool = False

    def __post_init__(self):
        policy_path = parser.get_path_arg("policy")
        if policy_path:
            cli_overrides = parser.get_cli_overrides("policy")
            self.policy = PreTrainedConfig.from_pretrained(policy_path, cli_overrides=cli_overrides)
            self.policy.pretrained_path = policy_path

        if self.teleop is None and self.policy is None:
            raise ValueError("Choose a policy, a teleoperator or both to control the robot")
        
    @classmethod
    def __get_path_fields__(cls) -> list[str]:
        return ["policy"]

@parser.wrap()
def record(cfg: RecordConfig) -> LeRobotDataset:
    init_logging()
    if cfg.display_data:
        init_rerun(session_name="neel_recording")
    
    robot = make_robot_from_config(cfg.robot)
    teleop = make_teleoperator_from_config(cfg.teleop) if cfg.teleop else None

    teleop_action_processor, robot_action_processor, robot_observation_processor = make_default_processors()



    pass

def main():
    record()


if __name__ == "__main__":
    main()