Python 3.7.0 (v3.7.0:1bf9cc5093, Jun 27 2018, 04:59:51) [MSC v.1914 64 bit (AMD64)] on win32
Type "copyright", "credits" or "license()" for more information.
>>> str
<class 'str'>
>>> arr
Traceback (most recent call last):
  File "<pyshell#1>", line 1, in <module>
    arr
NameError: name 'arr' is not defined
>>> arr=list(range(11))
>>> arr
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
>>> range(11)
range(0, 11)
>>> range(0, 11)
range(0, 11)
>>> list(0,11)
Traceback (most recent call last):
  File "<pyshell#6>", line 1, in <module>
    list(0,11)
TypeError: list expected at most 1 arguments, got 2
>>> list(12)
Traceback (most recent call last):
  File "<pyshell#7>", line 1, in <module>
    list(12)
TypeError: 'int' object is not iterable
>>> list(arr)
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
>>> arr/2
Traceback (most recent call last):
  File "<pyshell#9>", line 1, in <module>
    arr/2
TypeError: unsupported operand type(s) for /: 'list' and 'int'
>>> arr.append(111)
>>> arr
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 111]
>>> arr[-1]
111
>>> arr2=list( range(10,50,3) )
>>> arr2
[10, 13, 16, 19, 22, 25, 28, 31, 34, 37, 40, 43, 46, 49]
>>> print(arr)
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 111]
>>> for i in arr:
	if i%2==0:print(i)

	
0
2
4
6
8
10
>>> arr3=arr.extend(arr2)
>>> arr2
[10, 13, 16, 19, 22, 25, 28, 31, 34, 37, 40, 43, 46, 49]
>>> arr
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 111, 10, 13, 16, 19, 22, 25, 28, 31, 34, 37, 40, 43, 46, 49]
>>> arr3
>>> 
>>> arr-arr2
Traceback (most recent call last):
  File "<pyshell#24>", line 1, in <module>
    arr-arr2
TypeError: unsupported operand type(s) for -: 'list' and 'list'
>>> arr+arr2
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 111, 10, 13, 16, 19, 22, 25, 28, 31, 34, 37, 40, 43, 46, 49, 10, 13, 16, 19, 22, 25, 28, 31, 34, 37, 40, 43, 46, 49]
>>> arr
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 111, 10, 13, 16, 19, 22, 25, 28, 31, 34, 37, 40, 43, 46, 49]
>>> for i in arr:
	if i>9:arr.remove(i)

	
>>> arr
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 111, 13, 19, 25, 31, 37, 43, 49]
>>> arr.remove(-1)
Traceback (most recent call last):
  File "<pyshell#31>", line 1, in <module>
    arr.remove(-1)
