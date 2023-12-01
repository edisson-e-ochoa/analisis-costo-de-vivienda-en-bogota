from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import time
import csv

fields = ['property_type', 'rooms', 'garages', 'age', 'area', 'floor', 'administration_price', 'stratum', 'lat', 'lng', 'neighbourhood', 'locality', 'price']
with open("house_data.csv", "w", newline = '') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()

def scrap_page(url):
    request_site = Request(url, headers={"User-Agent":"Chrome 104.0.5112.79"})
    web = urlopen(request_site)
    house = BeautifulSoup(web, features="html.parser")
    info = json.loads(house.find("script",{"id":"__NEXT_DATA__" }).string)
    property_data = {}
    info = info['props']['pageProps']
    segmentation = info['segmentation']

    property_data['property_type'] = info['propertyType']['slug']
    property_data['rooms'] = segmentation['habitaciones']
    property_data['garages'] = info['garages']['id']
    property_data['age'] = info['age']['slug']
    property_data['area'] = info['area']
    property_data['floor'] = info['floor']['id']
    property_data['administration_price'] = int(float(info['administration']['price']))
    property_data['stratum'] = segmentation['estrato']
    location = info['locations']
    property_data['lat'] = location['lat']
    property_data['lng'] = location['lng']
    property_data['neighbourhood'] = location['neighbourhood']['name']
    property_data['locality'] = location['localities']['name']  # Tarea: Agregar excepciones TypeError
    property_data['price'] = info['price']
    with open("house_data.csv", 'a', newline = '') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writerow(property_data)


options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

def load_page(url):
    driver.get(url)
    time.sleep(0.5)
    page_source = driver.page_source
    page = BeautifulSoup(page_source, 'html.parser')
    return page

def scrap_site(url, page_number):
    page = load_page(url)
    tags = page.find_all('div',{'class':'MuiGrid-root MuiGrid-container MuiGrid-spacing-xs-4'})[0].children
    links =[]
    for child in tags:
        try:
            links.append("https://www.fincaraiz.com.co" + child.article.a.get('href')) 
        except AttributeError as e:
            continue
    for link in links:
        try:
            scrap_page(link)
            print("New property added")
        except TypeError:
            continue
        except IndexError:
            continue
        except:
            print("Server error, property not added.")
def total_houses(start_page):
    page = load_page(start_page)
    total_houses = int(page.find('h1').get_text().split()[0].replace('.',''))
    return total_houses


ages = ['1-8', '9-15', '16-30', '>30']

for stratum in range(1,7):
    start_page = "https://www.fincaraiz.com.co/apartamentos-casas/venta/bogota/bogota-dc?usado=true&pagina=1&estrato=" + str(stratum)
    total_houses_this_stratum = total_houses(start_page)
    if total_houses_this_stratum > 10000:
       for age in ages:
        start_page_this_age = start_page + "&antiguedad=" + str(age)
        total_houses_this_age = total_houses(start_page_this_age)
        total_pages_this_age = (total_houses_this_age // 25) + 1
        for page_number in range(1, total_pages_this_age + 1):
           url = "https://www.fincaraiz.com.co/apartamentos-casas/venta/bogota/bogota-dc?usado=true&pagina=" + str(page_number) + "&estrato=" + str(stratum) + "&antiguedad=" + str(age)
           scrap_site(url, page_number)
           print(f"Page {page_number} for stratum {stratum} and age {age} added") 
    else:
        total_pages_this_stratum = (total_houses_this_stratum // 25) + 1
        for page_number in range(1, total_pages_this_stratum + 1):
            url = "https://www.fincaraiz.com.co/apartamentos-casas/venta/bogota/bogota-dc?usado=true&pagina=" + str(page_number) + "&estrato=" + str(stratum)
            scrap_site(url, page_number)
            print(f"Page {page_number} for stratum {stratum} added") 
