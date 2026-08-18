from bs4 import BeautifulSoup

MED_1 = """
<html><body>
  <div class="yao-name">测试药片一</div>
  <div class="wrap"><div class="ml20"><dd>治标一</dd></div><div class="x"></div></div>
  <div class="js-price-red">9.9</div>
  <div id="pTop"><dt>规格</dt><dd>0.25g</dd><p>说明一</p></div>
  <div class="xg-yao-name">相关药A</div>
</body></html>
"""

MED_2 = """
<html><body>
  <div class="yao-name">测试药片二</div>
  <div class="wrap"><div class="ml20"><dd>治标二</dd></div><div class="x"></div></div>
  <div class="js-price-red">19.8</div>
  <div id="pTop"><dt>规格</dt><dd>0.5g</dd><p>说明二</p></div>
  <div class="xg-yao-name">相关药B</div>
</body></html>
"""

FIXTURES = {
    'http://y.wksc.com/goods/1.htm': MED_1,
    'http://y.wksc.com/goods/2.htm': MED_2,
}


def fake_fetch(url):
    """Module-level, picklable-by-reference fake fetcher for offline integration tests."""
    html = FIXTURES.get(url)
    if html is None:
        return None
    return BeautifulSoup(html, 'html.parser')