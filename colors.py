#!/usr/bin/env python3

import cv2
import numpy as np
import subprocess
from tqdm import tqdm
import ffmpeg
import os

fps = 60
seconds = 2
frameSize = (720, 720)
revs = 1/3
params = [1, 2, 3]
# https://www.fourcc.org/codecs.php
codec = 'DIVX' # 'MPEG'
# colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
colors = [(0, 127, 127), (127, 0, 127), (127, 127, 0)]

# revs = (1/3)/10
# fps = 120
# seconds = 10*6
# revs = 0.05*6


if os.path.basename(os.getcwd()) != "colors":
    print("Please run from colors folder only")

dir = 'videos'
for f in os.listdir(dir):
    print("deleting", os.path.join(dir, f))
    os.remove(os.path.join(dir, f))


blank_img = np.zeros((frameSize[1], frameSize[0], 3), dtype=np.uint8)
# blank_img.fill(255)
centroid = np.array(frameSize)/2
a = min(frameSize)/6
original_points = np.array([
    centroid + np.array([0, -2*a]),
    centroid + np.array([a*np.sqrt(3), a]),
    centroid + np.array([-a*np.sqrt(3), a]),
])


def mapper(x, k):
    # maps x (between 0 and 1) to a curve between 0 and 1
    # k determines the curve
    if x <= 0.5:
        assert x >= 0
        return 0.5*np.power(2*x, np.exp(k))
    else:
        return 1-mapper(1-x, k)


for i, k in enumerate(np.linspace(0, 4, 10)):
    out = cv2.VideoWriter(os.path.join('videos', f'colors{i}.avi'), cv2.VideoWriter_fourcc(*codec), fps, frameSize)

    centroid_shift = np.ones((3, 1)) @ centroid.reshape((1, 2))
    # basically used for antialiasing
    shift = 4

    num_frames = seconds*fps
    print("num_frames", num_frames)
    for i in tqdm(range(0, num_frames)):
        # angle = 2 * np.pi * revs * i/num_frames
        angle = 2 * np.pi * revs * mapper(i/num_frames, k)
        combined_img = None
        for i in range(3):
            color = colors[i]
            angle_modded = angle * params[i]
            rotm = np.array([
                [np.cos(angle_modded), -np.sin(angle_modded)],
                [np.sin(angle_modded), np.cos(angle_modded)]
            ])
            points = (original_points - centroid_shift) @ rotm.T + centroid_shift

            img = blank_img.copy()
            cv2.fillConvexPoly(img, np.around(2**shift * points).astype(np.int32), color=color, lineType=cv2.LINE_AA, shift=shift)

            if combined_img is None:
                combined_img = img
            else:
                combined_img = combined_img + img

        out.write(combined_img)

    out.release()


out = cv2.VideoWriter(os.path.join('videos', 'blank.avi'), cv2.VideoWriter_fourcc(*codec), fps, frameSize)
for i in tqdm(range(0, num_frames)):
    out.write(blank_img)
out.release()

# subprocess.run(["mpv", os.path.join('videos', 'colors.avi'), '--loop'])
