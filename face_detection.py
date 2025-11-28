import face_recognition
import cv2
import numpy as np
import csv
import os
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import pickle


username = ""
facedetected = False

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db



cred = credentials.Certificate("E:/coding/PBL/serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': "https://checking-attendance-default-rtdb.firebaseio.com/",
    'storageBucket' : "checking-attendance.appspot.com"
})


def Start():
    global facedetected
    global username

    ######### Import encoded file ###########
    file = open("Encodefile.p", "rb")
    encodedFile = pickle.load(file)
    file.close()
    known_face_encoding, known_faces_names = encodedFile


    students = known_faces_names.copy()
    counter = 0
    face_locations = []
    face_encodings = []
    face_names = []
    s = True

    cap = cv2.VideoCapture(0)

    while (facedetected == False):
        ret, frame = cap.read()
        rgb_frame = frame[:, :, ::-1]
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]

        if s:
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            face_names = []
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(known_face_encoding, face_encoding)
                name = ""
                face_distance = face_recognition.face_distance(known_face_encoding, face_encoding)
                best_match_index = np.argmin(face_distance)
                if matches[best_match_index]:
                    name = known_faces_names[best_match_index]

                face_names.append(name)
                if name in known_faces_names:
                    username = name
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    bottomLeftCornerOfText = (10, 100)
                    fontScale = 1.5
                    fontColor = (255, 0, 0)
                    thickness = 3
                    lineType = 2

                    #print(name + "Present")
                    cv2.putText(frame, name,
                                bottomLeftCornerOfText,
                                font,
                                fontScale,
                                fontColor,
                                thickness,
                                lineType)

                    if name in students:
                        students.remove(name)
                        #print(students)
                        if counter == 0:
                            counter = 1
                    
                    facedetected = True

            # if counter != 0:
            #     if counter == 1:
            #         studentsInfo = db.reference(f'Students/{name}').get()
            #         #print(studentsInfo)

        cv2.imshow("attendance system", frame)
        cv2.setWindowProperty("attendance system", cv2.WND_PROP_TOPMOST, 1)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    return username


### START ###
Start()