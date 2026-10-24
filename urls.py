"""
URL configuration for mailproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from mailapp import views

urlpatterns = [
    path("admin/", admin.site.urls),
    # path("", views.logins),
    path("", views.index),
    path("login/", views.logins),
    path("register/", views.register),
    path("userHome/", views.userHome),
    path("userHeader/", views.userHeader),
    path("adminHome/", views.adminHome),
    path("adminHeader/", views.adminHeader),
    path("viewUsers/", views.viewUsers),
    path("manageUser/", views.manageUser),
    path("viewProfile/", views.viewProfile),
    path("updateProfile/", views.updateProfile),
    path("compose/", views.compose),
    path("inbox/", views.inbox),
    path("readMail/", views.readMail),
    path("outBox/", views.outBox),
    path("deleteMail/", views.deleteMail),
    path("drafts/", views.drafts),
    path("readDraft/", views.readDraft),
    path("addFeedback/", views.addFeedback),
    path("viewFeedbacks/", views.viewFeedbacks),
    path("blockUser/", views.blockUser),
    path("blockedUsers/", views.blockedUsers),
    path("restrictUser/", views.restrictUser),
    path("allowUser/", views.allowUser),
]
