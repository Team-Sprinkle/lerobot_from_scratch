# lerobot_from_scratch
Repo to reproduce lerobot imitation learning from scratch (Purely for learning purpose)

## Breakdown of lerobot IL pipeline

[Original repo](https://github.com/huggingface/lerobot)

### Lerobot find port

#### [Link to code](https://github.com/huggingface/lerobot/blob/main/src/lerobot/scripts/lerobot_find_port.py)

#### What does the script do

Simple script which finds OS specific usb connected ports and finds a ports diff

#### Learning level (0-5)
0

### Motor Setup

#### [Link to code](https://github.com/huggingface/lerobot/blob/main/src/lerobot/scripts/lerobot_setup_motors.py)

#### What does the script do

Helper to set motor ids for every servo motors and baudrate. Basically returns the robot object based on the config flag and each robot individually implements setup_motors()

#### Learning level (0-5)
0


### Robot Calibration

#### [Link to code](https://github.com/huggingface/lerobot/blob/main/src/lerobot/scripts/lerobot_calibrate.py)

#### What does the script do

Generates json file with min and max range for each motor in the arm. Returns robot object based on config and each robot individually implements callibrate()

#### Learning level (0-5)
0


### Robot Teleoperate

#### [Link to code](https://github.com/huggingface/lerobot/blob/main/src/lerobot/scripts/lerobot_teleoperate.py)

#### What does the script do

Control a generic robot from a generic teleoperation device. In our case so101 leader controls so101 follower. Also has option to display some data in rerun

#### Learning level (0-5)
3


### Find Cameras

#### [Link to code](https://github.com/huggingface/lerobot/blob/main/src/lerobot/scripts/lerobot_find_cameras.py)

#### What does the script do

List connected cameras, print metadata and capture image with the camera

#### Learning level (0-5)
0

### Record the dataset

#### [Link to code](https://github.com/huggingface/lerobot/blob/main/src/lerobot/scripts/lerobot_record.py)

#### What does the script do

Script to record data from generic teleoperator device or by a policy. Creates a robot and a dataset and sets up a recording loop for a fixed amount of time

#### Learning level (0-5)
5

### Visualise the dataset

#### [Link to code](https://github.com/huggingface/lerobot/blob/main/src/lerobot/scripts/lerobot_dataset_viz.py)

#### What does the script do

Visualises dataset of type LeRobotDataset. Not needed if pushing data to hugging face

#### Learning level (0-5)
2


### Replay an episode

#### [Link to code](https://github.com/huggingface/lerobot/blob/main/src/lerobot/scripts/lerobot_replay.py)

#### What does the script do

Loads the dataset and sends actions to a robot in a loop

#### Learning level (0-5)
2


### Training

#### [Link to code](https://github.com/huggingface/lerobot/blob/main/src/lerobot/scripts/lerobot_train.py)

#### What does the script do

Weights and biases setup, policy setup, dataloader setup, and generic training loop for a policy and then also pushes trained model to hugging face

#### Learning level (0-5)
5









