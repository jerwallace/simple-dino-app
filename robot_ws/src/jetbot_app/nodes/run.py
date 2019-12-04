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

SPEED_GAIN = 0.10
STEERING_GAIN = 0.04
STEERING_DGAIN = 0.02
STEERING_BIAS = 0.05

print("Imported the libraries... Loading the models, getting ready to drive!!")

model_roadfollow = torchvision.models.resnet18(pretrained=False)
model_roadfollow.fc = torch.nn.Linear(512, 2)
model_roadfollow.load_state_dict(torch.load('/tmp/trained_models/best_steering_model_xy.pth'))
device = torch.device('cuda')
model = model_roadfollow.to(device)
model = model_roadfollow.eval().half()
camera = Camera.instance(width=224, height=224)
    
from jetbot import Robot
robot = Robot()

angle = 0.0
angle_last = 0.0
prev_class = -1
    
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
        angle = np.arctan2(x, y)
        pid = angle * STEERING_GAIN + (angle - angle_last) * STEERING_DGAIN
        angle_last = angle
        steering_slider = pid + STEERING_BIAS
        robot.left_motor.value = max(min(SPEED_GAIN + steering_slider, 1.0), 0.0)
        robot.right_motor.value = max(min(SPEED_GAIN - steering_slider, 1.0), 0.0)
    
while True:
    img = camera.value
    robot_stop = False
    msg = "Start..."
    move_bot(img, robot_stop)