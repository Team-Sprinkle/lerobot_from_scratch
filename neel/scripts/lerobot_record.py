"""
Created by Indraneel on 11/03/2025

Record dataset from Lerobot

"""
from dataclasses import dataclass, field
from pathlib import Path
import time

from lerobot.configs import parser
from lerobot.robots import RobotConfig, make_robot_from_config
from lerobot.teleoperators import TeleoperatorConfig, make_teleoperator_from_config
from lerobot.configs.policies import PreTrainedConfig
from lerobot.datasets.lerobot_dataset import LeRobotDataset
from lerobot.datasets.utils import combine_feature_dicts
from lerobot.datasets.pipeline_features import aggregate_pipeline_dataset_features, create_initial_features
from lerobot.utils.utils import init_logging
from lerobot.utils.visualization_utils import init_rerun, log_rerun_data
from lerobot.processor import make_default_processors
from lerobot.utils.control_utils import (
    sanity_check_dataset_robot_compatibility,
    init_keyboard_listener
)
from lerobot.datasets.video_utils import VideoEncodingManager


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
    video_encoding_batch_size: int = 1
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


def record_loop():
    pass

@parser.wrap()
def record(cfg: RecordConfig) -> LeRobotDataset:
    init_logging()
    if cfg.display_data:
        init_rerun(session_name="neel_recording")
    
    robot = make_robot_from_config(cfg.robot)
    teleop = make_teleoperator_from_config(cfg.teleop) if cfg.teleop else None

    teleop_action_processor, robot_action_processor, robot_observation_processor = make_default_processors()

    # Combines multiple dicts into one dict
    dataset_features = combine_feature_dicts(
        # Gets features from robot and transforms them with pipeline
        aggregate_pipeline_dataset_features(
            pipeline=teleop_action_processor,
            initial_features=create_initial_features(
                action=robot.action_features
            ),
            use_videos=cfg.dataset.video
        ),
        aggregate_pipeline_dataset_features(
            pipeline=robot_observation_processor,
            initial_features=create_initial_features(observation=robot.observation_features),
            use_videos=cfg.dataset.video
        )

    )

    dataset = LeRobotDataset(
        cfg.dataset.repo_id,
        root=cfg.dataset.root,
        batch_encoding_size=cfg.dataset.video_encoding_batch_size,
    )

    if hasattr(robot, "cameras") and len(robot.cameras) > 0:
        dataset.start_image_writer(
            num_processes=cfg.dataset.num_image_writer_processes,
            num_threads=cfg.dataset.num_image_writer_threads_per_camera * len(robot.cameras)
        )
    sanity_check_dataset_robot_compatibility(dataset, robot, cfg.dataset.fps, dataset_features)

    # Load pretrained policy TODO

    robot.connect()
    if teleop is not None:
        teleop.connect()

    listener, events = init_keyboard_listener()

    with VideoEncodingManager(dataset):
        recorded_episodes = 0
        while recorded_episodes < cfg.dataset.num_episodes and not events["stop_recording"]:
            print(f"Recording episode {dataset.num_episodes}")
            record_loop()

            # Sleep for 10 seconds
            time.sleep(10)

            dataset.save_episode()
            recorded_episodes += 1
    

    print('Stop recording')

    robot.disconnect()
    if teleop is not None:
        teleop.disconnect()

    if listener is not None:
        listener.stop()

    if cfg.dataset.push_to_hub:
        dataset.push_to_hub(tags=cfg.dataset.tags, private=cfg.dataset.private)

    print('Exiting')

    return dataset

def main():
    record()


if __name__ == "__main__":
    main()