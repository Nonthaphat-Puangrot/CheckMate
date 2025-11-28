import serial
from time import *
from datetime import datetime
import os
import csv
#from face_detection import *
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from Encoder import *
import mysql.connector


### Firebase ###
cred = credentials.Certificate("E:/coding/PBL/serviceAccountKey.json")
# firebase_admin.initialize_app(cred,{
#     'databaseURL': "https://checking-attendance-default-rtdb.firebaseio.com/",
#     'storageBucket' : "checking-attendance.appspot.com"
# })
ref = db.reference('Students')
RFID_match = ""


### MYSQL ###
# mydb = mysql.connector.connect(
#   host="25.3.63.19",
#   user="web",
#   password="",
#   database="pbl" 
# )

# mycursor = mydb.cursor()


### FACE DETECTION ###
#print("Please look at the camera for face detection")

### WRITE OUTPUT TO DB ###
def db_Writing(username, attendanceTime):
    file_path = "E:/coding/PBL/output/"
    os.makedirs(file_path, exist_ok=True)
    current_date = datetime.today().strftime('%d-%m-%Y')
    # Set the output file name
    output_file_name = f"{current_date}.csv"
    file_path_with_name = os.path.join(file_path, output_file_name)
    
    with open(file_path_with_name, 'a', newline='') as f:
        lnwriter = csv.writer(f)
        lnwriter.writerow([username, attendanceTime])

        ###upload to firebase##
        upload_csv_to_firebase_storage(f"E:/coding/PBL/output/{current_date}.csv",f"Outputs/{current_date}.csv")

        ##upload_csv_to_firebase_storage(f"E:/coding/PBL/output/{current_date}.csv",f"Outputs/{current_date}/{username}")


        #output for petch reading
        ref = db.reference(f'Outputs/{current_date}')
        data = {
            f"{username}": {
            "ArrivalTime": f"{attendanceTime}",
            "Name": f"{username}",
            }
        }
                
        for key,value in data.items():
            ref.child(key).set(value)

        ##### OUTPUT to mysql ####
        # sql = "INSERT INTO status (Name, Time, Date) VALUES (%s, %s, %s)"
        # val = (f"{username}", f"{attendanceTime}", f"{current_date}")
        # mycursor.execute(sql, val)
        # mydb.commit()


    ###### Scan RFID #####
def scanRFID(studentRFID, username):
    global RFID_match
    try:
        RFID_match = ""
        Arduino = serial.Serial('COM3', 9600, timeout=1)  # Set the timeout to 1 second

        # Read data from the serial port with a timeout
        while True:
            data = str(Arduino.readline().decode('ascii')).strip()
            print("Serial read:", data)
            if data:
                if studentRFID == data.strip():
                    print("Scanning COMPLETE")
                    attendanceTime = datetime.now().strftime("%H:%M:%S")
                    db_Writing(username, attendanceTime)
                    print(username, "has Entered")
                    print("__________________________________________")
                    RFID_match = True
                    return True  # Exit the loop after successful match
                    

                elif studentRFID != data.strip() and data.strip() != "":
                    print("RFID does not match", username)
                    return False
    except :
        print("error occure while scanning")

# def registerRFID(Registerusername,RegisterstudentID):
#     try:
#         Arduino = serial.Serial('COM3', 9600, timeout=1)  # Set the timeout to 1 second

#         # Read data from the serial port with a timeout
#         while True:
#             data = str(Arduino.readline().decode('ascii')).strip()
#             print("Serial read: ", data)
#             if data != "":
#                 registertoDB(Registerusername,RegisterstudentID, data)
#                 register_complete_event.set()
#                 return True
#     except Exception as e:
#         print("Error:", str(e))
    


### Upload file to DB ###
def upload_csv_to_firebase_storage(file_path, destination_path):
    bucket = storage.bucket()

    blob = bucket.blob(destination_path)
    blob.upload_from_filename(file_path)

    print('File uploaded successfully.')

import os
import csv

def registertoDB(Registerusername, RegisterstudentID, RegisterRFID):
    data = {
        f"{Registerusername}":
        {
            "ID": f"{RegisterstudentID}",
            "RFID": f"{RegisterRFID}",
            "Major": "Computer",
            "Year": "3"
        }
    }

    try:
        # Upload data to Firebase Realtime Database
        for key, value in data.items():
            ref.child(key).set(value)

        # Rename and upload photo to Firebase Storage
        os.rename("E:/coding/PBL/Registerface.png", f"E:/coding/PBL/{Registerusername}.png")
        bucket = storage.bucket()
        filedic = f"E:/coding/PBL/{Registerusername}.png"
        blob = bucket.blob(f"Photo/{Registerusername}.png")
        blob.upload_from_filename(filedic)

        # Remove the file using the correct file path
        os.remove(filedic)
        print("Register complete!!!")

    except Exception as e:
        print("An error occurred during the upload process. Uploading to local file photo and saving data to localDB.csv.")
        try:
            # Upload photo to local directory
            local_photo_path = f"E:/coding/PBL/Photo/{Registerusername}.png"
            os.rename("E:/coding/PBL/Registerface.png", local_photo_path)

            # Save data to localDB.csv
            with open("E:/coding/PBL/localDB.csv", mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([Registerusername, RegisterstudentID, RegisterRFID, "Computer", "3"])

        except Exception as e:
            print("Error occurred while uploading to local files.")
            print(str(e))

# Note: Make sure you have imported the necessary libraries and have initialized the Firebase Realtime Database and Storage before calling the function.

