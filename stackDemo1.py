Python 3.7.0 (v3.7.0:1bf9cc5093, Jun 27 2018, 04:59:51) [MSC v.1914 64 bit (AMD64)] on win32
Type "copyright", "credits" or "license()" for more information.
>>> class Stack(object):
	def __init__(self,limit=10):
		self.stack=[]
		self.limit=limit
	def __str__(self):
		str(self.stack)
	def push(self, data):
		if len(self.stack)>limit:
			print(' StackOverflowError')
		self.stack.append(data)
	def pop(self):
		if self.stack:
			return self.stack.pop()
		print('the stack is empty!')
	def size(self):
		return len(self.stack)

	
>>> stack1=Stack()
>>> stack1
<__main__.Stack object at 0x0000000002F87860>
>>> for i in range(10):
	stack1.push(i)

	
Traceback (most recent call last):
  File "<pyshell#22>", line 2, in <module>
    stack1.push(i)
  File "<pyshell#17>", line 8, in push
    if len(self.stack)>limit:
NameError: name 'limit' is not defined
>>> class Stack(object):
	def __init__(self,limit=10):
		self.stack=[]
		self.limit=limit
	def __str__(self):
		str(self.stack)
	def push(self, data):
		if len(self.stack)>=self.limit:
			print(' StackOverflowError')
		self.stack.append(data)
	def pop(self):
		if self.stack:
			return self.stack.pop()
		print('the stack is empty!')
	def size(self):
		return len(self.stack)

	
>>> stack1=Stack()
>>> for i in range(10):
	stack1.push(i)

	
>>> stack1
<__main__.Stack object at 0x0000000002F87828>
>>> stack1.size
<bound method Stack.size of <__main__.Stack object at 0x0000000002F87828>>
>>> stack1.size()
10
>>> stack1.push(121)
 StackOverflowError
>>> stack1.pop()
121
>>> stack1.pop()
9
>>> stack1.size()
9
>>> stack1.pop()
8
>>> stack1.pop()
7
>>> stack1.size()
7
>>> 
