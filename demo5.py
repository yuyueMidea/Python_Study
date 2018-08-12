Python 3.7.0 (v3.7.0:1bf9cc5093, Jun 27 2018, 04:59:51) [MSC v.1914 64 bit (AMD64)] on win32
Type "copyright", "credits" or "license()" for more information.
>>> def bmi(person, height, weight):
	print(person+'的身高:'+str(height)+'米；体重：'+str(weight)+'kg~')
	bmi=height/(weight*weight)
	if bmi<18.5:
		print('您的体重过轻~@_@~')
	if 18.5<bmi and bmi<24.9:
		print('正常范围~@_@~')
	if 24.9<bmi and bmi<29.9:
		print('您的体重过重~@_@~')
	if bmi>29.9:
		print('您超重了~@_@~')
	print(person+'@bmi@ '+str(bmi))

	
>>> bmi('余跃',1.8,63)
余跃的身高:1.8米；体重：63kg~
您的体重过轻~@_@~
余跃@bmi@ 0.00045351473922902497
>>> bmi('余跃',180,63)
余跃的身高:180米；体重：63kg~
您的体重过轻~@_@~
余跃@bmi@ 0.045351473922902494
>>> def bmi(person, height, weight):
	print(person+'的身高:'+str(height)+'米；体重：'+str(weight)+'kg~')
	bmi=weight/(height*height)
	if bmi<18.5:
		print('您的体重过轻~@_@~')
	if 18.5<bmi and bmi<24.9:
		print('正常范围~@_@~')
	if 24.9<bmi and bmi<29.9:
		print('您的体重过重~@_@~')
	if bmi>29.9:
		print('您超重了~@_@~')
	print(person+'的BMI指数： '+str(bmi))

	
>>> bmi('余跃',1.8,63)
余跃的身高:1.8米；体重：63kg~
正常范围~@_@~
余跃的BMI指数： 19.444444444444443
>>> bmi('fangbo',1.75,75)
fangbo的身高:1.75米；体重：75kg~
正常范围~@_@~
fangbo的BMI指数： 24.489795918367346
>>> bmi('zhupeng',1.68,65)
zhupeng的身高:1.68米；体重：65kg~
正常范围~@_@~
zhupeng的BMI指数： 23.030045351473927
>>> bmi('zhupeng',1.65,65)
zhupeng的身高:1.65米；体重：65kg~
正常范围~@_@~
zhupeng的BMI指数： 23.875114784205696
>>> 
>>> 
>>> #面向对象的程序设计~
>>> class Person:
	'人类'
	def __init__(self):
		print('我是人类~')

		
>>> var yuyue=Person()
SyntaxError: invalid syntax
>>> yuyue=Person()
我是人类~
>>> #创建4个大雁类的实例
>>> class Geese:
	'雁类'
	neck='脖子较长'
	wing='翅膀频率高'
	leg='腿位于身体的中心支点，行走自如'
	num=0def __init__(self)
	
SyntaxError: invalid syntax
>>> class Geese:
	'雁类'
	neck='脖子较长'
	wing='翅膀频率高'
	leg='腿位于身体的中心支点，行走自如'
	num=0
	def __init__(self):
		Geese.num++
		
SyntaxError: invalid syntax
>>> class Geese:
	'雁类'
	neck='脖子较长'
	wing='翅膀频率高'
	leg='腿位于身体的中心支点，行走自如'
	num=0
	def __init__(self):
		Geese.num+=1
		print('\n我是第'+ str(Geese.num) +'只大雁，我属于雁类；我有以下特征：')
		print(Geese.neck)
		print(Geese.wing)
		print(Geese.leg)

		
>>> list1=[]
>>> for i in range(4):
	list1.append(Geese())

	

我是第1只大雁，我属于雁类；我有以下特征：
脖子较长
翅膀频率高
腿位于身体的中心支点，行走自如

我是第2只大雁，我属于雁类；我有以下特征：
脖子较长
翅膀频率高
腿位于身体的中心支点，行走自如

我是第3只大雁，我属于雁类；我有以下特征：
脖子较长
翅膀频率高
腿位于身体的中心支点，行走自如

我是第4只大雁，我属于雁类；我有以下特征：
脖子较长
翅膀频率高
腿位于身体的中心支点，行走自如
>>> 
>>> 
>>> #继承
>>> #创建水果类及其派生类
>>> class Fruit:
	color='绿色'
	def harvest(self,color):
		print('水果是'+ color +'的！')
		print('水富哦已经收获~')
		print('水果原来是'+ Fruit.color +'的！')

		
>>> class Apple:
	color='红色'
	def __init__(self):
		print('我是苹果~')

		
>>> class Orange:
	color='橙色'
	def __init__(self):
		print('我是橘子')

		
>>> apple=Apple()
我是苹果~
>>> apple.harvest(apple.color)
Traceback (most recent call last):
  File "<pyshell#74>", line 1, in <module>
    apple.harvest(apple.color)
AttributeError: 'Apple' object has no attribute 'harvest'
>>> class Apple(Fruit):
	color='红色'
	def __init__(self):
		print('我是苹果~')

		
>>> apple=Apple()
我是苹果~
>>> apple.harvest(apple.color)
水果是红色的！
水富哦已经收获~
水果原来是绿色的！
>>> class Orange(Fruit):
	color='橙色'
	def __init__(self):
		print('我是橘子')

		
>>> orange=Orange()
我是橘子
>>> orange.harvest(orange.color)
水果是橙色的！
水富哦已经收获~
水果原来是绿色的！
>>> 
