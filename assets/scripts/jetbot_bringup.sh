#!/bin/bash
sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
sudo apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654
sudo apt-get update -y
sudo apt-get install ros-melodic-ros-base -y
sudo rosdep init
rosdep update
sudo su ggc_user --shell /bin/bash
sudo sh -c 'echo "source /opt/ros/melodic/setup.bash" >> ~/.bashrc'
exit