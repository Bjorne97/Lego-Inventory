from urllib import request
import requests
from bs4 import BeautifulSoup as soup
from selenium import webdriver
from PIL import Image
import json
import time
import os

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
URL_BASE = "https://www.lego.com/en-my/service/buildinginstructions/"
URL_BASE2 = "https://www.bricklink.com/v2/catalog/catalogitem.page?S="
URL_SUFFIX2 = '#T=S&O={"iconly":0}'

driver = None

def get_image_url2(set_id):
    print(set_id)
    url = f"{URL_BASE2}{set_id}{URL_SUFFIX2}"
    driver.get(url)
    time.sleep(1)
    page_soup = soup(driver.page_source, "html.parser")
    img = page_soup.findAll("img", {"valign" : "middle"})[0]
    url = "https:"+img["src"]
    return url

def get_image_url(set_id):
    url = f"{URL_BASE}{set_id}"
    driver.get(url)
    time.sleep(1)
    page_soup = soup(driver.page_source, "html.parser")
    div = page_soup.findAll("div", {"class" : "c-card__inner"})[0]
    style = div.div["style"]
    url = style.split('"')[1]
    return url

def correct_img(file_path):
    error_img_path = f"{DIR_PATH}/Images/error.jpg"
    img = Image.open(file_path)
    error_img = Image.open(error_img)
    return img == error_img


def download_images(set_ids):

    global driver
    options = webdriver.chrome.options.Options()
    options.headless = True
    driver = webdriver.Chrome("./chromedriver", chrome_options=options)

    for si in set_ids:
        url = get_image_url2(si)
        file_path = f"{DIR_PATH}/Images/Raw/{si}.jpg"
        request.urlretrieve(url, file_path)

        """
        if not correct_img(file_path):
            url = get_image_url2(si)
            request.urlretrieve(url, file_path)
        """

    driver.quit()

def get_set_ids():
    file_path = f"{DIR_PATH}/checked_lego_sets.json"

    f = open(file_path, "r")
    data = f.read()
    f.close()
    data = json.loads(data)

    set_ids = []
    for elem in data:
        lego_sets = elem["sets"]
        set_ids += [ls["id"] for ls in lego_sets]

    return set_ids


def remove_already_downloaded(set_ids):
    dir_path = f"{DIR_PATH}/Images/Raw"
    files = os.listdir(dir_path)
    sets_with_images = [f.split(".")[0] for f in files]

    sets_to_download = []
    for set_id in set_ids:
        if str(set_id) not in sets_with_images:
            sets_to_download.append(set_id)

    return sets_to_download


def img_to_square(pil_img, background_color):
    width, height = pil_img.size
    if width == height:
        return pil_img
    elif width > height:
        result = Image.new(pil_img.mode, (width, width), background_color)
        result.paste(pil_img, (0, (width - height) // 2))
        return result
    else:
        result = Image.new(pil_img.mode, (height, height), background_color)
        result.paste(pil_img, ((height - width) // 2, 0))
        return result


def resize_images():
    dir_path = f"{DIR_PATH}/Images"
    raw_image_files = set(os.listdir(f"{dir_path}/Raw"))
    square_image_files = set(os.listdir(f"{dir_path}/Square"))

    image_files = raw_image_files - square_image_files

    for img_name in image_files:
        img_path = f"{dir_path}/Raw/{img_name}"
        img = Image.open(img_path)

        new_img = img_to_square(img, (255, 255, 255))
        new_img.save(f"{dir_path}/Square/{img_name}")


def main():
    set_ids = get_set_ids()
    set_ids = remove_already_downloaded(set_ids)

    download_images(set_ids)
    print("All images downloaded")
    resize_images()
    print("All images resized")

if __name__ == '__main__':
    main()
