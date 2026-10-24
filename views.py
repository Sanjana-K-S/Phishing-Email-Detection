from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect
from .models import *
from django.db.models import Q
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from datetime import datetime
import datetime as dt
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd

# Create your views here.


def index(request):
    return render(request, "index.html")


def userHeader(request):
    return render(request, "USER/userHeader.html")


def adminHome(request):
    count = UserRegistration.objects.count()
    print(count)
    return render(request, "ADMIN/adminHome.html", {"count": count})


def adminHeader(request):
    return render(request, "ADMIN/adminHeader.html")


def logins(request):
    if request.POST:
        email = request.POST["email"]
        passw = request.POST["password"]
        print(email)
        print(passw)
        user = authenticate(username=email, password=passw)
        print(user)
        if user is not None:
            login(request, user)
            if user.userType == "Admin":
                messages.info(request, "Login Success")
                return redirect("/adminHome")
            elif user.userType == "User":
                id = user.id
                request.session["uid"] = id
                messages.info(request, "Login Success")
                return redirect("/userHome")
        else:
            print("Hiii")
            messages.error(request, "Invalid Username/Password")
    return render(request, "login.html")


def register(request):
    current_date = datetime.today().strftime("%Y-%m-%d")
    print(current_date)
    if request.POST:
        name = request.POST["name"]
        email = request.POST["email"]
        phone = request.POST["phone"]
        dob = request.POST["dob"]
        gender = request.POST["gender"]
        address = request.POST["address"]
        password = request.POST["password"]
        image = request.FILES["image"]
        logUser = Login.objects.create_user(
            username=email,
            password=password,
            userType="User",
            viewPass=password,
            is_active=0,
        )
        logUser.save()

        userReg = UserRegistration.objects.create(
            name=name,
            email=email,
            phone=phone,
            gender=gender,
            address=address,
            dob=dob,
            loginid=logUser,
            image=image,
        )
        userReg.save()
    return render(request, "register.html", {"current_date": current_date})


# **************************ADMIN**************************


def viewUsers(request):
    count = UserRegistration.objects.count()
    print(count)
    userData = UserRegistration.objects.all()
    return render(
        request, "ADMIN/viewUsers.html", {"count": count, "userData": userData}
    )


def blockedUsers(request):
    count = UserRegistration.objects.count()
    print(count)
    blockData = BlockList.objects.all()
    return render(request,"ADMIN/blockedUsers.html",{"blockData":blockData})


def restrictUser(request):
    id=request.GET["id"]
    print(id)
    restrictUser=Login.objects.filter(username=id).update(is_active=0)
    changeStatus=BlockList.objects.filter(blocked_user_id=id).update(status="Restricted")
    return redirect("/blockedUsers")

def allowUser(request):
    id=request.GET["id"]
    allowUser=Login.objects.filter(username=id).update(is_active=1)
    changeStatus=BlockList.objects.filter(blocked_user_id=id).update(status="Blocked")
    return redirect("/blockedUsers")

def manageUser(request):
    id = request.GET["id"]
    status = request.GET["status"]
    abc = Login.objects.get(id=id)
    abc.is_active = int(status)
    abc.save()
    if status == "0":
        messages.success(request, "User Rejected")
    else:
        messages.success(request, "User Approved")
    return redirect("/viewUsers")


def viewFeedbacks(request):
    count = UserRegistration.objects.count()
    print(count)
    feedbackData=Feedback.objects.all()
    return render(request,"ADMIN/viewFeedbacks.html",{"feedbackData":feedbackData,"count":count})

# **************************USER**************************


def userHome(request):
    id = request.session["uid"]
    userData = UserRegistration.objects.get(loginid=id)
    print(userData.image)
    image = userData.image
    return render(request, "USER/userHome.html", {"image": image})


def viewProfile(request):
    id = request.session["uid"]
    print(id)
    userData = UserRegistration.objects.filter(loginid=id)
    print(userData[0].image)
    image = userData[0].image
    return render(request, "USER/profile.html", {"image": image, "userData": userData})


