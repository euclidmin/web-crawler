from selenium import webdriver

driver = webdriver.Chrome('chromedriver')
driver.implicitly_wait(1)

driver.get('https://nid.naver.com/nidlogin.login')

driver.find_element_by_name('id').send_keys('euler73')
driver.find_element_by_name('pw').send_keys('rhdydals73.')
driver.find_element_by_xpath('//*[@id="frmNIDLogin"]/fieldset/input').click()

