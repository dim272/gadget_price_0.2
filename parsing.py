import re
from statistics import mean
from datetime import date, datetime

from data import *
import MyPerfectRequest.get as r


class Ekatalog:

    """ parsing e-catalog.ru """

    def __main_page(self):
        request = r.MyPerfectRequest(use_proxy=True, android_headers=True)
        url = 'https://www.e-katalog.ru/'
        soup = request.soup(url)
        today = date.today().strftime("%d.%m.%Y")
        db = EkatalogHomepage

        try:
            cache = soup.find_all('div', class_='main_slide')
        except:
            cache = False

        if cache:
            for item in cache:
                a = item.find('a')
                section = a.text
                href = a['href'].replace('/', '')
                link = url + href
                print(section, link)
                double = db.select().where(db.link == link)
                if not double:
                    l_all = self.__all_link_of_section(link)
                    db.create(section=section, link=link, link_all=l_all, updated=today)
                else:
                    db.update(updated=today).where(db.link == link).execute()

    @staticmethod
    def __all_link_of_section(url):
        home = 'https://www.e-katalog.ru'
        request = r.MyPerfectRequest(use_proxy=True, android_headers=True)
        soup = request.soup(url)
        try:
            a = soup.find('div', class_='all-link').find('a')
            href = a['href']
            link = home + href
        except:
            link = ''

        return link

    @staticmethod
    def __find_next_page_link(soup):
        pattern = 'https://www.e-katalog.ru'

        try:
            next_page = soup.find('a', id='pager_next')
            href = next_page.get('href')
            link = pattern + href
        except:
            link = False

        return link

    @staticmethod
    def __brands_links(url):
        pattern = 'https://www.e-katalog.ru'
        request = r.MyPerfectRequest(use_proxy=True, android_headers=True)
        soup = request.soup(url)
        today = date.today().strftime("%d.%m.%Y")
        db = EkatalogBrands

        try:
            links = soup.find('div', class_='brands-list').find_all('a')
        except:
            links = []

        if links:
            for each in links:
                brand = each.text
                try:
                    href = each.get('href') if 'list' in each.get('href') else ''
                except:
                    href = False

                if href:
                    link = pattern + href

                    double = db.select().where(db.link == link)
                    if not double:
                        db.create(brand=brand, link=link, updated=today)
                    else:
                        db.update(updated=today).where(db.brand == brand, db.link == link)
                else:
                    continue

    def __smartphones_links(self, url):
        pattern = 'https://www.e-katalog.ru'
        request = r.MyPerfectRequest(use_proxy=True, android_headers=True)
        db = EkatalogSmartphones
        today = date.today().strftime("%d.%m.%Y")

        while True:
            soup = request.soup(url)
            items = soup.find_all('table', class_='model-short-block')

            if not items:
                break

            for item in items:
                try:
                    a = item.find('a', class_='model-short-title')
                    href = a.get('href')
                    link = pattern + href
                except:
                    continue

                try:
                    img = item.find('div', class_='list-img').find('img', src=True).get('src')
                    img = pattern + img
                except:
                    img = ''

                text_list = a.find_all('span')
                model_name = text_list[0].text
                try:
                    storage = text_list[1].text
                    model = model_name + ' ' + storage
                except:
                    model = model_name

                double = db.select().where(db.link == link)

                if not double:
                    print('найден новый смартфон:', model, link)
                    db.create(model=model, link=link, img=img, updated=today)
                    self.smartphone_specification(link)
                else:
                    print('дата обновления обновлена')
                    db.update(updated=today).where(db.link == link)

            next_page = self.__find_next_page_link(soup)

            if next_page:
                url = next_page
            else:
                break

    @staticmethod
    def __brand_name_finder(soup):
        brand = ''

        try:
            script_list = soup.find('head').find_all('script')
        except:
            script_list = []

        for script in script_list:
            this_what_we_need = re.search(r'\bdataLayer\b', str(script))
            if this_what_we_need:
                a = str(script).split('"brand":"')
                b = a[1].split('"')
                brand = b[0]
                break
            else:
                continue

        return brand

    @staticmethod
    def __model_name_finder(soup, brand_name):
        brand_part_list = brand_name.split(' ')

        try:
            title = soup.find('div', id='top-page-title').get('data-title')
        except:
            title = ''

        if title:
            a = title.split('<span')
            b = a[0].strip().split(' ')

            if len(brand_part_list) > 1:
                for brand_part in brand_part_list:
                    b.remove(brand_part)
            else:
                b.remove(brand_name)

            if 'nfc' in a[0].lower():
                b.remove('NFC')

            model_name = ' '.join(b)
        else:
            model_name = ''

        return model_name

    @staticmethod
    def __display_parsing(each_spec):
        try:
            search_display = each_spec.get('title').split(',')
            display = re.sub("[^0-9.,]", "", search_display[0])
            display = display.replace(',', '.')
        except:
            display = ''

        return display

    @staticmethod
    def __storage_parsing(each_spec):
        try:
            search_storage = each_spec.get('title').split(',')
            storage = re.sub("[^0-9]", "", search_storage[0])
        except:
            storage = ''

        return storage

    @staticmethod
    def __ram_parsing(each_spec):
        try:
            search_ram = each_spec.get('title').split(',')
            ram = re.sub("[^0-9]", "", search_ram[1])
        except:
            ram = ''

        return ram

    @staticmethod
    def __num_cores_parsing(each_spec):
        try:
            search_core = each_spec.get('title').split(',')
            num_cores = re.sub("[^0-9.,]", "", search_core[0])
            num_cores = num_cores.replace(',', '.')
        except:
            num_cores = ''

        return num_cores

    @staticmethod
    def __core_speed_parsing(each_spec):
        try:
            search_speed = each_spec.get('title').split(',')
            core_speed = re.sub("[^0-9.,]", "", search_speed[1])
            core_speed = core_speed.replace(',', '.')
        except:
            core_speed = ''

        return core_speed

    @staticmethod
    def __battery_parsing(each_spec):
        try:
            search_battery = each_spec.get('title')
            battery = re.sub("[^0-9.]", "", search_battery)
        except:
            battery = ''

        return battery

    @staticmethod
    def __weight_parsing(each_spec):
        try:
            search_weight = each_spec.get('title')
            weight = re.sub("[^0-9.]", "", search_weight)
        except:
            weight = ''

        return weight

    @staticmethod
    def __tags_founder(soup):
        try:
            specifications = soup.find('div', class_='m-c-f1')
        except:
            specifications = ''

        try:
            required_blocks1 = specifications.find_all('span')
        except:
            required_blocks1 = ''

        try:
            required_blocks2 = specifications.find_all('a')
        except:
            required_blocks2 = ''

        required_blocks = required_blocks1 + required_blocks2

        return required_blocks

    def __release_parsing(self, soup):
        required_blocks = self.__tags_founder(soup)
        release = None

        if required_blocks:
            for block in required_blocks:
                its_release = re.search(r'\bгод\b', block.text)
                if its_release:
                    release = re.sub("[^0-9]", "", block.text)
                    break
        return release

    def __nfc_parsing(self, soup):
        required_blocks = self.__tags_founder(soup)

        nfc = 0

        if required_blocks:
            for block in required_blocks:
                its_nfc = re.search(r'\bNFC\b', block.text)
                if its_nfc:
                    nfc = 1
                    break
        return nfc

    @staticmethod
    def __is_in_stock(soup):
        in_stock = True
        try:
            top_block = soup.find('div', class_='desc-short-prices')
        except:
            top_block = ''
            in_stock = False

        not_in_stock = top_block.select('.desc-not-avail')
        expected_on_sale = top_block.select('.or')

        if not_in_stock or expected_on_sale:
            in_stock = False

        try:
            ref = soup.find('div', class_="wb-REF")
        except:
            ref = False

        if ref:
            in_stock = False

        return in_stock

    @staticmethod
    def __more_button_finder(soup):
        try:
            more_btn = soup.find('table', id='item-wherebuy-table') \
                .next_sibling.find('div', class_='list-more-div-small') \
                .get('jsource')
            url_pattern = more_btn.replace('amp;', '')
            url_pieces = url_pattern.split('_start_=')
            new_url = url_pieces[0] + '_start_=1&p_end_=100'
        except:
            new_url = ''

        return new_url

    @staticmethod
    def __price_parsing_sorter(list_):
        new_data = {}
        for one_dict in list_:
            for key in one_dict:
                try:
                    val = new_data[key]
                    new_data[key] = val + [one_dict[key]]
                except KeyError:
                    new_data[key] = [one_dict[key]]

        result = {}
        for key in new_data:
            price = max(new_data[key])
            result[key] = price

        return result

    def __price_parsing(self, soup):
        try:
            where_buy = soup.find('table', id="item-wherebuy-table")
            shops = where_buy.find_all("tr", {"class": True})
        except:
            shops = []

        favorite_shops = ['mts.ru', 'svyaznoy.ru', 'citilink.ru', 'м.видео', 'megafon.ru', 'eldorado.ru',
                          'ozon.ru', 'sbermegamarket.ru']

        result = []

        for shop in shops:
            try:
                shop_name = shop.find('a', class_="it-shop").text
            except:
                continue

            if shop_name.lower() not in favorite_shops:
                continue

            shop_name_dot_ru = re.search(r'\bru\b', shop_name)
            if shop_name_dot_ru:
                dict_key = shop_name.lower().replace('.ru', '')
            else:
                dict_key = 'mvideo'

            try:
                price_block = shop.find('td', class_="where-buy-price").text
                price = re.sub("[^0-9]", "", price_block)
            except:
                continue

            if dict_key == 'sbermegamarket':
                dict_key = 'sber_mm'

            result.append({dict_key: price})

        if result:
            sorted_results = self.__price_parsing_sorter(result)
        else:
            sorted_results = {}

        return sorted_results

    def __price_parsing_more_button(self, soup):
        try:
            where_buy = soup.find('table')
            shops = where_buy.find_all("tr", {"class": True})
        except:
            shops = []

        result = []

        favorite_shops = ['mts.ru', 'svyaznoy.ru', 'citilink.ru', 'м.видео', 'megafon.ru', 'eldorado.ru',
                          'ozon.ru', 'sbermegamarket.ru']

        for shop in shops:
            try:
                shop_name = shop.find('h3').next_sibling.find('a').text
            except AttributeError:
                try:
                    shop_name = shop.find('h3').parent.next_sibling.find('a').text
                except AttributeError:
                    continue

            if shop_name.lower() not in favorite_shops:
                continue

            shop_name_dot_ru = re.search(r'\bru\b', shop_name)
            if shop_name_dot_ru:
                dict_key = shop_name.lower().replace('.ru', '')
            else:
                dict_key = 'mvideo'

            blocks = shop.find_all('td')
            price_block = blocks[3]
            price = re.sub("[^0-9]", "", price_block.text)

            if dict_key == 'sbermegamarket':
                dict_key = 'sber_mm'

            result.append({dict_key: price})

        if result:
            sorted_results = self.__price_parsing_sorter(result)
        else:
            sorted_results = {}

        return sorted_results

    def smartphone_specification(self, url):
        print('Начинаем сбор данных смартфона по ссылке:', url)
        request = r.MyPerfectRequest(use_proxy=True, android_headers=True)
        soup = request.soup(url)

        brand = self.__brand_name_finder(soup)
        model = self.__model_name_finder(soup, brand)
        today = date.today().strftime("%d.%m.%Y")
        ram = ''
        storage = ''

        try:
            db = EkatalogSmartphones
            row = db.get(db.link == url)
            img = row.img
        except:
            img = ''

        spec_dict = {'brand': brand, 'model': model, 'url_ekatalog': url, 'updated': today, 'img': img}

        try:
            specifications = soup.find('div', class_='m-c-f2').select('.m-s-f3')
        except:
            specifications = []

        if specifications:
            for each_spec in specifications:

                its_display = re.search(r'\bЭкран\b', each_spec.text)
                if its_display:
                    display = self.__display_parsing(each_spec)
                    spec_dict['display'] = str(display)
                    continue

                its_storage = re.search(r'\bПамять\b', each_spec.text)
                if its_storage:
                    storage = self.__storage_parsing(each_spec)
                    ram = self.__ram_parsing(each_spec)
                    spec_dict['storage'] = str(storage)
                    spec_dict['ram'] = str(ram)
                    continue

                its_cpu = re.search(r'\bПроцессор\b', each_spec.text)
                if its_cpu:
                    cpu_num = self.__num_cores_parsing(each_spec)
                    core_speed = self.__core_speed_parsing(each_spec)
                    spec_dict['cpu_num'] = str(cpu_num)
                    spec_dict['core_speed'] = str(core_speed)
                    continue

                its_battery = re.search(r'\bЕмкость батареи\b', each_spec.text)
                if its_battery:
                    battery = self.__battery_parsing(each_spec)
                    spec_dict['battery'] = str(battery)
                    continue

                its_weight = re.search(r'\bВес\b', each_spec.text)
                if its_weight:
                    weight = self.__weight_parsing(each_spec)
                    spec_dict['weight'] = str(weight)
                    continue

        release = self.__release_parsing(soup)
        if release:
            spec_dict['release'] = str(release)

        nfc = self.__nfc_parsing(soup)
        spec_dict['nfc'] = nfc

        in_stock = self.__is_in_stock(soup)
        spec_dict['in_stock'] = bool(in_stock)

        avito_youla_links = self.__avito_youla_links(brand, model, ram, storage, nfc)

        spec_dict = {**spec_dict, **avito_youla_links}

        print(spec_dict)
        db = Smartphones
        db.insert_many(spec_dict).execute()
        smart = db.get(db.brand == brand, db.model == model, db.ram == ram, db.storage == storage, db.nfc == nfc)
        smart_id = smart.id

        self.__price_collect_and_insert_in_db(soup, request, today, smart_id)
        self.__second_markets_price(brand, model, ram, storage, nfc, today, smart_id)

    def __price_collect_and_insert_in_db(self, soup, request, today, smart_id):
        print('Берём цены из екаталога')
        new_url = self.__more_button_finder(soup)
        if new_url:
            soup_for_price_parsing = request.soup(new_url)
            ekatalog_price_dict = self.__price_parsing_more_button(soup_for_price_parsing)
        else:
            ekatalog_price_dict = self.__price_parsing(soup)

        ekatalog_price_dict = {**ekatalog_price_dict, **{'updated': today, 'smartphone_id': smart_id}}
        print('Записываем цены:', ekatalog_price_dict)
        Prices.insert_many(ekatalog_price_dict).execute()

    @staticmethod
    def __avito_youla_links(brand, model, ram, storage, nfc):
        a = Avito(brand, model, ram, storage, nfc)
        avito_link = a.link

        y = Youla(brand, model, ram, storage, nfc)
        youla_link = y.link

        return {'url_avito': avito_link, 'url_youla': youla_link}

    @staticmethod
    def __second_markets_price(brand, model, ram, storage, nfc, today, smart_id):
        print('собираем данные с авито и юлы')

        a = Avito(brand, model, ram, storage, nfc)
        avito_price_dict = a.data_mining()

        y = Youla(brand, model, ram, storage, nfc)
        youla_price_dict = y.data_mining()

        youla_avito_price = {**avito_price_dict, **youla_price_dict}
        youla_avito_price = {**youla_avito_price, **{'updated': today, 'smartphone_id': smart_id}}

        if youla_avito_price:
            print('вставляем данные в бд:', youla_avito_price)
            PricesSecondMarkets.insert_many(youla_avito_price).execute()
        else:
            print('нет данных с юлы и авито :(')

    def update(self):
        print("запустили update")
        self.__main_page()
        home_page_links = EkatalogHomepage
        mobiles_section = home_page_links.get(home_page_links.section == 'Мобильные')
        mobiles_section_url = mobiles_section.link
        print('взяли ссылку на мобильные:', mobiles_section_url)
        print('запускаем скан топ брендов')
        self.__brands_links(mobiles_section_url)
        brands_links = EkatalogBrands
        brands_list = brands_links.select()
        print('взяли список топ брендов:', brands_list)
        print('увеличиваем значение')
        for row in brands_list:
            brand = row.brand
            print(brand.strip())
            # keyboards.main.Brand.increase_top_value(brand)
        all_mobiles_select = home_page_links.get(home_page_links.section == 'Мобильные')
        all_mobiles_urls = all_mobiles_select.link_all
        print('взяли ссылку на все мобилки:', all_mobiles_urls)
        self.__smartphones_links(all_mobiles_urls)
        print('update екаталога закончен')

    def check_for_update(self, brand, model, ram, storage):
        print("запустили check_for_update", brand, model, ram, storage)
        db = Smartphones
        search = db.select().where(db.brand == brand, db.model == model, db.ram == ram, db.storage == storage)
        print(search)
        updated = ''
        for each in search:
            print(each)
            print(each.updated)
            updated = each.updated
        print('updated:', updated)

        if updated:
            updated = datetime.timestamp(datetime.strptime(updated, "%d.%m.%Y"))
            today = datetime.timestamp(datetime.now())

            days_gone = round((today - updated) / 86400)
            print('Days gone:', days_gone)

            if days_gone > 7:
                self.update()


