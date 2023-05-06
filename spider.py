import time
from spider_util import *

from multiprocessing.dummy import Pool as pl
import requests
import re
from pyquery import PyQuery
from bs4 import BeautifulSoup
import pandas as pd
import random


# 返回分区域后的url地址
def get_region_url(url, headers):
    region_list = []  # 每个区域的链接地址
    while not region_list:
        resp = requests.get(url, headers)
        page = BeautifulSoup(resp.text, 'html.parser')
        div = str(page.find('div', attrs={'data-role': 'ershoufang'}))
        doc = PyQuery(div)
        hrefs = doc('a').items()
        for href in hrefs:
            region_list.append(f'https://km.lianjia.com{href.attr("href")}')
    return region_list


# 获取当前分页页数
def get_total_page(url, headers):
    div = ''
    while div == '':
        resp = requests.get(url, headers)
        doc = PyQuery(resp.text)
        div = str(doc('div .house-lst-page-box'))
        obj = re.compile(r'totalPage&quot;:(?P<totalPage>.*?),&quot')
    total_page = int(obj.findall(div)[0])  # 当前房屋预览信息页面的页数
    return total_page


# 不同区域下按价格多少划分后的url地址
def min_divide_url(url):
    url_list = []
    for i in range(1, 11):
        # 拼接地址
        href = f'{url}p{i}/'
        url_list.append(href)
    return url_list


# 获取html页面下每套房详情的url
def get_house_url(url, headers):
    href_list = []  # 房屋预览页面下查看每套房屋详情的地址
    while not href_list:
        resp = requests.get(url, headers)
        doc = PyQuery(resp.text)
        hrefs = doc('a.noresultRecommend').items()
        for href in hrefs:
            href_list.append(href.attr('href'))
    return href_list


# 爬虫主程序，获取每套房的详情信息
def get_house_info(url):
    house_info = []
    name = ''
    while name == '' and not house_info:  # 用来判断是否获取到页面信息
        try:
            proxies = get_proxy()  # 随机获取ip代理地址
            resp = requests.get(url, headers=get_headers(), proxies=proxies)
        except:
            print(f'{proxies["https"]}代理ip地址连接超时')
            remove_proxy(proxies['https'])  # 移除连接超时的代理ip地址
            resp = requests.get(url, headers=get_headers())  # 不使用代理ip获取页面信息

        doc = PyQuery(resp.text)
        name = doc('a.info').text()
        price = doc('span.total').text()
        location = doc('div.areaName span.info a:first-child').text()
        district = doc('div.areaName span.info a:last-child').text()
        house_info.append(name)
        house_info.append(price)
        house_info.append(location)
        house_info.append(district)

        obj = re.compile(r'<li><span class="label">.*?</span>(?P<base>.*?)</li>', re.S)
        result = obj.finditer(resp.text)
        for item in result:
            house_info.append(item.group('base'))
    return house_info


if __name__ == '__main__':
    # 获取不同区域对应的链接地址
    region_list = get_region_url('https://km.lianjia.com/ershoufang/', {})
    count = 1  # 记录爬取的页数

    pool = pl(12)  # 初始化线程池
    for region in region_list:
        total_page = get_total_page(region, get_headers())  # 获取当前区域页面下的分页数
        if total_page == 100:  # 如果分页等于100，有超过100页数据，对当前区域下按照不同房屋价格区间进行爬取
            url_list = min_divide_url(region)  # 当前区域页面按照不同房屋价格区间划分后的链接地址

            for url in url_list:
                page_count = get_total_page(url, get_headers())  # 获取当前页面下的分页数
                for i in range(1, page_count + 1):  # 对所有分页进行数据爬取
                    house_list = []
                    time.sleep(random.randint(3, 5))
                    index = url.rfind('p')
                    href_list = get_house_url(f'{url[:index]}pg{i}{url[index:]}', get_headers())  # 拼接页数到地址
                    data_list = pool.map(get_house_info, href_list)  # 开启多线程爬取
                    for data in data_list:
                        house_list.append(data)

                    write_data(house_list)  # 每爬取一页的数据后便写出数据
                    print(f'爬取第{count}页数据完成')
                    count += 1
        else:  # 当前区域页面下的分页数小于100，直接按照区域进行爬取
            for i in range(1, total_page + 1):
                house_list = []
                href_list = get_house_url(f'{region}pg{i}', get_headers())  # 拼接页数到地址
                data_list = pool.map(get_house_info, href_list)  # 开启多线程爬取
                for data in data_list:
                    house_list.append(data)

                write_data(house_list)  # 每爬取一页的数据后便写出数据
                print(f'爬取第{count}页数据完成')
                count += 1
