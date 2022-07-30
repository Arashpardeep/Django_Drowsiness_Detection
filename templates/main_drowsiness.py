import cv2
import tensorflow as tf
from tensorflow.keras.models import load_model
import numpy as np 
from pygame import mixer

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
model = load_model(r'D:\Capstone_2022\models\model.h5')

mixer.init()
sound = mixer.Sound(r'D:\Capstone_2022\alarm.wav')
cap = cv2.VideoCapture(0)
score = 0 
while True:
    ret, frame = cap.read()
    height, width = frame.shape[0:2]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor = 1.2, minNeighbors = 3)
    eyes = eye_cascade.detectMultiScale(gray, scaleFactor = 1.1, minNeighbors = 1)
    
    cv2.rectangle(frame, (0, height-50), (200, height), (0, 0, 0), thickness = cv2.FILLED)
    
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, pt1 = (x, y), pt2 = (x+w, y+h), color = (0, 255, 0), thickness = 3)
    
    for (ex, ey, ew, eh) in eyes:
        cv2.rectangle(frame, pt1 = (ex, ey), pt2 = (ex+ew, ey+eh), color = (0, 255, 255), thickness = 3)
        eye = frame[ey:ey+eh, ex:ex+ew]
        eye = cv2.resize(eye, (80, 80))
        eye = eye/255
        eye = eye.reshape(80, 80, 3)
        eye = np.expand_dims(eye, axis = 0)
        prediction = model.predict(eye)
        
        if prediction[0][0] > 0.40:
            cv2.putText(frame, 'Closed', (10, height-20), fontFace = cv2.FONT_HERSHEY_COMPLEX_SMALL, fontScale = 1, 
                        color = (255, 255, 255), thickness = 1, lineType = cv2.LINE_AA)
            cv2.putText(frame, 'Score'+str(score), (100, height-20), fontFace = cv2.FONT_HERSHEY_COMPLEX_SMALL, fontScale = 1, 
                        color = (255, 255, 255), thickness = 1)
            score = score + 1
            if(score > 30):
#                 try:
                sound.play()
                if(score > 40):
                    score = 35
            elif(score < 30):
                sound.stop()
#                 except:
#                     pass
        
        elif prediction[0][1] > 0.80:
            cv2.putText(frame, 'Open', (10, height-20), fontFace = cv2.FONT_HERSHEY_COMPLEX_SMALL, fontScale = 1, 
                        color = (255, 255, 255), thickness = 1, lineType = cv2.LINE_AA)
            cv2.putText(frame, 'Score'+str(score), (100, height-20), fontFace = cv2.FONT_HERSHEY_COMPLEX_SMALL, fontScale = 1, 
                        color = (255, 255, 255), thickness = 1)
            score = score - 1
            if(score < 0):
                score = 0
    
    cv2.imshow('frame', frame)
    if cv2.waitKey(33) & 0xFF==ord('q'):
        break
        
cap.release()
cv2.destroyAllWindows()