from pprint import pprint
import os
import cv2
from PIL import Image
import matplotlib.pyplot as plt
from deepface.detectors import FaceDetector
from deepface import DeepFace
import json
import numpy as np

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def extract_faces(img_path: str):
    detector_name = 'retinaface'
    detector = FaceDetector.build_model('retinaface')
    img = cv2.imread(img_path)
    fname = img_path.split('/')[-1][:-4]
    faces = FaceDetector.detect_faces(detector, detector_name, img)
    for (i, face) in enumerate(faces):
        result = DeepFace.analyze(face[0], enforce_detection=False, actions=['emotion'])
        np.save(f'/home/danila/hindex/faces/F_{fname}_{i}', face[0])
        with open(f'/home/danila/hindex/predictions/F_{fname}_{i}', 'w+') as f:
            json.dump(result, f)
    return faces



def predict(faces):
    results = []
    for face in faces:
        result = DeepFace.analyze(face[0], enforce_detection=False, actions=['emotion'])
        results.append(result)
    return results


def process_single_image(path: str):
    extract_faces(path)


def batch_process(paths: list):
    for path in paths:
        process_single_image(path)

def process_directory(directory):
    files = [os.path.abspath(os.path.join(directory, p)) for p in os.listdir(directory)]
    return batch_process(files, directory)


def visualize(results):
    for fentry in results:
        print("===========================")
        print("Filename: ", fentry['img'])
        for index, face in enumerate(fentry['faces']):
            img = Image.fromarray(face[0])
            plt.imshow(img)
            plt.show()
            print(f"Dominant emotion: {fentry['predicts'][index]['dominant_emotion']}")
            print('Probability vector')
            pprint(fentry['predicts'][index]['emotion'])
