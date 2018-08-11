Python 3.7.0 (v3.7.0:1bf9cc5093, Jun 27 2018, 04:59:51) [MSC v.1914 64 bit (AMD64)] on win32
Type "copyright", "credits" or "license()" for more information.
>>> #这是一段Pyhon注释~
>>> '''这是一段Pyhon注释222'''
'这是一段Pyhon注释222'
>>> @这是一段Pyhon注释
这是一段Pyhon注释22
SyntaxError: invalid syntax
>>> @这是一段Pyhon注释2
@这是一段Pyhon注释
@这是一段Pyhon注释12
@这是一段Pyhon注释1234






KeyboardInterrupt
>>> python
Traceback (most recent call last):
  File "<pyshell#14>", line 1, in <module>
    python
NameError: name 'python' is not defined
>>> import keyword
>>> keyword
<module 'keyword' from 'C:\\Users\\Administrator.USER-20171224VG\\AppData\\Local\\Programs\\Python\\Python37\\lib\\keyword.py'>
>>> keyword.kwlist
['False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield']
>>> and
SyntaxError: invalid syntax
>>> True
True
>>> as
SyntaxError: invalid syntax
>>> type('aaa')
<class 'str'>
>>> type(12)
<class 'int'>
>>> type(12.43)
<class 'float'>
>>> type([1,2])
<class 'list'>
>>> type({name:'yy'})
Traceback (most recent call last):
  File "<pyshell#25>", line 1, in <module>
    type({name:'yy'})
NameError: name 'name' is not defined
>>> type({'name':'yy'})
<class 'dict'>
>>> type({1,2})
<class 'set'>
>>> type((1,2))
<class 'tuple'>
>>> str(1.78)
'1.78'
>>> True==1
True
>>> True==0
False
>>> False
False
>>> False==0
True
>>> False===0
SyntaxError: invalid syntax
>>> 7/2
3.5
>>> 11/2
5.5
>>> 11//2
5
>>> 7%2
1
>>> -7%2
1
>>> 7%-2
-1
>>> 5+11
16
>>> 5+=11
SyntaxError: can't assign to literal
>>> num=11
>>> num=num+2
>>> num
13
>>> num+=2
>>> num
15
>>> num*=2
>>> num
30
>>> input('请输入时间：')
请输入时间：12
'12'
>>> 1 and 2
2
>>> 1 or 2
1
>>> def f1(height, weight):
	bmi=weight/(height*height)
	return bmi

>>> f1(1.8,66)
20.37037037037037
>>> f1(1.8,55)
16.975308641975307
>>> f1(1.8,63)
19.444444444444443
>>> 1 || 2
SyntaxError: invalid syntax
>>> 1 | 2
3
>>> 1|2
3
>>> 1~2
SyntaxError: invalid syntax
>>> 1&2
0
>>> 1 & 2
0
>>> 1>0
True
>>> aa=11 if 1>0 else 00
>>> aa
11
>>> aa=11 if 1<0 else 00
>>> aa
0
>>> bb=12 if 1>0
SyntaxError: invalid syntax
>>> if 1>0 bb=123
SyntaxError: invalid syntax
>>> if 1>0:
	bb=12

	
>>> bb
12
>>> f1
<function f1 at 0x0000000002F93E18>
>>> f1()
Traceback (most recent call last):
  File "<pyshell#78>", line 1, in <module>
    f1()
TypeError: f1() missing 2 required positional arguments: 'height' and 'weight'
>>> def f2(num):
	if num==1:
		return 111
	elif num==2:
		return 222
	elif num==33:
		return 333
	else return 123321
	
SyntaxError: invalid syntax
>>> def f2(num):
	if num==1:
		return 111
	elif num==2:
		return 222
	elif num==33:
		return 333
	else:
		return 123321

	
>>> f2(1)
111
>>> f2(2)
222
>>> f2(4554)
123321
>>> for i in range(11):
	print(i)

	
0
1
2
3
4
5
6
7
8
9
10
>>> for i in range(11):
	print(i)
	if i>=2:
		break

	
0
1
2
>>> for i in range(11):
	print(i)
	ifi>=2:
		
SyntaxError: invalid syntax
>>> for i in range(11):
	print(i)
	if i>=2:
		return
	
SyntaxError: 'return' outside function
>>> for i in range(11):
	print(i)
	if i>=2:
		print(i*2)

		
0
1
2
4
3
6
4
8
5
10
6
12
7
14
8
16
9
18
10
20
>>> for i in range(11):
	print(i)
	print(i*2)

	
0
0
1
2
2
4
3
6
4
8
5
10
6
12
7
14
8
16
9
18
10
20
>>> str(17)
'17'
>>> str(17).endswith('7')
True
>>> for i in range(1,11):
	print(i, end=' ')

	
