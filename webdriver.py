from selenium import webdriver

# driver = webdriver.Chrome('chromedriver')
# driver.implicitly_wait(1)
#
# driver.get('https://nid.naver.com/nidlogin.login')
#
# driver.find_element_by_name('id').send_keys('euler73')
# driver.find_element_by_name('pw').send_keys('***********')
# driver.find_element_by_xpath('//*[@id="frmNIDLogin"]/fieldset/input').click()



import requests
from bs4 import BeautifulSoup

URL = "http://www.innak.kr/php/board.php?board=main&command=skin_insert&exe=insert_iboard1_home"
URL1 = "http://www.innak.kr/php/board.php?board=z03gofishing&command=skin_insert&exe=insert_iboard3.php"
URL2 = "http://www.innak.kr/php/board.php?board=bhotangler2019&command=body&no=2248"
req = requests.get(URL2)
soup = BeautifulSoup(req.content, 'html5lib')
# soup = BeautifulSoup(req.content, 'html.parser')

innak = []  # a list to store

maintext = soup.find_all('div', attrs={'id': 'mainTextBodyDiv'})
tables = maintext[0].find_all('table')

for table in tables:
    print(table.get_test())


#
# for row in table.findAll('div', attrs={'class': 'quote'}):
#     quote = {}
#     quote['theme'] = row.h5.text
#     quote['url'] = row.a['href']
#     quote['img'] = row.img['src']
#     quote['lines'] = row.h6.text
#     quote['author'] = row.p.text
#     quotes.append(quote)

# filename = 'inspirational_quotes.csv'
# with open(filename, 'wb') as f:
#     w = csv.DictWriter(f, ['theme', 'url', 'img', 'lines', 'author'])
#     w.writeheader()
#     for quote in quotes:
#         w.writerow(quote)