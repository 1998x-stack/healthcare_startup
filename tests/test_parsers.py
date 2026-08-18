from bs4 import BeautifulSoup

from scrapers.parsers import HospitalParser, MedicineParser, QAParser


def _soup(html):
    return BeautifulSoup(html, 'html.parser')


def _fetch(mapping):
    def fetch(url):
        html = mapping.get(url)
        return _soup(html) if html is not None else None
    return fetch


# --- Medicine ----------------------------------------------------------------

def test_medicine_extracts_fields():
    html = """
    <html><body>
      <div class="yao-name">测试药片</div>
      <div class="wrap"><div class="ml20"><dd>治标</dd></div><div class="x"></div></div>
      <div class="js-price-red">9.9</div>
      <div id="pTop"><dt>规格</dt><dd>0.25g</dd><p>说明文字</p></div>
      <div class="xg-yao-name">相关药A</div>
    </body></html>
    """
    data = MedicineParser().parse(_soup(html))
    assert data['药品名称'] == '测试药片'
    assert data['功能主治'] == '治标'
    assert data['参考价格'] == '9.9'
    assert data['商品介绍'] == {'规格': '0.25g'}
    assert '说明文字' in data['说明书']
    assert data['相关药品'] == ['相关药A']


def test_medicine_returns_none_when_no_name():
    assert MedicineParser().parse(_soup('<div>no drug here</div>')) is None


# --- QA ----------------------------------------------------------------------

LIST_HTML = """
<a class="th" href="ask/1.htm">问题一</a>
<a class="th" href="ask/2.htm">问题二</a>
"""

DETAIL_1 = """
<div class="replay-content-box">答案一</div>
<div class="doc-txt"><span>医生介绍一</span></div>
<div class="doc-goodat">擅长内科</div>
"""

DETAIL_2 = """
<div class="replay-content-box">答案二</div>
"""


def test_qa_extracts_rows():
    fetch = _fetch({
        'http://club.xywy.com/ask/1.htm': DETAIL_1,
        'http://club.xywy.com/ask/2.htm': DETAIL_2,
    })
    rows = QAParser().parse(_soup(LIST_HTML), fetch=fetch)
    assert len(rows) == 2
    q1 = rows[0]
    assert q1[0] == '问题一'
    assert q1[1] == 'http://club.xywy.com/ask/1.htm'
    assert q1[2] == '答案一'
    assert '医生介绍一' in q1[3]
    assert q1[4] == '擅长内科'


def test_qa_returns_falsy_when_no_fetch():
    assert not QAParser().parse(_soup(LIST_HTML), fetch=None)


# --- Hospital ---------------------------------------------------------------

HOSPITAL_HTML = """
<html><body>
  <h1>北京测试医院</h1>
  <ul class="public-list">
    <li><a href="//a.com/yiyuankeshi-pumch-1.html" title="内科">内科</a></li>
  </ul>
</body></html>
"""

MENZHEN_1 = """
<div class="cca"><a href="//a.com/doctor-1.html">张医生</a></div>
"""

DOCTOR_HTML = """
<div class="doctor-txt-infor-all">擅长心脏</div>
"""

JIESHAO_HTML = '<div class="t2">科室介绍文本</div>'


def test_hospital_extracts_keshi_and_doctor():
    keshi_url = 'http://a.com/yiyuankeshi-pumch-1.html'
    jieshao_url = 'http://a.com/yiyuankeshijieshao-pumch-1.html'
    menzhen_p1 = 'http://a.com/yiyuankeshimenzhenshijian-pumch-1.html?&page=1'
    doctor_url = 'http://a.com/doctor-1.html'
    fetch = _fetch({
        jieshao_url: JIESHAO_HTML,
        menzhen_p1: MENZHEN_1,
        doctor_url: DOCTOR_HTML,
    })
    data = HospitalParser().parse(_soup(HOSPITAL_HTML), url='x.htm', fetch=fetch)

    assert data['hospital_name'] == '北京测试医院'
    keshi = data['keshi_info'][0]
    assert keshi['keshi_name'] == '内科'
    assert keshi['keshi_url'] == keshi_url
    assert keshi['jieshao_text'] == '科室介绍文本'
    doc = keshi['doctor_info_list'][0]
    assert doc[0] == '张医生'
    assert doc[1] == doctor_url
    assert doc[2] == '擅长心脏'


def test_hospital_returns_none_without_url():
    assert HospitalParser().parse(_soup(HOSPITAL_HTML), url=None, fetch=None) is None