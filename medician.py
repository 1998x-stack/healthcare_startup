
import sys,os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

from libs.utils import save_js, get_soup
from libs.log import Log
from tqdm import trange
from multiprocessing import Process, Queue


def get_info(url, logger):
    soup = get_soup(url, logger)
    ret_js = {}
    try:
        yao_name = soup.select_one('.yao-name').text.strip()
        care_function = soup.select_one('.ml20:nth-child(1) dd').text.strip()
        price = soup.select_one('.js-price-red').text.strip()
        intro1 = [a.text.strip() for a in soup.select('#pTop dt')]
        intro2 = [a.text.strip() for a in soup.select('#pTop dd')]

        shuomingshu = '\n'.join([a.text.strip() for a in soup.select('#pTop p')])
        xg_yao_name_list = [a.text.strip() for a in soup.select('.xg-yao-name')]

        ret_js['药品名称'] = yao_name
        ret_js['功能主治'] = care_function
        ret_js['参考价格'] = price
        ret_js['商品介绍'] = {a:b for a,b in zip(intro1, intro2)}
        ret_js['说明书'] = shuomingshu
        ret_js['相关药品'] = xg_yao_name_list

        save_js(ret_js, logger=logger, save_folder = './data/medician', file_name=f'{yao_name}.json')
    
        return yao_name, ret_js
    except:
        return None, None


def worker(task_queue, result_queue, logger):
    while True:
        try:
            url = task_queue.get()
            yao_name, ret_js = get_info(url, logger)
            if yao_name:
                result_queue.put((yao_name, ret_js))
            task_queue.task_done()
        except Exception as e:
            logger.log_exception(f"Error while processing {url}: {e}")
            task_queue.task_done()

def main(logger, num_processes=4):
    task_queue = Queue()
    result_queue = Queue()
    processes = []

    # Enqueue tasks
    for i in trange(1, 100001):
        url = f'http://y.wksc.com/goods/{i}.htm'
        task_queue.put(url)

    # Start processes
    for i in range(num_processes):
        p = Process(target=worker, args=(task_queue, result_queue, logger))
        p.daemon = True
        p.start()
        processes.append(p)

    # Wait for tasks to complete
    task_queue.join()

    # Collect results
    js = {}
    while not result_queue.empty():
        yao_name, ret_js = result_queue.get()
        js[yao_name] = ret_js

    # Terminate processes
    for p in processes:
        p.terminate()
    save_js(js, logger=logger, save_folder = './data', file_name='wksc_medician.json')
    return js


if __name__ == '__main__':
    logger = Log('medician')
    main(logger)