1 2 3 4 5 6 7 8 9 10 
>>> str1='我是一条字符串~'
>>> str1[0]
'我'
>>> str1[-1]
'~'
>>> str1.split('')
Traceback (most recent call last):
  File "<pyshell#121>", line 1, in <module>
    str1.split('')
ValueError: empty separator
>>> str1.split()
['我是一条字符串~']
>>> str1[1:5]
'是一条字'
>>> str1*2
'我是一条字符串~我是一条字符串~'
>>> arr=[]*5
>>> arr
[]
>>> arr=[1]*5
>>> arr
[1, 1, 1, 1, 1]
>>> len(str1)
8
>>> arr=[11,22,33,18,64,27,9,54]
>>> arr
[11, 22, 33, 18, 64, 27, 9, 54]
>>> max(arr)
64
>>> min(arr)
9
>>> sum(arr)
238
>>> str(arr)
'[11, 22, 33, 18, 64, 27, 9, 54]'
>>> arr
[11, 22, 33, 18, 64, 27, 9, 54]
>>> str1
'我是一条字符串~'
>>> list(str1)
['我', '是', '一', '条', '字', '符', '串', '~']
>>> for i in range(str1):
	print(i)

	
Traceback (most recent call last):
  File "<pyshell#141>", line 1, in <module>
    for i in range(str1):
TypeError: 'str' object cannot be interpreted as an integer
>>> for i in range(list(str1)):
	print(i)

	
Traceback (most recent call last):
  File "<pyshell#143>", line 1, in <module>
    for i in range(list(str1)):
TypeError: 'list' object cannot be interpreted as an integer
>>> str1
'我是一条字符串~'
>>> str2='123654'
>>> for i in range(list(str2)):
	print(i)

	
Traceback (most recent call last):
  File "<pyshell#148>", line 1, in <module>
    for i in range(list(str2)):
TypeError: 'list' object cannot be interpreted as an integer
>>> list(str2)
['1', '2', '3', '6', '5', '4']
>>> arr
[11, 22, 33, 18, 64, 27, 9, 54]
>>> for i in range(arr):
	print(i)

	
Traceback (most recent call last):
  File "<pyshell#153>", line 1, in <module>
    for i in range(arr):
TypeError: 'list' object cannot be interpreted as an integer
>>> for i in list(str1):
	print(i)

	
我
是
一
条
字
符
串
~
>>> for i in list(str2):
	print(i)

	
1
2
3
6
5
4
>>> str1
'我是一条字符串~'
>>> str1[2:5]
'一条字'
>>> str1[1:-1]
'是一条字符串'
>>> str1[0:-1]
'我是一条字符串'
>>> str1[-1,0]
Traceback (most recent call last):
  File "<pyshell#163>", line 1, in <module>
    str1[-1,0]
TypeError: string indices must be integers
>>> str1[-1]
'~'
>>> arr
[11, 22, 33, 18, 64, 27, 9, 54]
>>> for index,item in enumerate(arr):
	print(index+1, item)

	
1 11
2 22
3 33
4 18
5 64
6 27
7 9
8 54
>>> enumerate(arr)
<enumerate object at 0x0000000002FA0E58>
>>> for x,y in enumerate(list(str1)):
	print(x+1, y)

	
1 我
2 是
3 一
4 条
5 字
6 符
7 串
8 ~
>>> arr
[11, 22, 33, 18, 64, 27, 9, 54]
>>> arr.append(121)
>>> arr
[11, 22, 33, 18, 64, 27, 9, 54, 121]
>>> arr.insert(212)
Traceback (most recent call last):
  File "<pyshell#176>", line 1, in <module>
    arr.insert(212)
TypeError: insert() takes exactly 2 arguments (1 given)
>>> arr.insert(2,212)
>>> arr
[11, 22, 212, 33, 18, 64, 27, 9, 54, 121]
>>> arr.remove(121)
>>> arr
[11, 22, 212, 33, 18, 64, 27, 9, 54]
>>> sort(arr)
Traceback (most recent call last):
  File "<pyshell#181>", line 1, in <module>
    sort(arr)
NameError: name 'sort' is not defined
>>> arr.sort()
>>> arr
[9, 11, 18, 22, 27, 33, 54, 64, 212]
>>> arr.max()
Traceback (most recent call last):
  File "<pyshell#184>", line 1, in <module>
    arr.max()
AttributeError: 'list' object has no attribute 'max'
>>> arr2=[15,54,19,64,18,84]
>>> sorted(arr)
[9, 11, 18, 22, 27, 33, 54, 64, 212]
>>> sorted(arr2)
[15, 18, 19, 54, 64, 84]
>>> arr2
[15, 54, 19, 64, 18, 84]
>>> 
