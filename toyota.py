import requests
import csv
import time
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

def write_csv(lines, file_name):
    with open(file=file_name, encoding='utf-8', mode='a', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerows(lines)


def read_html():
    with open(file='toyota_manuals_base.html', mode='r') as file:
        return file.read()


def send_request(url):
    try:
        res = requests.get(url=url)
        if res.status_code == requests.codes.ok:
            return res
        return None
    except Exception as e:
        print(e)
        time.sleep(2)
        return send_request(url)


def parse(content):
    return BeautifulSoup(content.text, 'html5lib')


def get_feature():
    vehicle_data = json.loads(send_request(base_url).text)['body']['vehicles']
    for item in vehicle_data:
        detailed_items = item['vehiclesDetails']
        for detailed_item in detailed_items:
            if detailed_item['year'] == year:
                model_code = detailed_item['modelCode']
                model = model_code.upper().replace('-', ' ')
                model_url = 'https://toyota.com/{}/{}-features'.format(model_code, model_code)
                response = send_request(url=model_url)
                if response is None:
                    continue
                model_soup = parse(response)
                sections = model_soup.select('.refresh-features-slider-container section')
                for section in sections:
                    sec = section.find(attrs={'class': 'category-title'}).text.strip()
                    slides = section.select('.slide .slide-content')
                    for slide in slides:
                        title = slide.find(attrs={'class': 'slide-title'}).text.strip()
                        description = slide.find(attrs={'class': 'slide-description'}).text.strip()
                        if slide.find('source').has_attr('data-srcset'):
                            image_url = 'https://toyota.com' + slide.find('source')['data-srcset']
                        elif slide.find('source').has_attr('data-src'):
                            image_url = 'https://toyota.com' + slide.find('source')['data-src']
                        line = [year, 'Toyota', model, sec, title, description, image_url]
                        print(line)
                        write_csv(lines=[line], file_name='Toyota_Features_2021_Again.csv')


def get_gallery():
    vehicle_data = json.loads(send_request(base_url).text)['body']['vehicles']
    for item in vehicle_data:
        detailed_items = item['vehiclesDetails']
        for detailed_item in detailed_items:
            if detailed_item['year'] == year:
                model_code = detailed_item['modelCode']
                model = model_code.upper().replace('-', ' ')
                for category in categories:
                    category_url = 'https://toyota.com/{}/photo-gallery/{}'.format(model_code, category)
                    response = send_request(url=category_url)
                    if response is None:
                        continue
                    category_soup = parse(send_request(url=category_url))
                    sections = category_soup.select('#{} > a'.format('{}-gallery'.format(category)))
                    for section in sections:
                        if section.has_attr('data-image'):
                            image_url = 'https://toyota.com' + section['data-image']
                            line = [year, 'Toyota', model, category.upper(), image_url]
                            print(line)
                            write_csv(lines=[line], file_name='Toyota_Gallery_2021_Again.csv')


def get_driver():
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    return driver


def get_manuals():
    manuals_soup = BeautifulSoup(read_html(), 'html5lib')
    options = manuals_soup.find(id='car-drop-model').select('option')
    driver = get_driver()
    for option in options:
        if option.has_attr('value'):
            model = option['value'].replace('string:', '')
            if not model:
                continue
            model_url = 'https://www.toyota.com/owners/resources/warranty-owners-manuals/{}/2021'.format(model.lower().replace(' ', '-'))
            print(model_url)
            driver.get(model_url)
            time.sleep(3)
            page_content = driver.page_source
            model_soup = BeautifulSoup(page_content, 'html5lib')
            subs = model_soup.select('.inner_wrapper .docs-container a')
            for sub in subs:
                title = sub.select('.pdf-block .manual-title')[0].text.strip()
                pdf_link = sub['href']
                line = [year, 'Toyota', model, title, pdf_link]
                print(line)
                write_csv(lines=[line], file_name='Toyota_Manuals_2021.csv')


if __name__ == '__main__':
    year = '2021'
    categories = ['exterior', 'interior']
    base_url = 'https://www.toyota.com/ToyotaSite/rest/globalnav/vehicledata/'
    manuals_url = 'https://www.toyota.com/owners/resources/warranty-owners-manuals'
    get_gallery()
