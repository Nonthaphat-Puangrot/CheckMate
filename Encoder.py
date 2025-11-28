import os
import face_recognition
import pickle
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("E:/coding/PBL/serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://checking-attendance-default-rtdb.firebaseio.com/",
    'storageBucket' : "checking-attendance.appspot.com"
})

def encodeNewFace():
     # Function to download an image from Firebase Storage
    def download_image(bucket, image_blob, local_folder):
        image_name = os.path.basename(image_blob.name).replace(".png", "")
        local_image_path = os.path.join(local_folder, f"{image_name}.png")
        image_blob.download_to_filename(local_image_path)
        return local_image_path

    # Load existing encodings and names from the pickle file
    try:
        with open("Encodefile.p", "rb") as file:
            encodedFile = pickle.load(file)
            known_face_encoding, known_faces_names = encodedFile
    except FileNotFoundError:
        # Handle the case when the file doesn't exist yet
        known_face_encoding = []
        known_faces_names = []

    # Load all images from Firebase Storage and save new faces locally
    bucket = storage.bucket()
    blobs = list(bucket.list_blobs(prefix="Queue_List/"))
    for blob in blobs:
        face_name = os.path.basename(blob.name).replace(".png", "")
        if face_name not in known_faces_names:
            try:
                local_image_path = download_image(bucket, blob, "E:/coding/PBL/Photo")
            except Exception as e:
                # Handle the exception (e.g., Firebase Storage connection issue)
                print(f"Failed to download image from Firebase Storage: {e}")
                local_image_path = f"E:/coding/PBL/Photo/{face_name}.png"

            face_image = face_recognition.load_image_file(local_image_path)
            face_encodings = face_recognition.face_encodings(face_image)

            if len(face_encodings) > 0:
                # If at least one face is detected, use the first one
                face_encoding = face_encodings[0]
                known_face_encoding.append(face_encoding)
                known_faces_names.append(face_name)
            else:
                # Handle the case when no faces are detected
                print(f"No face detected in {local_image_path}")

    print("encode finished")

    # Save the updated encodings and names to the pickle file
    with open("Encodefile.p", "wb") as file:
        encodedFile = [known_face_encoding, known_faces_names]
        pickle.dump(encodedFile, file)

    print("file saved")
    

while True:
    encodeNewFace()
