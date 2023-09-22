from flask import Flask, render_template, request,  redirect, url_for, Response
from flask_sqlalchemy import SQLAlchemy
from database_model import db, Account,generate_id, get_date
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import cv2
from deepface import DeepFace



face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml') 
cap = cv2.VideoCapture(0)


app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/users_image'
folder_path = app.config['UPLOAD_FOLDER']



db.init_app(app)





@app.route('/', methods=["POST", "GET"])
def login():

    if request.method == "POST":
        username_login = request.form.get('username_login')
        password_login = request.form.get('password_login')
 
        
        account_data = Account.query.filter_by(name=username_login, password=password_login).first()

        if account_data:
            if account_data.name == username_login and account_data.password == password_login:
                print("Login Success")
                return redirect(url_for('face_recognition'))

            else:
                login_failed = "Incorrect Username or Password"
                return render_template('home.html', login_failed=login_failed)

        else:
            if username_login == "" and password_login == "":
                insert_login_failed = "Please insert the username and password"
                return render_template('home.html', insert_login_failed=insert_login_failed)
        
            login_failed = "Account not found"
            return render_template('home.html', login_failed=login_failed)

    return render_template('home.html')

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get("password")
        confirm_password = request.form.get('confirm_password')
        male_checkbox = request.form.get('male_checkbox')
        female_checkbox = request.form.get('female_checkbox')
        privacy_checkbox = request.form.get('privacy_checkbox')
        choose_file = request.files['choose_file']

        existing_account = Account.query.filter(
            (Account.name == username) | (Account.email == email)
        ).first()
        if existing_account:
            not_created = "Username or Email has been used"
            print(not_created)   
            return render_template("registration_page.html", not_created=not_created)
        
        elif len(username)< 4:
            short_username = "Your username is too short"
            print(short_username)
            return render_template("registration_page.html", short_username=short_username)
        
        elif password != confirm_password:
            not_match = "Password not match"
            print(not_match)
            return render_template("registration_page.html", not_match=not_match)

        elif len(password) < 8:
            not_match = "Password must be more than 8 characters"
            print(not_match)
            return render_template("registration_page.html", not_match=not_match)
        
        elif privacy_checkbox != "yes":
            privacy = "You must accept the privacy statement"
            print(privacy)
            return render_template("registration_page.html", privacy=privacy)
        elif not choose_file:
            
            no_pic = "Chosse a Picture"
            print(no_pic)
            return render_template('registration_page.html', no_pic=no_pic)
            
        else:
            if male_checkbox == 'yes':
                gender = "Male"
            elif female_checkbox == "yes":
                gender = "Female"
            else:
                choose_gender = "You must to choose your gender"
                print(choose_gender)
                return render_template("registration_page.html", choose_gender=choose_gender)
            
            id_created = generate_id() # Generate Id for Users
            date_joined = get_date()
            date_joined = str(date_joined)
           

            

            # Save the uploaded file with its original filename
            pic_file_name = secure_filename(choose_file.filename)
            pic_file_path = os.path.join(app.config['UPLOAD_FOLDER'], pic_file_name) # save file to the folder

            choose_file.save(pic_file_path) #save file

            image = cv2.imread(pic_file_path) # read the file in Chosse_file = pic_name_path
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Detect faces in the image
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            if len(faces) == 0:
                # No faces detected
                os.remove(pic_file_path)  # Remove the file if No face detected
                face_detection_failed = "Face not detected in the uploaded picture"
                print(face_detection_failed)
                return render_template('registration_page.html', face_detection_failed=face_detection_failed)


            print("Picture: FACE DETECTED")
            file_extension = os.path.splitext(pic_file_name)[1]  # Get the file extension
            new_file_name = username # the username == new file name

            # os.rename(current_file_name, new_file_name)
            os.rename(os.path.join(app.config['UPLOAD_FOLDER'], pic_file_name), os.path.join(app.config['UPLOAD_FOLDER'], new_file_name + file_extension)) #Rename the File
            
            pic_file_name = new_file_name+file_extension # make the file to the username

            name_pic = ""
            for i in app.config['UPLOAD_FOLDER']:
                if pic_file_name:
                    name_pic = "Image_File Existing: "
            add_account = Account(id_created=id_created, profile_pic=pic_file_name, name=username, email=email, password=password, gender=gender, date_joined=date_joined,)

            account_created = "Account Created"  
            print("Picture Added")
            print(account_created)
            print(name_pic + pic_file_name)

            ### Add the pic_file_name

            db.session.add(add_account)
            db.session.commit()
            return redirect(url_for('login', account_created=account_created))

                
    return render_template("registration_page.html")



@app.route('/accounts_list')
def accounts_list():
    accounts_list = Account.query.all() 
    return render_template('accounts_list.html', accounts_list=accounts_list)


@app.route('/choose_camera', methods=["POST", "GET"])
def choose_camera():
    global cap

    if request.method == "POST":
        camera1 = request.form.get('camera1')
        camera2 = request.form.get('camera2')

        if camera1 == "yes":
            camera_index = 1  
            print("Using CAMERA 1")
        elif camera2 == "yes":
            camera_index = 2
            print("Using Default CAMERA")

        cap = cv2.VideoCapture(camera_index)

        return redirect(url_for('face_recognition'))

    return render_template('face_recognition.html')


def generate_frames():
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = frame[y:y+h, x:x+w]
 
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()  

            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


@app.route('/camera')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/face_recognition', methods=['GET', 'POST'])
def face_recognition():
    try:
        cv2.VideoCapture(0)
        camera_active = "."
    except:
        cv2.VideoCapture(1)
        camera_active = "."
    
    if request.method == 'POST':

        model_name = "Facenet" 
        verified_face = ""
        name = ""
        date_scan = ""
        face_detected = ""
        not_face_detected = ""
        not_found = "No found"
        print("SCANNING....")

        _,frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)


        if len(faces) == 0: 
            not_face_detected = "No Faces Detected !!!!"
            print(not_face_detected)
            return render_template('face_recognition.html',not_face_detected=not_face_detected)
        else:
            face_detected = "Face Detected !"
            print(face_detected)

            if os.path.exists(folder_path):
                contents = os.listdir(folder_path)
                stop_loop = False
                for item in contents:
                    image_path = os.path.join(folder_path, item)

                    for (x, y, w, h) in faces:
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        roi_gray = gray[y:y + h, x:x + w]
                        roi_color = frame[y:y + h, x:x + w]

                        authentication = DeepFace.verify(frame, image_path, model_name, enforce_detection=False)

                        if authentication['verified']:
                            verified_face = 'FACE MATCH'
                            name = item # name of image file
                            print(f'Match: {name}')
                            print('SCANNING DONE !')
                            stop_loop = True
                            date_scan = get_date()
                            date_scan = str(date_scan)
                        else:
                            name = not_found
                            date_scan = not_found
                            verified_face = "FACE NOT MATCH"
                            print(verified_face)
                    if stop_loop:
                        break
            else:
                print(f"The folder '{folder_path}' does not exist.")
            return render_template('face_recognition.html', verified_face=verified_face, name=name, face_detected=face_detected, date_scan=date_scan)
        
    return render_template('face_recognition.html', camera_active=camera_active)
    




            

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

