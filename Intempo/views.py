from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required



def index(request):
    context_dict = {}
    context_dict["temp_message"] = "placeholder!"

    #visitor_cookie_handler(request)

    response = render(request, 'intempo/index.html', context=context_dict)
    return response