def updateProfile(request):
    id = request.session["uid"]
    print(id)
    current_date = datetime.today().strftime("%Y-%m-%d")
    print(current_date)
    userData = UserRegistration.objects.filter(loginid=id)
    image = userData[0].image
    userData = UserRegistration.objects.filter(loginid=id)
    if request.POST:
        name = request.POST["name"]
        email = request.POST["email"]
        phone = request.POST["phone"]
        dob = request.POST["dob"]
        gender = request.POST["gender"]
        address = request.POST["address"]
        password = request.POST["password"]
        image = request.FILES["image"]
        logUser = Login.objects.get(id=id)
        logUser.username = email
        logUser.viewPass = password
        logUser.set_password(password)
        logUser.save()

        userReg = UserRegistration.objects.get(loginid=id)
        userReg.name = name
        userReg.phone = phone
        userReg.email = email
        userReg.dob = dob
        userReg.gender = gender
        userReg.address = address
        userReg.image = image
        userReg.save()
        redirect("/viewProfile")
    return render(request,"USER/updateProfile.html",{"userData": userData, "current_date": current_date,"image":image})

import pickle
pipe = pickle.load(open("Naive_model.pkl","rb"))
def compose(request):
    uid = request.session["uid"]
    uEmail=UserRegistration.objects.get(loginid=uid)
    print(uEmail,"IDIDIDIDID")
    mailid=uEmail.email
    print(mailid)
    current_date = datetime.today().strftime("%Y-%m-%d")
    current_time = dt.datetime.now().strftime("%I:%M %p")
    print("Current Time:", current_time)
    userData = UserRegistration.objects.filter(loginid=uid)
    print(userData[0].image)
    image = userData[0].image
    email=userData[0].email
    count=Message.objects.filter(sendto=email).count()
    if "send" in request.POST:
        toaddress=request.POST['to']
        subject=request.POST['subject']
        desc=request.POST['desc']
        print(toaddress)
        print(subject)
        print(desc)
        blockCheckQry=BlockList.objects.filter(Q(blocking_user_id=mailid)&Q(blocked_user_id=toaddress))
        if blockCheckQry:
            messages.error(request, "User Blocked")
        else:
            sendMail=Message.objects.create(fromMail=uEmail,sendto=toaddress,subject=subject,description=desc,date=current_date,time=current_time)
            sendMail.save()

            text = request.POST
            emails = text['desc']
            print(emails)
            list_email = [emails]
            output = pipe.predict(list_email)[0]
            print(output)

            # Save prediction result in the Message model
            sendMail.prediction_result = output
            sendMail.save()
            # if output == 1:
            #     messages.warning(request, "Warning: This Email has been classified as SPAM.")
            # elif output == 0:
            #     messages.success(request, "Success: This Email is NOT classified as SPAM.")

            return render(request, 'USER/compose.html', {"image": image, "count": count, "prediction": output})

        # return redirect("/viewMail")
    elif "draft" in request.POST:
        toaddress=request.POST['to']
        subject=request.POST['subject']
        desc=request.POST['desc']
        print(toaddress)
        print(subject)
        print(desc)
        draftMail=Drafts.objects.create(fromMail=uEmail,sendto=toaddress,subject=subject,description=desc,date=current_date,time=current_time)
        draftMail.save()
        messages.success(request,"Added to Drafts")
    return render(request,'USER/compose.html',{"image":image,"count":count})

def inbox(request):
    id = request.session["uid"]
    userData = UserRegistration.objects.filter(loginid=id)
    print(userData[0].image)
    image = userData[0].image
    email=userData[0].email
    ##########Profile Image##########
    # getting Inbox Messages
    inboxData=Message.objects.filter(Q(sendto=email)&Q(status="Sent")).order_by("-date")
    # print(inboxData)
    count=Message.objects.filter(sendto=email).count()
    return render(request,'USER/inbox.html',{"image":image,"inboxData":inboxData,"count":count})

