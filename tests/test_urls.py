from scrapers.urls import add_page_querystring, get_link, medicine_urls, qa_urls, replace_url_path


def test_add_page_querystring_only_once():
    u = 'http://x/y1.htm'
    u2 = add_page_querystring(u, 2)
    assert u2.endswith('?&page=2')
    assert add_page_querystring(u2, 3) == u2


def test_get_link_full_url():
    assert get_link('//a.com/p/q.htm') == 'http://a.com/p/q.htm'


def test_get_link_no_match_returns_input():
    assert get_link('http://full.com/x.htm') == 'http://full.com/x.htm'


def test_replace_url_path():
    base = 'http://a.com/yiyuankeshi-pumch-x.htm'
    out = replace_url_path(base, 'yiyuankeshi-pumch-', 'yiyuankeshimenzhenshijian-pumch-')
    assert 'yiyuankeshimenzhenshijian-pumch-x.htm' in out


def test_medicine_urls_shape():
    urls = medicine_urls(count=5)
    assert len(urls) == 5
    assert urls[0] == 'http://y.wksc.com/goods/1.htm'
    assert urls[-1] == 'http://y.wksc.com/goods/5.htm'


def test_qa_urls_shape():
    urls = qa_urls(count=3)
    assert len(urls) == 3
    assert urls[0] == 'http://club.xywy.com/list_all_1.htm'
    assert urls[-1] == 'http://club.xywy.com/list_all_3.htm'