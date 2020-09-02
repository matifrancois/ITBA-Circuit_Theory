import os

import cv2


class ImageManagement:
    @staticmethod
    def concat_images(imga, imgb):
        im1 = cv2.imread(imga)
        im2 = cv2.imread(imgb)
        return cv2.vconcat([im1, im2])

    @staticmethod
    def get_image_name(folder_path, name):
        i = 1
        if os.path.isfile(folder_path + "/" + name + ".png"):
            while os.path.isfile(folder_path + "/" + name + "(" + str(i) + ").png"):
                i = i + 1
            return folder_path + "/" + name + "(" + str(i) + ").png"
        else:
            return folder_path + "/" + name + ".png"

    @staticmethod
    def save_image(folder_path, image, name):
        i = 1
        if os.path.isfile(folder_path + "/" + name + ".png"):
            while os.path.isfile(folder_path + "/" + name + "(" + str(i) + ").png"):
                i = i + 1
            image.savefig(folder_path + "/" + name + "(" + str(i) + ").png")
            return folder_path + "/" + name + "(" + str(i) + ").png"
        else:
            image.savefig(folder_path + "/" + name + ".png")
            return folder_path + "/" + name + ".png"
