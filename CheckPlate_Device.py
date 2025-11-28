import cv2
import firebase_admin
from firebase_admin import credentials, storage
from firebase_admin import db
import firebase_admin
import time
import board
import busio
from digitalio import DigitalInOut, Direction
import adafruit_fingerprint
import serial
import random
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import font
import cv2
import numpy as np
from datetime import datetime

studentID = ""
studentFID = ""
username = ""
fingerIndex = ""

complete_checking = False
data = ""

# Load the pre-trained Haar cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml')

cred = credentials.Certificate("E:\coding\PBL/serviceAccountKey.json")
# cred = credentials.Certificate("E:/coding/PBL/serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
   'databaseURL': "https://checking-attendance-default-rtdb.firebaseio.com/",
   'storageBucket': "checking-attendance.appspot.com"
})


uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)
finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)






##################################################################### Menu ####################################################################################






def startMainMenu():
    def on_Register_click():
        global data, complete_checking
        data = ""
        complete_checking = False
        root.destroy()
        registerMain()

    def attendance_check():
        global facedetected
        root.destroy()
        facedetected = False
        Facedetection()

    root = tk.Tk()
    root.geometry("1920x1080")
    root.title("Checkmate Main menu")  # Set the window title

    # Background image
    background_img = Image.open("E:\coding\PBL/Resource/background.png")
    #background_img = Image.open("E:\coding\PBL\Resource\Background.png")
    background_img = background_img.resize((1920 ,1080))  # Adjust the size to match the window
    background_img = ImageTk.PhotoImage(background_img)
    background_label = tk.Label(root, image=background_img)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)


    # Custom font
    custom_font = font.Font(family="Luxora Grotesk", size=18, weight="normal")


    # Navigation bar frame
    navbar_frame = tk.Frame(root, bg="#f8f8f6")
    navbar_frame.pack(side=tk.TOP, fill=tk.X, ipady=8)


    # Logo
    logo_img = Image.open("E:\coding\PBL\Resource/checkmate_new_black_vector.png")
    #logo_img = Image.open("E:\coding\PBL\Resource\checkmate_new_black_vector.png")
    logo_img = logo_img.resize((60, 60))  # Adjust the size asqq needed
    logo_img = ImageTk.PhotoImage(logo_img)
    logo_label = tk.Label(navbar_frame, image=logo_img, borderwidth=0, relief="flat")
    logo_label.pack(side=tk.LEFT, padx= 15)

    # Buttons
    button1 = tk.Button(navbar_frame, text="REGISTER", command=on_Register_click, bg="#f8f8f6", bd=0, font=custom_font,fg = "#000000")
    button1.pack(side=tk.RIGHT, padx=50)
    button2 = tk.Button(navbar_frame, text="ATTENDANCE CHECK", command=attendance_check, bg="#f8f8f6", bd=0, font=custom_font,fg = "#000000")
    button2.pack(side=tk.RIGHT, padx=0)

    root.mainloop()






##################################################################### ATTENDANCE ####################################################################################




