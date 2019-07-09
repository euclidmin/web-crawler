from selenium import webdriver

driver = webdriver.Chrome('chromedriver')
driver.implicitly_wait(1)

driver.get('https://www.google.com')
