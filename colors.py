#!/usr/bin/env python3

import cv2
import numpy as np
import subprocess
from tqdm import tqdm
import ffmpeg
import os

fps = 60
seconds = 2
# frameSize = (720, 720)
frameSize = (2048,)*2
revs = 1/3
spin_rates = [1, 2, 3]
# basically used for antialiasing
shift = 4


if os.path.basename(os.getcwd()) != "colors":
    print("Please run from colors folder only")

dir = 'images'
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
centroid_shift = np.ones((3, 1)) @ centroid.reshape((1, 2))
k = 1.5


def mapper(x, k):
    # maps x (between 0 and 1) to a curve between 0 and 1
    # k determines the curve
    if x <= 0.5:
        assert x >= 0
        return 0.5*np.power(2*x, np.exp(k))
    else:
        return 1-mapper(1-x, k)


def get_colors(seed):
    np.random.seed(seed)
    """tries random colors until adding them up still results in valid color"""
    # repeat = True
    # while repeat:
    #     repeat = False
    #     colors = [[np.random.randint(0, 256) for _ in range(3)] for _ in range(3)]
    #     for i in range(3):
    #         if np.sum([color[i] for color in colors]) >= 256:
    #             repeat = True

    """picks two random colors, and third one is calculated to make sum
    white (or black)"""
    max = 255
    repeat = True
    while repeat:
        repeat = False
        colors = [[np.random.randint(0, max+1) for _ in range(3)] for _ in range(2)]
        for i in range(3):
            if np.sum([color[i] for color in colors]) > max:
                repeat = True

        third = [max - np.sum(color[i] for color in colors) for i in range(3)]
        colors.append(third)

    return colors


def seg_intersect(a1,a2, b1,b2):
    """Note: this function is really buggy"""
    da = a2-a1
    db = b2-b1
    dp = a1-b1

    def perp( a ) :
        b = np.empty_like(a)
        b[0] = -a[1]
        b[1] = a[0]
        return b

    dap = perp(da)
    denom = np.dot( dap, db)
    num = np.dot( dap, dp )
    return (num / denom.astype(float))*db + b1


for i in tqdm(range(20)):
    colors = get_colors(i)
    num_frames = seconds*fps
    angle = 2*np.pi/32
    combined_img = None
    points_list = []
    for j in range(3):
        color = colors[j]
        angle_modded = angle * spin_rates[j]
        rotm = np.array([
            [np.cos(angle_modded), -np.sin(angle_modded)],
            [np.sin(angle_modded), np.cos(angle_modded)]
        ])
        points = (original_points - centroid_shift) @ rotm.T + centroid_shift
        points_list.append(points)

        img = blank_img.copy()
        cv2.fillConvexPoly(img,
            np.around(2**shift * points).astype(np.int32),
            color=color,
            lineType=cv2.LINE_AA,
            shift=shift)
        # cv2.fillConvexPoly(img, np.around(points).astype(np.int32), color=color, lineType=cv2.LINE_AA)

        if combined_img is None:
            combined_img = img
        else:
            combined_img = combined_img + img

    # points = np.array([seg_intersect(
    #     points_list[0][j%3],
    #     points_list[0][(j+1)%3],
    #     points_list[2][(j-1)%3],
    #     points_list[2][j%3]) for j in range(3)])
    #
    # cv2.fillConvexPoly(combined_img,
    #     np.around(2**shift * points).astype(np.int32),
    #     color=(0, 0, 0),
    #     lineType=cv2.LINE_AA,
    #     shift=shift)

    # for point in points:
    #     cv2.circle(combined_img,
    #         np.around(2**shift * point).astype(np.int32),
    #         radius=2**shift * 20,
    #         thickness=cv2.FILLED,
    #         color=(0, 0, 255),
    #         lineType=cv2.LINE_AA,
    #         shift=shift)

    cv2.imwrite(f"{dir}/image_{i}.png", combined_img)

    # import matplotlib.pyplot as plt
    # import matplotlib.image as mpimg
    # img = mpimg.imread("image.png")
    # imgplot = plt.imshow(img)
    # plt.show()