class Pda:

    """ parsing 4pda.ru/devdb """

    def __init__(self):
        self._domain = 'https://4pda.ru/devdb/'

    @staticmethod
    def _categories_link_parsing(soup):
        # collect links of all categories on the main page
        db = PdaCategories
        today = date.today().strftime("%d.%m.%Y")

        try:
            category_block_list = soup.find('div', class_='types-list').find_all('div', class_='type-row')
        except:
            category_block_list = []

        for category in category_block_list:
            try:
                title = category.find('div', class_='title-text').find('h2').text
                href = category.find('div', class_='title-text').find('a').get('href')
                link = 'https:' + href + '/all'
            except:
                continue

            if title and link:
                try:
                    link_in_db = db.get(db.link == link)
                except:
                    link_in_db = ''

                if link_in_db:
                    continue
                else:
                    db.create(category=title, link=link, updated=today)

    @staticmethod
    def _get_brand_name_brands_links_parsing(title):
        try:
            title_split = title.split(' (')
            brand_name = title_split[0]
        except:
            brand_name = ''

        return brand_name

    def _brands_links_parsing(self, soup, category_name):
        # collect links of all brands in a given category
        today = date.today().strftime("%d.%m.%Y")
        db = PdaBrands

        try:
            blocks_list = soup.find_all('ul', class_='word-list')
        except:
            blocks_list = []

        for block in blocks_list:
            try:
                brands_list = block.find_all('li')
            except:
                brands_list = []

            for brand in brands_list:
                try:
                    a = brand.find('a')
                    title = a.text
                    href = a.get('href')
                except:
                    continue

                link = 'https:' + href.replace('/all', '') + '/all'

                try:
                    is_double = db.select().where(db.link == link)
                except:
                    is_double = ''

                if is_double:
                    continue

                brand_name = self._get_brand_name_brands_links_parsing(title)

                if link and brand_name:
                    db.create(category=category_name, brand=brand_name, link=link, updated=today)
                else:
                    continue

    @staticmethod
    def _models_links_parsing(soup, brand_name):
        # collect link and image for each model in a given brand
        db = PdaSmartphones

        try:
            models_list = soup.find_all('div', class_='box-holder')
        except:
            models_list = []

        for model in models_list:
            try:
                img = model.find('img')
                img_href = img.get('src')
                name = model.find('div', class_='name').find('a')
                model_name = name.text
                model_href = name.get('href')
            except:
                continue

            its_ipod = re.search(r'\bipod\b', model_name.lower())
            if its_ipod:
                continue

            img_link = 'https:' + img_href
            model_link = 'https:' + model_href

            try:
                is_double = db.select().where(db.link == model_link)
            except:
                is_double = ''

            if is_double:
                continue

            db.create(brand=brand_name, model=model_name, link=model_link, img=img_link)

    @staticmethod
    def _check_for_Redmi(given_dict):
        # {'brand': 'Redmi', 'model': 'Note 9'} => {'brand': 'Xiaomi', 'model': 'Redmi Note 9'}
        result = given_dict

        try:
            brand = result.get('brand')
            model = result.get('model')
        except:
            brand = 'error'
            model = 'error'

        if brand.lower() == 'redmi':
            new_brand = 'Xiaomi'
            new_model = 'Redmi ' + model
            result['brand'] = new_brand
            result['model'] = new_model

        return result

    @staticmethod
    def _check_val_for_split(row_value):
        # 'N4s (N4s snapdragon варианты с этим значением:n4s snapdragon)' => 'N4s'
        split = row_value.split(' (')
        if len(split) > 1:
            model_name = split[0]
        else:
            model_name = row_value

        return model_name

    def _specifications_parsing_main(self, specifications_list):
        result = {}
        for row in specifications_list:
            try:
                row_title = row.find('dt').text.lower()
                row_value = row.find('dd').text
            except:
                continue

            its_brand = re.search(r'производитель', row_title)
            if its_brand:
                brand = self._check_val_for_split(row_value)
                result['brand'] = brand.strip()
                continue

            its_model = re.search(r'модель', row_title)
            if its_model:
                model = self._check_val_for_split(row_value)
                result['model'] = model.strip()
                continue

            its_release = re.search(r'год', row_title)
            if its_release:
                release = self._check_val_for_split(row_value)
                release = re.sub("[^0-9]", "", release)
                result['release'] = str(release)
                continue

            its_os = re.search(r'система', row_title)
            if its_os:
                os = self._check_val_for_split(row_value)
                result['os'] = os
                continue

            its_battery = re.search(r'аккум', row_title)
            if its_battery:
                battery = self._check_val_for_split(row_value)
                battery = re.sub("[^0-9]", "", battery)
                result['battery'] = str(battery)
                continue

        result = self._check_for_Redmi(result)
        # {'brand': 'Redmi', 'model': 'Note 9'} => {'brand': 'Xiaomi', 'model': 'Redmi Note 9'}

        return result  # {'brand': val, 'model': val, 'release': val, 'os': val, 'battery': val}

    @staticmethod
    def _specifications_parsing_dimensions(specifications_list):
        result = {}

        for row in specifications_list:
            try:
                row_title = row.find('dt').text.lower()
                row_value = row.find('dd').text
            except:
                continue

            its_dimensions = re.search(r'габариты', row_title)
            if its_dimensions:
                result['dimensions'] = row_value
                continue

            its_weight = re.search(r'вес', row_title)
            if its_weight:
                try:
                    weight = re.sub("[^0-9]", "", row_value)
                except:
                    continue
                result['weight'] = str(weight)
                continue

        return result  # {'dimensions': val, 'weight': val}

    def _specifications_parsing_cpu(self, specifications_list):
        result = {}

        for row in specifications_list:
            try:
                row_title = row.find('dt').text.lower()
                row_value = row.find('dd').text
            except:
                continue

            its_cpu = re.search(r'процессор', row_title)
            if its_cpu:
                cpu = self._check_val_for_split(row_value)
                result['cpu'] = cpu
                continue

            its_core_speed = re.search(r'частота', row_title)
            if its_core_speed:
                core_speed = self._check_val_for_split(row_value)
                core_speed = re.sub("[^0-9]", "", core_speed)
                result['core_speed'] = str(core_speed)
                continue

        return result  # {'cpu': val, 'core_speed': val}

    @staticmethod
    def _mb_to_gb(memory_list):
        # ['0,200', '1 mb', '20 mb', '1mb', '9', '90', '0.250']

        result = [re.sub("[^0-9,.]", "", ram.replace(',', '.')) for ram in memory_list]
        # ['0.200', '1', '20', '1', '9', '90', '0.250']

        result = [float(ram) / 1000 if float(ram) >= 1 else float(ram) for ram in result]
        # [0.2, 0.001, 0.02, 0.001, 0.009, 0.09, 0.25]

        result = [str(ram) for ram in result]
        # ['0.2', '0.001', '0.02', '0.001', '0.009', '0.09', '0.25']

        return result

    def _get_memory_size_list(self, row_title, row_value):
        result_list = []

        try:
            memory_list = row_value.split(' (')
            memory_list = memory_list[0]
        except:
            memory_list = row_value

        try:
            memory_list = memory_list.split('/')
            if len(memory_list) > 1:
                for memory in memory_list:
                    result_list.append(memory)
            else:
                result_list = memory_list
        except:
            result_list.append(memory_list[0])

        if re.search(r'мб', row_title):
            result_list = self._mb_to_gb(result_list)
        else:
            result_list = [re.sub("[^0-9.]", "", val.replace(',', '.')) for val in result_list]

        return result_list  # ['3', '4', '6']

    @staticmethod
    def _get_memory_split(all_row):
        result = []

        try:
            dropdown_list = all_row.find('dd').find_all('div', class_='dropdown')
        except:
            dropdown_list = []

        for dropdown in dropdown_list:
            try:
                li_list = dropdown.find('ul').find_all('li')
            except:
                li_list = []

            for li in li_list:
                try:
                    a = li.find('a').text
                except:
                    continue

                ram_and_storage = a.split('/')
                print(ram_and_storage)
                if len(ram_and_storage) > 1:
                    ram = ram_and_storage[0]
                    storage = ram_and_storage[1]
                    if ram.isdigit() and storage.isdigit():
                        result.append({ram: storage})

        return result  # [{'4': '64'}, {'6': '128'}]

    @staticmethod
    def _memory_result_generator(ram_list, storage_list):
        # ram_list = ['3', '4', '6']
        # storage_list = ['32', '64']

        result = []

        if len(ram_list) == 1 and len(storage_list) > 1:
            for key in ram_list:
                for val in storage_list:
                    result.append({key: val})

        elif len(ram_list) == len(storage_list):
            x = len(ram_list) - 1
            while x >= 0:
                result.append({ram_list[x]: storage_list[x]})
                x -= 1

        elif len(ram_list) > len(storage_list) == 1:
            for val in storage_list:
                for key in ram_list:
                    result.append({key: val})

        elif len(ram_list) > len(storage_list) > 1:
            x = len(storage_list) - 1
            while x >= 0:
                result.append({ram_list[x]: storage_list[x]})
                x -= 1
            result.append({ram_list[-1]: storage_list[-1]})
        else:
            result.append({ram_list[0]: storage_list[0]})

        return result  # [{'4': '64'}, {'3': '32'}, {'6': '64'}]

    @staticmethod
    def _delete_doubles_memory_result(result):
        result_without_doubles = []

        for x in result:
            if x not in result_without_doubles:
                result_without_doubles.append(x)

        return result_without_doubles

    def _specifications_parsing_storage(self, specifications_list):
        result = []
        split = []
        ram_list = []
        storage_list = []

        for row in specifications_list:
            its_split = False

            try:
                row_title = row.find('dt').text.lower()
            except:
                try:
                    row_title = row.find('dt').find('span').text.lower()
                    its_split = True
                except:
                    continue

            try:
                row_value = row.find('dd').text
            except:
                try:
                    row_value = row.find('dd').find('span').text
                    its_split = True
                except:
                    continue

            try:
                check_to_split = row_value.split('(')
                if len(check_to_split) > 1:
                    its_split = True
            except:
                pass

            if its_split:
                split_data = self._get_memory_split(row)  # [{'4': '64'}, {'6': '128'}]
                split = split + split_data

            its_rom = re.search(r'rom', row_title)
            its_ram = re.search(r'оперативная', row_title)
            if its_rom or its_ram:
                ram_list = self._get_memory_size_list(row_title, row_value)  # ['3', '4', '6']
                continue

            its_storage = re.search(r'встроенная', row_title)
            if its_storage:
                storage_list = self._get_memory_size_list(row_title, row_value)  # ['32', '64', '128']

        if ram_list and storage_list:
            result = self._memory_result_generator(ram_list, storage_list)  # [{'3': '32'}, {'4': '64'}, {'6': '128'}]

        if split:
            result = result + split  # [{'3': '32'}, {'4': '64'}, {'4': '64'}, {'6': '128'}]

        result = self._delete_doubles_memory_result(result)  # [{'3': '32'}, {'4': '64'}, {'6': '128'}]

        return result

    @staticmethod
    def _specifications_parsing_display(specifications_list):
        result = {}

        for row in specifications_list:
            try:
                row_title = row.find('dt').text.lower()
                row_value = row.find('dd').text
            except:
                continue

            its_display = re.search(r'размер экрана', row_title)
            if its_display:
                try:
                    display = re.sub("[^0-9,.]", "", row_value)
                except:
                    continue
                result['display'] = str(display)
                continue

        return result  # {'display': val}

    @staticmethod
    def _create_dicts_of_results(result_dict, storage_block):
        list_of_results = []

        for memory_values in storage_block:
            try:
                ram = list(memory_values.keys())[0]
                storage = list(memory_values.values())[0]
            except:
                continue
            new_dict = {**result_dict, **{'ram': ram, 'storage': storage}}
            list_of_results.append(new_dict)

        return list_of_results
        # [
        # {'brand': 'val', 'model': 'val', 'release': 'val', 'os': 'val', 'battery': 'val', 'ram': '6', 'storage': '64'},
        # {'brand': 'val', 'model': 'val', 'release': 'val', 'os': 'val', 'battery': 'val', 'ram': '3', 'storage': '32'}
        # ]

    @staticmethod
    def _check_db_for_duplicates(result_dict):
        duplicate = True
        double = True
        db = Smartphones

        try:
            brand = result_dict.get('brand')
            model = result_dict.get('model')
            ram = result_dict.get('ram')
            storage = result_dict.get('storage')
            nfc = result_dict.get('nfc')
            double = db.select().where(db.brand == brand, db.model == model,
                                       db.ram == ram, db.storage == storage, db.nfc == nfc)
        except:
            pass

        if not double:
            duplicate = False

        return duplicate

    @staticmethod
    def _get_nfc_from_ekatalog_db(result_dict):
        db = Smartphones  # Ekatalog database
        nfc = False
        try:
            brand = result_dict.get('brand')
            model = result_dict.get('model')
            ram = result_dict.get('ram')
            storage = result_dict.get('storage')
            model_in_ekatalog = db.get(db.brand == brand, db.model == model,
                                       db.ram == ram, db.storage == storage)
            nfc = model_in_ekatalog.nfc
        except:
            pass

        result = {**result_dict, **{'nfc': bool(nfc)}}

        return result

    def _models_specifications_parsing(self, soup, model_img):
        # collect data specification smartphone
        db = Smartphones
        today = date.today().strftime("%d.%m.%Y")
        result = {'img': model_img, 'updated': today}
        list_of_results = []
        storage_block = None

        try:
            specifications_blocks = soup.find_all('div', class_='specifications-list')
        except:
            specifications_blocks = []

        for block in specifications_blocks:
            try:
                title = block.find('h3', class_='specifications-title').text.lower()
            except:
                continue

            try:
                specifications_list = block.find_all('dl', class_='specifications-row')
            except:
                continue

            its_main = re.search(r'общее', title)
            if its_main:
                main_block = self._specifications_parsing_main(specifications_list)
                # {'brand': val, 'model': val, 'release': val, 'os': val, 'battery': val}
                result = {**result, **main_block}
                continue

            its_dimensions = re.search(r'размеры', title)
            if its_dimensions:
                dimensions_block = self._specifications_parsing_dimensions(specifications_list)
                # {'dimensions': val, 'weight': val}
                result = {**result, **dimensions_block}
                continue

            its_cpu = re.search(r'процессор', title)
            if its_cpu:
                cpu_block = self._specifications_parsing_cpu(specifications_list)
                # {'cpu': val, 'core_speed': val}
                result = {**result, **cpu_block}
                continue

            its_storage = re.search(r'память', title)
            if its_storage:
                storage_block = self._specifications_parsing_storage(specifications_list)
                # [{'3': '32'}, {'4': '64'}, {'6': '64'}]
                continue

            its_display = re.search(r'мультимедиа', title)
            if its_display:
                display = self._specifications_parsing_display(specifications_list)
                result = {**result, **display}
                # {'display': val}
                continue

        if storage_block:
            list_of_results = self._create_dicts_of_results(result, storage_block)
        else:
            list_of_results.append(result)

        for result_dict in list_of_results:
            result_dict_with_nfc = self._get_nfc_from_ekatalog_db(result_dict)
            duplicate = self._check_db_for_duplicates(result_dict_with_nfc)
            if not duplicate:
                print('================> New row in base:\n', result_dict_with_nfc)
                db.insert_many(result_dict_with_nfc).execute()

    def total_parsing(self):
        # start a general collection or update of all data from the 4pda.ru/devdb/
        url = self._domain
        request = r.MyPerfectRequest(use_proxy=True, desktop_headers=True)

        # soup = r.soup(url)
        # self._categories_link_parsing(soup)
        #
        # try:
        #     categories = Pda_db.CategoriesLinksPda.select()
        # except:
        #     categories = []
        #
        # for category in categories:
        #     try:
        #         title = category.category
        #         link = category.link
        #     except:
        #         continue
        #     soup = r.soup(link)
        #     self._brands_links_parsing(soup, title)
        #
        # try:
        #     smartphones_brands = Pda_db.BrandsLinksPda.select().where(Pda_db.BrandsLinksPda.category == 'Телефоны')
        # except:
        #     smartphones_brands = []
        #
        # for brand in smartphones_brands:
        #     try:
        #         brand_name = brand.brand
        #         link = brand.link
        #     except:
        #         continue
        #
        #     if not brand_name or not link:
        #         continue
        #
        #     soup = r.soup(link)
        #     self._models_links_parsing(soup, brand_name)

        try:
            smartphones_links = PdaSmartphones.select()
        except:
            smartphones_links = []

        db_specifications = Smartphones

        for row in smartphones_links:
            try:
                id = row.id
                brand = row.brand
                model = row.model
                img = row.img
                link = row.link
                print('\n', id, brand, model, link)
            except:
                continue

            if not img or not link:
                continue

            try:
                is_double = db_specifications.get(db_specifications.brand == brand, db_specifications.model == model)
            except:
                is_double = False

            if is_double:
                continue

            soup = request.soup(link)
            self._models_specifications_parsing(soup, img)


