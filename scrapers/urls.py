import re


def add_page_querystring(url, page_num):
    """Append ?&page=N to url if not already present, else return unchanged."""
    if re.search(r'(\?&page=\d+)$', url):
        return url
    return url + '?&page={}'.format(page_num)


def replace_url_path(url, old_path='yiyuankeshi-pumch-', new_path='yiyuankeshimenzhenshijian-pumch-'):
    """Replace a literal path segment (default: keshi -> menzhen shijian)."""
    return url.replace(old_path, new_path)


def get_link(url):
    """Turn a protocol-relative URL (//domain/path) into a full http URL.

    Returns the input unchanged when it does not match, and None for empty input.
    """
    if not url:
        return None
    m = re.match(r'//(.*?)/(.*?)$', url)
    if not m:
        return url
    domain, path = m.group(1), m.group(2)
    return f'http://{domain}/{path}'


def medicine_urls(count=100000):
    return [f'http://y.wksc.com/goods/{i}.htm' for i in range(1, count + 1)]


def qa_urls(count=1000):
    return [f'http://club.xywy.com/list_all_{i}.htm' for i in range(1, count + 1)]