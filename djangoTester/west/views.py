# -*- coding:utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from west.models import Character
from django.core.context_processors import request
# Create your views here.

def first_page(request):
    return HttpResponse("<p>西餐</p>")

# staff ver1.0
# def staff(request):
#     staff_list=Character.objects.all()
#     staff_str=map(str,staff_list)
#     context={'label':' '.join(staff_str)}
#     return render(request,'templay.html',context)

#staff ver1.1
def staff(request):
    staff_list=Character.objects.all()
    return render(request,'templay.html',{'staffs':staff_list})

def templay(request):
    context     ={}
    context['label']='HelloWorld!'
    return render(request,'templay.html',context)

def bootstrap3(request):
    return render(request,'hello2/bootstrap3templay.html')

