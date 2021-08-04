#!/usr/bin/env python3

import cv2
import matplotlib.pyplot as plt
import numpy as np
import subprocess
from tqdm import tqdm

fps = 60
seconds = 3
revs = 1/3
# revs = (1/3)/10
# fps = 120
# seconds = 10*6
# revs = 0.05*6


frameSize = (2048,)*2
blank_img = np.zeros((frameSize[0], frameSize[1], 3), dtype=np.uint8)
# blank_img.fill(255)
centroid = np.array(frameSize)/2
a = frameSize[0]/8
original_points = np.array([
    centroid + np.array([0, -2*a]),
    centroid + np.array([a*np.sqrt(3), a]),
    centroid + np.array([-a*np.sqrt(3), a]),
])


out = cv2.VideoWriter(f'videos/colors.avi', cv2.VideoWriter_fourcc(*'DIVX'), fps, frameSize)

centroid_shift = centroid.reshape((2, 1)) @ np.ones((1, 3))
# colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
colors = [(0, 127, 127), (127, 0, 127), (127, 127, 0)]
params = [1, 2, 3]
shift = 4

num_frames = seconds*fps
print("num_frames", num_frames)
for i in tqdm(range(0, num_frames)):
    angle = 2*np.pi*revs*i/num_frames
    combined_img = None
    for i in range(3):
        color = colors[i]
        angle_modded = angle*params[i]
        rotm = np.array([
            [np.cos(angle_modded), -np.sin(angle_modded)],
            [np.sin(angle_modded), np.cos(angle_modded)]
        ])
        points = ((rotm @ (original_points.T - centroid_shift)) + centroid_shift).T

        img = blank_img.copy()
        # cv2.fillConvexPoly(img, points = np.around(points).astype(np.int32), color=color, lineType=cv2.LINE_AA)
        cv2.fillConvexPoly(img, np.around(2**shift * points).astype(np.int32), color=color, lineType=cv2.LINE_AA, shift=shift)
        if combined_img is None:
            combined_img = img
        else:
            combined_img = combined_img + img

    out.write(combined_img)

out.release()

# extensions = ("mp4", "webm")
# extensions = ("mp4",)
# import os
# for extension in extensions:
#     try:
#         os.remove(f'videos/colors.{extension}')
#     except FileNotFoundError:
#         pass
# for extension in extensions:
#     subprocess.run(["ffmpeg", "-i", 'videos/colors.avi', '-an', f'videos/colors.{extension}', '-y'])
# if "mp4" in extensions:
#     subprocess.run(["mpv", 'videos/colors.mp4', '--window-maximized'])

subprocess.run(["mpv", 'videos/colors.avi', '--window-maximized', '--loop'])
