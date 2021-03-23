from bs4 import BeautifulSoup
import requests
import fake_useragent
import time
import csv

HOST = 'https://dostavka.dixy.ru/'
URL = 'https://dostavka.dixy.ru/catalog/'

fake_user = fake_useragent.UserAgent().random
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,"
              "image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "User-agent": fake_user
}


def get_html(url):
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 200:
        return r
    else:
        print('Ошибка в запросе страницы')


def get_main_menu(html):
    """
    Собираем все ссылки меню со страницы 'Каталог'
    :param html:
    :return: dict_main_menu
    """

    soup = BeautifulSoup(html.content, 'html.parser')
    main_menu = soup.find('div', 'catalog_section_list').find_all('div', 'item_block')
    dict_main_menu = []
    for mm in main_menu:
        dict_main_menu.append({
                mm.find('a').find('img').get('title').strip(): HOST + mm.find('a').get('href')[1:]})

    return dict_main_menu


def get_count_pages(url):
    """
    Пагинация.
    Собираем количество страниц для обработки в выбранной категории товаров
    :param url: сслыка из списка 'Ктегории товаров'
    :return: int(count_pages)
    """
    html = get_html(url)

    soup = BeautifulSoup(html.content, 'html.parser')
    try:
        paginator = soup.find('div', 'module-pagination').find_all('a')
        count_pages = [p.text.strip() for p in paginator][-1]
        return int(count_pages)
    except AttributeError:
        print('Одна страница с товарами')
        return 1


def get_content(html):
    """
    По категории товара собираем все товары имеющиеся в продаже
    :param html: сслыка из словаря dict_main_menu
    :return: list_category_products [[name, price], ...]
    """
    soup = BeautifulSoup(html.content, 'html.parser')

    blocks = soup.find('div', 'catalog_block items row margin0 js_append ajax_load block flexbox')\
        .find_all('div', 'col-lg-3 col-md-6 col-sm-6 item item-parent item_block')

    list_category_products = []

    for block in blocks:
        try:
            item_title = block.find('div', 'item_info').find('a').text.strip()
            # print('Товар:', item_title)
        except AttributeError:
            item_title = '-'

        try:
            prices = block.find('div', 'price_value_block values_wrapper').find('span').text.strip()
            # print('Цена:', prices)
        except AttributeError:
            prices = '-'

        list_category_products.append([item_title, prices])

    return list_category_products


def save_file(lst, path):
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Наименование', 'Цена'])
        for rows in lst:
            for row in rows:
                writer.writerow([row[0], row[1]])


if __name__ == '__main__':
    d_main_menu = get_main_menu(get_html(URL))

    print('Категории товаров')
    for number_dos_menu, category in enumerate(d_main_menu):
        print(number_dos_menu + 1, '-', ''.join(*category))
    question_1 = int(input('Введите номер меню:\n-> '))
    print()

    category = d_main_menu[question_1 - 1]
    url_category = category[''.join(*category)]

    print(f'Идет парсинг товаров в категории:\n{"".join(*category)}\n')

    list_category_products = []
    i = 0
    for n in range(get_count_pages(url_category)):
        url = url_category + f'?PAGEN_1={n + 1}'
        print(f'Обработка страницы {i + 1}...')
        add_content = get_content(get_html(url))
        list_category_products.append(add_content)

        time.sleep(1)

        i += 1
        if i == 1:
            break

    list_category_products = [*list_category_products]
    path = f'{"".join(*category)}.csv'
    save_file(list_category_products, path)
