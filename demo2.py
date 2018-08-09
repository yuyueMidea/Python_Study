Python 3.7.0 (v3.7.0:1bf9cc5093, Jun 27 2018, 04:59:51) [MSC v.1914 64 bit (AMD64)] on win32
Type "copyright", "credits" or "license()" for more information.
>>> set1={1,12,31,51,18}
>>> set1
{1, 12, 18, 51, 31}
>>> type(set1)
<class 'set'>
>>> arr=[1,2,1,4,8,7,4]
>>> tu1=(12,51,18,64,49)
>>> type(tu1)
<class 'tuple'>
>>> set1.add(18)
>>> set1
{1, 12, 18, 51, 31}
>>> set1.add(arr)
Traceback (most recent call last):
  File "<pyshell#8>", line 1, in <module>
    set1.add(arr)
TypeError: unhashable type: 'list'
>>> set1
{1, 12, 18, 51, 31}
>>> set1.remove(51)
>>> set1
{1, 12, 18, 31}
>>> arr.remove(1)
>>> arr
[2, 1, 4, 8, 7, 4]
>>> arr.remove(1)
>>> arr
[2, 4, 8, 7, 4]
>>> arr.remove(8)
>>> arr
[2, 4, 7, 4]
>>> obj={'name':'yuyue', 'age':26, 'tel':18825237023,'qq':1062827804}
>>> pbj
Traceback (most recent call last):
  File "<pyshell#19>", line 1, in <module>
    pbj
NameError: name 'pbj' is not defined
>>> type(obj)
<class 'dict'>
>>> obj['age']
26
>>> set2={12,18,68,48,53}
>>> set1
{1, 12, 18, 31}
>>> set1&set2
{18, 12}
>>> set2-set1
{48, 68, 53}
>>> set1|set2
{1, 68, 12, 48, 18, 53, 31}
>>> arr
[2, 4, 7, 4]
>>> set3=set(arr)
>>> set3
{2, 4, 7}
>>> set4=set(x for x in range(22):if x%3==0)
SyntaxError: invalid syntax
>>> set4=set(x for x in range(22) if x%3==0)
>>> set4
{0, 3, 6, 9, 12, 15, 18, 21}
>>> str1='my name is'
>>> str2='yuyue'
>>> str1+str2
'my name isyuyue'
>>> str1+' : '+str2
'my name is : yuyue'
>>> str1[3:8]
'name '
>>> str1.split(' ')
['my', 'name', 'is']
>>> str1.split(' ', 1)
['my', 'name is']
>>> str1.split()
['my', 'name', 'is']
>>> str1
'my name is'
>>> str1[1:]
'y name is'
>>> str3='@'.join(arr)
Traceback (most recent call last):
  File "<pyshell#43>", line 1, in <module>
    str3='@'.join(arr)
TypeError: sequence item 0: expected str instance, int found
>>> strarr=str1.split()
>>> strarr
['my', 'name', 'is']
>>> str3='@'.join(strarr)
>>> str3
'my@name@is'
>>> str3.count('@')
2
>>> str3.find('@')
2
>>> "@" in str3
True
>>> str3.lower()
'my@name@is'
>>> str3.upper()
'MY@NAME@IS'
>>> import re
>>> re
<module 're' from 'C:\\Users\\Administrator.USER-20171224VG\\AppData\\Local\\Programs\\Python\\Python37\\lib\\re.py'>
>>> pattern=r'^my'
>>> pattern
'^my'
>>> type(pattern)
<class 'str'>
>>> re.match(pattern,str3)
<re.Match object; span=(0, 2), match='my'>
>>> 
