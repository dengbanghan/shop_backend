#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: dengbanghan@gmail.com
# @Date: 2025/5/3

import hashlib
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Optional, Dict
import requests
from app.core.config import settings
from app.core.logging import logger


class WeChatPayService:
    def __init__(self):
        self.appid = settings.WECHAT_APPID
        self.mch_id = settings.WECHAT_MCH_ID
        self.api_key = settings.WECHAT_API_KEY
        self.notify_url = settings.WECHAT_NOTIFY_URL

    def create_order(self, order_no: str, amount: int, desc: str,
                     client_ip: str, openid: Optional[str] = None) -> Dict:
        """创建微信支付订单"""
        url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
        nonce_str = self.generate_nonce_str()
        params = {
            "appid": self.appid,
            "mch_id": self.mch_id,
            "nonce_str": nonce_str,
            "body": desc,
            "out_trade_no": order_no,
            "total_fee": amount,
            "spbill_create_ip": client_ip,
            "notify_url": self.notify_url,
            "trade_type": "JSAPI" if openid else "NATIVE",
            "openid": openid
        }
        params["sign"] = self.generate_sign(params)

        xml_data = self.dict_to_xml(params)
        response = requests.post(url, data=xml_data, headers={'Content-Type': 'application/xml'})
        response.raise_for_status()

        result = self.xml_to_dict(response.text)
        if result.get("return_code") != "SUCCESS":
            logger.error(f"WeChat pay error: {result.get('return_msg')}")
            raise ValueError(result.get("return_msg", "WeChat pay error"))

        return result

    def query_order(self, order_no: str) -> Dict:
        """查询订单状态"""
        url = "https://api.mch.weixin.qq.com/pay/orderquery"
        nonce_str = self.generate_nonce_str()
        params = {
            "appid": self.appid,
            "mch_id": self.mch_id,
            "out_trade_no": order_no,
            "nonce_str": nonce_str
        }
        params["sign"] = self.generate_sign(params)

        xml_data = self.dict_to_xml(params)
        response = requests.post(url, data=xml_data, headers={'Content-Type': 'application/xml'})
        response.raise_for_status()

        return self.xml_to_dict(response.text)

    def refund(self, order_no: str, refund_no: str,
               total_fee: int, refund_fee: int) -> Dict:
        """申请退款"""
        url = "https://api.mch.weixin.qq.com/secapi/pay/refund"
        nonce_str = self.generate_nonce_str()
        params = {
            "appid": self.appid,
            "mch_id": self.mch_id,
            "nonce_str": nonce_str,
            "out_trade_no": order_no,
            "out_refund_no": refund_no,
            "total_fee": total_fee,
            "refund_fee": refund_fee,
            "notify_url": self.notify_url
        }
        params["sign"] = self.generate_sign(params)

        xml_data = self.dict_to_xml(params)
        # 需要配置证书
        response = requests.post(url, data=xml_data,
                                 cert=(settings.WECHAT_CERT_PATH, settings.WECHAT_KEY_PATH),
                                 headers={'Content-Type': 'application/xml'})
        response.raise_for_status()

        return self.xml_to_dict(response.text)

    def process_callback(self, xml_data: str) -> Dict:
        """处理支付回调"""
        callback_data = self.xml_to_dict(xml_data)
        if not self.verify_callback_sign(callback_data):
            raise ValueError("Invalid signature")

        return callback_data

    def generate_sign(self, params: Dict) -> str:
        """生成签名"""
        sorted_params = sorted(params.items(), key=lambda x: x[0])
        sign_str = "&".join([f"{k}={v}" for k, v in sorted_params if k != "sign" and v is not None])
        sign_str += f"&key={self.api_key}"
        return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()

    def verify_callback_sign(self, params: Dict) -> bool:
        """验证回调签名"""
        if "sign" not in params:
            return False
        sign = params.pop("sign")
        return sign == self.generate_sign(params)

    def generate_nonce_str(self, length: int = 32) -> str:
        """生成随机字符串"""
        import random
        import string
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    def dict_to_xml(self, params: Dict) -> str:
        """字典转XML"""
        xml = ["<xml>"]
        for k, v in params.items():
            if v is not None:
                xml.append(f"<{k}>{v}</{k}>")
        xml.append("</xml>")
        return "".join(xml)

    def xml_to_dict(self, xml_data: str) -> Dict:
        """XML转字典"""
        root = ET.fromstring(xml_data)
        return {child.tag: child.text for child in root}