def Facedetection():
    global username, studentID, studentRFID, facedetected, username_label, studentID_label, retake_button, username_font, guide_label, capture_button, done_button

    def on_Register_click():
        ##stop working thread ##
        global data, complete_checking
        complete_checking = False
        root.destroy()
        #registerMain()

    def attendance_check():
        retake()

    def retake():
        try:
            global facedetected, username_label, studentID_label, retake_button, done_button
            facedetected = False
            username_label.destroy()
            studentID_label.destroy()
            retake_button.destroy()
            done_button.destroy()
            guide_label.destroy()
            display_camera()




        except:
            facedetected = False
            display_camera()


    def mainMenu():
        root.destroy()
        startMainMenu()


    def next():
        global guide_label, done_button, retake_button, username_label, studentID_label, studentID
        guide_label.destroy()
        done_button.destroy()
        retake_button.destroy()
        username_label.destroy()
        studentID_label.destroy()
        root.update()
        guide_label = tk.Label(root, text=" Please place your finger on the scanner ", font=username_font, fg="#29201B", relief=tk.SOLID)
        guide_label.configure(highlightbackground="#29201B", highlightcolor="#29201B", highlightthickness=1)
        guide_label.place(relx=0.7, rely=0.45, anchor=tk.CENTER)
        root.update()


        value = finger_Identification()
        if value:
            attendanceTime = datetime.now().strftime("%H:%M:%S")
            guide_label.destroy()
            root.update()
            guide_label = tk.Label(root, text=f"        Scanning COMPLETE      \n {username} \n has entered at {attendanceTime}",font=username_font, fg="#29201B", relief=tk.SOLID)
            guide_label.configure(highlightbackground="#29201B", highlightcolor="#29201B", highlightthickness=1)
            guide_label.place(relx=0.7, rely=0.45, anchor=tk.CENTER)


            ### Update info to output DB ###
            output_ref = db.reference("Outputs")
            current_datetime = datetime.now()
            registeration_Date = current_datetime.strftime('%d-%m-%Y')
            registeration_Month = int(current_datetime.strftime('%m'))
            output_data = {

                            registeration_Date : {
                                "Username" : f"{studentID}@kmitl.ac.th",
                                "Status" : "Present",
                                "Month": registeration_Month
                            }
                        }
            output_ref.update(output_data)

            root.update()
            mainmenu_button = tk.Button(root, text=" Done ", command=mainMenu, font=username_font, bd=0, fg="#9bc05a", bg="#eae9e9")
            mainmenu_button.place(relx=0.7, rely=0.75, anchor=tk.CENTER)
            root.update()




        elif value == False:
            guide_label.destroy()
            root.update()
            guide_label = tk.Label(root, text=f"Fingerprint does not match with \n {username}", font=username_font, fg="#29201B", relief=tk.SOLID)
            guide_label.configure(highlightbackground="#29201B", highlightcolor="#29201B", highlightthickness=1)
            guide_label.place(relx=0.7, rely=0.45, anchor=tk.CENTER)
            root.update()




            ##delay
            root.after(2500, guide_label.destroy())




            guide_label = tk.Label(root, text=" Please place your finger on the scanner ", font=username_font, fg="#29201B", relief=tk.SOLID)
            guide_label.configure(highlightbackground="#29201B", highlightcolor="#29201B", highlightthickness=1)
            guide_label.place(relx=0.7, rely=0.55, anchor=tk.CENTER)
            root.update()
            finger_Identification()


    #### new function ####
    def readDB():
        global studentID, username, studentFID, retake_button, done_button
        print("reading DB of", username)
        # Online database
        faceinfo = db.reference(f'/Identification_Queue/device1').get()
        username = str(faceinfo['username'])
        studentFID = str(faceinfo['FID'])
       
        #delete device1
        faceinfo = db.reference(f'/Identification_Queue/device1')
        faceinfo.delete()


        studentinfo = db.reference(f'/Students/{username}').get()
        studentID = str(studentinfo['ID'])
        print(f"{username}: {studentFID}")
        displayName(username, studentID)
        retake_button = tk.Button(root, text="Not you?", command=retake, font=username_font, bd=0, fg="#BA0000", bg="#eae9e9")
        retake_button.place(relx=0.6, rely=0.85, anchor=tk.CENTER)
        done_button = tk.Button(root, text=" Next ", command=next, font=username_font, bd=0, fg="#9bc05a", bg="#eae9e9")
        done_button.place(relx=0.8, rely=0.85, anchor=tk.CENTER)


       
   
    def finger_Identification():
        global studentID, username, studentFID, guide_label
        def get_fingerprint():
            """Get a finger print image, template it, and see if it matches!"""
            print("Waiting for image...")
            while finger.get_image() != adafruit_fingerprint.OK:
                pass
            print("Templating...")
            if finger.image_2_tz(1) != adafruit_fingerprint.OK:
                return False
            print("Searching...")
            if finger.finger_search() != adafruit_fingerprint.OK:
                return False
            return True




        # Main loop for fingerprint identification
        print("----------------")
        while True:
            if finger.read_templates() != adafruit_fingerprint.OK:
                raise RuntimeError("Failed to read templates")
            print("Fingerprint templates:", finger.templates)
            if get_fingerprint():
                print("Detected #", finger.finger_id, "with confidence", finger.confidence)
                if (str(finger.finger_id) == str(studentFID)):
                    print(f"usermatch welcome {username}: {studentID}")
                    return True








                else:
                    print("fingerprint doesn't match")
                return False
            else:
                print("Finger not found")
                guide_label = tk.Label(root, text=f"Fingerprint not found \n please place your finger on the scanner again", font=username_font, fg="#29201B", relief=tk.SOLID)
                guide_label.configure(highlightbackground="#29201B", highlightcolor="#29201B", highlightthickness=1)
                guide_label.place(relx=0.7, rely=0.55, anchor=tk.CENTER)
                root.update()
                get_fingerprint()
   








    def display_camera():
            global guide_label, capture_button, username_label,studentID_label, username
            guide_label.destroy()
            guide_label = tk.Label(root, text=" Please look at the camera \nfor face detection", font=username_font, fg="#29201B", relief=tk.SOLID)
            guide_label.configure(highlightbackground="#29201B", highlightcolor="#29201B", highlightthickness=1)
            guide_label.place(relx=0.7, rely=0.5, anchor=tk.CENTER)


            capture_button.destroy()
            #root.update()




            cap = cv2.VideoCapture(0)  # Set the camera index to 0 for the default camera




            # Create a label to hold the video feed
            camera_label = tk.Label(root)
            camera_label.place(x=100, y=100)




