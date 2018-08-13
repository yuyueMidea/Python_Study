Python 3.7.0 (v3.7.0:1bf9cc5093, Jun 27 2018, 04:59:51) [MSC v.1914 64 bit (AMD64)] on win32
Type "copyright", "credits" or "license()" for more information.
>>> arr1=[x for x in range(11) if x%2==0]
>>> arr1
[0, 2, 4, 6, 8, 10]
>>> def quick_sort(arr):
	length=len(arr)
	if(length<=1):
		return arr
	else:
		mid=arr[0]
		big=[x for x in arr[1:] if x>mid]
		small=[x for x in arr[1:] if x<mid]
		return quick_sort(small)+[mid]+quick_sort(big)

	
>>> arr1
[0, 2, 4, 6, 8, 10]
>>> arr1[1:]
[2, 4, 6, 8, 10]
>>> import math
>>> math
<module 'math' (built-in)>
>>> math.ramdom()
Traceback (most recent call last):
  File "<pyshell#17>", line 1, in <module>
    math.ramdom()
AttributeError: module 'math' has no attribute 'ramdom'

>>> math.ram
Traceback (most recent call last):
  File "<pyshell#18>", line 1, in <module>
    math.ram
AttributeError: module 'math' has no attribute 'ram'
>>> arr2=[15,8,46,27,13,51]
>>> quick_sort(arr2)
[8, 13, 15, 27, 46, 51]
>>> 
