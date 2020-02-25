import sys
import requests
import time
from datetime import datetime
from bs4 import BeautifulSoup
from Encrypt import Encrypt


class Student:
    """
    stu = {
        'stuid': "学号",
        'password': "密码",
        (可选)'year': 当前年份,
        (可选)'term': 当前学期
    }
    """

    def __init__(self, stu):
        self.session = requests.session()
        self.stuid = stu['stuid']
        self.password = stu['password']
        try:
            self.year = int(stu['year'])
            self.term = int(stu['term'])
        except:
            if datetime.now().month <= 8:
                self.year = datetime.now().year - 1
                if datetime.now().month <= 2:
                    # 第二学期
                    self.term = 1
                else:
                    # 第一学期
                    self.term = 1
            else:
                # 第一学期
                self.year = datetime.now().year
                self.term = 1
        if self.term == 1:
            self.term = 3
        else:
            self.term = 12
        self.login()

    def login(self):
        session = self.session
        stuid = self.stuid
        password = self.password

        time_now = int(time.time())
        session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'Content-Length': '0',
            'Host': 'jwgl.njtech.edu.cn',
            'Referer': 'https://jwgl.njtech.edu.cn/',
            'Upgrade-Insecure-Requests': '1'
        })
        # print(time_now)

        # 准备publickey
        url = 'https://jwgl.njtech.edu.cn/xtgl/login_getPublicKey.html?time=' + str(time_now)
        r = session.get(url)
        publickey = r.json()

        # 准备csrftoken
        url = 'https://jwgl.njtech.edu.cn/xtgl/login_slogin.html?language=zh_CN&_t=' + str(time_now)
        r = session.get(url)
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, 'html.parser')
        csrftoken = soup.find('input', attrs={'id': 'csrftoken'}).attrs['value']
        # print(csrftoken)

        # 准备密码
        # print(publickey['modulus'])
        # print(publickey['exponent'])
        encrypt = Encrypt(publickey['modulus'], publickey['exponent'], password)
        rsacode = encrypt.rsa_encrypt()

        try:
            url = 'https://jwgl.njtech.edu.cn/xtgl/login_slogin.html?time=' + str(time_now)
            data = {
                'csrftoken': csrftoken,
                'mm': rsacode,
                'yhm': stuid
            }
            result = session.post(url, data=data)
            if '用户名或密码不正确' in result.text:
                raise FError("用户名或密码错误")
        except FError:
            raise FError("用户名或密码错误")
        except:
            raise FError("false 未知错误，请联系网站管理员")

    def info(self):
        session = self.session
        url = 'https://jwgl.njtech.edu.cn/xsxxxggl/xsgrxxwh_cxXsgrxx.html?gnmkdm=N100801&layout=default'
        data = {}

        try:
            info = session.get(url)
            info.encoding = info.apparent_encoding
            soup = BeautifulSoup(info.text, 'html.parser')
            data['id'] = soup.find(id='col_xh').find(class_="form-control-static").string
            data['name'] = soup.find(id='col_xm').find(class_="form-control-static").string
            data['grade'] = soup.find(id='col_njdm_id').find(class_="form-control-static").string
            data['grade'] = data['grade'].replace("\t", "").replace("\n", "").replace("\r", "")
            data['college'] = soup.find(id='col_jg_id').find(class_="form-control-static").string
            data['college'] = data['college'].replace("\t", "").replace("\n", "").replace("\r", "")
            data['major'] = soup.find(id='col_zyh_id').find(class_="form-control-static").string
            data['major'] = data['major'].replace("\t", "").replace("\n", "").replace("\r", "")
            data['class'] = soup.find(id='col_bh_id').find(class_="form-control-static").string
            data['class'] = data['class'].replace("\t", "").replace("\n", "").replace("\r", "")
            return data
        except:
            raise FError("未知错误，请联系网站管理员")

    def course(self):
        session = self.session
        data = []
        url = 'https://jwgl.njtech.edu.cn/kbcx/xskbcx_cxXsKb.html?gnmkdm=N2151'

        try:
            form_data = {
                'xnm': self.year,
                'xqm': self.term,
            }
            lesson = session.post(url, data=form_data)
            lesson = lesson.json()
            stuid = lesson['xsxx']['XH']
            for item in lesson['kbList']:
                data.append({
                    'tittle': item['kcmc'],
                    'day': item['xqj'],
                    'time': item['jcs'],
                    'week': item['zcd']
                })
            # print(str(data))
            data = self.standardise(data)
            if len(data) == 0:
                raise FError("当前学期课表为空，请联系管理员修改")
            return data
        except FError:
            raise FError("当前学期课表为空，请联系管理员修改")
        except:
            raise FError("未知错误，请联系网站管理员")

    @staticmethod
    def standardise(data):
        for lesson in data:
            # time
            time_start = int(lesson['time'].split("-")[0])
            time_end = int(lesson['time'].split("-")[1])
            # print("%d %d" % (time_start, time_end))
            lesson['time'] = ""
            for t in range(time_start, time_end + 1):
                lesson['time'] += str(t) + ','
            # week
            week = ""
            week_str = lesson['week']
            week_str = week_str.replace("周", "")
            week_str = week_str.split(",")
            for sub_week_str in week_str:
                if sub_week_str.find("(双)") != -1 or sub_week_str.find("(单)") != -1:
                    step = 2
                else:
                    step = 1
                sub_week_str = sub_week_str.replace("(双)", "")
                sub_week_str = sub_week_str.replace("(单)", "")
                sub_week_str = sub_week_str.split("-")
                first = int(sub_week_str[0])
                last = int(sub_week_str[len(sub_week_str) - 1])
                # print("MIN"+str(first)+" MAX"+str(last))
                for i in range(first, last + 1, step):
                    week += str(i) + ","
            # week = week.rstrip(",")
            lesson['week'] = week
            # print(str(lesson))
        return data

    def grade(self):
        session = self.session
        data = []
        url = 'https://jwgl.njtech.edu.cn/cjcx/cjcx_cxDgXscj.html?doType=query&gnmkdm=N305005'

        try:
            form_data = {
                'xnm': self.year,
                'xqm': self.term,
            }
            grades = session.post(url, data=form_data)
            # grades = session.post(url)
            grades = grades.json()
            # print(grades)
            for item in grades['items']:
                data.append({
                    'tittle': item['kcmc'],
                    'credit': item['xf'],
                    'grade': item['cj'],
                    'point': item['jd'],
                })
            if len(data) == 0:
                raise FError("当前学期成绩为空，请联系管理员修改")
            return data
        except FError:
            raise FError("当前学期成绩为空，请联系管理员修改")
        except:
            raise FError("未知错误，请联系网站管理员")


class FError(Exception):
    pass


if __name__ == "__main__":
    stu = {
        'stuid': sys.argv[1],
        'password': sys.argv[2],
        'year': sys.argv[3],
        'term': sys.argv[4]
    }
    try:
        student = Student(stu)
        for info in student.info().items():
            print(info)
        print()
        for course in student.course():
            print(course)
        print()
        for grade in student.grade():
            print(grade)
    except Exception as e:
        print(e)
