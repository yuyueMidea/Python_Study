Python 3.7.0 (v3.7.0:1bf9cc5093, Jun 27 2018, 04:59:51) [MSC v.1914 64 bit (AMD64)] on win32
Type "copyright", "credits" or "license()" for more information.
>>> def bubble_sort(arr):
	length=len(arr)
	for i in range(length):
		flag=false
		for j in range(length-1):
			if arr[j]>arr[j+1]:
				flag=true
				arr[j],arr[j+1]=arr[j+1],arr[j]
		if not flag:break
	return arr

>>> arr1=[11,15,57,49,61,29,24]
>>> bubble_sort(arr1)
Traceback (most recent call last):
  File "<pyshell#12>", line 1, in <module>
    bubble_sort(arr1)
  File "<pyshell#10>", line 4, in bubble_sort
    flag=false
NameError: name 'false' is not defined
>>> def bubble_sort(arr):
	length=len(arr)
	for i in range(length):
		flag=False
		for j in range(length-1):
			if arr[j]>arr[j+1]:
				flag=True
				arr[j],arr[j+1]=arr[j+1],arr[j]
		if not flag:break
	return arr

>>> arr1
[11, 15, 57, 49, 61, 29, 24]
>>> bubble_sort(arr1)
[11, 15, 24, 29, 49, 57, 61]
>>> True
True
>>> not True
False
>>> not False
True
>>> break
SyntaxError: 'break' outside loop
>>> for i in range(5):
	print(i)
	if i>2:break

	
0
1
2
3
>>> 
