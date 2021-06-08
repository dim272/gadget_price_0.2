from random import choice

import requests
from bs4 import BeautifulSoup

from data import ProxyList


class MyPerfectProxy:

    @staticmethod
    def __get_soup():
        url = 'https://free-proxy-list.net/'
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'lxml')
        return soup

    def new_list(self):
        soup = self.__get_soup()
        db = ProxyList

        try:
            tr_list = soup.find('table', id='proxylisttable').find('tbody').find_all('tr')
        except KeyError:
            tr_list = []

        if tr_list:
            for tr in tr_list:
                td = tr.find_all('td')
                ip = td[0].text
                port = td[1].text
                schema = 'https' if 'yes' in td[6].text else 'http'
                server = ip + ':' + port
                db.create(schema=schema, proxy=server)


class MyPerfectRequest(MyPerfectProxy):
    def __init__(self, use_proxy=False, desktop_headers=False, android_headers=False, ios_headers=False):
        self.__use_proxy = use_proxy
        self.__desktop_h = desktop_headers
        self.__android_h = android_headers
        self.__ios_h = ios_headers

    @staticmethod
    def __random_headers(file_name):
        with open(file_name, 'r') as f:
            lines = f.readlines()
            random_line = choice(lines).replace('\n', '').replace('"', '')
            headers = {'User-Agent': random_line}
            return headers

    def __headers(self):
        desktop_headers = 'MyPerfectRequest/headers.csv'
        android_headers = 'MyPerfectRequest/headers_android.csv'
        iOS_headers = 'MyPerfectRequest/headers_iOS.csv'

        headers = ''

        if self.__android_h or self.__ios_h:
            if self.__android_h and self.__ios_h:
                random_ = choice([0, 1])
                if random_:
                    headers = self.__random_headers(android_headers)
                else:
                    headers = self.__random_headers(iOS_headers)

            elif self.__android_h:
                headers = self.__random_headers(android_headers)

            elif self.__ios_h:
                headers = self.__random_headers(iOS_headers)
        else:
            headers = self.__random_headers(desktop_headers)

        return headers

    def __proxy_check(self, server, url):
        headers = self.__headers()
        try:
            req = requests.get(url, headers=headers, proxies=server, timeout=7)
        except requests.exceptions.RequestException:
            req = ''

        return req

    def __request_with_proxy(self, url):
        req = ''

        while True:
            proxy_list = ProxyList.select()

            if not proxy_list:
                print('Get new proxies list')
                self.new_list()
                continue
            for i in proxy_list:
                schema = i.schema
                ip = i.proxy
                server = {schema: ip}
                req = self.__proxy_check(server, url)
                print('PROXY', f'{schema}:{ip}', 'IS', bool(req), 'FOR', url)
                if req:
                    break
                else:
                    ProxyList.delete().where(ProxyList.proxy == ip).execute()
                    continue
            if req:
                break

        return req

    def __request(self, url):
        if self.__use_proxy:
            req = self.__request_with_proxy(url)
        else:
            headers = self.__headers()
            req = requests.get(url, headers=headers, timeout=3)

        return req

    def soup(self, url):
        r = self.__request(url)
        soup = BeautifulSoup(r.text, 'lxml')
        return soup

    def manual_request_and_soup(self, url, server):
        headers = self.__headers()
        req = requests.get(url, headers=headers, proxies=server, timeout=5)
        soup = BeautifulSoup(req.text, 'lxml')

        return soup
