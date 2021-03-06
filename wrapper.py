from params import *
import numpy as np
import cv2
import random
import os
import json
import time
import gym
import tensorflow as tf
from tensorflow.keras.initializers import VarianceScaling
from tensorflow. keras.layers import Add, Dense, Flatten, Input, Conv2D, Lambda, Subtract
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from network import build_q_network, process_frame

class GameWrapper:
    def __init__(self, env_name, no_op_steps=10, history_length=4):
        self.env = gym.make(env_name)
        self.no_op_steps = no_op_steps
        self.history_length = 4

        self.state = None
        self.last_lives = 0

    def reset(self, evaluation=False):

        self.frame = self.env.reset()
        self.last_lives = 0

        if evaluation:
            for _ in range(random.randint(0, self.no_op_steps)):
                self.env.step(1)

        self.state = np.repeat(process_frame(self.frame), self.history_length, axis=2)

    def step(self, action, render_mode=None):
        new_frame, reward, terminal, info = self.env.step(action)

        if info['ale.lives'] < self.last_lives:
            life_lost = True
        else:
            life_lost = terminal
        self.last_lives = info['ale.lives']

        processed_frame = process_frame(new_frame)
        self.state = np.append(self.state[:, :, 1:], processed_frame, axis=2)

        if render_mode == 'rgb_array':
            return processed_frame, reward, terminal, life_lost, self.env.render(render_mode)
        elif render_mode == 'human':
            self.env.render()

        return processed_frame, reward, terminal, life_lost