############################################## problem ###########################################
           
            def update_frame():
                global username, facedetected, studentID, retake_button, username_label, studentID_label


                ret, frame = cap.read()




                if not ret:
                    # Error capturing frame from the camera
                    print("Error capturing frame from the camera.")
                    return username




                if not facedetected:




                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)




                    for (x, y, w, h) in faces:
                        # Save the face image
                        facedetected = True
                        face_img = frame[y:y+h, x:x+w]
                        cv2.imwrite("E:\coding\PBL/Resource/device1.png", face_img)

                        # Upload the image to Firebase Storage
                        bucket = storage.bucket()
                        blob = bucket.blob("Identify_List/device1.png")
                        blob.upload_from_filename("E:\coding\PBL/Resource/device1.png")








                        # Draw rectangles around the detected faces
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)




                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
                frame = Image.fromarray(frame)
                frame = frame.resize((570, 675))  # Adjust the size as needed
                frame = ImageTk.PhotoImage(frame)
                camera_label.configure(image=frame,padx = 80)
                camera_label.image = frame




                camera_label.after(10, update_frame)  # Update every 10 milliseconds
                if facedetected:
                    faceDetected()
                    cap.release()  # Release the camera capture




############################################################################################################################################
            if not facedetected:
                update_frame()


    def faceDetected():
        global username_label, guide_label, studentID_label, username, facedetected, studentID, retake_button, done_button

        guide_label.destroy()
        # Name
        username_label = tk.Label(root, text="Processing Face...", font=username_font, fg="#29201B", bg="#f7f4f1")
        username_label.place(relx=0.7, rely=0.45, anchor=tk.CENTER)
        studentID_label = tk.Label(root, text="", font=username_font, fg="#29201B", bg="#f7f4f1")
        studentID_label.place(relx=0.7, rely=0.55, anchor=tk.CENTER)

        root.after(5000, readDB)
        #displayName(username, studentID)






    def displayName(username, studentID):
        global username_label, studentID_label, guide_label
        username_label.destroy()
        studentID_label.destroy()
        username_label = tk.Label(root, text="Name: " + username, font=username_font, fg="#29201B", bg="#f7f4f1")
        username_label.place(relx=0.7, rely=0.45, anchor=tk.CENTER)
        studentID_label = tk.Label(root, text="Student's ID: " + studentID, font=username_font, fg="#29201B", bg="#f7f4f1")
        studentID_label.place(relx=0.7, rely=0.55, anchor=tk.CENTER)






    root = tk.Tk()
    root.geometry("1920x1080")
   
    root.title("Attendance Checking")  # Set the window title
    root.configure(bg="#f7f4f1")  # Set the background color




    # Background
    background_label = tk.Label(root, bg="#f8f8f6")
    background_label.place(x=0, y=0, relwidth=1, relheight=1)




    # Custom font
    username_font = font.Font(family="Luxora Grotesk", size=31, weight="normal")
    custom_font = font.Font(family="Luxora Grotesk", size=18, weight="normal")






    capture_button = tk.Button(root, text="Capture", command=display_camera, font=username_font, bd=0, fg="#000000", bg="#f8f8f6")
    capture_button.place(relx=0.2, rely=0.85, anchor=tk.CENTER)


    # Navigation bar frame
    navbar_frame = tk.Frame(root, bg="#f8f8f6")
    navbar_frame.pack(side=tk.TOP, fill=tk.X, ipady=8)


    # Logo
    logo_img = Image.open("E:\coding\PBL\Resource/checkmate_new_black_vector.png")
    logo_img = logo_img.resize((60, 60))  # Adjust the size asqq needed
    logo_img = ImageTk.PhotoImage(logo_img)
    logo_label = tk.Label(navbar_frame, image=logo_img, borderwidth=0, relief="flat")
    logo_label.pack(side=tk.LEFT, padx= 15)



    # No image
    random_img = random.randint(1, 6)
    no_img = Image.open(f"E:\coding\PBL/Resource/capture.png")
    no_img = no_img.resize((570, 675))
    no_img = ImageTk.PhotoImage(no_img)




    placeholder_label = tk.Label(root, image=no_img)
    placeholder_label.place(x=100, y=100)




    #Guide Label
    guide_label = tk.Label(root, text=" Press the capture button \nfor face detection", font=username_font, fg="#29201B", relief=tk.SOLID)
    guide_label.configure(highlightbackground="#29201B", highlightcolor="#29201B", highlightthickness=1)
    guide_label.place(relx=0.7, rely=0.5, anchor=tk.CENTER)




    # Buttons
    button1 = tk.Button(navbar_frame, text="Register", command=on_Register_click, bg="#f8f8f6", bd=0, font=custom_font, fg="#adadac")
    button1.pack(side=tk.RIGHT, padx=10)
    button2 = tk.Button(navbar_frame, text="Attendance check", command=attendance_check, bg="#f8f8f6", bd=0, font=custom_font, fg="#000000")
    button2.pack(side=tk.RIGHT, padx=10)




    root.mainloop()




    return studentID








