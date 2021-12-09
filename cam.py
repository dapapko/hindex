import pygame.image, pygame.display, pygame.camera
import sys
import uuid
import requests
from ferBackend import FERBackend

pygame.camera.init()
cameras = pygame.camera.list_cameras()
print ("Using camera %s ..." % cameras[0])
if len(sys.argv) == 1:
   print("You need to specify key")
   sys.exit(1) 
webcam = pygame.camera.Camera(cameras[0])
token = sys.argv[1]
webcam.start()

# grab first frame
img = webcam.get_image()
pygame.image.save(img, "image.jpg")
WIDTH = img.get_width()
HEIGHT = img.get_height()
screen = pygame.display.set_mode( ( WIDTH, HEIGHT ) )
pygame.display.set_caption("pyGame Camera View")

while True :
    # Feed it with events every frame
    events = pygame.event.get()
    for e in events:
        screen.blit(img, (0,0))
        pygame.display.flip()
        img = webcam.get_image()
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_d: sys.exit(1)
            if e.key == pygame.K_w:
                print('Обработка')
                key = str(uuid.uuid4())
                pygame.image.save(img, f"image_{key}.jpg")
                # Not tested yet
                backend = FERBackend(f"image_{key}.jpg")
                backend.exec()
                print(backend.output())
                data = {"key":token, "result":backend.output()}
                r = requests.post('http://localhost:5000/setresult', json=data)
