import urllib.parse
import re
from bs4 import BeautifulSoup
import requests

class FishingCrawler:

    def __init__(self, ue=None):
        # 초기화 필요한 컨테이너 변수들 선언
        self.soup = None
        self.fishing_record = dict()
        self.ue = ue


    def get_html(self, url=None):
        if url is not None :
            self.url = url
        else:
            print("check : url is None")
            print("check : req is None")
            return

        req = requests.get(self.url)
        self.soup = BeautifulSoup(req.content, 'html5lib')
        # return self.soup


    def extract_angler_info(self, soup=None):
        if self.soup is not None:
            s = self.soup
        elif soup is not None:
            s = soup
        else:
            print("check : soup is None")
            return

        maintext = s.find('div', attrs={'id': 'mainTextBodyDiv'})
        angler_info_table_lefts = maintext.find_all('td', attrs={'class': 'b_detail_left'})
        angler_info_table_rights = maintext.find_all('td', attrs={'class': 'b_detail_right'})

        def _combine_strip(angler_info_table_lefts, angler_info_table_rights):
            for angler_info_left, angler_info_right in zip(angler_info_table_lefts, angler_info_table_rights):
                left_text = angler_info_left.get_text().strip()
                right_text = angler_info_right.get_text().strip()
                self.fishing_record[left_text] = right_text

        _combine_strip(angler_info_table_lefts, angler_info_table_rights)
        self.maintext = maintext


    def extract_body_text(self, bodytextID='bodytextID2247'):
        # import re
        def _remove_control_chart(s):
            return re.sub('[\t\xa0]', '', s)

        if self.maintext is None:
            print("check : maintext is None")
            return

        body_text_raw = self.maintext.find('td', attrs={'id': bodytextID})

        if body_text_raw is None:
            self.fishing_record['body_text'] = 'This document does not exist.'
            return
        else:
            body_text_striped = body_text_raw.get_text().strip()
            body_text = _remove_control_chart(body_text_striped)
            self.fishing_record['body_text'] = body_text


    def crawl(self):
        ue = self.ue
        for url in ue:
            self.get_html(url)
            self.extract_angler_info()
            bodytextID = ue.get_bodytextID()
            self.extract_body_text(bodytextID)
            print(self.fishing_record)


class UrlEncoder:
    # import urllib.parse
    def __init__(self, site_url='http://www.innak.kr/php/board.php',
                 params={'board':'bhotangler2019','command':'body','no':'2247'},
                 no_list=None):
        self.site_url=site_url
        self.params=params
        self.url = None
        self.no_list = no_list
        self.size = None
        self.index = None


    def __iter__(self):
        self.index = 0
        self.size = len(self.no_list)
        return self

    def __next__(self):
        if self.index >= self.size:
            raise StopIteration

        num = self.no_list[self.index]
        self.params['no'] = str(num)
        self.url = self.combine()

        self.index += 1
        return self.url


    def combine(self):
        encoded_params = urllib.parse.urlencode(self.params)
        self.url = self.site_url + '?' + encoded_params
        return self.url


    def get_url(self):
        if self.url is None:
            print("check : url is None")

        return self.url


    def get_next_url(self):
        num_str = self.params['no']
        num_int = int(num_str) + 1
        num_str = str(num_int)
        self.params['no'] = num_str
        self.combine()
        return self.url

    def get_bodytextID(self):
        if self.params is None:
            print('check : params')
        else:
            num_str = self.params['no']
            bodytextID = 'bodytextID' + num_str
        return bodytextID


def main():
    params = {
        'board': 'bhotangler2019',
        'command': 'body',
        'no': '2247'
    }
    # no_list = [2247, 2248, 2249, 2250]
    no_list = range(2247, 2257)
    # no_list = range(1139, 1239)
    # no_list = [1145]
    ue = UrlEncoder(site_url='http://www.innak.kr/php/board.php', params=params, no_list=no_list)
    ue.combine()

    fc = FishingCrawler(ue=ue)
    fc.crawl()


if __name__ == '__main__' :
    main()





