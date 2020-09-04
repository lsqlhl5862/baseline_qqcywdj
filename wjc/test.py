import re
my_str="2019年10月二十四日"
regex = "(.十)"
my_str1 = re.findall(regex, my_str)
print(my_str1)

CN_NUM={
    u'四':4,u'二': 2,
}


for key in CN_NUM:
    my_str3=re.sub(key+'十',str(CN_NUM[key])+'十',my_str)
print(my_str3)

my_str33=re.sub('.年','.-',my_str)
print(my_str33)

print('O'=='Ο')

