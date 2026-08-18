"""Per-site parsers bound to scrapers via the factory.

Each parser implements ``parse(soup, url=None, fetch=None, logger=None)`` and
returns a dict (or list) record extracted from the page. ``fetch(url) -> soup``
is injected so parsers can reach sub-pages; in production it defaults to
``libs.utils.get_soup`` and in tests to a fixture-driven fake.
"""

import abc
from urllib.parse import urljoin

from scrapers.urls import add_page_querystring, get_link, replace_url_path

QA_PREFIX = 'http://club.xywy.com'


class BaseParser(abc.ABC):
    name = 'base'

    @abc.abstractmethod
    def parse(self, soup, url=None, fetch=None, logger=None):
        raise NotImplementedError


class MedicineParser(BaseParser):
    name = 'medicine'

    def parse(self, soup, url=None, fetch=None, logger=None):
        yao_tag = soup.select_one('.yao-name')
        if yao_tag is None:
            return None
        yao_name = yao_tag.text.strip()
        intro_dt = [a.text.strip() for a in soup.select('#pTop dt')]
        intro_dd = [a.text.strip() for a in soup.select('#pTop dd')]
        return {
            '药品名称': yao_name,
            '功能主治': soup.select_one('.ml20:nth-child(1) dd').text.strip()
            if soup.select_one('.ml20:nth-child(1) dd') else '',
            '参考价格': soup.select_one('.js-price-red').text.strip()
            if soup.select_one('.js-price-red') else '',
            '商品介绍': dict(zip(intro_dt, intro_dd)),
            '说明书': '\n'.join(p.text.strip() for p in soup.select('#pTop p')),
            '相关药品': [a.text.strip() for a in soup.select('.xg-yao-name')],
        }


class QAParser(BaseParser):
    name = 'qa'
    prefix = QA_PREFIX

    def parse(self, soup, url=None, fetch=None, logger=None):
        if fetch is None:
            return None
        rows = []
        for th in soup.select('.th'):
            href = th.get('href', '')
            detail_url = urljoin(self.prefix, href)
            ques_text = th.text.strip()
            detail_soup = fetch(detail_url)
            ans_text = info_text = good_text = ''
            if detail_soup is not None:
                ans_text = '\n'.join(
                    a.text.strip() for a in detail_soup.select('.replay-content-box'))
                info_text = '  '.join(
                    a.text.strip() for a in detail_soup.select('.doc-txt span'))
                good_tag = detail_soup.select_one('.doc-goodat')
                if good_tag is not None:
                    good_text = good_tag.text.strip()
            rows.append([ques_text, detail_url, ans_text, info_text, good_text])
        return rows


class HospitalParser(BaseParser):
    name = 'hospital'
    max_page = 8

    # -- keshi page selectors -------------------------------------------------
    jieshao_select = ('body > div.w1000.mt10.bc.clearfix > div.z-left-site.fl.bdr-top '
                      '> div.bdr-all.mt20.clearfix > div')

    def parse(self, soup, url=None, fetch=None, logger=None):
        if url is None or soup is None:
            return None

        name_tag = soup.select_one('h1') or soup.select_one('.hos-name')
        hospital_name = name_tag.text.strip() if name_tag else ''

        keshi_info = []
        for a in soup.select('.public-list li > a'):
            keshi_name = a.get('title')
            keshi_url = get_link(a['href'])
            if not keshi_name or not keshi_url:
                continue

            jieshao_url = replace_url_path(keshi_url, 'yiyuankeshi-', 'yiyuankeshijieshao-')
            jieshao_text = self._jieshao_text(jieshao_url, fetch)

            menzhen_url = replace_url_path(keshi_url, 'yiyuankeshi-', 'yiyuankeshimenzhenshijian-')
            doctor_list = self._doctor_list(menzhen_url, fetch)

            keshi_info.append({
                'keshi_name': keshi_name,
                'keshi_url': keshi_url,
                'jieshao_url': jieshao_url,
                'jieshao_text': jieshao_text,
                'menzhen_url': menzhen_url,
                'doctor_info_list': doctor_list,
            })

        return {
            'hospital_name': hospital_name,
            'hospital_url': url,
            'keshi_info': keshi_info,
        }

    def _jieshao_text(self, jieshao_url, fetch):
        if fetch is None:
            return ''
        jieshao_soup = fetch(jieshao_url)
        if jieshao_soup is None:
            return ''
        node = jieshao_soup.select_one(self.jieshao_select)
        if node is not None:
            return node.text.strip()
        node = jieshao_soup.select_one('.t2')
        return node.text.strip() if node is not None else ''

    def _doctor_list(self, menzhen_url, fetch):
        doctor_list = []
        if fetch is None:
            return doctor_list
        for page_num in range(1, self.max_page + 1):
            page_url = add_page_querystring(menzhen_url, page_num)
            menzhen_soup = fetch(page_url)
            if menzhen_soup is None:
                break
            links = menzhen_soup.select('.cca a')
            if not links:
                break
            for a in links:
                doctor_name = a.text.strip()
                doctor_info_url = get_link(a['href'])
                doctor_info = ''
                if doctor_info_url:
                    doctor_soup = fetch(doctor_info_url)
                    if doctor_soup is not None:
                        doctor_info = '\n'.join(
                            n.text.strip().replace('收起↑', '')
                            for n in doctor_soup.select('.doctor-txt-infor-all'))
                doctor_list.append([doctor_name, doctor_info_url, doctor_info])
        return doctor_list


PARSER_REGISTRY = {
    'hospital': HospitalParser,
    'medicine': MedicineParser,
    'qa': QAParser,
}