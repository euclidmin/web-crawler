import urllib.parse

from bs4 import BeautifulSoup
import requests

class FishingCrawler:

    def __init__(self, soup=None, url=None, maintext=None):
        # 초기화 필요한 컨테이너 변수들 선언
        self.soup = soup
        self.url = url
        self.fishing_record = dict()
        self.maintext = maintext


    def get_html(self, url=None):
        # u = url ? url : self.url
        if url is not None :
            u = url
        elif self.url is not None:
            u = self.url
        else:
            print("check : url is None")
            print("check : req is None")
            return

        req = requests.get(u)
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


    def extract_body_text(self):
        import re
        def _remove_control_chart(s):
            return re.sub('[\t\xa0]', '', s)

        if self.maintext is not None:
            maintext = self.maintext
        else:
            print("check : maintext is None")
            return

        body_text_raw = maintext.find('td', attrs={'id': 'bodytextID2247'})
        # body_text_striped = body_text_raw.get_text().strip().replace('\xa0', '').splitlines()
        body_text_striped = body_text_raw.get_text().strip()
        body_text = _remove_control_chart(body_text_striped)
        self.fishing_record['body_text'] = body_text


    def crawl(self):
        self.get_html()
        # self.extract_angler_info(self.soup, record)
        self.extract_angler_info()
        self.extract_body_text()
        return self.fishing_record


class UrlEncoder:
    # import urllib.parse
    def __init__(self, site_url='http://www.innak.kr/php/board.php',
                 params={'board':'bhotangler2019','command':'body','no':'2247'},
                 board=None, command=None, no=None):
        self.site_url=site_url
        self.params=params
        self.board=board
        self.command=command
        self.no=no
        self.url = None


    def combine(self, params=None):

        if self.params is None:
            self.params = {
                'board':'bhotangler2019',
                'command':'body',
                'no':'2247'
            }
        else:
            params = self.params

        encoded_params = urllib.parse.urlencode(params)
        self.url = self.site_url + '?' + encoded_params
        return self.url



    def get_url(self):
        if self.url is None:
            print("check : url is None")

        return self.url


    def get_next(self):
        num_str = self.params['no']
        num_int = int(num_str) + 1
        num_str = str(num_int)
        self.params['no'] = num_str
        self.combine()
        return self.url




def main():

    ue = UrlEncoder(site_url='http://www.innak.kr/php/board.php')
    url = ue.combine()

    fc = FishingCrawler(url=url)
    record = fc.crawl()
    print(record)


if __name__ == '__main__' :
    main()





