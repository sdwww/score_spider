import os
import re
import threading
import time

import requests

from ScoreThread import ScoreThread


# 保存网页内容
def save_html(save_path, file_name, content):
    try:
        if not os.path.isdir(save_path + '/'):
            os.mkdir(save_path + '/')
        html = open(save_path + '/' + file_name + '.html', 'w', encoding='utf-8')
        html.write(content)
        html.close()
        return True
    except IOError:
        return False


def get_school_dict(session, head):
    # 获取大学与id关系并保存
    school_dict = {}
    for i in range(1, 5):
        content = session.get(
            'http://data.api.gkcx.eol.cn/soudaxue/queryschool.html?messtype=jsonp&'
            'callback=jQuery18307013630659283934_1497580101517&province=&schooltype=&'
            'page=' + str(i) + '&size=30&keyWord1=&schoolprop=&'
                               'schoolflag=211%E5%B7%A5%E7%A8%8B&schoolsort=&schoolid=&_=1497580101995',
            headers=head).text
        page_name = 'school_id_' + str(i)
        if save_html('./saved_html', page_name, content):
            print('网页' + page_name + '保存成功')
        else:
            print('网页' + page_name + '保存失败')
        # print(content[content.find('schoolid'):150])

        p_id = r'schoolid.+"(.+)"'
        pattern_id = re.compile(p_id)
        school_id_list = pattern_id.findall(content)

        p_name = r'schoolname.+"(.+)"'
        pattern_name = re.compile(p_name)
        school_name_list = pattern_name.findall(content)

        for i in range(len(school_id_list)):
            school_dict[school_name_list[i]] = school_id_list[i]
    return school_dict


def get_province_dict():
    # 获取省份与id关系并保存
    province_dict = {"安徽": "10008", "澳门": "10145", "北京": "10003", "重庆": "10028", "福建": "10024",
                     "甘肃": "10023", "贵州": "10026", "广东": "10011", "广西": "10012", "河北": "10016",
                     "河南": "10017", "黑龙江": "10031", "湖北": "10021", "湖南": "10022", "海南": "10019",
                     "江苏": "10014", "江西": "10015", "吉林": "10004", "辽宁": "10027", "内蒙古": "10002",
                     "宁夏": "10007", "青海": "10030", "上海": "10000", "山东": "10009", "山西": "10010",
                     "陕西": "10029", "四川": "10005", "天津": "10006", "新疆": "10013", "西藏": "10025",
                     "香港": "10020", "云南": "10001", "台湾": "10146", "浙江": "10018"}
    return province_dict


# 生成路径
def build_path(school_dict, province_dict):
    subject_dict = {'文科': 10034, '理科': 10035}
    complete_path = []
    for province_name, province_id in province_dict.items():
        for subject_name, subject_id in subject_dict.items():
            for school_name, school_id in school_dict.items():
                for year in range(2014, 2017):
                    url = 'http://gkcx.eol.cn/schoolhtm/specialty/' + str(
                        school_id) + '/' + str(subject_id) + '/specialtyScoreDetail_' \
                          + str(year) + '_' + str(province_id) + '.htm'
                    complete_path.append([province_name, subject_name, school_name + str(year), url])
    return complete_path


# 创建多线程
def create_threads(thread_count, session, lock, path, head):
    threads = []
    for i in range(thread_count):
        course_thread = ScoreThread(name=i, session=session, lock=lock, path=path, head=head)
        course_thread.start()
        threads.append(course_thread)
    for thread in threads:
        thread.join()

# #读取错误文件
# def read_error_log():

if __name__ == "__main__":
    start = time.clock()
    course_session = requests.session()
    # 构造headers
    agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' \
            '(KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36'
    headers = {
        "Host": "gkcx.eol.cn",
        'User-Agent': agent
    }

    school_info = get_school_dict(course_session, headers)
    province_info = get_province_dict()
    complete_path = build_path(school_info, province_info)
    #
    course_lock = threading.RLock()
    create_threads(thread_count=1, session=course_session, lock=course_lock, path=complete_path, head=headers)
    print('总时间为:', time.clock() - start)