class SecondMarket:

    def _different_search_requests(self):
        brand = self.brand.lower()
        model = self.model.lower()
        model2 = self.model.lower().replace(' ', '')
        storage = self.storage
        ram = self.ram
        search_requests = []

        if not storage and not ram:
            search_requests.append(model)

            search_requests.append(model2)

            v = brand + ' ' + model
            search_requests.append(v)

            v = brand + ' ' + model2
            search_requests.append(v)

        elif not storage:
            v = brand + ' ' + model + ' ' + ram + 'gb'
            search_requests.append(v)

            v = brand + ' ' + model2 + ' ' + ram + 'gb'
            search_requests.append(v)

            v = model + ' ' + ram + 'gb'
            search_requests.append(v)

            v = model2 + ' ' + ram + 'gb'
            search_requests.append(v)

        elif not ram:
            v = brand + ' ' + model + ' ' + storage + 'gb'
            search_requests.append(v)

            v = brand + ' ' + model2 + ' ' + storage + 'gb'
            search_requests.append(v)

            v = model + ' ' + storage + 'gb'
            search_requests.append(v)

            v = model2 + ' ' + storage + 'gb'
            search_requests.append(v)

        else:
            v = brand + ' ' + model + ' ' + ram + '/' + storage
            search_requests.append(v)

            v = brand + ' ' + model + ' ' + ram + ' ' + storage
            search_requests.append(v)

            v = brand + ' ' + model + ' ' + ram + 'gb' + '/' + storage + 'gb'
            search_requests.append(v)

            v = brand + ' ' + model + ' ' + ram + 'gb' + ' ' + storage + 'gb'
            search_requests.append(v)

            v = model + ' ' + ram + '/' + storage
            search_requests.append(v)

            v = model + ' ' + ram + ' ' + storage
            search_requests.append(v)

            v = brand + ' ' + model + ' ' + storage
            search_requests.append(v)

            v = model + ' ' + storage
            search_requests.append(v)

            v = brand + ' ' + model2 + ' ' + ram + '/' + storage
            search_requests.append(v)

            v = brand + ' ' + model2 + ' ' + ram + ' ' + storage
            search_requests.append(v)

            v = brand + ' ' + model2 + ' ' + ram + 'gb' + '/' + storage + 'gb'
            search_requests.append(v)

            v = brand + ' ' + model2 + ' ' + ram + 'gb' + ' ' + storage + 'gb'
            search_requests.append(v)

            v = model2 + ' ' + ram + '/' + storage
            search_requests.append(v)

            v = model2 + ' ' + ram + ' ' + storage
            search_requests.append(v)

            v = brand + ' ' + model2 + ' ' + storage
            search_requests.append(v)

            v = model2 + ' ' + storage
            search_requests.append(v)

        return search_requests

    def _link_generator(self):
        domain = self.link_pattern
        brand = self.brand.replace(' ', '+').lower()
        model = self.model.replace(' ', '+').lower()
        storage = self.storage
        ram = self.ram

        if brand == 'apple':
            if storage:
                link = domain + brand + '+' + model + '+' + storage
            else:
                link = domain + brand + '+' + model
        else:
            if storage and ram:
                link = domain + brand + '+' + model + '+' + ram + 'gb' + '+' + storage + 'gb'
            elif storage:
                link = domain + brand + '+' + model + '+' + storage + 'gb'
            elif ram:
                link = domain + brand + '+' + model + '+' + ram + 'gb'
            else:
                link = domain + brand + '+' + model

            if self.nfc:
                link = link + '+nfc'

        return link

    def _title_sorting(self, data):
        result = {}
        search_requests = self.search_requests

        for d in data:
            title = list(d.keys())[0].lower()
            price = list(d.values())[0]

            for search_request in search_requests:
                search = re.search(search_request, title)
                if search:

                    if not self.nfc:
                        search_nfc = re.search('nfc', title)
                        if not search_nfc:
                            try:
                                val = result[price]
                            except:
                                val = 0
                            result[price] = val + 1

                    else:
                        try:
                            val = result[price]
                        except:
                            val = 0
                        result[price] = val + 1

        sorted_result = {}

        for w in sorted(result, key=result.get, reverse=True):
            sorted_result[w] = result[w]

        return sorted_result

    def _price_sorting(self, sorted_data):
        name = self.name

        values_sorted_list = list(sorted_data.values())

        if len(values_sorted_list) > 1:
            top1_value = values_sorted_list[0]
            top2_value = values_sorted_list[1]
        else:
            top1_value = top2_value = values_sorted_list[0]

        price_list = []
        top_price_list = []

        for d in sorted_data:
            key = d
            val = sorted_data[key]

            if not key or not val:
                continue
            if val == top1_value or val == top2_value:
                top_price_list.append(int(key))
                price_list.append(int(key))
            else:
                price_list.append(int(key))

        middle_price = mean(top_price_list)
        middle_price = round(middle_price / 500) * 500

        result = {f'{name}': middle_price}

        return result

    def _data_sorting(self, data):
        # data = [{title: price}]
        sorted_data = self._title_sorting(data)
        if sorted_data:
            sorted_result = self._price_sorting(sorted_data)
        else:
            sorted_result = {}

        return sorted_result


