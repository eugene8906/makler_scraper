import csv
import time
from bs4 import BeautifulSoup
import requests
import os
import json
from datetime import datetime


def get_all_pages():
    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }

    # r = requests.get(url='https://makler.md/ru/computers-and-office-equipment/laptops?list&currency_id=5&list=detail', headers=headers)

    # if not os.path.exists('data'):
    #     os.mkdir('data')

    # with open('data/page_1.html', 'w') as file:
    #     file.write(r.text)

    with open('data/page_1.html') as file:
        src = file.read()


    soup = BeautifulSoup(src, 'lxml')
    pages_count = int(soup.find_all('a', class_='paginator_pageLink')[-1].text)

    for i in range(0, pages_count):
        url = f'https://makler.md/ru/computers-and-office-equipment/laptops?list&currency_id=5&page={i}&list=detail'
        
        r = requests.get(url=url, headers=headers)

        with open(f'data/page_{i+1}.html', 'w') as file:
            file.write(r.text)

        time.sleep(2)
        
    return pages_count


def collect_data(pages_count):
    cur_date = datetime.now().strftime('%d_%m_%Y')

    with open(f'data_{cur_date}.csv', 'w') as file:
        writer = csv.writer(file)

        writer.writerow(
            (
                'Товар',
                'Цена',
                'Номер телефона',
                'Ссылка'
            )
        )

    data = []

    for page in range(1, pages_count + 1):
        with open(f'data/page_{page}.html') as file:
            src = file.read()

        soup = BeautifulSoup(src, 'lxml')
        items_cards = soup.find_all('div', class_='ls-detail_infoBlock')

        for item in items_cards:
            product_title = item.find('a', class_='ls-detail_anUrl').text
            product_price = item.find('div', class_='ls-detail_anData').find('span', class_="ls-detail_price", default=None)
            if product_price:
                product_price = product_price.text
            else:
                product_price = "цена не указана"
            seller_phone = item.find('div', class_='ls-detail_anData').find_all()
            if seller_phone:
                last_tag = seller_phone[-1]
                seller_phone = last_tag.text
            else:
                seller_phone = 'Номер не указан'
            product_url = f'https://makler.md{item.find("a", class_="ls-detail_anUrl").get("href")}'

            # print(f'title: {product_title}, price: {product_price}, phone: {seller_phone}, url: {product_url}')

            data.append(
                {
                    'product_title': product_title,
                    'product_price': product_price,
                    'seller_phone': seller_phone,
                    'product_url': product_url
                }
            )

            with open(f'data_{cur_date}.csv', 'a') as file:
                writer = csv.writer(file)

                writer.writerow(
                    (
                        product_title,
                        product_price,
                        seller_phone,
                        product_url
                    )
                )


        print(f'[INFO] Обработана страница {page}/{pages_count}')

    with open(f'data_{cur_date}.json', 'a') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)



def main():
    pages_count = get_all_pages()
    collect_data(pages_count=pages_count)



if __name__ == '__main__':
    main()