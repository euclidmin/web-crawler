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
URL2 = "http://www.innak.kr/php/board.php?board=bhotangler2019&command=body&no=2247"
req = requests.get(URL2)
soup = BeautifulSoup(req.content, 'html5lib')
# soup = BeautifulSoup(req.content, 'html.parser')

innak = []  # a list to store

# maintext = soup.find_all('div', attrs={'id': 'mainTextBodyDiv'})
# len(soup.contents) is 1
# tables = maintext[0].find_all('table')

maintext = soup.find('div', attrs={'id': 'mainTextBodyDiv'})
# len(soup.contents) is 57
# tables = maintext.find_all('table')
angler_info_table_lefts = maintext.find_all('td',attrs={'class':'b_detail_left'})
angler_info_table_rights = maintext.find_all('td',attrs={'class':'b_detail_right'})

data2248 = {}
for angler_info_left, angler_info_right in zip(angler_info_table_lefts, angler_info_table_rights):
    left_text = angler_info_left.get_text().strip()
    right_text = angler_info_right.get_text().strip()
    # data2248 = {td_l:td_r}
    data2248[left_text] = right_text

body_text_raw = maintext.find('td', attrs={'id':'bodytextID2247'})
body_text_striped = body_text_raw.get_text().strip().replace('\xa0', '').splitlines()

body_text = []
for line in body_text_striped :
    print(line)
    # if line.isspace():
    if line.isprintable():
        body_text.append(line)
    else :
        pass


data2248['body_text'] = body_text





import re
def remove_control_chart(s):
    return re.sub(r'\\x..', '', s)



'',


for td_right in td_rights:
    td_right.get_text().strip()




td_rights[0].get_text().strip()


for table in tables:
    print(table.get_text())

for link in soup.find_all('a'):
    if link.a is not None:
        print(link.a['href'])
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