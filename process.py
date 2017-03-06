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


def process():
    # url : "http://cgi.kg.qq.com/fcgi-bin/kg_ugc_getdetail?callback=jsopgetsonginfo&v=4&shareid=nj6u64nNvAeQZnWW&g"
    personal_center_url = "http://kg.qq.com/node/personal?uid=639b9d832725338b"
    resp = requests.get(personal_center_url)
    d = pq(resp.text)
    print([i.attr("href") for i in d(".opus_show")(".mod_playlist__box")("a").items()])
    shareids = [parse_qs(urlparse(i.attr("href")).query)["s"][0] for i in d(".opus_show")(".mod_playlist__box")("a").items()]
    detail_infos = ["http://cgi.kg.qq.com/fcgi-bin/kg_ugc_getdetail?callback=jsopgetsonginfo&v=4&shareid={}".format(i)
                    for i in shareids]
    with open('detail_infos.json', 'w') as fd:
        json.dump(detail_infos, fd)
    re_json = re.compile("jsopgetsonginfo\((.*)\)")
    for i in detail_infos:
        try:
            resp = requests.get(i).content.decode('gbk')
            print(resp)
            data_json = json.loads(re_json.findall(resp)[0])
            with open("{}.mp3".format(data_json["data"]["song_name"]), "wb") as fd:
                fd.write(requests.get(data_json["data"]["playurl"]).content)
        except:
            traceback.print_exc()


def process_on():
    if not os.path.exists('detail_infos.json'):
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
        with open('detail_infos.json', 'r') as fd:
            infos_saved = json.load(fd)
        re_json = re.compile("jsopgetsonginfo\((.*)\)")
        for i in detail_infos:
            if i not in infos_saved:
                infos_saved.append(i)
                try:
                    resp = requests.get(i).content.decode('gbk')
                    print(resp)
                    data_json = json.loads(re_json.findall(resp)[0])
                    with open("{}.mp3".format(data_json["data"]["song_name"]), "wb") as fd:
                        fd.write(requests.get(data_json["data"]["playurl"]).content)
                except:
                    traceback.print_exc()
        with open('detail_infos.json', 'w') as fd:
            json.dump(infos_saved, fd)
        print('==========>Download complete.Now sleep 1h..')
        sleep(3600)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="switch on to inspect skywanwan")
    parser.add_argument('--on', action='store_true')
    args = parser.parse_args()
    try:
        if args.on:
            print('=================>on')
            process_on()
        else:
            process()
    except:
        traceback.print_exc()