"""""""( Imports)"""""""
import re
import os
import time, csv
import pandas as pd
import urllib.request
from pathlib import Path
from selenium import webdriver
from dataclasses import dataclass
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

if not os.path.exists("images"):
    os.makedirs("images")

data_folder = Path(__file__).resolve().parent / "data"

"""""""( Make csv to save Scraped Data )"""""""


def make_csv(filename: str, data, new=True):
    """make a csv file with the given filename
    and enter the data
    """
    mode = "w" if new else "a"
    with open(filename, mode, newline="", encoding="utf-8") as f:
        f.writelines(data)


"""""""( Start webdriver_manager )"""""""

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--disable-notifications")
driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
driver.maximize_window()


"""""""( Read csv file to get values )"""""""


with open("url.csv", "r") as file:
    reader = csv.reader(file)
    new_category = ""
    new_sub_category = ""
    for row in reader:
        value1 = row[0]
        sitemap1 = row[0].split(" > ")[1]
        sitemap2 = row[0].split(" > ")[2]
        sitemap3 = row[0].split(" > ")[3]
        value = row[0]
        category = row[0].split(" > ")[1]
        sub_category = row[0].split(" > ")[3]

        if category != new_category:
            new_category = category
            try:
                os.mkdir(f"{category}")
                print("Folder created successfully!")
            except FileExistsError:
                print("Folder already exists!")

        if sub_category != new_sub_category:
            new_sub_category = sub_category
            try:
                os.mkdir(f"{category}/{sub_category}")
                print("folder created successfully!")
            except FileExistsError:
                print("folder already exists!")

            make_csv(
                f"{category}/{sub_category}/{sub_category}.csv",
                "Title,Price,SKU,Stock,weigth,Description,Main Category,Sub-Category,Sub-Sub-Category,Product URl,Image URl\n",
                new=True,
            )
        make_csv(f"{category}/{sub_category}/{sub_category}.csv", "\n", new=False)
        value2 = row[1]

        """""""( Get value from CSV file and use as URL )"""""""

        try:
            URL = f"{value2}"
            driver.get(f"{URL}")
            time.sleep(1)

            # accept cookies

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

            """""""( open url check if product is available )"""""""

            """""""( select view all product in page filter )"""""""

            try:
                print("Check url")
                check_filter = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//*[@class='sorting_controls']")
                    )
                )
                time.sleep(0.5)
                get_all_items = driver.find_element(
                    By.XPATH,
                    "//*[@class='selectWrapper selectWrapperPageSize select_order']",
                ).click()
                time.sleep(1)
                try:
                    select_view_all = driver.find_element(
                        By.XPATH,
                        "//*[contains(normalize-space(), 'View all')][@class='dijitReset dijitMenuItemLabel']",
                    ).click()
                except:
                    pass

                time.sleep(5)

                """""""( get all products and open each product on next page )"""""""

                all_elements = driver.find_elements(
                    By.XPATH, "//*[@class='product_name_link product_view_gtm']"
                )
                time.sleep(1)
                for element in all_elements:
                    time.sleep(1)
                    action_chains = ActionChains(driver)
                    action_chains.key_down(Keys.CONTROL)
                    action_chains.click(element)
                    action_chains.key_up(Keys.CONTROL)
                    action_chains.perform()
                    driver.switch_to.window(driver.window_handles[-1])
                    time.sleep(1)

                    """""""( ====================== )"""""""

                    """""""( download all images available on product page )"""""""

                    try:
                        image_elements = driver.find_elements(
                            By.XPATH,
                            "//div[@class='s7thumb' and ./*[@class='s7thumboverlay']]",
                        )
                        url_regex = r'url\("?(https?:\/\/[^\)\"]+)"?\)'
                        title_of_product = driver.find_element(
                            By.XPATH, "//*[@id='estore_product_title']"
                        )
                        for i, image in enumerate(image_elements):
                            try:
                                style = image.get_attribute("style")
                                matches = re.findall(url_regex, style)
                                url = matches[0].replace("=85&", "=500&")
                                urllib.request.urlretrieve(
                                    url,
                                    f"{category}/{sub_category}/{title_of_product.text.replace('/','').replace(':','')}{i}.jpg",
                                )
                            except:
                                pass
                    except:
                        pass

                    """""""( ====================== )"""""""

                    time.sleep(0.5)

                    """""""( Get product title. )"""""""

                    print(title_of_product.text)
                    make_csv(
                        f"{category}/{sub_category}/{sub_category}.csv",
                        f"{title_of_product.text.replace(',','-')},",
                        new=False,
                    )

                    """""""( get product price )"""""""

                    try:
                        product_price = driver.find_element(
                            By.XPATH,
                            "//*[@class='price price_redesign'][@id='PDP_productPrice']",
                        )
                        time.sleep(0.5)
                        print(product_price.text)
                        make_csv(
                            f"{category}/{sub_category}/{sub_category}.csv",
                            f"{product_price.text},",
                            new=False,
                        )
                    except:
                        product_price1 = driver.find_element(
                            By.XPATH, "//*[@class='price'][@id='PDP_productPrice']"
                        )
                        time.sleep(0.5)
                        print(product_price1.text)
                        make_csv(
                            f"{category}/{sub_category}/{sub_category}.csv",
                            f"{product_price1.text},",
                            new=False,
                        )
                    try:
                        time.sleep(0.5)

                        """""""( get product SKU number )"""""""

                        sku_num = driver.find_element(
                            By.XPATH,
                            "//*[@class='productid productid_redesign'][@id='productId']",
                        )
                        print(sku_num.text)
                        make_csv(
                            f"{category}/{sub_category}/{sub_category}.csv",
                            f"{sku_num.text},",
                            new=False,
                        )
                    except:
                        time.sleep(0.5)
                        sku_num1 = driver.find_element(
                            By.XPATH, "//*[@class='productid'][@id='productId']"
                        )
                        print(sku_num1.text)
                        make_csv(
                            f"{category}/{sub_category}/{sub_category}.csv",
                            f"{sku_num1.text},",
                            new=False,
                        )

                    """""""( check if product is out of stock )"""""""

                    try:
                        time.sleep(0.5)
                        stock = driver.find_element(
                            By.XPATH, "//*[@id='sold_out_text']/h5"
                        )
                        print(stock.text)
                        make_csv(
                            f"{category}/{sub_category}/{sub_category}.csv",
                            f"{stock.text},",
                            new=False,
                        )
                    except:
                        make_csv(
                            f"{category}/{sub_category}/{sub_category}.csv",
                            ",",
                            new=False,
                        )

                    """""""( get weight and convert in volume )"""""""

                    try:
                        title_of_product = driver.find_element(
                            By.XPATH, "//*[@id='estore_product_title']"
                        )
                        title = title_of_product.text
                        ml_value = re.search(r"\d+ml", title).group(0)
                        kg_value = int(ml_value[:-2]) / 1000
                        print(kg_value)
                        make_csv(
                            f"{category}/{sub_category}/{sub_category}.csv",
                            f"{kg_value}Kg,",
                            new=False,
                        )
                    except:
                        make_csv(
                            f"{category}/{sub_category}/{sub_category}.csv",
                            f",",
                            new=False,
                        )
                        pass

                    """""""( get ptoduct discription )"""""""

                    try:
                        try:
                            time.sleep(0.5)
                            description = driver.find_element(
                                By.XPATH, "//*[@id='contentOmnipresent']/*[@dir='ltr']"
                            )
                            description1 = driver.find_element(
                                By.XPATH, "//*[@id='contentCollapse']"
                            )
                            descriptionnn = description.get_attribute("innerHTML").replace('\n', '').replace(',', '')
                            description11 = description1.get_attribute("innerHTML").replace('\n', '').replace(',', '')
                            make_csv(
                                f"{category}/{sub_category}/{sub_category}.csv",
                                f'''"{descriptionnn}{description11}",''',
                                new=False,
                            )
                            
                        except:
                            description2 = driver.find_element(
                                By.XPATH, "//*[@id='estore_product_longdesc']"
                            )
                            description22 = description2.get_attribute("innerHTML").replace('\n', '').replace(',', '')
                            make_csv(
                                f"{category}/{sub_category}/{sub_category}.csv",
                                f'''"{description22}",''',
                                new=False,
                            )
                            
                    except:
                        
                        make_csv(
                            f"{category}/{sub_category}/{sub_category}.csv",
                            ",",
                            new=False,
                        )

                    """""""( get current product url )"""""""

                    urll = driver.current_url

                    """""""( image url )"""""""

                
                    make_csv(
                        f"{category}/{sub_category}/{sub_category}.csv",
                        f"{sitemap1},{sitemap2},{sitemap3},{urll},",
                        new=False,
                    )
                    try:
                        image_elements = driver.find_elements(
                            By.XPATH,
                            "//div[@class='s7thumb' and ./*[@class='s7thumboverlay']]",
                        )
                        url_regex = r'url\("?(https?:\/\/[^\)\"]+)"?\)'
                        for image in image_elements:
                            try:
                                style = image.get_attribute("style")
                                matches = re.findall(url_regex, style)
                                image_url = matches[0].replace("=85&", "=500&")
                               
                                make_csv(
                                    f"{category}/{sub_category}/{sub_category}.csv",
                                    f'''"{image_url}",''',
                                    new=False,
                                )
                                
                            except:
                                pass
                        make_csv(f"{category}/{sub_category}/{sub_category}.csv", "\n", new=False)   
                    except:
                        pass
                        make_csv(
                            f"{category}/{sub_category}/{sub_category}.csv",
                            f"N/A,N/A,N/A,N/A,N/A,N/A/{sitemap1},{sitemap2},{sitemap3},N/A,N/A,\n",
                            new=False,
                        )
                    driver.execute_script("window.close();")
                    driver.switch_to.window(driver.window_handles[-1])

            except Exception as e:
                print(e)
                make_csv(
                    f"{category}/{sub_category}/{sub_category}.csv",
                    f"N/A,N/A,N/A,N/A,N/A,N/A/{sitemap1},{sitemap2},{sitemap3},N/A,N/A,\n",
                    new=False,
                )

        except:
            make_csv(
                f"{category}/{sub_category}/{sub_category}.csv",
                f"N/A,N/A,N/A,N/A,N/A,N/A/{sitemap1},{sitemap2},{sitemap3},N/A,N/A,\n",
                new=False,
            )

time.sleep(5)
driver.quit()
