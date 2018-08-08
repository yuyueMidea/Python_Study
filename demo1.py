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
>>> 
