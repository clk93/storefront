from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
# Request handler
# Request -> response

def sayHello(request):
    return render(request, "hello.html", {"name":"Tina"})