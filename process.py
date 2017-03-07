# -*- coding: utf-8 -*-
# @Time    : 3/6/2017 9:27 PM
# @Author  : Wayne Yang

import argparse
import json
import os
import re
import requests
import traceback
from urllib.parse import urlparse, parse_qs
from pyquery import PyQuery as pq
from time import sleep
from datetime import datetime


def process():
    # url : "http://cgi.kg.qq.com/fcgi-bin/kg_ugc_getdetail?callback=jsopgetsonginfo&v=4&shareid=nj6u64nNvAeQZnWW&g"
    personal_center_url = "http://kg.qq.com/node/personal?uid=639b9d832725338b"
    resp = requests.get(personal_center_url)
    d = pq(resp.text)
    print([i.attr("href") for i in d(".opus_show")(".mod_playlist__box")("a").items()])
    shareids = [parse_qs(urlparse(i.attr("href")).query)["s"][0] for i in d(".opus_show")(".mod_playlist__box")("a").items()]
    detail_infos = ["http://cgi.kg.qq.com/fcgi-bin/kg_ugc_getdetail?callback=jsopgetsonginfo&v=4&shareid={}".format(i)
                    for i in shareids]
    with open('songs.json', 'w') as fd:
        songs = []
        re_json = re.compile("jsopgetsonginfo\((.*)\)")
        for i in detail_infos:
            try:
                resp = requests.get(i).content.decode('gbk')
                print(resp)
                data_json = json.loads(re_json.findall(resp)[0])
                song_info = {}
                song_info['name'] = data_json["data"]["song_name"]
                song_info['url'] = data_json["data"]["playurl"]
                songs.append(song_info['name'])
                with open("{}.mp3".format(song_info['name']), "wb") as f:
                    f.write(requests.get(song_info['url']).content)
            except:
                traceback.print_exc()
        json.dump(songs, fd, indent=4, ensure_ascii=False)


def process_on():
    if not os.path.exists('songs.json'):
        process()
    personal_center_url = "http://kg.qq.com/node/personal?uid=639b9d832725338b"
    while True:
        resp = requests.get(personal_center_url)
        d = pq(resp.text)
        shareids = [parse_qs(urlparse(i.attr("href")).query)["s"][0] for i in
                    d(".opus_show")(".mod_playlist__box")("a").items()]
        detail_infos = [
            "http://cgi.kg.qq.com/fcgi-bin/kg_ugc_getdetail?callback=jsopgetsonginfo&v=4&shareid={}".format(i)
            for i in shareids]
        with open('songs.json', 'r') as fd:
            songs = json.load(fd)
        re_json = re.compile("jsopgetsonginfo\((.*)\)")
        for i in detail_infos:
            try:
                resp = requests.get(i).content.decode('gbk')
                print(resp)
                data_json = json.loads(re_json.findall(resp)[0])
                song_info = {}
                song_info['name'] = data_json["data"]["song_name"]
                song_info['url'] = data_json["data"]["playurl"]
                if song_info['name'] not in songs:
                    songs.append(song_info['name'])
                    with open("{}.mp3".format(song_info['name']), "wb") as f:
                        f.write(requests.get(song_info['url']).content)
            except:
                traceback.print_exc()
        with open('songs.json', 'w') as fd:
            json.dump(songs, fd, indent=4, ensure_ascii=False)
        print('[*]{}----Download complete.Now sleep 1h..'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        sleep(3600)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="switch on to inspect skywanwan")
    parser.add_argument('--on', action='store_true')
    args = parser.parse_args()
    try:
        if args.on:
            print('[+]on...')
            process_on()
        else:
            process()
    except:
        traceback.print_exc()