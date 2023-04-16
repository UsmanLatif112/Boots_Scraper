from selenium.webdriver.common.by import By
from dataclasses import dataclass


@dataclass
class Selector:
    xpath_type: str
    xpath: str


class HomeResources:
    tabs = Selector(By.XPATH, "//div/ul/li/ul/li/ul/li/ul/li/a")


# Imports

import re
import time, csv
import pandas as pd
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

#  Make csv to save Scraped Data


def make_csv(filename: str, data, new=True):
    """make a csv file with the given filename
    and enter the data
    """
    mode = "w" if new else "a"
    with open(filename, mode, newline="", encoding="utf-8") as f:
        f.writelines(data)


# make csv file
make_csv("Boots.csv", "categories road map,categories URL\n", new=True)
make_csv("Boots.csv", "\n", new=False)


# Start webdriver_manager

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--disable-notifications")
driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
driver.maximize_window()

# URl of WebApplication
URL = "https://www.boots.com/site-map"

driver.get(f"{URL}")
try:
    accept_cookies = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "//*[@id='onetrust-group-container']")
        )
    )
    accept_cookies = driver.find_element(
        By.XPATH,
        "//*[@class='banner-actions-container']/*[@id='onetrust-accept-btn-handler']",
    ).click()
    time.sleep(1)
except:
    pass

# main_catogries = driver.find_element(By.XPATH, "//*[@class='topLevelMenuListItem']/*[@id='topLevelLink_1590591']").click()
# time.sleep(0.5)
# //a[contains(@name, ':') and string-length(@name)-string-length(translate(@name,':',''))=4]
tabs = driver.find_elements(HomeResources.tabs.xpath_type, HomeResources.tabs.xpath)


def format(url):
    url = (
        url.replace("https://www.boots.com", "Shop by department")
        .replace("/", " > ")
        .replace("-", " ")
    )
    return url


for tab in tabs:
    url = tab.get_attribute("href")
    if url and url.count("/") == 5:
        title = format(url)
        make_csv("Boots.csv", f"{title}, {url}\n", new=False)
        print(title, url)
