from peewee import *

from config import *

ekatalog = PostgresqlDatabase(database=e_db, user=user, password=pwd, host=host)
pda = PostgresqlDatabase(database=p_db, user=user, password=pwd, host=host)
smartphones = PostgresqlDatabase(database=s_db, user=user, password=pwd, host=host)
proxies = PostgresqlDatabase(database=proxy, user=user, password=pwd, host=host)


''' Smartphones.db '''


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


''' Ekatalog.db '''


class E(Model):

    class Meta:
        database = ekatalog


class EkatalogHomepage(E):
    id = PrimaryKeyField(unique=True)
    section = CharField(null=True)
    link = CharField(null=True)
    link_all = CharField(null=True)
    updated = CharField(null=True)


class EkatalogBrands(E):
    id = PrimaryKeyField(unique=True)
    brand = CharField(null=True)
    link = CharField(null=True)
    updated = CharField(null=True)


class EkatalogSmartphones(E):
    id = PrimaryKeyField(unique=True)
    model = CharField(null=True)
    link = CharField(null=True)
    img = CharField(null=True)
    updated = CharField(null=True)


''' Pda.db '''


class P(Model):

    class Meta:
        database = pda


class PdaCategories(P):
    id = PrimaryKeyField(unique=True)
    category = CharField(null=True)
    link = CharField(null=True)
    updated = CharField(null=True)


class PdaBrands(P):
    id = PrimaryKeyField(unique=True)
    category = CharField(null=True)
    brand = CharField(null=True)
    link = CharField(null=True)
    updated = CharField(null=True)


class PdaSmartphones(P):
    id = PrimaryKeyField(unique=True)
    brand = CharField(null=True)
    model = CharField(null=True)
    link = CharField(null=True)
    img = CharField(null=True)
    updated = CharField(null=True)


''' proxies.db '''


class ProxyList(Model):
    schema = CharField()
    proxy = CharField()

    class Meta:
        database = proxies


def create_tables():
    with smartphones:
        smartphones.create_tables([TopBrands, Smartphones, Prices, PricesSecondMarkets])

    with ekatalog:
        ekatalog.create_tables([EkatalogHomepage, EkatalogBrands, EkatalogSmartphones])

    with pda:
        pda.create_tables([PdaCategories, PdaBrands, PdaSmartphones])

    with proxies:
        proxies.create_tables([ProxyList])


if __name__ == '__main__':
    create_tables()
