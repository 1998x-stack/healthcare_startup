# -*- coding: utf-8 -*-

import sys,os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

import time
from multiprocessing import Process, JoinableQueue
from libs.utils import get_soup, save_js
from libs.log import Log

def get_ans_info_good(ques_ans_url, logger):
    soup = get_soup(ques_ans_url, logger=logger)
    try:
        ans_text = '\n'.join([a.text.strip() for a in soup.select('.replay-content-box')])
    except:
        logger.log_exception()
        ans_text = ''
    try:
        info_text = '  '.join([a.text.strip() for a in soup.select('.doc-txt span')])
    except:
        logger.log_exception()
        info_text = ''
    try:
        good_text = soup.select_one('.doc-goodat').text.strip()
    except:
        logger.log_exception()
        good_text = ''
        
    return ans_text, info_text, good_text

def get_head_url(ques_url, prefix_url, logger):
    
    soup = get_soup(ques_url, logger=logger)
    ret_list = []
    for th in soup.select('.th'):
        ques_ans_url = prefix_url + th['href']
        ques_text = th.text.strip()
        ans_text, info_text, good_text = get_ans_info_good(ques_ans_url, logger=logger)
        ret_list.append([ques_text, ques_ans_url, ans_text, info_text, good_text])
    return ret_list


def worker(task_queue, result_queue, prefix_url, logger):
    while True:
        try:
            ques_url = task_queue.get()
            result_queue.put(get_head_url(ques_url, prefix_url, logger))
            task_queue.task_done()
        except Exception as e:
            print(f"Error while processing {ques_url}: {e}")
            task_queue.task_done()

def main(prefix_url, logger, file_name, start_time, num_processes = 4):
    
    task_queue = JoinableQueue()
    result_queue = JoinableQueue()
    processes = []

    # Enqueue tasks
    for ques_url in ques_url_list:
        task_queue.put(ques_url)

    # Start processes
    for i in range(num_processes):
        p = Process(target=worker, args=(task_queue, result_queue,  prefix_url, logger))
        p.daemon = True
        p.start()
        processes.append(p)

    # Wait for tasks to complete
    task_queue.join()

    # Collect results
    final_list = []
    while not result_queue.empty():
        final_list.extend(result_queue.get())
        time_now = time.time()
        if time_now -  start_time > 100:
            save_js({'ques_ans':final_list}, logger, save_folder='./data/', file_name=file_name)
            start_time = time_now
        
    
    # Terminate processes
    for p in processes:
        p.terminate()

    # Process results
    save_js({'ques_ans':final_list}, logger, save_folder='./data/', file_name=file_name)


if __name__ == '__main__':
    ques_url_list = [f'http://club.xywy.com/list_all_{i}.htm' for i in range(1,1001)]
    file_name = 'ques_ans.js'
    prefix_url = 'http://club.xywy.com'
    logger = Log('ques_ans')
    start_time = time.time()
    main(prefix_url, logger, file_name, start_time, num_processes=10)