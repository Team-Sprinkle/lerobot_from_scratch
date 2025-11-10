"""
Created by Indraneel on 11/10/2025



"""
import logging

import torch

from lerobot.utils.utils import init_logging
from lerobot.configs import parser
from lerobot.configs.train import TrainPipelineConfig
from lerobot.rl.wandb_utils import WandBLogger
from lerobot.utils.random_utils import set_seed
from lerobot.utils.utils import get_safe_torch_device
from lerobot.datasets.factory import make_dataset
from lerobot.policies.factory import make_policy


@parser.wrap()
def train(cfg: TrainPipelineConfig):
    """
        Training!
    """
    cfg.validate()

    if cfg.wandb.enable and cfg.wandb.project:
        wandb_logger = WandBLogger(cfg)
    else:
        wandb_logger = None
        logging.info("Wandb logger is disabled")
    
    if cfg.seed is not None:
        set_seed(cfg.seed)

    # Check if device is available
    device = get_safe_torch_device(cfg.policy.device, log=True)
    # Tried different convolutional algorithms for your hardware and then picks the best one
    torch.backends.cudnn.benchmark = True
    # Useful for newer nvidia gpu, using tf32 math is faster at the cost of some accuracy
    torch.backends.cuda.matmul.allow_tf32 = True

    logging.info("Creating dataset")
    dataset = make_dataset(cfg)

    # TODO eval env

    logging.info("Creating policy")
    policy = make_policy(
        cfg=cfg.policy,
        ds_meta=dataset.meta
    )





def main():
    init_logging()
    train()
    
if __name__== "__main__":
    main()