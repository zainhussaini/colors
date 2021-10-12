import numpy as np
import cv2
from multiprocessing import Pool
from tqdm import tqdm
import subprocess


def show_image(img):
    """Shows an image until you press 'X' to close it"""
    if img.dtype != np.uint8:
        img = img.astype(np.uint8)

    window_name = "image"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    height, width, _ = img.shape
    if height > 1000 or width > 1920:
        new_width = 1920//4*3
        new_height = 1080//4*3
    elif min(height, width) < 600:
        new_width = 600
        new_height = 600
    else:
        new_width = width
        new_height = height

    cv2.resizeWindow('image', new_width, new_height)
    cv2.moveWindow(window_name, (1920-new_width)//2, (1080-new_height)//2)

    while True:
        cv2.imshow(window_name, img)
        keyCode = cv2.waitKey(1)
        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            break
    cv2.destroyAllWindows()


def generate_colors():
    A = np.random.randint(0, 256, (3,))
    B = np.random.randint(0, 256, (3,))
    x = np.minimum(A, B)
    y = np.maximum(A, B) - x
    z = 255 - x - y
    return (x,y,z)


def triangle_coordinates(frame_size, angle_deg):
    angle = np.deg2rad(angle_deg)
    centroid = np.array(frame_size)/2
    a = min(frame_size)/6
    original_points = np.array([
        centroid + np.array([0, -2*a]),
        centroid + np.array([a*np.sqrt(3), a]),
        centroid + np.array([-a*np.sqrt(3), a]),
    ])
    rotm = np.array([
        [np.cos(angle), -np.sin(angle)],
        [np.sin(angle), np.cos(angle)]
    ])
    centroid_shift = np.ones((3, 1)) @ centroid.reshape((1, 2))
    points = (original_points - centroid_shift) @ rotm.T + centroid_shift
    return points


def generate_frame(frame_size_final, scale, colors, angle):
    frame_size = [i*scale for i in frame_size_final]
    base_img = np.zeros((frame_size[1], frame_size[0], 3), np.uint8)

    new_img = base_img.copy()
    for i in range(3):
        points = triangle_coordinates(frame_size, i*angle)
        color = colors[i]

        shift = 2
        new_img += cv2.fillPoly(base_img,
            pts=[np.around(points * 2**shift).astype(np.int)],
            color=color.tolist(),
            lineType=cv2.LINE_8,
            shift=shift)

    new_img = cv2.resize(new_img, frame_size_final, interpolation=cv2.INTER_AREA)
    return new_img


def helper(params):
    return generate_frame(*params)


def main():
    frame_size_final = (1920, 1080)
    scale = 4

    image_width, image_height = frame_size_final
    filepath = f"videos/video_{image_width}x{image_height}.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = 60
    writer = cv2.VideoWriter(filepath, fourcc, fps, (image_width, image_height))

    colors = generate_colors()
    angles = np.arange(0, 120, 0.5)
    params = ((frame_size_final, scale, colors, angle) for angle in angles)

    with Pool() as pool:
        for frame in tqdm(pool.imap(helper, params), total=len(angles)):
            assert frame.dtype == np.uint8
            writer.write(frame)
    writer.release()

    # temppath = "temp.mp4"
    # subprocess.run(f"mv {filepath} {temppath}".split(" "))
    # subprocess.run(f"ffmpeg -an -i {temppath} -vcodec libx264 -pix_fmt yuv420p -profile:v baseline -level 3 {filepath}".split(" "))
    # subprocess.run(f"rm {temppath}".split(" "))

    # subprocess.run(f"mpv {filepath} --fs --loop".split(" "))



if __name__ == '__main__':
    main()