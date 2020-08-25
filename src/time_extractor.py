import re
import chardet
from datetime import datetime,timedelta


# 匹配正则表达式
matchs = {
    1:(r'\d{4}%s\d{1,2}%s\d{1,2}%s \d{1,2}%s\d{1,2}%s\d{1,2}%s','%%Y%s%%m%s%%d%s %%H%s%%M%s%%S%s'),
    2:(r'\d{4}%s\d{1,2}%s\d{1,2}%s \d{1,2}%s\d{1,2}%s','%%Y%s%%m%s%%d%s %%H%s%%M%s'),
    3:(r'\d{4}%s\d{1,2}%s\d{1,2}%s','%%Y%s%%m%s%%d%s'),
    4:(r'\d{2}%s\d{1,2}%s\d{1,2}%s','%%y%s%%m%s%%d%s'),
   
    # 没有年份
    5:(r'\d{1,2}%s\d{1,2}%s \d{1,2}%s\d{1,2}%s\d{1,2}%s','%%m%s%%d%s %%H%s%%M%s%%S%s'),
    6:(r'\d{1,2}%s\d{1,2}%s \d{1,2}%s\d{1,2}%s','%%m%s%%d%s %%H%s%%M%s'),
    7:(r'\d{1,2}%s\d{1,2}%s','%%m%s%%d%s'),
    

    # 没有年月日
    8:(r'\d{1,2}%s\d{1,2}%s\d{1,2}%s','%%H%s%%M%s%%S%s'),
    9:(r'\d{1,2}%s\d{1,2}%s','%%H%s%%M%s'),
}

# 正则中的%s分割
splits = [
    {1:[('年','月','日','点','分','秒'),('-','-','',':',':',''),('\/','\/','',':',':',''),('\.','\.','',':',':','')]},
    {2:[('年','月','日','点','分'),('-','-','',':',''),('\/','\/','',':',''),('\.','\.','',':','')]},
    {3:[('年','月','日'),('-','-',''),('\/','\/',''),('\.','\.','')]},
    {4:[('年','月','日'),('-','-',''),('\/','\/',''),('\.','\.','')]},

    {5:[('月','日','点','分','秒'),('-','',':',':',''),('\/','',':',':',''),('\.','',':',':','')]},
    {6:[('月','日','点','分'),('-','',':',''),('\/','',':',''),('\.','',':','')]},
    {7:[('月','日'),('-',''),('\/',''),('\.','')]},

    {8:[('点','分','秒'),(':',':','')]},
    {9:[('点','分'),(':','')]},
]

def func(parten,tp):
    re.search(parten,parten)
    

parten_other = '\d+天前|\d+分钟前|\d+小时前|\d+秒前'

class TimeFinder(object):

    def __init__(self,base_date=None):
        self.base_date = base_date
        self.match_item = []
        
        self.init_args()
        self.init_match_item()

    def init_args(self):
        # 格式化基础时间
        if not self.base_date:
            self.base_date = datetime.now()
        if self.base_date and not isinstance(self.base_date,datetime):
            try:
                self.base_date = datetime.strptime(self.base_date,'%Y-%m-%d %H:%M:%S')
            except Exception as e:
                raise 'type of base_date must be str of%Y-%m-%d %H:%M:%S or datetime'

    def init_match_item(self):
        # 构建穷举正则匹配公式 及提取的字符串转datetime格式映射
        for item in splits:
            for num,value in item.items():
                match = matchs[num]
                for sp in value:
                    tmp = []
                    for m in match:
                        tmp.append(m%sp)
                    self.match_item.append(tuple(tmp))

    def get_time_other(self,text):
        m = re.search('\d+',text)
        if not m:
            return None
        num = int(m.group())
        if '天' in text:
            return self.base_date - timedelta(days=num)
        elif '小时' in text:
            return self.base_date - timedelta(hours=num)
        elif '分钟' in text:
            return self.base_date - timedelta(minutes=num)
        elif '秒' in text:
            return self.base_date - timedelta(seconds=num)

        return None

    def find_time(self,text):
         # 格式化text为str类型
        if isinstance(text,bytes):
            encoding =chardet.detect(text)['encoding']
            text = text.decode(encoding)

        res = []
        parten = '|'.join([x[0] for x in self.match_item])

        parten = parten+ '|' +parten_other
        match_list = re.findall(parten,text)
        if not match_list:
            return None
        for match in match_list:
            for item in self.match_item:
                try:
                    date = datetime.strptime(match,item[1].replace('\\',''))
                    if date.year==1900:
                        date = date.replace(year=self.base_date.year)
                        if date.month==1:
                            date = date.replace(month=self.base_date.month)
                            if date.day==1:
                                date = date.replace(day=self.base_date.day)
                    res.append(datetime.strftime(date,'%Y-%m-%d %H:%M:%S'))
                    break
                except Exception as e:
                    date = self.get_time_other(match)
                    if date:
                        res.append(datetime.strftime(date,'%Y-%m-%d %H:%M:%S'))
                        break
        if not res:
            return None
        return res

def test():
    timefinder =TimeFinder(base_date='2020-04-23 00:00:00')
    for text in ['2012年12月12日','3小时前','在2012/12/13哈哈','时间2012-12-11 12:22:30','日期2012-13-11','测试2013.12.24','今天12:13']:
        res = timefinder.find_time(text)
        print('text----',text)
        print('res---',res)

if __name__ == '__main__':
    test()
