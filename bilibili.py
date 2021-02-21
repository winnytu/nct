import requests
import json

url = 'https://api.bilibili.com/x/space/arc/search?mid=67618650&ps=30&tid=0&pn=1&keyword=&order=pubdate&jsonp=jsonp'
custom_headers = {
    'Host': 'api.bilibili.com',
    'accept': 'application/json, text/plain, */*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6,ja;q=0.5',
    'origin': 'https://space.bilibili.com',
    'referer': 'https://space.bilibili.com/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36'
}

resp = requests.get(url, headers=custom_headers)
datas= json.loads(resp.text)
list = datas['data']['list']['vlist']
for video in list:
    print(video['title'])
