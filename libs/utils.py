import sys,os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

import requests
from requests.exceptions import RequestException, Timeout
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import json, time, random, csv, codecs


def save_js(js, logger, save_folder = './data/', file_name = 'jibinginfo.json', exists_ok=False):

    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    # 处理文件名中的非法字符
    for char in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
        file_name = file_name.replace(char, '')

    
    save_path = os.path.join(save_folder, file_name)

    # 保存 JSON 文件
    try:
        if exists_ok and os.path.exists(save_path):
            with codecs.open(save_path, 'a', encoding='utf-8') as f:
                json.dump(js, f, ensure_ascii=False, indent=4)
        else:
            with codecs.open(save_path, 'w', encoding='utf-8') as f:
                json.dump(js, f, ensure_ascii=False, indent=4)
        logger.log_info(f'JSON 文件{file_name} 已成功保存到 {save_path}')
    except Exception as e:
        print(f'保存 JSON 文件{file_name} 时出错：{str(e)}')
        logger.log_exception()

def save_csv(data, logger, save_folder='./data/', file_name='data.csv'):
    # 如果目录不存在则创建
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    # 处理文件名中的非法字符
    for char in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
        file_name = file_name.replace(char, '')

    save_path = os.path.join(save_folder, file_name)
    
    # 保存 CSV 文件
    try:
        with open(save_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for row in data:
                writer.writerow(row)
        logger.log_info(f'CSV 文件{file_name} 已成功保存到 {save_path}')
    except Exception as e:
        print(f'保存 CSV 文件{file_name} 时出错：{str(e)}')
        logger.log_exception()

def get_soup(url, logger, timeout=10):
    # 创建一个UserAgent对象，用于随机生成User-Agent头
    ua = UserAgent()
    # 定义爬取目标URL和请求头
    headers = {
        'User-Agent': ua.random,
    }

    time.sleep(random.uniform(0.5, 1.5))

    # 发送请求，获取响应
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
    except (RequestException, Timeout):
        logger.log_exception(url, 'status code is: ', response.status_code)
        return None
    # 解析HTML文本
    try:
        soup = BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')
    except AttributeError:
        logger.log_exception("Response content attribute error!!!")
        return None
    return soup