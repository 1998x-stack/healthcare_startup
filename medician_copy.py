
from libs.utils import save_js, get_soup
from libs.log import Log
from tqdm import trange

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

        save_js(js, logger=logger, save_folder = './data/medician', file_name=f'{yao_name}.json')
    
        return yao_name, ret_js
    except:
        return None, None
    
    
if __name__ == '__main__':
    # TODO: 10,0000
    logger = Log('medician')
    js = {}
    for i in trange(1, 100001):
        url = f'http://y.wksc.com/goods/{i}.htm'
        yao_name, ret_js = get_info(url, logger)
        if yao_name:
            js[yao_name] = ret_js
        

    save_js(js, logger=logger, save_folder = './data', file_name='wksc_medician.json')

