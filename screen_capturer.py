from PIL import ImageGrab, Image, ImageChops
import os
import sys
import pickle
from scipy.misc import imread
from scipy import sum, average
import numpy as np
import math


# ----------------------------------------------------------------------------------------------------------------------
# caputure image
# ----------------------------------------------------------------------------------------------------------------------
# for i in range(1000):
#     time.sleep(0.5)
#     im = ImageGrab.grab(bbox=(0,280,405,820))
#     #im = ImageGrab.grab() full screen
#     im.save('screen_shots/screenshot-{}.png'.format(i))
# ----------------------------------------------------------------------------------------------------------------------

class GameController:
    def __init__(self, run_bbox, end_bbox, GAME_START_THRESHOLD):
        self.pic_uuid = 0
        self.run_bbox = run_bbox
        self.end_bbox = end_bbox
        self.GAME_START_THRESHOLD = GAME_START_THRESHOLD

    def _save_screenshot(self, path, bbox):
        im = ImageGrab.grab(bbox=bbox)
        im.save(path)
        self.pic_uuid += 1

    def get_img_feature(self, thin_factor=1, img_compress_ratio=1.0, is_img_save=False):
        im = ImageGrab.grab(bbox=self.run_bbox).convert('1')
        # image resize
        original_size = im.size
        compressed_size = (
            math.floor(img_compress_ratio * original_size[0]), math.floor(img_compress_ratio * original_size[1]))
        # print ("compressed_size: ", compressed_size)
        im = im.resize(compressed_size)
        #
        # print (im)
        arr = np.array(im)
        arr_shape = arr.shape
        arr = 1 * arr.flatten()
        if is_img_save:
            im.save('test.png')
        # im.save('test-{}.png'.format(self.pic_uuid))
        arr = arr[::thin_factor]
        return arr, arr_shape

    def remove_screen_shots(self):
        self.pic_uuid = 0
        clear_folder = 'running_screen_shots'
        file_list = os.listdir(clear_folder)
        for file in file_list:
            file_path = os.path.join(clear_folder, file)
            os.remove(file_path)

    def is_game_start(self, start_img):

        #
        start_pic_path = os.path.join('start_end_shots', start_img)
        #
        screenshot_path = 'running_screen_shots/{}.png'.format(self.pic_uuid)
        self._save_screenshot(screenshot_path, self.run_bbox)
        #

        diff = self._compare_images(start_pic_path, screenshot_path)
        print("diff: {}".format(diff))

        #os.remove(screenshot_path)  # remove file after comparision

        if diff <= self.GAME_START_THRESHOLD:
            return True
        else:
            return False

    def take_start_screen_shots(self):
        """
        Take screen shots in order to get start/end image
        """
        screenshot_path = 'running_screen_shots/{}.png'.format(self.pic_uuid)
        self._save_screenshot(screenshot_path, self.run_bbox)
        self.pic_uuid += 1

    def take_end_screen_shots(self):
        """
        Take screen shots in order to get start/end image
        """
        screenshot_path = 'running_screen_shots/{}.png'.format(self.pic_uuid)
        self._save_screenshot(screenshot_path, self.end_bbox)
        self.pic_uuid += 1

    def is_game_end(self, end_img):

        #
        GAME_END_THRESHOLD = 1.0
        #
        end_pics_folder_path = 'start_end_shots'
        end_pic_path = end_img
        end_pic_path = os.path.join(end_pics_folder_path, end_pic_path)
        #
        path = 'running_screen_shots/{}.png'.format(self.pic_uuid)
        self._save_screenshot(path, self.end_bbox)
        #

        n_m = self._compare_images(end_pic_path, path)
        # print("n_m: {}".format(n_m))

        os.remove(path)  # remove file after comparision

        if n_m <= GAME_END_THRESHOLD:
            return True
        else:
            return False

    def _compare_images(self, img1_path, img2_path):

        def _to_grayscale(arr):
            "If arr is a color image (3D array), convert it to grayscale (2D array)."
            if len(arr.shape) == 3:
                return average(arr, -1)  # average over the last axis (color channels)
            else:
                return arr

        def _normalize(arr):
            rng = arr.max() - arr.min()
            amin = arr.min()
            return (arr - amin) * 255 / rng

        img1 = _to_grayscale(imread(img1_path).astype(float))
        img2 = _to_grayscale(imread(img2_path).astype(float))

        # normalize to compensate for exposure difference
        img1 = _normalize(img1)
        img2 = _normalize(img2)
        # calculate the difference and its norms
        diff = img1 - img2  # elementwise for scipy arrays
        m_norm = sum(abs(diff))  # Manhattan norm
        # z_norm = norm(diff.ravel(), 0)  # Zero norm

        img_size = img1.size
        n_m = m_norm / img_size
        return n_m
