import urllib.parse
import re
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlencode, unquote, quote_plus
import requests
import xml.etree.ElementTree as et


def url_encode():
    url = 'http://www.geosangkorea.com/shop/goods/goods_view.php'
    params = [
        {
            'goodsno': '19069',
            'category': '012021005'},
        {
            'goodsno': '19068',
            'category': '012021005'},
        {
            'goodsno': '20609',
            'category': '012021005'},
        {
            'goodsno': '19072',
            'category': '012021005'},
        {
            'goodsno': '19571',
            'category': '012021005'},
        {
            'goodsno': '20611',
            'category': '012021005'},
        {
            'goodsno': '21106',
            'category': '019011'},
        {
            'goodsno': '21108',
            'category': '019011'},
        {
            'goodsno': '21109',
            'category': '019011'},
    ]

    urls = []
    for param in params:
        encoded_args = urlencode(param, safe='%')
        goods_url = url + '?' + encoded_args
        urls.append(goods_url)
    return urls


def get_html(url):
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'html5lib')
    return soup


def main():
    session = get_session()
    goods_urls = url_encode()

    for goods_url in goods_urls:
        get_options(session, goods_url)


def get_session():
    login_url = 'http://www.geosangkorea.com/shop/member/login_ok.php'
    user = 'mahafishing'
    password = 'akgkvltld0125!'
    session = requests.session()
    params = dict()
    params['m_id'] = user
    params['password'] = password
    res = session.post(login_url, data=params)
    res.raise_for_status()
    print(res.headers)
    print(session.cookies.get_dict())
    return session


def get_options(session, goods_url):
    goods_res = session.get(goods_url)
    soup = BeautifulSoup(goods_res.content, 'html5lib')

    # 전체 페이지에서 제품 스펙 있는 디비젼만 오려온다.
    goods_spec = soup.find('div', attrs={'id': 'goods_spec'})

    # 제품 이름
    goods_name = goods_spec.find('div', attrs={'style': 'padding:10px 0 10px 5px'})
    goods_name_text = goods_name.get_text().strip()
    print(goods_name_text)

    # 제품 옵션별 개수
    options = goods_spec.find_all('option')
    for option in options:
        option_text = option.get_text().strip()
        print(option_text)







    print('Good!')








if __name__ == '__main__' :
    main()