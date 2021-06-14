from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from data import *

'''

[Apple] > [iPhone 11] > [128]
[Xiaomi] > [Redmi Note 9] > [4] > [64]

'''


class Choice:
    def __init__(self):
        self.__page = 1
        self._items_used = 0

    def __get_len_items(self):
        return len(self.items)

    def __rows_we_need(self):
        num = self.__get_len_items()

        if num % 3 != 0:
            result = (num // 3) + 1
        else:
            result = int(num / 3)

        return result

    @staticmethod
    def _breadcrumbs_button_generator(select, item):
        cd = f'select:{select.lower()}:item:{item}'
        btn = InlineKeyboardButton(text=item, callback_data=cd)
        return btn

    def __button_generator(self, item):
        class_name = self.__class__.__name__
        cd = f'select:{class_name.lower()}:item:{item}'
        btn = InlineKeyboardButton(text=item, callback_data=cd)
        return btn

    @staticmethod
    def __error_button():
        return InlineKeyboardButton(text='Ошибка', callback_data='select:control:item:start')

    @staticmethod
    def _start_button():
        return InlineKeyboardButton(text='< Начало', callback_data='select:control:item:start')

    def __next_page_button(self):
        class_name = self.__class__.__name__
        cd = f'select:{class_name.lower()}:item:next'
        btn = InlineKeyboardButton(text='>', callback_data=cd)
        return btn

    def __prev_page_button(self):
        class_name = self.__class__.__name__
        cd = f'select:{class_name.lower()}:item:prev'
        btn = InlineKeyboardButton(text='<', callback_data=cd)
        return btn

    def __breadcrumbs_row_generator(self):
        class_name = self.__class__.__name__
        breadcrumbs_row = []

        if class_name != 'Brand':
            start_button = self._start_button()
            breadcrumbs_row.append(start_button)
            brand_name = self.brand
            brand_button = self._breadcrumbs_button_generator('brand', brand_name)
            breadcrumbs_row.append(brand_button)
            if class_name == 'Ram':
                model_name = self.model
                model_button = self._breadcrumbs_button_generator('model', model_name)
                breadcrumbs_row.append(model_button)
            if class_name == 'Storage':
                model_name = self.model
                model_button = self._breadcrumbs_button_generator('model', model_name)
                breadcrumbs_row.append(model_button)
                ram = self.ram
                ram_button = self._breadcrumbs_button_generator('ram', ram)
                breadcrumbs_row.append(ram_button)

        return breadcrumbs_row

    def __row_generator(self, row_number):
        row = []
        counter = 1
        while counter <= 3 and self._items_used < self.__get_len_items():
            item = self.items[self._items_used]
            btn = self.__button_generator(item)

            if counter == 1:
                if row_number == 1:
                    if self._items_used == 0:
                        row.append(btn)
                        counter += 1
                        self._items_used += 1
                    else:
                        row.append(self.__prev_page_button())
                        counter += 1
                else:
                    row.append(btn)
                    counter += 1
                    self._items_used += 1
            elif counter == 2:
                row.append(btn)
                counter += 1
                self._items_used += 1
            elif counter == 3:
                if row_number == 3 and self._items_used == (self.__get_len_items() - 1):
                    row.append(btn)
                    counter += 1
                    self._items_used += 1
                elif row_number == 3:
                    row.append(self.__next_page_button())
                    counter += 1
                else:
                    row.append(btn)
                    counter += 1
                    self._items_used += 1
            else:
                row.append(self.__error_button())
                counter += 1

        return row

    def keyboard_generator(self):
        inline_keyboard = []
        breadcrumbs = self.__breadcrumbs_row_generator()
        row_number = 1

        if breadcrumbs:
            inline_keyboard.append(breadcrumbs)

        if self.__rows_we_need() > 3:
            rows_we_need = 3
        else:
            rows_we_need = self.__rows_we_need()

        while row_number <= rows_we_need:
            row = self.__row_generator(row_number)
            inline_keyboard.append(row)
            row_number += 1

        keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
        return keyboard

    def next_page(self):
        self.__page += 1

    def prev_page(self):
        if self.__page != 1:
            self.__page -= 1
            if self.__page == 1:
                self._items_used -= 15
            else:
                self._items_used -= 14
        else:
            self._items_used -= 8


class Brand(Choice):
    def __init__(self):
        self.items = self.__get_top_brands()
        super().__init__()

    @staticmethod
    def __get_top_brands():
        print('Top brands')
        db = TopBrands
        select = db.select(db.brand).order_by(db.top.desc())
        brand_list = []
        for each in select:
            brand_list.append(each.brand)
        print(brand_list)
        return brand_list

    @staticmethod
    def increase_top_value(brand_name):
        db = TopBrands
        try:
            select = db.get(db.brand.contains(brand_name.strip()))
            top = select.top
            top += 1
            select.update(top=top).where(db.brand == select.brand).execute()
        except DoesNotExist:
            db.create(brand=brand_name, top=1)


class Model(Choice):
    def __init__(self, brand):
        self.brand = brand
        self.items = self.__get_models()
        super().__init__()

    def __get_models(self):
        print('Get models to brand:', self.brand.strip())
        db = Smartphones
        select = db.select(db.model).where(db.brand == self.brand.strip()).order_by(db.top.desc())
        model_list = []
        for each in select:
            model = each.model
            if model not in model_list:
                model_list.append(model)

        print(model_list)
        return model_list

    @staticmethod
    def increase_top_value(model_name):
        print('Increase top value model:', model_name)
        db = Smartphones
        try:
            select = db.get(db.model.contains(model_name.strip()))
            top = select.top
            print('increase top value from:', top)
            print(select.model)

            try:
                top += 1
            except TypeError:
                top = 1
            print('to:', top)
            select.update(top=top).where(db.model == select.model).execute()
        except DoesNotExist:
            pass


class Ram(Choice):
    def __init__(self, brand, model):
        self.brand = brand
        self.model = model
        self.items = self.__get_ram()
        super().__init__()

    def __get_ram(self):
        print('get ram')
        db = Smartphones
        select = db.select(db.ram).where(db.brand == self.brand.strip(), db.model == self.model.strip())
        ram_list = []
        for each in select:
            try:
                ram = each.ram
                print(ram)
            except:
                continue
            if ram not in ram_list:
                ram_list.append(ram)

        return ram_list


class Storage(Choice):
    def __init__(self, brand, model, ram):
        self.brand = brand
        self.model = model
        self.ram = ram
        self.items = self.__get_storage()
        super().__init__()

    def __get_storage(self):
        print('get storage')
        db = Smartphones

        if self.ram:
            select = db.select(db.storage).where(db.brand == self.brand.strip(),
                                                 db.model == self.model.strip(),
                                                 db.ram == self.ram.strip())
        else:
            select = db.select(db.storage).where(db.brand == self.brand.strip(),
                                                 db.model == self.model.strip())
        storage_list = []
        for each in select:
            try:
                storage = each.storage
            except:
                continue
            if storage not in storage_list:
                storage_list.append(storage)

        return storage_list


class Breadcrumbs(Choice):
    def __init__(self, ):
        super().__init__()

    def breadcrumbs_keyboard(self, brand, model, ram, storage):
        values = [brand, model, ram, storage]
        specifications = []
        for val in values:
            if val:
                specifications.append([f'{val}', val])

        breadcrumbs = []
        start_button = self._start_button()
        breadcrumbs.append(start_button)
        for each in specifications:
            select = each[0]
            item = each[1]
            button = self._breadcrumbs_button_generator(select, item)
            breadcrumbs.append(button)

        return breadcrumbs


class FinaleKeyboard(Breadcrumbs):

    def __init__(self):
        super().__init__()

    def links_to_markets(self):
        print(self.id)
        db = Smartphones
        search = db.select().where(db.id == self.id)
        links = {}

        if search:
            for item in search:
                ekatalog = item.url_ekatalog
                if ekatalog:
                    links['E-Katalog'] = ekatalog
                avito = item.url_avito
                if avito:
                    links['Avito'] = avito
                youla = item.url_youla
                if youla:
                    links['Youla'] = youla

        return links

    @staticmethod
    def market_button_generator(name, link):
        return InlineKeyboardButton(text=name, url=link)

    def generate(self):
        breadcrumbs = self.breadcrumbs_keyboard(self.brand, self.model, self.ram, self.storage)
        inline_keyboard = [breadcrumbs]

        links = self.links_to_markets()
        if links:
            links_block = []
            for item in links:
                link = links.get(item)
                market_button = self.market_button_generator(item, link)
                links_block.append(market_button)
            inline_keyboard.append(links_block)

        keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

        return keyboard


class Info:

    def __init__(self):
        self.id = None

    def specifications(self):
        db = Smartphones

        specifications = db.select().where(db.brand == self.brand, db.model == self.model,
                                           db.ram == self.ram, db.storage == self.storage)

        id_ = db.get(db.brand == self.brand, db.model == self.model, db.ram == self.ram, db.storage == self.storage)
        self.id = smart_id = id_.id

        release = os_ = weight = dimensions = battery = display = cpu = in_stock = cpu_num = core_speed = '---'

        for item in specifications:
            release = item.release
            os_ = item.os
            weight = item.weight
            dimensions = item.dimensions
            battery = item.battery
            display = item.display
            cpu = item.cpu
            in_stock = item.in_stock
            cpu_num = item.cpu_num
            core_speed = item.core_speed
            img = item.img

        if self.ram and self.storage:
            first_row = f'{self.brand} {self.model} {self.ram}/{self.storage}'
        elif self.ram and not self.storage:
            first_row = f'{self.brand} {self.model} {self.ram}'
        elif (not self.ram and self.storage) or self.brand == 'Apple':
            first_row = f'{self.brand} {self.model} {self.storage}'
        else:
            first_row = f'{self.brand} {self.model}'

        if in_stock:
            in_stock = 'Есть в продаже'
        else:
            in_stock = 'Нет в продаже'

        message = f'{first_row}\n' \
                  f'Релиз: {release}, Экран: {display}\n' \
                  f'ОС: {os_}, Аккум.: {battery} мАч\n' \
                  f'Проц.: {cpu}\n' \
                  f'Количество ядер: {cpu_num}, Такт. частота: {core_speed} ГГц\n' \
                  f'Габариты (мм): {dimensions}\n' \
                  f'Вес: {weight} гр., {in_stock}'

        prices = self.prices(smart_id)

        if prices:
            for row in prices:
                message += f'\n{row}'

        return {'text': message, 'img': img, 'smartphone_id': smart_id}

    @staticmethod
    def prices(smartphone_id):
        prices_table = Prices

        try:
            prices = prices_table.select().where(prices_table.smartphone_id == smartphone_id)
        except DoesNotExist:
            prices = []

        prices2_table = PricesSecondMarkets

        try:
            prices2 = prices2_table.select().where(prices2_table.smartphone_id == smartphone_id)
        except DoesNotExist:
            prices2 = []

        ozon = yandex = mvideo = eldorado = citilink = svyaznoy = \
            aliexpress = megafon = mts = sber = avito = youla = ''

        message = []

        for item in prices:
            ozon = item.ozon
            yandex = item.yandex
            mvideo = item.mvideo
            eldorado = item.eldorado
            citilink = item.citilink
            svyaznoy = item.svyaznoy
            megafon = item.megafon
            mts = item.mts
            sber = item.sber_mm
            aliexpress = item.aliexpress

        for item in prices2:
            avito = item.avito
            youla = item.youla

        if ozon:
            row = f'Озон: {ozon} р'
            message.append(row)

        if yandex:
            row = f'Яндекс: {yandex} р'
            message.append(row)

        if mvideo:
            row = f'М-Видео: {mvideo} р'
            message.append(row)

        if eldorado:
            row = f'Эльдорадо: {eldorado} р'
            message.append(row)

        if citilink:
            row = f'Citilink: {citilink} р'
            message.append(row)

        if svyaznoy:
            row = f'Связной: {svyaznoy} р'
            message.append(row)

        if megafon:
            row = f'Мегафон: {megafon} р'
            message.append(row)

        if mts:
            row = f'МТС: {mts} р'
            message.append(row)

        if aliexpress:
            row = f'AliExpress: {aliexpress} р (возможно не новый)'
            message.append(row)

        if sber:
            row = f'СберМегаМаркет: {sber} р'
            message.append(row)

        if avito:
            row = f'Авито: {avito} р (средняя)'
            message.append(row)

        if youla:
            row = f'Юла: {youla} р (средняя)'
            message.append(row)

        if message:
            message.insert(0, '-------- цены --------')

        return message

    def avito_youla_update(self):
        pass
        # a = Avito(self.brand, self.model, self.storage, self.ram)
        # y = Youla(self.brand, self.model, self.storage, self.ram)
        # avito_parsing = a.data_mining()
        # youla_parsing = y.data_mining()
        # result = {**avito_parsing, **youla_parsing}
        # return result

    # добавить результат в базу смартфонов с екаталога "smarphones"
    # если происходит парсинг, реализовать выдачу последовательную выдачу финального сообщения:
    # сперва то, что есть в базе (характеристики и имг), после парсинга цены


class FinaleMessage(Info, FinaleKeyboard):
    def __init__(self, brand, model, ram, storage, smartphone_id=None):
        self.brand = brand
        self.model = model
        self.ram = ram
        self.storage = storage
        self.id = smartphone_id
        super().__init__()
