# -*- coding: utf-8 -*-
import json
from Crypto.Cipher import AES
import base64
import scrapy
from scrapy.http import Request, FormRequest
from cloudmusic.items import CloudmusicItem


class Music163Spider(scrapy.Spider):
    name = 'music163'
    allowed_domains = ['music.163.com']
    second_param = "010001"
    third_param = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
    forth_param = "0CoJUm6Qyw8W8jud"
    page = None
    total = None
    current_page = 0
    songid = 108539
    count = 0
    encSecKey = "257348aecb5e556c066de214e531faadd1c55d814f9be95fd06d6bff9f4c7a41f831f6394d5a3fd2e3881736d94a02ca919d952872e7d0a50ebfa1769a7a62d512f5f1ca21aec60bc3819a9c3ffca5eca9a0dba6d6f7249b06f5965ecfff3695b54e1c28f3f624750ed39e7de08fc8493242e26dbc4484a01c76f739e135637c"
    start_url = "https://music.163.com/weapi/v1/resource/comments/R_SO_4_{songid}?csrf_token"

    def start_requests(self):
        yield FormRequest(url=self.start_url.format(songid=self.songid),
                          formdata={"params": self.get_params(self.current_page), "encSecKey": self.encSecKey},
                          callback=self.comment_parse)

    def comment_parse(self, response):
        data = json.loads(response.text)
        if not self.total:
            self.total = data["total"]
            if (self.total % 20 == 0):
                self.page = self.total / 20
            else:
                self.page = int(self.total / 20) + 1
        if self.current_page <= self.page:
            print(self.current_page,self.page)
            item = CloudmusicItem()
            for comment in data.get("comments"):
                self.count += 1
                item["nickname"] = comment["user"]["nickname"]
                item["content"] = comment["content"]
                item["commentId"] = comment["commentId"]
                yield item
            print(self.count)
            self.current_page += 1
            yield FormRequest(url=self.start_url.format(songid=self.songid),
                              formdata={"params": self.get_params(self.current_page), "encSecKey": self.encSecKey},
                              callback=self.comment_parse)

    def get_params(self, page):
        # 获取encText，也就是params
        iv = "0102030405060708"
        first_key = self.forth_param
        second_key = 'F' * 16
        if page == 0:
            first_param = '{rid:"", offset:"0", total:"true", limit:"20", csrf_token:""}'
        else:
            offset = str((page - 1) * 20)
            first_param = '{rid:"", offset:"%s", total:"%s", limit:"20", csrf_token:""}' % (offset, 'false')
        self.encText = self.AES_encrypt(first_param, first_key, iv)
        self.encText = self.AES_encrypt(self.encText.decode('utf-8'), second_key, iv)
        return self.encText

    def AES_encrypt(self, text, key, iv):
        # AES加密
        pad = 16 - len(text) % 16
        text = text + pad * chr(pad)
        encryptor = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
        encrypt_text = encryptor.encrypt(text.encode('utf-8'))
        encrypt_text = base64.b64encode(encrypt_text)
        return encrypt_text
