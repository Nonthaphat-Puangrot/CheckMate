import threading
import time
import firebase_admin
from firebase_admin import credentials, db, storage, initialize_app
import numpy as np
import pickle
import io
from PIL import Image
import face_recognition
import mysql.connector
from datetime import datetime

# Initialize Firebase Admin SDK
cred = credentials.Certificate("E:/coding/PBL/serviceAccountKey.json")
initialize_app(cred, {
    'databaseURL': "https://checking-attendance-default-rtdb.firebaseio.com/",
    'storageBucket': "checking-attendance.appspot.com"
})

username = ""
facedetected = False
imagefile = ""
lock = threading.Lock()

def fetch_images_from_storage(folder_path):
    global imagefile
    bucket = storage.bucket()
    blobs = bucket.list_blobs(prefix=folder_path)

    images = []

    for blob in blobs:
        # Check if the blob is a file (not a folder)
        if "." in blob.name:
            imagefile = blob.name
            print(f"Fetching image: {imagefile}")
            image_bytes = blob.download_as_bytes()
            image_stream = io.BytesIO(image_bytes)
            image_pil = Image.open(image_stream).convert("RGB")
            images.append(np.array(image_pil))

    return images

def encode_faces():
    while True:
        try:
            with open("Encodefile.p", "rb") as file:
                encodedFile = pickle.load(file)
                known_face_encoding, known_faces_names = encodedFile
        except FileNotFoundError:
            known_face_encoding = []
            known_faces_names = []

        bucket = storage.bucket()
        blobs = list(bucket.list_blobs(prefix="Queue_List/"))
        if blobs:
            for blob in blobs:
                face_name = blob.name.split("/")[-1].replace(".png", "")
                if face_name not in known_faces_names:
                    try:
                        image_bytes = blob.download_as_bytes()
                        image_stream = io.BytesIO(image_bytes)
                        face_image = Image.open(image_stream).convert("RGB")
                    except Exception as e:
                        print(f"Failed to download image from Firebase Storage: {e}")
                        continue

                    face_encodings = face_recognition.face_encodings(np.array(face_image))

                    if len(face_encodings) > 0:
                        face_encoding = face_encodings[0]
                        known_face_encoding.append(face_encoding)
                        known_faces_names.append(face_name)
                    else:
                        print(f"No face detected in {blob.name}")

                    blob.delete()
                    print(f"Deleted image: {blob.name}")

            with open("Encodefile.p", "wb") as file:
                encodedFile = [known_face_encoding, known_faces_names]
                pickle.dump(encodedFile, file)

            print("Face encoding finished")
            delete_images_from_storage("Queue_List/")
            print("Deleted from queue list")

        time.sleep(5)  # Adjust sleep duration based on processing time

def face_detection(frame):
    with open("Encodefile.p", "rb") as file:
        encodedFile = pickle.load(file)
    known_face_encoding, known_faces_names = encodedFile

    global username, facedetected

    students = known_faces_names.copy()
    counter = 0
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encoding, face_encoding)
        face_distance = face_recognition.face_distance(known_face_encoding, face_encoding)
        best_match_index = np.argmin(face_distance)

        if matches[best_match_index]:
            name = known_faces_names[best_match_index]

            if name in students:
                students.remove(name)   
                if counter == 0:
                    counter = 1
            print("detecting ", name)
            return name

    return None

def process_identification_queue():
    identification_queue_ref = db.reference('/Identification_Queue')

    while True:
        identify_images = fetch_images_from_storage("Identify_List/")

        if identify_images:
            for image in identify_images:
                try:
                    image_name = imagefile.split("/")[-1]
                    deviceNum = image_name.split(".")[0]

                    username = face_detection(image)
                    
                    if username is None:
                        print(f"No face detected or recognized in image from {deviceNum}")
                        continue
                    
                    studentinfo = db.reference(f'Students/{username}').get()
                    
                    if studentinfo is None:
                        print(f"Student {username} not found in database")
                        continue
                    
                    studentFID = str(studentinfo['FID'])

                    data = {
                        f"{deviceNum}": {
                            "username": username,
                            "FID": studentFID,
                        }
                    }
                    for key, value in data.items():
                        identification_queue_ref.child(key).set(value)
                    
                    print(f"Successfully identified {username} from {deviceNum}")

                except Exception as e:
                    print(f"Error processing image: {e}")
                    continue

            delete_images_from_storage("Identify_List/")

        print("Processing face")
        time.sleep(5)  # Adjust sleep duration based on processing time

def delete_images_from_storage(folder_path):
    global facedetected, username
    bucket = storage.bucket()

    for blob in bucket.list_blobs(prefix=folder_path):
        if "." in blob.name:
            blob.delete()
            print(f"Deleted image: {blob.name}")

    print(username)
    facedetected = False
    username = ""

def insert_data_to_mysql():
    while True:
        try:
            current_datetime = datetime.now()
            registerDate = current_datetime.strftime('%d-%m-%Y')

            output_info = db.reference(f'Outputs/{registerDate}').get()
            
            if output_info:
                print(f"Processing attendance data for {registerDate}")
                email = output_info.get('Username')
                Status = output_info.get('Status')
                Month = output_info.get('Month')

                if email and Status and Month:
                    mydb = mysql.connector.connect(
                        host="25.8.57.205",
                        user="web",
                        password="",  # Password is empty, please ensure it's secure.
                        database="pbl"
                    ) 

                    sql = "INSERT INTO status (Date, Username, Status, Month) VALUES (%s, %s, %s, %s)"
                    val = (registerDate, email, Status, Month)
                    mycursor = mydb.cursor()
                    mycursor.execute(sql, val)
                    mydb.commit()
                    mycursor.close()
                    mydb.close()
                    print(f"Inserted attendance record for {email}")
                else:
                    print("Missing required fields in output data")
            else:
                print(f"No attendance data found for {registerDate}")
        
        except Exception as e:
            print(f"Error inserting data to MySQL: {e}")
        
        time.sleep(10)  # Check for new attendance data every 10 seconds

if __name__ == "__main__":
    encode_thread = threading.Thread(target=encode_faces)
    identify_thread = threading.Thread(target=process_identification_queue)
    mysql_thread = threading.Thread(target=insert_data_to_mysql)

    encode_thread.start()
    identify_thread.start()
    mysql_thread.start()

    encode_thread.join()
    identify_thread.join()
    mysql_thread.join()
    