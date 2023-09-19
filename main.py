import asyncio
import logging
import json
import pprint
import random
import re
import time
import requests
import urllib3
import execjs
import certifi
from bs4 import BeautifulSoup as bs
from httpx import AsyncClient, AsyncHTTPTransport, Proxy
from httpx_socks import AsyncProxyTransport
import multiprocessing
import fake_useragent.fake
import logging
import ssl

certifi.where()

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}

logging.basicConfig(level=logging.DEBUG)

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

result = []

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
        result.append(
            {"ip":ip, "port":port, "protocol":protocol}
        )
    pprint.pprint(result)
    store(result)

def get_proxy(data):
    index_to_remove = []  # 예외가 발생한 데이터의 인덱스를 저장할 리스트
    for index, i in enumerate(data):
        ip = i["ip"]
        port = i["port"]
        proxy = {
            "http": "socks5://{}:{}".format(ip, port),
            "https": "socks5://{}:{}".format(ip, port)
        }
        print(proxy)
        try:
            test_url = f"http://ip-api.com/json/"
            urllib3.disable_warnings()
            response = requests.get(url=test_url, headers=headers, proxies=proxy, verify=False, timeout=3)
            #page = bs(response.text, "html.parser")
            if response.status_code == 200:
                print("우회된 아이피입니다.")
                pprint.pprint(response.json())
                # 성공한 경우 아무 작업도 하지 않고 다음 데이터로 이동
                continue
            else:
                print("fail")
                # 예외가 발생한 데이터의 인덱스를 기록
                index_to_remove.append(index)
        except Exception as e:
            print(e)
            # 예외가 발생한 데이터의 인덱스를 기록
            index_to_remove.append(index)

    # 예외가 발생한 데이터 삭제
    for index in reversed(index_to_remove):
        del data[index]

    final_store(data)

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

def process_data(data_chunk):
    index_to_remove = []
    for index, i in enumerate(data_chunk):
        ip = i["ip"]
        port = i["port"]
        proxy = {
            "http": "socks5://{}:{}".format(ip, port),
            "https": "socks5://{}:{}".format(ip, port)
        }
        print(proxy)
        try:
            test_url = f"https://api.myip.com/"
            urllib3.disable_warnings()
            response = requests.get(url=test_url, headers=headers, proxies=proxy, verify=False, timeout=3)
            if response.status_code == 200:
                print("우회된 아이피입니다.")
                pprint.pprint(response.json())
                continue
            else:
                print("fail")
                index_to_remove.append(index)
        except Exception as e:
            print(e)
            index_to_remove.append(index)

    return index_to_remove

def async_process_data(args):
    result = asyncio.run(async_multi_proxy_test(args))
    #pprint.pprint(result)
    return result

def run_with_multiprocessing(data, num_processes):
    start = time.time()
    pool = multiprocessing.Pool(processes=num_processes)
    chunk_size = len(data) // num_processes
    data_chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
    results = pool.map(process_data, data_chunks)
    pool.close()
    pool.join()

    index_to_remove = []
    for result in results:
        index_to_remove.extend(result)

    for index in reversed(index_to_remove):
        del data[index]
    end = time.time()

    final_store(data)
    print(f"실행 시간: {end - start}")
    pprint.pprint(data)


def run_with_multiprocessing_and_async(data, num_processes):
    total = []
    start = time.time()
    pool = multiprocessing.Pool(processes=num_processes)
    chunk_size = len(data) // num_processes
    data_chunks = [(data[i:i + chunk_size]) for i in range(0, len(data), chunk_size)]
    tmp = pool.map(async_process_data, data_chunks)
    if not tmp == []:
        for i in tmp:
            total.extend(i)
    pool.close()
    pool.join()
    pprint.pprint(total)
    end = time.time()
    print(f"실행 시간: {end - start}")
    final_store(total)


async def async_proxy_test(data, result):
    start = time.time()
    random.shuffle(data)
    await asyncio.gather(
        *[proxy_test(result, proxy_data=proxy_data) for proxy_data in data],
    )
    pprint.pprint(result)
    final_store(result)
    end = time.time()
    print(f"실행 시간: {end - start}")

