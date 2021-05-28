from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def index(request):
    return HttpResponse("Hello Word")

def say_hello_to(request, name):
    return HttpResponse("Hello " + name)

def say_number(request, num):
    return HttpResponse("Hello " + str(num))
