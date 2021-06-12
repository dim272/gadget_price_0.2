from peewee import *

from config import *

smartphones = PostgresqlDatabase(database=s_db, user=user, password=pwd, host=host)
proxies = PostgresqlDatabase(database=proxy, user=user, password=pwd, host=host)


''' Smartphones '''


class S(Model):

    class Meta:
        database = smartphones


class TopBrands(S):
    id = PrimaryKeyField(unique=True)
    brand = CharField()
    top = IntegerField(null=True)


class Smartphones(S):
    id = PrimaryKeyField(unique=True)
    brand = CharField()
    model = CharField()
    ram = CharField(null=True)
    storage = CharField(null=True)
    nfc = BooleanField(null=True)
    release = CharField(null=True)
    os = CharField(null=True)
    display = CharField(null=True)
    cpu = CharField(null=True)
    cpu_num = CharField(null=True)
    core_speed = CharField(null=True)
    battery = CharField(null=True)
    weight = CharField(null=True)
    dimensions = CharField(null=True)
    in_stock = BooleanField(null=True)
    url_ekatalog = CharField(null=True)
    url_avito = CharField(null=True)
    url_youla = CharField(null=True)
    img = CharField(null=True)
    top = IntegerField(null=True)
    updated = CharField(null=True)


class Prices(S):
    id = PrimaryKeyField(unique=True)
    ozon = CharField(null=True)
    yandex = CharField(null=True)
    mvideo = CharField(null=True)
    eldorado = CharField(null=True)
    citilink = CharField(null=True)
    svyaznoy = CharField(null=True)
    megafon = CharField(null=True)
    mts = CharField(null=True)
    sber_mm = CharField(null=True)
    smartphone_id = ForeignKeyField(Smartphones, to_field='id')
    updated = CharField(null=True)


class PricesSecondMarkets(S):
    id = PrimaryKeyField(unique=True)
    avito = CharField(null=True)
    youla = CharField(null=True)
    smartphone_id = ForeignKeyField(Smartphones, to_field='id')
    updated = CharField(null=True)


smartphones.bind([Smartphones, Prices, PricesSecondMarkets])

''' Ekatalog '''


class EkatalogHomepage(S):
    id = PrimaryKeyField(unique=True)
    section = CharField(null=True)
    link = CharField(null=True)
    link_all = CharField(null=True)
    updated = CharField(null=True)


class EkatalogBrands(S):
    id = PrimaryKeyField(unique=True)
    brand = CharField(null=True)
    link = CharField(null=True)
    updated = CharField(null=True)


class EkatalogSmartphones(S):
    id = PrimaryKeyField(unique=True)
    model = CharField(null=True)
    link = CharField(null=True)
    img = CharField(null=True)
    updated = CharField(null=True)


''' Pda '''


class PdaCategories(S):
    id = PrimaryKeyField(unique=True)
    category = CharField(null=True)
    link = CharField(null=True)
    updated = CharField(null=True)


class PdaBrands(S):
    id = PrimaryKeyField(unique=True)
    category = CharField(null=True)
    brand = CharField(null=True)
    link = CharField(null=True)
    updated = CharField(null=True)


class PdaSmartphones(S):
    id = PrimaryKeyField(unique=True)
    brand = CharField(null=True)
    model = CharField(null=True)
    link = CharField(null=True)
    img = CharField(null=True)
    updated = CharField(null=True)


''' proxies '''


class ProxyList(Model):
    schema = CharField()
    proxy = CharField()

    class Meta:
        database = proxies


def create_tables():
    smartphones.create_tables([TopBrands, Smartphones, Prices, PricesSecondMarkets, EkatalogHomepage,
                               EkatalogBrands, EkatalogSmartphones, PdaCategories, PdaBrands, PdaSmartphones])
    proxies.create_tables([ProxyList])


if __name__ == '__main__':
    create_tables()
