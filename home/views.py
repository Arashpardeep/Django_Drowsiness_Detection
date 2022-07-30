# from email.message import EmailMessage
import sys
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from Drowsiness_Detection_System import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
# from . tokens import generate_token
# from subprocess import run, PIPE
import cv2
import tensorflow as tf
from tensorflow.keras.models import load_model
import numpy as np 
from pygame import mixer


# Create your views here.
def signin(request):
    if not request.user.is_authenticated:

        if request.method == 'POST':
            username = request.POST['username']
            pass1 = request.POST['pass1']
            user = authenticate(username = username, password = pass1)

            if user is not None:
                login(request, user)
                fname = user.first_name
                messages.success(request, f"You are logged in successfully as {username}")
                request.session['username'] = True
                return render(request, 'home.html', {'username':username})
            else:
                messages.error(request, "Wrong Credentials")
                return redirect('signin')

        return render(request, 'login.html')

    else:
        messages.error(request, "You are already logged in")
        return redirect('index')

def Signup(request):
    if request.method == "POST":    
        username = request.POST['username'] 
        fname = request.POST['fname'] 
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if User.objects.filter(username = username):
            messages.error(request, "Username already exist! Please try some other username")
            return redirect('signup')

        if User.objects.filter(email = email):
            messages.error(request, "Email already registered! Please login to your account!")
            return render(request, 'login.html')

        if len(username)>15:
            messages.error(request, "Username must be under 15 characters")
            return redirect('signup')

        if pass1 != pass2:
            messages.error(request, "Passwords didn't match")
            return redirect('signup')

        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric!")
            return redirect('signup')

        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.save()
        messages.success(request, "Your account has been successfully created!")

        # Welcome Email
        # subject = "Welcome to our Drowsiness Detection System site"
        # message = "Hello " + myuser.username + "!! \n" + "Welcome to Drowsiness Detection System!! \n Thanks for visiting our website.\n We have also sent you a confirmation email, please confirm your email address in order to activate your account\n\n Have a nice day!!"
        # from_email = settings.EMAIL_HOST_USER
        # to_list = [myuser.email]
        # send_mail(subject, message, from_email, to_list, fail_silently = True)

        # # Email Adress Confirmation Email
        # current_site = get_current_site(request)
        # email_subject = "Confirm your Email @ Drowsiness Detection System - Login!!"
        # message2 = render_to_string('email_confirmation.html', {
        #     'name': myuser.first_name,
        #     'domain': current_site.domain,
        #     'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
        #     'token': generate_token.make_token(myuser)
        # })
        # email = EmailMessage(
        #     email_subject, 
        #     message2,
        #     settings.EMAIL_HOST_USER,
        #     [myuser.email],
        # )
        # email.fail_silently = True
        # email.send()

        return redirect('signin') 

    return render(request, 'Signup.html')

def signout(request):
    logout(request)
    messages.success(request, "Logged Out successfully!")
    return redirect('signin')

def index(request):
    myuser = request.user
    username = myuser.username
    if request.user.is_authenticated:
        return render(request, 'home.html', {'username':username})
    else:
        messages.error(request, "Anonymous users are not allowed to enter into the website! Please do login first")
        return redirect('signin')

def statistics(request):
    myuser = request.user
    username = myuser.username
    return render(request, 'Statistics.html', {'username':username})

def working(request):
    myuser = request.user
    username = myuser.username
    return render(request, 'Working.html', {'username':username})

def profile(request):
    myuser = request.user
    username = myuser.username
    fname = myuser.first_name
    lname = myuser.last_name
    email = myuser.email
    return render(request, 'profile.html', {'username':username, 'fname':fname, 'lname': lname, 'email': email})

# def activate(request, uid64, token):
#     try:
#         uid = force_str(urlsafe_base64_decode(uid64))
#         myuser = User.objects.get(pk = uid)
#     except (TypeError, ValueError, OverflowError, User.DoesNotExist):
#         myuser = None

#     if myuser is not None and generate_token.check_token(myuser, token):
#         myuser.is_active = True
#         myuser.save()
#         login(request, myuser)
#         return redirect('index')
#     else:
#         return render(request, 'activation_failed.html')

def webcam(request):
    myuser = request.user
    username = myuser.username
    # out = run(sys.executable, ['C:\\Capstone_django-version\\Drowsiness_Detection_System\\templates\\main_drowsiness.py'], shell = False, stdout=PIPE)
    # print(out)
    # return render(request, 'home.html', {'data': out.stdout})

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
    model = load_model(r'C:\\Capstone_django-version\\Drowsiness_Detection_System\\templates\\models\\model.h5')

    mixer.init()
    sound = mixer.Sound(r'C:\\Capstone_django-version\\Drowsiness_Detection_System\\templates\\alarm.wav')
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

    return render(request, 'home.html', {'username':username})
