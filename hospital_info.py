# -*- coding: utf-8 -*-

import sys,os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))


from libs.utils import save_js, get_soup
from libs.log import Log


from multiprocessing import Process
from queue import Queue
import pandas as pd
import numpy as np
import json, re
logger = Log('hospital_info')


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

def get_doctor_info_from_menzhen_list(menzhen_url, logger,  max_page=8):
    doctor_info_list = []
    
    for page_num in range(1, max_page+1):
        menzhen_url = add_page_querystring(menzhen_url, page_num)
        menzhen_soup = get_soup(menzhen_url)
        if menzhen_soup is not None:
            for a in menzhen_soup.select('.cca a'):
                doctor_name = a.text.strip()
                doctor_info_url = get_link(a['href'])
                logger.info(f'doctor name : {doctor_name}, doctor url : {doctor_info_url}')
                doctor_soup = get_soup(doctor_info_url)
                # TODO: .showtimetable.db
                doctor_info = '\n'.join([a.text.strip().replace('收起↑', '') for a in doctor_soup.select('.doctor-txt-infor-all')])
                doctor_info_list.append([doctor_name, doctor_info_url, doctor_info])
        else:
            break
        
    return doctor_info_list



def get_hos_info(hos_url, hos_name, hos_type, save_folder, logger):
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
        keshi_info_js['doctor_info_list'] = get_doctor_info_from_menzhen_list(menzhen_url, logger)
        
        save_js(keshi_info_js, save_folder=os.path.join(save_folder, keshi_name), file_name=f'{keshi_name}.json', exists_ok=True)
        
        hos_info_js['keshi_info'].append(keshi_info_js)

    save_js(hos_info_js, save_folder=save_folder, file_name=f'{hos_name}_{hos_type}.json', exists_ok=True)
    print('E=E='*30)
    return hos_info_js




def worker(task_queue, result_queue, save_folder, logger=logger):
    while True:
        try:
            location, hos_url, hos_name, hos_type = task_queue.get()
            hos_info_js = get_hos_info(hos_url, hos_name, hos_type, os.path.join(os.path.join(save_folder, location), hos_name), logger)
            result_queue.put({'location' : location , 'hos_info_js' : hos_info_js})
            task_queue.task_done()
        except Exception as e:
            print(f"Error while processing {hos_url}: {e}")
            logger.log_exception()
            task_queue.task_done()


def main(beijing_js, save_folder, logger, num_processes=4):
    task_queue = Queue()
    result_queue = Queue()
    processes = []

    # Enqueue tasks
    for location, hospital_js in beijing_js.items():
        for hos_name, hos_url, hos_type in zip(hospital_js['hospital_name'], hospital_js['hospital_url'], hospital_js['hospital_type']):
            task_queue.put((location, hos_url, hos_name, hos_type))

    # Start processes
    for i in range(num_processes):
        p = Process(target=worker, args=(task_queue, result_queue, save_folder))
        p.daemon = True
        p.start() # TypeError: cannot pickle '_thread.lock' object
        processes.append(p)

    # Wait for tasks to complete
    task_queue.join()

    # Collect results
    beijing_hos_js = {}
    while not result_queue.empty():
        location_hos_info_js = result_queue.get()
        location = location_hos_info_js['location']
        hos_info_js = location_hos_info_js['hos_info_js']
        if location not in beijing_hos_js:
            beijing_hos_js[location] = []
        beijing_hos_js[location].append(hos_info_js)

    # Terminate processes
    for p in processes:
        p.terminate()

    save_js(beijing_hos_js, save_folder=save_folder, file_name='beijing_hospital.json')
    
    return beijing_hos_js


if __name__ == '__main__':
    
    
    
    if not os.path.exists('./beijing_hospital.json'):
        df = pd.read_csv('yiyuandiqu-beijing.csv')
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

        beijing_js = {col : transfer2js(df[col].values) for col in df.columns}

        save_js(beijing_js, logger=logger, save_folder='.', file_name='beijing_hospital.json')
    else:
        with open('beijing_hospital.json', 'r', encoding='utf-8') as f:
            beijing_js = json.load(f)
            
            
    
    main(beijing_js, save_folder = './data/hospital0', logger=logger, num_processes=4)