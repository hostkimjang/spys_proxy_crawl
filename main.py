import logging
import json
import pprint
import re
import time
import requests
import urllib3
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL:@SECLEVEL=1'
import execjs
from bs4 import BeautifulSoup as bs

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"})
resp = session.post("https://spys.one/en/socks-proxy-list/")
soup = bs(resp.text, "html.parser")
sp = soup.select("tr:nth-child(1)")
xx0 = sp[2].select("input[type=hidden]")[0].attrs["value"]

payload = {
    'xx0': xx0,
    'xpp': '5',
    'xf1': '0',
    'xf4': '0',
    'xf5': '0'
}

url = "https://spys.one/en/socks-proxy-list/"

list = []

def get_index():
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"})
    resp = session.post("https://spys.one/en/socks-proxy-list/")
    soup = bs(resp.text, "html.parser")
    sp = soup.select("tr:nth-child(1)")
    xx0 = sp[2].select("input[type=hidden]")[0].attrs["value"]

    payload = {
        'xx0': xx0,
        'xpp': '5',
        'xf1': '0',
        'xf4': '0',
        'xf5': '0'
    }

    try:
        rsp = session.post(url=url, data=payload)
        if rsp.status_code == 200:
            html = rsp.text
            return html
        else:
            exit('Can not get the website.')
    except ConnectionError:
        exit('Please run your proxy app and try again.')


def parse_proxy_info(html):
    pattern = re.compile('onmouseout.*?spy14>(.*?)<.*?>"(.*?)<\/.*?>([HTTPS|SOCKS5]+)', re.S)
    info = re.findall(pattern, html)
    if len(info) > 30:
        print('PROXY: {}'.format(len(info)))
    else:
        exit('Operation too frequent, please change your proxy and try again later.')
    if 'https-' in url:
        pattern_js = re.compile('\/javascript">(eval.*\)\))')
    else:
        pattern_js = re.compile('table><script.*?>(.*?)<\/script')
    ec = re.findall(pattern_js, html)
    if 'eval(' in ec[0]:
        with open('ejs.js', 'w+', encoding='utf8') as f:
            f.write(ec[0][5:-1])
        hc = execjs.eval(open('ejs.js', 'r', encoding='utf8').read())
        eec = hc.replace(';', ';\n')
    else:
        eec = ec[0].replace(';', ';\n')
    ctx ="""
    function
    port()
    {
    % s
    return port;
    }"""


    for i in info:
        ip = i[0]
        protocol = i[2].lower()
        a = i[1].replace('+(', '+String(').replace('))', ')')
        b = 'port = ' + a[1:]
        c = eec + b
        d = ctx % (str(c))
        port = execjs.compile(d).call('port')
        print(f"ip:{ip}, port:{port}, protocol:{protocol}")
        list.append(
            {"ip":ip, "port":port, "protocol":protocol}
        )
    pprint.pprint(list)
    store(list)

def get_proxy():
    data = load_data()
    for i in data:
        ip = i["ip"]
        port = i["port"]
        #protocol = i["protocol"]
        proxy = {
            "http": "socks5://{}:{}".format(ip, port),
            "https": "socks5://{}:{}".format(ip, port)
        }
        try:
            test_url = f"https://checkip.amazonaws.com/"
            response = requests.get(url=test_url, headers=headers, proxies=proxy, timeout=10)
            page = bs(response.text, "html.parser")
            if response.status_code == 200:
                print("우회된 아이피입니다.")
                print(response.text)
                #rint(page.select("h2.radar-heading.c.eu.d.il.ec.jo")[0].text)
                # print(page.select("p.lead:nth-child(2)")[0].text)
                continue
            else:
                print("fail")
                return None
        except Exception as e:
            print(e)
            continue
"""
        try:
            response = requests.get(url=test_url, headers=headers, proxies=proxy, timeout=3)
            page = bs(response.text, "html.parser")
            if response.status_code == 200:
                print("success")
                print(page.select("h1.Title.h3.mb-6.js-ipdata-ip-address")[0].text)
                #print(page.select("p.lead:nth-child(2)")[0].text)
                return proxy
            else:
                print("fail")
                return None
        except Exception as e:
            print(e)
            continue
"""


def store(list):
    with open("proxy.json", "wt", encoding='utf-8') as f:
        json.dump(list, f, ensure_ascii=False, indent=4)
    print("store is done")

def load_data():
    with open("proxy.json", "rt", encoding='utf-8') as f:
        data = json.load(f)
        return data

#html = get_index()
#parse_proxy_info(html)
get_proxy()