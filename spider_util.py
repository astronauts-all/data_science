import random
import pandas as pd

host_list = []
port_list = []
# 获取ip代理地址
with open('host.txt', mode='r', encoding='utf-8') as f:
    lines = f.readlines()
    for line in lines:
        data_list = line.split(':')
        host_list.append(data_list[0])
        port_list.append(data_list[1].strip())

# 将ip代理地址转化为固定格式后存储
proxy_list = []
for i in range(len(host_list)):
    proxy_list.append(f'http://{host_list[i]}:{port_list[i]}')


# 随机获取一个ip代理地址
def get_proxy():
    proxy = random.choice(proxy_list)
    proxies = {
        "http": proxy,
        "https": proxy
    }
    return proxies


# 用来移除连接超时的ip代理地址
def remove_proxy(proxy):
    if proxy in proxy_list:
        proxy_list.remove(proxy)


# 随机获取请求头信息
def get_headers():
    headers = [{
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
        'Connection': 'close'
    },
        {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.68',
            'Connection': 'close'
        }
    ]
    return random.choice(headers)


# 用于写出数据
def write_data(data_list):
    data = pd.DataFrame(data_list)
    data.to_csv('昆明二手房数据.csv', mode='a', encoding='utf-8', index=False)
