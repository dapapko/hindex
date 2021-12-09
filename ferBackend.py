from fer import FER
from fer import Video
import cv2

class FERBackend():
    def __init__(self, path):
        self.path = path
        self.__output__ = {}

    def exec(self):
        img = cv2.imread(self.path)
        detector = FER()
        output = detector.detect_emotions(img)
        print(output)
        o = dict()
        if len(output) == 0:
              print("Try again. Face not found")
              return
        o['happy'] = float(output[0]['emotions']['happy'])
        o['sad'] = float(output[0]['emotions']['sad'])
        o['surprise'] = float(output[0]['emotions']['surprise'])
        o['neutral'] = float(output[0]['emotions']['neutral'])
        o['angry'] = float(output[0]['emotions']['angry'])
        o['disgust'] = float(output[0]['emotions']['disgust'])
        o['fear'] = float(output[0]['emotions']['fear'])
        self.__output__ = o    

    def exec_video(self):
        video = Video(self.path)
        detector = FER(mtcnn=True)
        output = video.analyze(detector, display=True)
        self.__output__ = output
    
    def output(self):
        return self.__output__        