ValueError: list.remove(x): x not in list
>>> arr.remove(49)
>>> arr
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 111, 13, 19, 25, 31, 37, 43]
>>> len(arr)
17
>>> arr.sort()
>>> arr
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 13, 19, 25, 31, 37, 43, 111]
>>> arr.reverse
<built-in method reverse of list object at 0x0000000002DE8AC8>
>>> arr.reverse()
>>> arr
[111, 43, 37, 31, 25, 19, 13, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
>>> arr3
>>> 
>>> arr3=[]
>>> arr3
[]
>>> for i in range(4):
	arr3.append(i)

	
>>> arr3
[0, 1, 2, 3]
>>> for i in range(4):
	arr3.append([])
	for j in range(3):
		arr3[i].append(j)

		
Traceback (most recent call last):
  File "<pyshell#52>", line 4, in <module>
    arr3[i].append(j)
AttributeError: 'int' object has no attribute 'append'
>>> arr3
[0, 1, 2, 3, []]
>>> arr3=[]
>>> 
>>> for i in range(4):
	arr3.append([])
	for j in range(3):
		arr3[i].append(j)

		
>>> arr3
[[0, 1, 2], [0, 1, 2], [0, 1, 2], [0, 1, 2]]
>>> arr3[1]
[0, 1, 2]
>>> arr3[0][0]
0
>>> arr3[0][2]
2
>>> arr3[0][3]
Traceback (most recent call last):
  File "<pyshell#62>", line 1, in <module>
    arr3[0][3]
IndexError: list index out of range
>>> arr3[0].append(121)
>>> arr3
[[0, 1, 2, 121], [0, 1, 2], [0, 1, 2], [0, 1, 2]]
>>> for v in range(5):
	arr3[0].append(v)

	
>>> arr3
[[0, 1, 2, 121, 0, 1, 2, 3, 4], [0, 1, 2], [0, 1, 2], [0, 1, 2]]
>>> name=('zhangsan','lisi','wangwu')
>>> name
('zhangsan', 'lisi', 'wangwu')
>>> type(arr)
<class 'list'>
>>> type(name)
<class 'tuple'>
>>> tuple(range(11))
(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
>>> arr2
[10, 13, 16, 19, 22, 25, 28, 31, 34, 37, 40, 43, 46, 49]
>>> tuple(arr)
(111, 43, 37, 31, 25, 19, 13, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0)
>>> tu1=tuple(arr)
>>> tu1
(111, 43, 37, 31, 25, 19, 13, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0)
>>> arr
[111, 43, 37, 31, 25, 19, 13, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
>>> sale=[x for x in arr if x>10]
>>> sale
[111, 43, 37, 31, 25, 19, 13]
>>> tu1
(111, 43, 37, 31, 25, 19, 13, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0)
>>> tu1[-1]
0
>>> tu1[0]
111
>>> tu1[0]='hello~'
Traceback (most recent call last):
  File "<pyshell#84>", line 1, in <module>
    tu1[0]='hello~'
TypeError: 'tuple' object does not support item assignment
>>> tu1[0]
111
>>> tu1[0]=123456
Traceback (most recent call last):
  File "<pyshell#86>", line 1, in <module>
    tu1[0]=123456
TypeError: 'tuple' object does not support item assignment
>>> tu2=(123,456,789)
>>> tu2
(123, 456, 789)
>>> tu1
(111, 43, 37, 31, 25, 19, 13, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0)
>>> tu1+tu2
(111, 43, 37, 31, 25, 19, 13, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 123, 456, 789)
>>> tu2
(123, 456, 789)
>>> tu1
(111, 43, 37, 31, 25, 19, 13, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0)
>>> tu3
Traceback (most recent call last):
  File "<pyshell#93>", line 1, in <module>
    tu3
NameError: name 'tu3' is not defined
>>> tu3=('yuanzhu3',)
>>> tu3
('yuanzhu3',)
>>> type(tu3)
<class 'tuple'>
>>> tu2
(123, 456, 789)
>>> tu2+tu3
(123, 456, 789, 'yuanzhu3')
>>> arr4=[v for v in range(12) if v%2==0]
>>> arr4
[0, 2, 4, 6, 8, 10]
>>> tu4=(x for x in range(22,111) if x%11==0)
>>> tu4
<generator object <genexpr> at 0x00000000032B4048>
>>> tu4=(x for x in range(4))
>>> tu4
<generator object <genexpr> at 0x00000000032B4138>
>>> tu4=tuple(tu4)
>>> tu4
(0, 1, 2, 3)
>>> tu4.__next__()
Traceback (most recent call last):
  File "<pyshell#107>", line 1, in <module>
    tu4.__next__()
AttributeError: 'tuple' object has no attribute '__next__'
>>> obj
Traceback (most recent call last):
  File "<pyshell#108>", line 1, in <module>
    obj
NameError: name 'obj' is not defined
>>> obj={}
>>> obj
{}
>>> type(obj)
<class 'dict'>
>>> obj={'name':'yuyue', 'age':26, 'tel':18825237023}
>>> obj
{'name': 'yuyue', 'age': 26, 'tel': 18825237023}
>>> obj[name]
Traceback (most recent call last):
  File "<pyshell#114>", line 1, in <module>
    obj[name]
KeyError: ('zhangsan', 'lisi', 'wangwu')
>>> obj.name
Traceback (most recent call last):
  File "<pyshell#115>", line 1, in <module>
    obj.name
AttributeError: 'dict' object has no attribute 'name'
>>> obj.get(name)
>>> obj
{'name': 'yuyue', 'age': 26, 'tel': 18825237023}
>>> obj.get('name')
'yuyue'
>>> obj.get('num')
>>> obj.get('num','none~')
'none~'
>>> obj.items
<built-in method items of dict object at 0x00000000032AAB40>
>>> obj.items()
dict_items([('name', 'yuyue'), ('age', 26), ('tel', 18825237023)])
>>> for i in obj.items():
	print(i)

	
('name', 'yuyue')
('age', 26)
('tel', 18825237023)
>>> obj['age']
26
>>> obj[age]
Traceback (most recent call last):
  File "<pyshell#127>", line 1, in <module>
    obj[age]
NameError: name 'age' is not defined
>>> obj['name']
'yuyue'
>>> for x,y in obj.items()
SyntaxError: invalid syntax
>>> for x,y in obj.items():
	print(x,y)

	
name yuyue
age 26
tel 18825237023
>>> obj['marry']='no'
>>> obj
{'name': 'yuyue', 'age': 26, 'tel': 18825237023, 'marry': 'no'}
>>> del obj['marry']
>>> obj
{'name': 'yuyue', 'age': 26, 'tel': 18825237023}
>>> if 'name' in obj:print(123)

123
>>> if 'x' in obj:print(456)

>>> if 'name1' in obj:print(123)

>>> if 'name' in obj:print(123)

123
>>> if 'sa' in obj:
	print(121)
	else:
		
SyntaxError: invalid syntax
>>> if 'as' in obj:
	print(1211)
	else:print(4545)
	
SyntaxError: invalid syntax
>>> if 'aa' in obj:
	print(111)
else:
	print(2222)

	
2222
>>> set1
Traceback (most recent call last):
  File "<pyshell#156>", line 1, in <module>
    set1
NameError: name 'set1' is not defined
>>> set1={121,'zhangsan',14.24,''}
>>> set1
{'', 121, 'zhangsan', 14.24}
>>> type(set1)
<class 'set'>
>>> arr
[111, 43, 37, 31, 25, 19, 13, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
>>> setarr=set(arr)
>>> aetarr
Traceback (most recent call last):
  File "<pyshell#162>", line 1, in <module>
    aetarr
NameError: name 'aetarr' is not defined
>>> setarr
{0, 1, 2, 3, 4, 37, 6, 7, 8, 9, 5, 43, 13, 111, 19, 25, 31}
>>> setarr.add('string1')
>>> setarr
{0, 1, 2, 3, 4, 37, 6, 7, 8, 9, 5, 43, 13, 111, 'string1', 19, 25, 31}
>>> setarr.pop()
0
>>> setarr
{1, 2, 3, 4, 37, 6, 7, 8, 9, 5, 43, 13, 111, 'string1', 19, 25, 31}
>>> setarr.clear()
>>> setarr
set()
>>> setarr=set(arr2)
>>> setarr
{34, 37, 40, 10, 43, 13, 46, 16, 49, 19, 22, 25, 28, 31}
>>> setarr.remove(43)
>>> setarr.remove(49)
>>> setarr
{34, 37, 40, 10, 13, 46, 16, 19, 22, 25, 28, 31}
>>> setarr.remove(22)
>>> setarr.remove(40)
>>> setarr.remove(46)
>>> setarr
{34, 37, 10, 13, 16, 19, 25, 28, 31}
>>> 
