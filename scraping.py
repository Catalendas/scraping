import sqlite3
import requests

from bs4 import BeautifulSoup
import re
import pandas as pd
import math
import os


url = 'https://www.eneba.com/br/store/all?drms[]=xbox&page=1&regions[]=argentina&regions[]=turkey&regions[]=middle_east&types[]=game&types[]=subscription'

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"}

con = sqlite3.connect("../eneba-api/prisma/dev.db")
cur = con.cursor()

site = requests.get(url, headers=headers)
soup = BeautifulSoup(site.content, 'html.parser')
qtd_itens = soup.find('span', class_='n1DQi7').get_text().strip()

end_page = math.ceil(int(qtd_itens) / 20)

dict_games = {"name": [], "preco": []}

for i in range(1, end_page + 1):
    url_page = f'https://www.eneba.com/br/store/all?drms[]=xbox&page={i}&regions[]=argentina&regions[]=turkey&regions[]=middle_east&types[]=game&types[]=subscription'
    site = requests.get(url_page, headers=headers)
    soup = BeautifulSoup(site.content, 'html.parser')
    produtos = soup.find_all('div', class_='uy1qit')

    for produto in produtos:
        # Get game_name, image_url, game_url, game_value
        game_name = produto.find('span', class_=re.compile('YLosEL')).get_text().strip()
        image_url = produto.find('img', class_=re.compile('v5wuNi'))["src"]
        game_url = produto.find('a', class_=re.compile('oSVLlh'))["href"]
        game_value = produto.find('span', class_=re.compile('L5ErLT')).get_text().strip()
        game_isActive = produto.find('span', class_=re.compile('kq4D4Y'))

        # Format value
        game_valueNumber = re.findall(r'\d', game_value)
        game_valueComplet = ''.join(game_valueNumber)
        game_valueFormated = float(game_valueComplet) / 100

        # Get game description
        game = requests.get(f"https://www.eneba.com{game_url}", headers=headers)
        gameSoup = BeautifulSoup(game.content, "html.parser")
        # game_description = gameSoup.find("div", class_=re.compile('Wz6WhX'))
        game_category = gameSoup.find_all("li", class_=re.compile('Akwlh_'))
        game_country = gameSoup.find("strong", class_=re.compile('cEhl9f')).get_text().strip()
        list_category = []

        for category in game_category:
            item = category.find('a', class_=re.compile('BGWKEB')).get_text()
            list_category.append(item)

        # Format game_value
        game_valueNumber = re.findall(r'\d', game_value)
        game_valueComplet = ''.join(game_valueNumber)
        game_valueFormated = float(game_valueComplet) / 100

        # Post to api
        response = requests.post(os.environ.get('API_URL'), json={
            "game_name": f"{game_name}", 
            "game_eneba_url": f"{game_url}", 
            "game_image_url": f"{image_url}", 
            # "game_description": f"{game_description}", 
            "game_price": game_valueFormated,
            "game_isActive": f"{False if game_isActive else True}",
            "game_categories": list_category,
            "game_country": f"{game_country}"
        })

        print("item enviado")

