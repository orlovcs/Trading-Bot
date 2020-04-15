import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re





driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', )
driver.get("https://finance.yahoo.com/gainers")
result = driver.page_source #load entire page
assert "Stock" in driver.title

tbody = driver.find_element_by_tag_name("tbody")
for row in tbody.find_elements_by_tag_name("tr"):
   for cell in row.find_elements_by_tag_name("td"):
      label = cell.get_attribute('aria-label')
      value = cell.text
      print(label+": "+value)

#the feeling when everything smoothly functions


# regex_d = re.compile('<a class="Fw(600)">(.+?)</td>')  
# element = driver.find_element_by_id("content")
# element = driver.find_element(s)_by_tag_name("div")
# element = driver.find_element_by_name("contentBox")
# element = driver.find_element_by_class_name("h3")

#scores = find_scores.findall(result) #send in the regex
driver.close()
