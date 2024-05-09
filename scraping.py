import sqlite3
import requests

from bs4 import BeautifulSoup
import re
import pandas as pd
import math
import os


url = 'https://www.eneba.com/br/store/all?drms[]=xbox&page=1&regions[]=argentina&regions[]=turkey&regions[]=middle_east&types[]=game&types[]=subscription'

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"}

# con = sqlite3.connect("../eneba-api/prisma/dev.db")
# cur = con.cursor()

site = requests.get(url, headers=headers)
soup = BeautifulSoup(site.content, 'html.parser')
qtd_itens = soup.find('span', class_='n1DQi7').get_text().strip()
# print(qtd_itens)

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
        game_value_search = produto.find('span', class_=re.compile('L5ErLT'))
        if game_value_search:
            game_value = game_value_search.get_text().strip()
        else:
            game_value = '0'
        game_isActive = produto.find('span', class_=re.compile('kq4D4Y'))
        game_country = produto.find("div", class_=re.compile('Pm6lW1')).get_text().strip()
        print(f"nome do jogo: {game_name}")

        # Format value
        game_valueNumber = re.findall(r'\d', game_value)
        game_valueComplet = ''.join(game_valueNumber)
        game_valueFormated = float(game_valueComplet) / 100

        # Get game description
        game = requests.get(f"https://www.eneba.com{game_url}", headers=headers)
        gameSoup = BeautifulSoup(game.content, "html.parser")
        # game_description = gameSoup.find("div", class_=re.compile('Wz6WhX'))
        game_category = gameSoup.find_all("li", class_=re.compile('Akwlh_'))
        game_plataform = gameSoup.find_all("ul", class_=re.compile('oBo9oN'))
        # print(f"pais do jogo: {game_country}")
        # print(f"Jogo está ativo?: {game_isActive}")
        list_category = []
        plataform_name = []

        for category in game_category:
            item = category.find('a', class_=re.compile('BGWKEB'))

            if item:
                category_game = item.text
            else: 
                category_game = "Nenhuma"    
            list_category.append(category_game)
        
        palavras_proibidas = ["PlayStation 3", "Linux"]

        if game_plataform === None:
            continue
        
        print(game_plataform)
        for plataform in game_plataform:
            plataformName = plataform.text

            if plataformName and not any(palavra in plataformName for palavra in palavras_proibidas):
                
                plataform_name.append(plataform.text)

        # Format game_value
        # print(f"Valor do jogo: {game_value}")
        # print(f"Valor formatado: {game_valueFormated}")

        # Post to api
        response = requests.post("https://gamesbusca-api.onrender.com/products", json={
            "product_name": f"{game_name}", 
            "product_url": f"{game_url}", 
            "product_image_url": f"{image_url}", 
            # "game_description": f"{game_description}", 
            "product_price": game_valueFormated,
            "product_isActive": f"{False if game_isActive else True}",
            "product_gender": list_category,
            "product_country": f"{game_country}",
            "product_type": "Jogo",
            "plataform_name": plataform_name
        })

        print("item enviado")