class Avito(SecondMarket):

    """ parsing avito.ru """

    def __init__(self, brand, model, ram=None, storage=None, nfc=False):
        self.brand = brand
        self.model = model
        self.storage = storage
        self.ram = ram
        self.nfc = nfc
        self.name = 'avito'
        self.link_pattern = 'https://m.avito.ru/rossiya/telefony?q='
        self.link = self._link_generator()
        self.search_requests = self._different_search_requests()

    @staticmethod
    def _soup(url):
        request = r.MyPerfectRequest(use_proxy=True, android_headers=True)
        soup = request.soup(url)
        return soup

    @staticmethod
    def _find_next_page(soup):
        domain = 'https://m.avito.ru'

        try:
            pages = soup.find('div', 'pagination-pages').find_all('a')
        except:
            pages = []

        if pages:
            a = pages[-1]
            href = a.get('href')
            link = domain + href
        else:
            link = ''

        return link

    @staticmethod
    def _get_titles_and_prices(soup):
        result = []

        try:
            items = soup.find_all('div', {'data-marker': 'item'})
        except:
            items = []

        if items:
            for item in items:
                try:
                    title = item.find('a', {'data-marker': 'item-title'}).find('h3').text
                    price = item.find('span', {'data-marker': 'item-price'}).text
                    price = re.sub("[^0-9]", "", price)
                except:
                    continue

                if title and price:
                    result.append({title: price})
        else:
            try:
                items = soup.find_all('div', {'data-marker': 'item/title'})
            except:
                items = []

            for item in items:
                try:
                    title = item.find('a').text
                    price = item.next_sibling.find('div', {'data-marker': 'item/price'}).text
                    price = re.sub("[^0-9]", "", price)
                except:
                    continue

                if title and price:
                    result.append({title: price})

        return result

    def data_mining(self):
        result = []
        sorted_result = {}
        url = self.link

        while True:
            soup = self._soup(url)
            items = self._get_titles_and_prices(soup)
            if items:
                result = result + items

            next_page = self._find_next_page(soup)

            if not next_page or next_page == url:
                break
            else:
                url = next_page
                continue

        if result:
            sorted_result = self._data_sorting(result)

        return sorted_result


