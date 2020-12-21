from bs4 import BeautifulSoup as soup
from selenium import webdriver
import json
import time
import os

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
URL_BASE = "https://www.bricklink.com/v2/catalog/catalogitem.page?S="
URL_SUFFIX = '#T=S&O={"iconly":0}'
URL_BASE2 = "https://www.brickeconomy.com/set/"
URL_PREFIX2 = "-1/"

driver = None

def read_data(file_path):
    f = open(file_path, "r")
    data = f.read()
    f.close()
    return data


def write_data(file_path, data):
    f = open(file_path, "w")
    f.write(data)
    f.close()


def get_data(set_id):
    url = f"{URL_BASE}{set_id}{URL_SUFFIX}"
    driver.get(url)
    time.sleep(1)
    page_soup = soup(driver.page_source, "html.parser")

    span = page_soup.findAll("span", {"id" : "item-name-title"})
    name = span[0].text

    td = page_soup.findAll("td", {"valign" : "TOP", "width" : "38%"})
    year = int(td[0].findAll("a")[0].text)

    td = page_soup.findAll("td", {"valign" : "TOP", "width" : "31%"})
    pieces = int(td[0].findAll("a")[0].text.split(" ")[0])

    data = {"name" : name, "year" : year, "pieces" : pieces}
    return data


def get_price(set_id):
    url = f"{URL_BASE2}{set_id}{URL_PREFIX2}"
    driver.get(url)
    time.sleep(1)
    page_soup = soup(driver.page_source, "html.parser")

    divs = page_soup.findAll("div", {"class" : "row rowlist"})
    for elem in divs:
        eds = elem.findAll("div")
        if eds[0].get_text() == "Retail price":
            return eds[1].get_text()


def update_data(lego_sets):
    global driver
    options = webdriver.chrome.options.Options()
    options.headless = True
    driver = webdriver.Chrome("./chromedriver", chrome_options=options)

    for ls in lego_sets:
        si = ls["id"]
        data = get_data(si)
        price = get_price(si)
        data["price"] = price if price else "N/A"
        for key in data:
            if not ls[key]:
                ls[key] = data[key]

    driver.quit()


def copy_all_data(set_info, all_data):

    already_data = {ls["id"] : ls for elem in all_data for ls in elem["sets"]}
    all_sets = [ls for elem in set_info for ls in elem["sets"]]

    default_info = {"name" : "", "year" : 0, "pieces" : 0, "price" : ""}

    for ls in all_sets:
        si = ls["id"]
        ls.update(default_info)
        if si in already_data:
            for key in default_info.keys():
                if key in already_data[si]:
                    ls[key] = already_data[si][key]

    return set_info




def remove_complete(set_info, all_data):
    data = copy_all_data(set_info, all_data)

    not_complete_sets = [ls for elem in data for ls in elem["sets"]
                         if not(ls["name"] and ls["year"] and ls["pieces"] and ls["price"])]

    return not_complete_sets

def main():
    set_info_file_path = f"{DIR_PATH}/checked_lego_sets.json"
    all_data_file_path = f"{DIR_PATH}/lego_sets_all_data.json"
    set_info = json.loads(read_data(set_info_file_path))
    all_data = json.loads(read_data(all_data_file_path))
    lego_sets = remove_complete(set_info, all_data)

    update_data(lego_sets)
    write_data(all_data_file_path, json.dumps(set_info, indent=2))
    print("All data updated")

if __name__ == '__main__':
    main()
