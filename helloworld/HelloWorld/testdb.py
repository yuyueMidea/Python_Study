# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render,redirect

from TestModel.models import Test


# 数据库操作
def query(request):
    # add a new
    if request.method=='POST':
        a_name= request.POST['a_name']
        if a_name:
            Test.objects.create(name=a_name)

    # 通过objects这个模型管理器的all()获得所有数据行，相当于SQL中的SELECT * FROM
    list = Test.objects.all()
    return render(request, 'hello.html', {'list': list})
def delete(request):
    del_id = request.GET.get("id", None)  # 获取到get请求的参数中的id内容
    if del_id:
        del_obj = Test.objects.get(id=del_id)  # 继承models中的数据库类
        del_obj.delete()  # 删除操作

        # list = Test.objects.all()
        # return render(request, 'hello.html',  {'list': list})
        return redirect("/testdb")
    else:
        return HttpResponse("ERROR,检查数据后再试")  # 若不存在数据或其他错误