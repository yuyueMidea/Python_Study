# from django.http import HttpResponse
#
#
# def hello(request):
#     return HttpResponse("Hello world ! this is yuyue---123")


from django.shortcuts import render


def hello(request):
    context = {}
    context['hello'] = 'list World!'
    return render(request, 'list.html', context)

def index(request):
    return render(request, 'index.html')

def home(request):
    context2 = {}
    context2['hello'] = 'back home----'
    context2['list1'] = [34,456,768,98,435]
    return render(request, 'list.html', context2)