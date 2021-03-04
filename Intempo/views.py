from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required



def index(request):
    context_dict = {}
    context_dict[""] = ""

    response = render(request, 'intempo/index.html', context=context_dict)
    return response


def albums(request):
    context_dict = {}
    context_dict[""] = ""

    response = render(request, 'intempo/albums.html', context=context_dict)
    return response


def album_page(request):
    context_dict = {}
    context_dict["name"] = "placeholder album name"
    context_dict["description"] = "placeholder description"

    response = render(request, 'intempo/album_page.html', context=context_dict)
    return response


def profile(request):
    context_dict = {}
    context_dict["username"] = "placeholder username"

    response = render(request, 'intempo/profile.html', context=context_dict)
    return response


def signup(request):
    context_dict = {}
    context_dict[""] = ""

    response = render(request, 'intempo/signup.html', context=context_dict)
    return response


def login(request):
    context_dict = {}
    context_dict[""] = ""

    response = render(request, 'intempo/login.html', context=context_dict)
    return response