async def async_multi_proxy_test(data):
    #pprint.pprint(data)
    print("프로세서 하나 시작")
    #time.sleep(100)
    result = []
    await asyncio.gather(
        *[multi_proxy_test(result, proxy_data=proxy_data) for proxy_data in data],
    )
    pprint.pprint(result)
    print("일단 프로세서 하나 끝남")
    return result
    #final_store(result)

async def multi_proxy_test(result:list, proxy_data: dict):
    ip = proxy_data["ip"]
    port = proxy_data["port"]
    protocol = proxy_data["protocol"]

    #proxy = {
    #    "all://": "{}://{}:{}".format(protocol,ip, port)
    #}
    proxy = f"{protocol}://{ip}:{port}"

    headers = {'User-Agent': fake_useragent.FakeUserAgent().random}
    test_url = 'https://api.myip.com/'

    proxy_ssl = ssl.SSLContext(ssl.PROTOCOL_TLS)
    proxy_ssl.verify_mode = ssl.CERT_REQUIRED
    proxy_ssl.load_verify_locations(certifi.where())

    transport = AsyncProxyTransport.from_url(proxy, verify=False)

    try:
        async with AsyncClient(transport=transport) as client:
            res = await client.get(test_url, headers=headers, timeout=10)
            logging.debug(res.json())
            print(res.json())
            #print(json.dumps(proxy, indent=4, ensure_ascii=False, escape_forward_slashes=False))
            #print(json.dumps(res.json(), indent=4, ensure_ascii=False, escape_forward_slashes=False))
    except Exception as e:
        print(e)
    else:
        result.append({
            "ip": ip,
            "port": port,
            "protocol": protocol
        })
    return result

async def proxy_test(result:list, proxy_data: dict):
    ip = proxy_data["ip"]
    port = proxy_data["port"]
    protocol = proxy_data["protocol"]

    #proxy = {
    #    "all://": "{}://{}:{}".format(protocol,ip, port)
    #}
    proxy = f"{protocol}://{ip}:{port}"

    headers = {'User-Agent': fake_useragent.FakeUserAgent().random}
    test_url = 'https://api.myip.com/'

    proxy_ssl = ssl.SSLContext(ssl.PROTOCOL_TLS)
    proxy_ssl.verify_mode = ssl.CERT_REQUIRED
    proxy_ssl.load_verify_locations(certifi.where())

    transport = AsyncProxyTransport.from_url(proxy, verify=False)

    try:
        async with AsyncClient(transport=transport) as client:
            res = await client.get(test_url, headers=headers, timeout=10)
            logging.debug(res.json())
            print(res.json())
            #print(json.dumps(proxy, indent=4, ensure_ascii=False, escape_forward_slashes=False))
            #print(json.dumps(res.json(), indent=4, ensure_ascii=False, escape_forward_slashes=False))
    except Exception as e:
        print(e)
    else:
        result.append({
            "ip": ip,
            "port": port,
            "protocol": protocol
        })
    return result

def store(list):
    with open("proxy.json", "wt", encoding='utf-8') as f:
        json.dump(list, f, ensure_ascii=False, indent=4)
    print("store is done")

def final_store(list):
    with open("proxy_final.json", "wt", encoding='utf-8') as f:
        json.dump(list, f, ensure_ascii=False, indent=4)

def load_data():
    with open("proxy.json", "rt", encoding='utf-8') as f:
        data = json.load(f)
        return data


#html = get_index()
#parse_proxy_info(html)
#get_proxy(data = load_data())


if __name__ == '__main__':
    #result = []
    #html = get_index()
    #parse_proxy_info(html)
    #get_proxy(data = load_data())
    data = load_data()
    num_processes = 4
    #run_with_multiprocessing(data, num_processes)
    #run_with_multiprocessing_and_async(data, num_processes)
    asyncio.run(async_proxy_test(data, result))