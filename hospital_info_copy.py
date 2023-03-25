import sys,os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

import pandas as pd
import re, json
from requests.exceptions import RequestException, Timeout
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup, UnicodeDammit
import time, random
import numpy as np

def transfer2js(df_value):
    js = {
        'hospital_name' : [],
        'hospital_url' : [],
        'hospital_type' : []
    }
    for i, value in enumerate(df_value):
        if isinstance(value, float) and np.isnan(value):
            break
        if i % 3 == 0:
            js['hospital_name'].append(value)
        elif i % 3 == 1:
            assert value.startswith('http')
            js['hospital_url'].append(value)
        else:
            assert value.startswith('(')
            js['hospital_type'].append(value)
    
    return js


def save_js(js, save_folder = './data/', file_name = 'jibinginfo.json'):

    if not os.path.exists(save_folder):
        os.makedirs(save_folder, exist_ok=True)

    # 处理文件名中的非法字符
    for char in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
        file_name = file_name.replace(char, '')
    
    save_path = os.path.join(save_folder, file_name)

    # 保存 JSON 文件
    try:
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(js, f, ensure_ascii=False, indent=4)
        print(f'JSON 文件已成功保存到 {save_path}。')
    except Exception as e:
        print(f'保存 JSON 文件时出错：{str(e)}')

def add_page_querystring(url, page_num):
    # 匹配 URL 末尾是否已经有 ?&page=i 查询字符串
    match = re.search(r'(\?&page=\d+)$', url)
    if match:
        # 如果已经有查询字符串，则直接返回原 URL
        return url
    else:
        # 否则在 URL 末尾加上 ?&page=i 查询字符串，i 为未知数，可在调用函数时传入
        return url + '?&page={}'.format(page_num)

def replace_url_path(url, old_path='yiyuankeshi-pumch-', new_path='yiyuankeshimenzhenshijian-pumch-'):
    # 使用正则表达式匹配需要替换的路径部分
    pattern = re.compile(r'(?<=//)(.*?)(?=/'+old_path+')')
    match = pattern.search(url)

    # 如果找到了需要替换的路径部分，则进行替换
    if match:
        new_url = url.replace(old_path, new_path)
        return new_url
    else:
        # 如果没有找到需要替换的路径部分，则返回原始链接
        return url
    
def get_link(url):
    try:
        # 匹配 URL 中的域名和路径
        match = re.match(r'//(.*?)/(.*?)$', url)
        if not match:
            raise ValueError('Invalid URL')
        domain = match.group(1)
        path = match.group(2)

        # 拼接链接并返回
        link = f'http://{domain}/{path}'
        return link

    except (ValueError, AttributeError):
        return None

def get_soup(url, timeout=10):
    # 创建一个UserAgent对象，用于随机生成User-Agent头
    ua = UserAgent()
    # 定义爬取目标URL和请求头
    headers = {
        'User-Agent': ua.random,
        'Connection': 'keep-alive'
    }

    time.sleep(random.uniform(0.5, 1.5))

    # 发送请求，获取响应
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
    except (RequestException, Timeout):
        print(url, 'status code is: ', response.status_code)
        return None
    # 解析HTML文本
    try:
        soup = BeautifulSoup(response.content, 'html.parser', from_encoding=UnicodeDammit(response.content).original_encoding)
    except AttributeError:
        print("Response content attribute error!!!")
        return None
    return soup
    
    
def get_doctor_info_from_menzhen_list(menzhen_url, max_page=8):
    doctor_info_list = []
    
    for page_num in range(1, max_page+1):
        menzhen_url = add_page_querystring(menzhen_url, page_num)
        menzhen_soup = get_soup(menzhen_url)
        if menzhen_soup is not None:
            for a in menzhen_soup.select('.cca a'):
                doctor_name = a.text.strip()
                doctor_info_url = get_link(a['href'])
                print(f'doctor name : {doctor_name}, doctor url : {doctor_info_url}')
                doctor_soup = get_soup(doctor_info_url)
                # TODO: .showtimetable.db
                doctor_info = '\n'.join([a.text.strip().replace('收起↑', '') for a in doctor_soup.select('.doctor-txt-infor-all')])
                doctor_info_list.append([doctor_name, doctor_info_url, doctor_info])
        else:
            break
        
    return doctor_info_list


def get_hos_info(hos_url, hos_name, hos_type, save_folder):
    print('S=S='*30)
    print(f'hospital info: {hos_name}, {hos_type}, {hos_url}')
    hos_info_js = {
        'hospital_name' : hos_name,
        'hospital_type' : hos_type,
        'hospital_url' : hos_url,
        'keshi_info' : [],
    }
    hos_soup = get_soup(hos_url)
    for a in hos_soup.select('.public-list li > a'):
        keshi_info_js = {}
        # 科室的name，url，介绍
        keshi_name = a.get('title')
        keshi_url = get_link(a['href'])
        jieshao_url = replace_url_path(hos_url, old_path='yiyuankeshi-pumch-', new_path='yiyuankeshijieshao-pumch-')
        jeishao_soup = get_soup(jieshao_url)
        jieshao_select = 'body > div.w1000.mt10.bc.clearfix > div.z-left-site.fl.bdr-top > div.bdr-all.mt20.clearfix > div'
        try:
            jieshao_text = jeishao_soup.select_one(jieshao_select).text.strip()
        except:
            try:
                jieshao_text = jeishao_soup.select_one('.t2').text.strip()
            except:
                jieshao_text = ''
        
        print(f'正在爬取{keshi_name}, 链接是{keshi_url}')
        
        menzhen_url = replace_url_path(keshi_url, old_path='yiyuankeshi-pumch-', new_path='yiyuankeshimenzhenshijian-pumch-')
        
        keshi_info_js['keshi_name'] = keshi_name
        keshi_info_js['keshi_url'] = keshi_url
        keshi_info_js['jieshao_url'] = jieshao_url
        keshi_info_js['jieshao_text'] = jieshao_text
        keshi_info_js['menzhen_url'] = menzhen_url
        keshi_info_js['doctor_info_list'] = get_doctor_info_from_menzhen_list(menzhen_url)
        
        save_js(keshi_info_js, save_folder=os.path.join(save_folder, keshi_name), file_name=f'{keshi_name}.json')
        
        hos_info_js['keshi_info'].append(keshi_info_js)

    save_js(hos_info_js, save_folder=save_folder, file_name=f'{hos_name}_{hos_type}.json')
    print('E=E='*30)
    return hos_info_js


if __name__ == '__main__':
    
    df = pd.read_csv('yiyuandiqu-beijing.csv')
    beijing_js = {col : transfer2js(df[col].values) for col in df.columns}


    beijing_hos_js = {}
    for location, hospital_js in beijing_js.items():
        beijing_hos_js[location] = []
        for hos_name, hos_url, hos_type in zip(hospital_js['hospital_name'], hospital_js['hospital_url'], hospital_js['hospital_type']):
            save_folder = f'./data/hospital/{location}/{hos_name}'
            hos_info_js = get_hos_info(hos_url, hos_name, hos_type, save_folder)
            beijing_hos_js[location].append(hos_info_js)
            
    save_js(beijing_hos_js, save_folder='./data/hospital', file_name='beijing_hospital.json')