##################################################################### Register ####################################################################################





def registerMain():
    global video_capture, guide_label, username_label, studentID_label, retake_button, done_button, face_detected, capture_button, placeholder_label, referral_entry, register_facedetected, registerCompleted

    registerCompleted = False
    register_facedetected = False

    def attendance_check():
        ##stop working thread ##
        root.destroy()
        Facedetection()


    def register():
        global data, complete_checking
        data = ""
        complete_checking = False
        root.destroy()
        registerMain()


    def retake():
        global video_capture, register_facedetected, guide_label, username_entry, studentID_entry, username_label, studentID_label, retake_button, done_button
        register_facedetected = False
        retake_button.destroy()
        done_button.destroy()
        root.update()

        display_camera()


        #show_video()


    def mainmenu():
        root.destroy()
        startMainMenu()

    def next():
        global fingerIndex, username, guide_label, done_button, retake_button

        done_button.destroy()
        retake_button.destroy()

        #get existed FID
        try:
            studentFID = db.reference(f"Students/{username}").get()
            fingerIndex = int(studentFID['FID'])
        except:
            if fingerIndex == "":
                ## readnumber from index file
                with open('fingerIndex.txt', 'r+') as file:
                    # Read each line in the file
                    for line in file:
                        # Convert each line to an integer and print
                        fingerIndex = int(line.strip())
                    New_fingerIndex = fingerIndex + 1
                    file.write(f"{New_fingerIndex}")
        register_Scanning(fingerIndex)
        
    def register_Scanning(fingerIndex):
        global guide_label, mainmenu_button,username, studentID
        ## Fingerprint scanning ##
        print("FID : ", fingerIndex)
        guide_label = tk.Label(root, text=" Press your finger on the scanner", font=username_font, fg="#29201B", relief=tk.SOLID)
        guide_label.place(relx=0.7, rely=0.5, anchor=tk.CENTER)
        root.update()

        FingerValid = enroll_finger(fingerIndex)

        if FingerValid == True:
            ## register complete ##
            guide_label.destroy()
            root.update()
            guide_label = tk.Label(root, text=" Registeration completed ", font=username_font, fg="#29201B", relief=tk.SOLID)
            guide_label.place(relx=0.7, rely=0.5, anchor=tk.CENTER)
            root.approveimg = Image.open(f"E:\coding\PBL/Resource/approve.png")
            root.approveimg = root.approveimg.resize((575, 680))
            root.approveimg = ImageTk.PhotoImage(root.approveimg)

            placeholder_label = tk.Label(root, image=root.approveimg,borderwidth=0, relief="flat", highlightthickness=0)
            placeholder_label.place(x=100, y=150)
            root.update()
            print("register Complete")

            # Upload the image to Firebase Storage
            bucket = storage.bucket()
            blob = bucket.blob(f"Queue_List/{username}.png")
            blob.upload_from_filename(f"E:\coding\PBL\Registerface\{username}.png")

            register_ref = db.reference(f"Students")
            data = {

                            f"{username}" : {
                                "FID" : fingerIndex
                            }
                        }
            for key, value in data.items():
                register_ref.child(key).update(value)

            mainmenu_button = tk.Button(root, text=" Done ", command=mainmenu, font=username_font, bd=0, fg="#9bc05a", bg="#eae9e9")
            mainmenu_button.place(relx=0.7, rely=0.75, anchor=tk.CENTER)
            root.update()

        else:
            print("Error occure pelase try again")
            root.after(2500, register_Scanning(fingerIndex))
            guide_label.destroy()
            root.update()
            mainmenu_button = tk.Button(root, text=" Done ", command=mainmenu, font=username_font, bd=0, fg="#9bc05a", bg="#eae9e9")
            mainmenu_button.place(relx=0.7, rely=0.75, anchor=tk.CENTER)
            guide_label = tk.Label(root, text=" Registeration completed ", font=username_font, fg="#29201B", relief=tk.SOLID)
            guide_label.place(relx=0.7, rely=0.5, anchor=tk.CENTER)

            root.update()   
            

            
        
    def enroll_finger(location):
        global username, guide_label
        #Take a 2 finger images and template it, then store in 'location
        for fingerimg in range(1, 3):
            if fingerimg == 1:
                print("Place finger on sensor...", end="")
            else:
                print("Place same finger again...", end="")
                guide_label.destroy()
                root.update()
                guide_label = tk.Label(root, text=" Please remove your finger and \n place the same finger again ", font=username_font, fg="#29201B", relief=tk.SOLID)
                guide_label.place(relx=0.7, rely=0.5, anchor=tk.CENTER)
                root.update()
                

            while True:
                i = finger.get_image()
                if i == adafruit_fingerprint.OK:
                    print("Image taken")
                    break
                if i == adafruit_fingerprint.NOFINGER:
                    print(".", end="")
                elif i == adafruit_fingerprint.IMAGEFAIL:
                    print("Imaging error")
                    return False
                else:
                    print("Other error")
                    return False

            print("Templating...", end="")
            i = finger.image_2_tz(fingerimg)
            if i == adafruit_fingerprint.OK:
                print("Templated")
            else:
                if i == adafruit_fingerprint.IMAGEMESS:
                    print("Image too messy")
                elif i == adafruit_fingerprint.FEATUREFAIL:
                    print("Could not identify features")
                elif i == adafruit_fingerprint.INVALIDIMAGE:
                    print("Image invalid")
                else:
                    print("Other error")
                return False

            if fingerimg == 1:
                print("Remove finger")
                time.sleep(1)
                while i != adafruit_fingerprint.NOFINGER:   
                    i = finger.get_image()

        print("Creating model...", end="")
        i = finger.create_model()
        if i == adafruit_fingerprint.OK:
            print("Created")
        else:
            if i == adafruit_fingerprint.ENROLLMISMATCH:
                print("Prints did not match")
            else:
                print("Other error")
            return False

        print("Storing model #%d..." % location, end="")
        i = finger.store_model(location)
        if i == adafruit_fingerprint.OK:
            print("Stored")
        else:
            if i == adafruit_fingerprint.BADLOCATION:
                print("Bad storage location")
            elif i == adafruit_fingerprint.FLASHERR:
                print("Flash storage error")
            else:
                print("Other error")
            return False

        return True

    

    def display_camera():
            global guide_label, capture_button, username_label,studentID_label, username, register_facedetected
            guide_label.destroy()
            guide_label = tk.Label(root, text=" Please look at the camera \nfor face detection", font=username_font, fg="#29201B", relief=tk.SOLID)
            guide_label.configure(highlightbackground="#29201B", highlightcolor="#29201B", highlightthickness=1)
            guide_label.place(relx=0.7, rely=0.5, anchor=tk.CENTER)


            capture_button.destroy()
            #root.update()


            cap = cv2.VideoCapture(0)  # Set the camera index to 0 for the default camera


            # Create a label to hold the video feed
            camera_label = tk.Label(root)
            camera_label.place(x=100, y=150)

           
            def update_frame():
                global username, facedetected, studentID, retake_button, username_label, studentID_label, register_facedetected

                ret, frame = cap.read()


                if not ret:
                    # Error capturing frame from the camera
                    print("Error capturing frame from the camera.")
                    return username


                if not register_facedetected:


                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)


                    for (x, y, w, h) in faces:
                        # Save the face image
                        register_facedetected = True
                        face_img = frame[y:y+h, x:x+w]
                        cv2.imwrite(f"E:\coding\PBL/Registerface/{username}.png", face_img)

                        # Draw rectangles around the detected faces
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)


                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
                frame = Image.fromarray(frame)
                frame = frame.resize((570, 675))  # Adjust the size as needed
                frame = ImageTk.PhotoImage(frame)
                camera_label.configure(image=frame,padx = 80)
                camera_label.image = frame


                camera_label.after(10, update_frame)  # Update every 10 milliseconds
                if register_facedetected:
                    cap.release()  # Release the camera capture
                    faceDetected()
                    

            if not register_facedetected:
                update_frame()




    def faceDetected():
        global username_label, guide_label, studentID_label, username, facedetected, studentID, retake_button, done_button

        root.update()
        guide_label.destroy()
        retake_button = tk.Button(root, text="Not you?", command=retake, font=username_font, bd=0, fg="#BA0000", bg="#eae9e9")
        retake_button.place(relx=0.6, rely=0.85, anchor=tk.CENTER)
        done_button = tk.Button(root, text=" Next ", command=next, font=username_font, bd=0, fg="#9bc05a", bg="#eae9e9")
        done_button.place(relx=0.8, rely=0.85, anchor=tk.CENTER)
        root.update()

        #root.after(5000, readDB)
        ##scan finger next na


   
    def reffered():
        global guide_label, done_button, retake_button,capture_button
        guide_label.destroy()
        done_button.destroy()
        retake_button.destroy()
        

        capture_button = tk.Button(root, text="Capture", command=display_camera, font=username_font, bd=0, fg="#000000", bg="#f8f8f6")
        capture_button.place(relx=0.2, rely=0.85, anchor=tk.CENTER)


        # No image
        root.no_img = Image.open(f"E:\coding\PBL/Resource/capture.png")
        root.no_img = root.no_img.resize((570, 675))
        root.no_img = ImageTk.PhotoImage(root.no_img)



        placeholder_label = tk.Label(root, image=root.no_img,borderwidth=0, relief="flat", highlightthickness=0)
        placeholder_label.place(x=100, y=150)


        #Guide Label
        guide_label = tk.Label(root, text=" Press the capture button \nfor face detection", font=username_font, fg="#29201B", relief=tk.SOLID)
        #guide_label.configure(highlightbackground="#29201B", highlightcolor="#29201B", highlightthickness=1)
        guide_label.place(relx=0.7, rely=0.5, anchor=tk.CENTER)


    def find_student_by_referral_code(referral_code):
        global username, studentID
        try:
            # Reference to the 'Students' node in the database
            ref = db.reference('Students')


            # Query for the student with the specified referral code
            query = ref.order_by_child('ReferralCode').equal_to(referral_code).limit_to_first(1)
            result = query.get()


            if result:
                # The result is a dictionary where the key is the student's username
                DBusername = list(result.keys())[0]
                student_details = result[DBusername]


                studentID = student_details.get("ID")
                username = DBusername
                return True
            else:
                return False


        except Exception as e:
            return str(e)
   
    def referCheck():
        global guide_label, done_button, retake_button,username_label, studentID_label
        referral_code = referral_entry.get()
        valid_refer = find_student_by_referral_code(referral_code)


        if valid_refer:
            guide_label.destroy()
            referral_entry.destroy()
            check_button.destroy()
            root.update()


            username_label = tk.Label(root, text=f"Name: {username}", font=username_font, fg="#29201B", bg="#f8f8f6")
            username_label.place(relx=0.632, rely=0.3, anchor=tk.CENTER)
            studentID_label = tk.Label(root, text=f"Student ID: {studentID}", font=username_font, fg="#29201B", bg="#f8f8f6")
            studentID_label.place(relx=0.6, rely=0.38, anchor=tk.CENTER)
            retake_button = tk.Button(root, text="Not you?", command=register, font=username_font, bd=0, fg="#BA0000", bg="#eae9e9")
            retake_button.place(relx=0.6, rely=0.85, anchor=tk.CENTER)
            done_button = tk.Button(root, text=" Next ", command=reffered, font=username_font, bd=0, fg="#9bc05a", bg="#eae9e9")
            done_button.place(relx=0.8, rely=0.85, anchor=tk.CENTER)
            root.update()


        else:
            guide_label.destroy()
            referral_entry.destroy()
            check_button.destroy()
            root.update()


            guide_label = tk.Label(root, text=" Invalid referral code, please enter again", font=username_font, fg="#29201B", relief=tk.SOLID)
            #guide_label.configure(highlightbackground="#29201B", highlightcolor="#29201B", highlightthickness=1)
            guide_label.place(relx=0.7, rely=0.5, anchor=tk.CENTER)
            root.after(2000, register)


           
    root = tk.Tk()
    root.geometry("1920x1080")


    root.title("Register")
    root.configure(bg="#f7f4f1")


    # Background
    background_label = tk.Label(root, bg="#f8f8f6")
    background_label.place(x=0, y=0, relwidth=1, relheight=1)


    # Navigation bar frame
    navbar_frame = tk.Frame(root, bg="#f8f8f6")
    navbar_frame.pack(side=tk.TOP, fill=tk.X, ipady=8)


    # Custom font
    username_font = font.Font(family="Luxora Grotesk", size=31, weight="normal")
    custom_font = font.Font(family="Luxora Grotesk", size=18, weight="normal")


    #root.logo_img = Image.open("E:/coding/PBL/Resource/checkmate_new_black_vector.png")
    root.logo_img = Image.open("E:\coding\PBL\Resource/checkmate_new_black_vector.png")
    
    root.logo_img = root.logo_img.resize((60, 60))
    root.logo_img = ImageTk.PhotoImage(root.logo_img)


    root.referral_img = Image.open("E:\coding\PBL\Resource/referral.png")
    root.referral_img = root.referral_img.resize((570, 650))
    root.referral_img = ImageTk.PhotoImage(root.referral_img)


    root.searchimg = Image.open("E:\coding\PBL\Resource/search.png")
    root.searchimg = root.searchimg.resize((40, 40))
    root.searchimg = ImageTk.PhotoImage(root.searchimg)
   
    # Logo
    logo_label = tk.Label(navbar_frame, image=root.logo_img, borderwidth=0, relief="flat")
    logo_label.pack(side=tk.LEFT, padx=15)


    # ReferralD
    referral_label = tk.Label(root, image=root.referral_img, borderwidth=0, relief="flat", highlightthickness=0)
    referral_label.place(relx=.2, rely= .45, anchor=tk.CENTER)


    # Guide label
    guide_label = tk.Label(root, text="Insert your referral code here,\n to finish your registration process ",font=username_font, fg="#29201B", relief=tk.SOLID)
    #guide_label.configure(highlightbackground="#29201B", highlightcolor="#29201B", highlightthickness=1)
    guide_label.place(relx=0.7, rely=0.435, anchor=tk.CENTER)


    # Referral code entry
    referral_entry = tk.Entry(root, font=username_font, bg="#ffffff", width=18)
    referral_entry.place(relx=0.7, rely=0.535, anchor=tk.CENTER)


    # Create the button with the image
    check_button = tk.Button(root,image = root.searchimg, borderwidth=0,relief="flat" ,highlightthickness=0, command=referCheck)
    check_button.pack(side=tk.RIGHT, padx=260)


    # Buttons
    button1 = tk.Button(navbar_frame, text="Register", command=register, bg="#f8f8f6", bd=0, font=custom_font, fg="#adadac")
    button1.pack(side=tk.RIGHT, padx=10)
    button2 = tk.Button(navbar_frame, text="Attendance check", command=attendance_check,bg="#f8f8f6", bd=0, font=custom_font, fg="#000000")
    button2.pack(side=tk.RIGHT, padx=10)




startMainMenu()



