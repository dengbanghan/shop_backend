#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: dengbanghan@gmail.com
# @Date: 2025/5/3

import time
import hashlib
import json
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.models.payment import Payment, PaymentStatus, PaymentMethod
from app.models.order import Order
from app.core.config import settings
from app.core.logging import logger
import requests


class PaymentService:
    def __init__(self, db: Session):
        self.db = db

    def create_payment(self, order: Order, method: PaymentMethod) -> Payment:
        """创建支付记录"""
        payment_no = self.generate_payment_no()
        payment = Payment(
            order_id=order.id,
            payment_no=payment_no,
            method=method,
            amount=order.payment_amount,
            status=PaymentStatus.PENDING
        )
        self.db.add(payment)
        self.db.commit()
        return payment

    def generate_payment_no(self) -> str:
        """生成支付流水号"""
        timestamp = int(time.time() * 1000)
        rand_part = hashlib.md5(str(timestamp).encode()).hexdigest()[:6]
        return f"PY{timestamp}{rand_part}"

    def process_payment(self, order_id: int):
        """处理支付(实际调用第三方支付)"""
        order = self.db.query(Order).get(order_id)
        if not order:
            raise ValueError("订单不存在")

        payment = order.payment
        if not payment:
            payment = self.create_payment(order, PaymentMethod.WECHAT)  # 默认微信支付

        if payment.status == PaymentStatus.SUCCESS:
            return {"status": "already_paid"}

        # 调用第三方支付API
        payment_result = self.call_payment_gateway(payment)

        # 更新支付状态
        if payment_result["success"]:
            payment.status = PaymentStatus.SUCCESS
            payment.transaction_id = payment_result["transaction_id"]
            payment.paid_time = datetime.now()
            payment.payment_info = json.dumps(payment_result)

            # 更新订单状态
            order.status = 2  # 已付款
            order.payment_time = datetime.now()
        else:
            payment.status = PaymentStatus.FAILED
            payment.payment_info = json.dumps(payment_result)

        self.db.commit()
        return payment_result

    def call_payment_gateway(self, payment: Payment) -> dict:
        """调用第三方支付网关(模拟)"""
        # 实际项目中这里会调用微信/支付宝/京东的支付API
        logger.info(f"Calling payment gateway for payment: {payment.payment_no}")

        # 模拟支付成功
        if settings.DEBUG or payment.amount < 1000:  # 测试或小额支付自动成功
            return {
                "success": True,
                "transaction_id": f"TX{int(time.time())}{payment.id}",
                "payment_no": payment.payment_no,
                "amount": float(payment.amount),
                "method": payment.method.name,
                "code_url": "https://example.com/qrcode",  # 支付二维码
                "message": "支付成功"
            }
        else:
            # 模拟支付失败
            return {
                "success": False,
                "payment_no": payment.payment_no,
                "error_code": "PAYMENT_FAILED",
                "message": "支付失败"
            }

    def handle_payment_callback(self, payment_no: str, data: dict) -> bool:
        """处理支付回调"""
        payment = self.db.query(Payment).filter(Payment.payment_no == payment_no).first()
        if not payment:
            logger.error(f"Payment not found: {payment_no}")
            return False

        if payment.status == PaymentStatus.SUCCESS:
            logger.warning(f"Payment already processed: {payment_no}")
            return True

        # 验证回调数据的真实性(实际项目中需要验证签名等)
        if self.verify_callback_data(data):
            payment.status = PaymentStatus.SUCCESS
            payment.transaction_id = data.get("transaction_id")
            payment.paid_time = datetime.now()
            payment.callback_time = datetime.now()
            payment.callback_content = json.dumps(data)

            # 更新订单状态
            order = payment.order
            order.status = 2  # 已付款
            order.payment_time = datetime.now()

            self.db.commit()
            logger.info(f"Payment callback processed: {payment_no}")
            return True
        else:
            logger.error(f"Invalid callback data for payment: {payment_no}")
            return False

    def verify_callback_data(self, data: dict) -> bool:
        """验证回调数据(模拟)"""
        # 实际项目中需要根据支付平台的要求验证签名等
        return True

    def refund(self, order_id: int, amount: Optional[float] = None) -> dict:
        """退款"""
        order = self.db.query(Order).get(order_id)
        if not order or not order.payment:
            raise ValueError("订单或支付记录不存在")

        payment = order.payment
        if payment.status != PaymentStatus.SUCCESS:
            raise ValueError("只有已支付的订单可以退款")

        if amount is None:
            amount = payment.amount
        else:
            if amount > payment.amount - payment.refund_amount:
                raise ValueError("退款金额超过可退金额")

        # 调用第三方退款API
        refund_result = self.call_refund_gateway(payment, amount)

        if refund_result["success"]:
            payment.refund_amount += amount
            payment.refund_time = datetime.now()

            # 更新订单状态
            if payment.refund_amount >= payment.amount:
                order.status = 6  # 退款中
            self.db.commit()

        return refund_result

    def call_refund_gateway(self, payment: Payment, amount: float) -> dict:
        """调用第三方退款网关(模拟)"""
        logger.info(f"Calling refund gateway for payment: {payment.payment_no}, amount: {amount}")

        # 模拟退款成功
        return {
            "success": True,
            "refund_id": f"RF{int(time.time())}{payment.id}",
            "payment_no": payment.payment_no,
            "refund_amount": float(amount),
            "message": "退款成功"
        }