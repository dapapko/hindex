from deepface import DeepFace

import cv2

class FERBackend():
    def __init__(self, path, db_path=''):
        self.path = path
        self.__output__ = {}
        self.db_path = db_path

    def exec(self):
        self.__output__ = DeepFace.analyze(img_path = self.path, actions = ['emotion'])

    def exec_stream(self):
      DeepFace.stream(db_path = self.db_path)
    