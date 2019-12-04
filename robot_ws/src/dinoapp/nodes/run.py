#!/usr/bin/env python3
import sys
import torch
import torchvision
import torch.nn.functional as F
import time
import datetime
import numpy as np
import cv2
import torchvision.transforms as transforms
import PIL.Image
import os
import logging
logging.basicConfig(level=logging.DEBUG)
from jetbot import Camera

try: 
    print("Loading the models, getting ready to drive!!")
    model_roadfollow = torchvision.models.resnet18(pretrained=False)
    model_roadfollow.fc = torch.nn.Linear(512, 2)
    model_roadfollow.load_state_dict(torch.load('/tmp/mlmodels/best_steering_model_xy.pth'))
    
    device = torch.device('cuda')
    
    model = model_roadfollow.to(device)
    model = model_roadfollow.eval().half()
    
    camera = Camera.instance(width=224, height=224)

    from jetbot import Robot
    robot = Robot()
    speed_gain_slider = 0.10
    steering_gain_slider = 0.04
    steering_dgain_slider = 0.02
    steering_bias_slider = 0.05
    angle = 0.0
    angle_last = 0.0
    prev_class = -1
except Exception as e:
    print("Error occured.")
    
dino_names = [
    'Spinosaurus',
    'Dilophosaurus',
    'Stegosaurus',
    'Triceratops',
    'Brachiosaurus',
    'Unknown']

mean = 255.0 * np.array([0.485, 0.456, 0.406])
stdev = 255.0 * np.array([0.229, 0.224, 0.225])

mean_roadfollow = torch.Tensor([0.485, 0.456, 0.406]).cuda().half()
std_roadfollow = torch.Tensor([0.229, 0.224, 0.225]).cuda().half()

normalize = torchvision.transforms.Normalize(mean, stdev)

def preprocess(camera_value):
    global device, normalize
    x = camera_value
    x = cv2.cvtColor(x, cv2.COLOR_BGR2RGB)
    x = x.transpose((2, 0, 1))
    x = torch.from_numpy(x).float()
    x = normalize(x)
    x = x.to(device)
    x = x[None, ...]
    return x

def preprocess_roadfollow(image):
    image = PIL.Image.fromarray(image)
    image = transforms.functional.to_tensor(image).to(device).half()
    image.sub_(mean_roadfollow[:, None, None]).div_(std_roadfollow[:, None, None])
    return image[None, ...]
    
def move_bot(image, robot_stop):
    global angle, angle_last    
    if robot_stop:
        robot.stop()
        robot.left_motor.value=0
        robot.left_motor.value=0
        time.sleep(2)
        robot_stop = False
    else:
        xy = model_roadfollow(preprocess_roadfollow(image)).detach().float().cpu().numpy().flatten()
        x = xy[0]
        y = (0.5 - xy[1]) / 2.0
        speed_slider = speed_gain_slider
        angle = np.arctan2(x, y)
        pid = angle * steering_gain_slider + (angle - angle_last) * steering_dgain_slider
        angle_last = angle
        steering_slider = pid + steering_bias_slider
        robot.left_motor.value = max(min(speed_slider + steering_slider, 1.0), 0.0)
        robot.right_motor.value = max(min(speed_slider - steering_slider, 1.0), 0.0)
    
while True:
    img = camera.value
    robot_stop = False
    msg = "Start..."
    move_bot(img, robot_stop)