class Youla(SecondMarket):

    """ parsing youla.ru """

    def __init__(self, brand, model, ram=None, storage=None, nfc=False):
        self.brand = brand
        self.model = model
        self.storage = storage
        self.ram = ram
        self.nfc = nfc
        self.name = 'youla'
        self.link_pattern = 'https://youla.ru/moskva?q='
        self.link = self._link_generator()
        self.search_requests = self._different_search_requests()

    @staticmethod
    def _soup(url):
        request = r.MyPerfectRequest(use_proxy=True, desktop_headers=True)
        soup = request.soup(url)
        return soup

    @staticmethod
    def _find_next_page(soup):
        try:
            next_page = soup.find('a', class_='_paginator_next_button').get('href')
        except:
            next_page = False

        return next_page

    @staticmethod
    def _get_titles_and_prices(soup):
        try:
            ads = soup.find_all('li', class_="product_item")
        except:
            ads = []

        result = []

        for ad in ads:
            try:
                title = ad.find('div', class_="product_item__title").text
                price = ad.find('div', class_="product_item__description").find('div').text
                price = re.sub("[^0-9]", "", price)
            except:
                continue

            if title and price:
                result.append({title: price})

        return result

    def data_mining(self):
        url = self.link

        titles_prices_list = []

        while True:
            soup = self._soup(url)
            new_titles_prices_list = self._get_titles_and_prices(soup)
            titles_prices_list = titles_prices_list + new_titles_prices_list
            new_url = self._find_next_page(soup)
            if new_url:
                url = new_url
                continue
            else:
                break

        sorted_result = self._data_sorting(titles_prices_list)

        return sorted_result
