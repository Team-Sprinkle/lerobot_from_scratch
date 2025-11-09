"""
Created by Indraneel on 11/08/2025



"""
from pathlib import Path
from dataclasses import dataclass
import time

from lerobot.configs import parser
from lerobot.policies.factory import make_policy, make_pre_post_processors
from lerobot.policies.pretrained import PreTrainedPolicy
from lerobot.robots import RobotConfig, make_robot_from_config, Robot
from lerobot_record import DatasetRecordConfig, RecordConfig
from lerobot.utils.utils import init_logging
from lerobot.utils.visualization_utils import init_rerun
from lerobot.utils.control_utils import sanity_check_dataset_name, init_keyboard_listener
from lerobot.processor import make_default_processors, PolicyAction, PolicyProcessorPipeline, RobotAction, RobotProcessorPipeline, RobotObservation
from lerobot.processor.rename_processor import rename_stats
from lerobot.datasets.utils import combine_feature_dicts, build_dataset_frame
from lerobot.datasets.lerobot_dataset import LeRobotDataset 
from lerobot.datasets.pipeline_features import aggregate_pipeline_dataset_features, create_initial_features
from lerobot.datasets.video_utils import VideoEncodingManager
from lerobot.datasets.image_writer import safe_stop_image_writer


@safe_stop_image_writer
def record_loop(
    robot: Robot,
    events: dict,
    fps: int,
    robot_action_processor: RobotProcessorPipeline[
        tuple[RobotAction, RobotObservation], RobotAction
    ],
    robot_observation_processor: RobotProcessorPipeline[
        RobotObservation, RobotObservation
    ],
    dataset: LeRobotDataset | None = None,
    policy: PreTrainedPolicy
):
    pass

@parser.wrap()
def record(cfg: RecordConfig):
    init_logging()
    if cfg.display_data:
        init_rerun(session_name="recording")
    
    robot = make_robot_from_config(cfg.robot)

    teleop_action_processor, robot_action_processor, robot_observation_processor = make_default_processors()

    dataset_features = combine_feature_dicts(
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

    sanity_check_dataset_name(cfg.dataset.repo_id, cfg.policy)
    dataset = LeRobotDataset.create(
        cfg.dataset.repo_id,
        cfg.dataset.fps,
        root=cfg.dataset.root,
        robot_type=robot.name,
        features=dataset_features,
        use_videos=cfg.dataset.video,
        image_writer_processes=cfg.dataset.num_image_writer_processes,
        image_writer_threads=cfg.dataset.num_image_writer_threads_per_camera * len(robot.cameras),
        batch_encoding_size=cfg.dataset.video_encoding_batch_size
    )

    # Load pretrained policy
    if cfg.policy is None:
        raise RuntimeError("Policy cannot be None")
    policy = make_policy(cfg.policy, ds_meta=dataset.meta)
    preprocessor, postprocessor = make_pre_post_processors(
        policy_cfg=cfg.policy,
        pretrained_path=cfg.policy.pretrained_path,
        dataset_stats=rename_stats(dataset.meta.stats, cfg.dataset.rename_map),
        preprocessor_overrides={
            "device_processor": {"device": cfg.policy.device},
            "rename_observations_processor": {"rename_map": cfg.dataset.rename_map},
        }
    )

    robot.connect()

    listener, events = init_keyboard_listener()

    with VideoEncodingManager(dataset):
        recorded_episodes = 0
        while recorded_episodes < cfg.dataset.num_episodes and not events["stop_recording"]:
            print(f"Recording episode {dataset.num_episodes}")
            record_loop()
            print("Finished recording")

            time.sleep(10)


            if events["rerecord_episode"]:
                print("Rerecord episode")
                events["rerecord_episode"] = False
                events["exit_early"] = False
                dataset.clear_episode_buffer()
                continue
                
            
            dataset.save_episode()
            recorded_episode +=1
    
    print("Stop recording")

    robot.disconnect()


    if listener is not None:
        listener.stop()


def main():
    record()

if __name__ == "__main__":
    main()