def readMail(request):
    cnt=0
    cntn=0
    id = request.session["uid"]
    userData = UserRegistration.objects.filter(loginid=id)
    print(userData[0].image)
    image = userData[0].image
    ##########Profile Image##########

    # view single Message
    mid=request.GET['id']
    msgData=Message.objects.get(id=mid)
    email=userData[0].email
    count=Message.objects.filter(sendto=email).count()

    ################TESTING

    frm1=msgData.fromMail.email
    sub=msgData.subject
    con=msgData.description
    print("***************************************************************************")
    print(con)
    analyser = SentimentIntensityAnalyzer()
    vadersenti = analyser.polarity_scores(con)
    cnt=cnt+vadersenti['pos']
    cntn=cntn+vadersenti['neg']
    print(cnt)
    print(cntn)
    cntn=cntn*100
    data=pd.read_csv("phishing_site_urls.csv")
    # if(data["URL"]==con):
    # if con in data['URL']:
    # print
    # print(con in data['URL'])
    cc=0
    for cd in data["URL"]:
        cc=cc+1
        # print(cd)
        print(type(con) ) 
        if con==cd:
            cntn=75
            break;  
        
        if cc>=50:
            break

    try:
        import emailph
    except:
        msg=""

    return render(request,'USER/readMail.html',{"image":image,"msgData":msgData,"count":count,"cnt":cnt,"cntn":cntn,"cc":cc})

def deleteMail(request):
    id=request.GET['id']
    abc=Message.objects.filter(id=id).delete()
    return redirect("/outBox")

def outBox(request):
    id = request.session["uid"]
    userData = UserRegistration.objects.filter(loginid=id)
    print(userData[0].image)
    image = userData[0].image
    ##########Profile Image##########
    print(id)
    outBoxData=Message.objects.filter(Q(fromMail_id__loginid=id)&Q(status="Sent")).order_by('-date', '-time')
    # print(outBoxData)
    return render(request,"USER/outBox.html",{"outBoxData":outBoxData,"image":image})

def drafts(request):
    id = request.session["uid"]
    userData = UserRegistration.objects.filter(loginid=id)
    print(userData[0].image)
    image = userData[0].image
    ##########Profile Image##########
    print(id)
    draftData=Drafts.objects.filter(Q(fromMail_id__loginid=id)&Q(status="Draft")).order_by('-date', '-time')
    # print(draftData)
    return render(request,"USER/drafts.html",{"draftData":draftData,"image":image})

def readDraft(request):
    id = request.session["uid"]
    uEmail=UserRegistration.objects.get(loginid=id)
    userData = UserRegistration.objects.filter(loginid=id)
    print(userData[0].image)
    image = userData[0].image
    ##########Profile Image##########

    # view single Message
    mid=request.GET['id']
    msgData=Drafts.objects.get(id=mid)
    email=userData[0].email
    count=Drafts.objects.filter(sendto=email).count()
    current_time = dt.datetime.now().strftime("%I:%M %p")
    current_date = datetime.today().strftime("%Y-%m-%d")

    if request.POST:
        toaddress=request.POST['to']
        subject=request.POST['subject']
        desc=request.POST['desc']
        print(toaddress)
        print(subject)
        print(desc)
        sendMail=Message.objects.create(fromMail=uEmail,sendto=toaddress,subject=subject,description=desc,date=current_date,time=current_time)
        sendMail.save()
        print(mid)
        deleteMail=Drafts.objects.filter(id=mid).delete()
        print(deleteMail,"HELLO")
        return redirect("/outBox")
    return render(request,'USER/readDrafts.html',{"image":image,"msgData":msgData,"count":count})

def addFeedback(request):
    id=request.session['uid']
    userData = UserRegistration.objects.filter(loginid=id)
    print(userData[0].image)
    image = userData[0].image
    print(id)
    uid=UserRegistration.objects.get(loginid__id=id)
    if request.POST:
        subject=request.POST['subject']
        feedback=request.POST['desc']
        addFeedback=Feedback.objects.create(subject=subject,feedback=feedback,uid=uid)
        addFeedback.save()
        messages.success(request,"Feedback Added")
    return render(request,"USER/addFeedback.html",{"image":image})

def blockUser(request):
    fromm=request.GET['from']
    to=request.GET['to']
    print(fromm,to)
    blockQry=BlockList.objects.create(blocking_user_id=to,blocked_user_id=fromm)
    blockQry.save()
    messages.success(request,f"{fromm} Blocked")
    return redirect("/inbox")
