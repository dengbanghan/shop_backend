#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: dengbanghan@gmail.com
# @Date: 2025/5/3

from datetime import datetime
from sqlalchemy.orm import Session
from app.models.promotion import Promotion, Coupon, PromotionStatus
from app.schemas.promotion import CouponCreate, PromotionCreate
from app.crud.promotion import (
    create_promotion, get_promotion, get_valid_promotions,
    create_coupon, get_coupon_by_code, update_coupon
)
from app.core.logging import logger


class PromotionService:
    def __init__(self, db: Session):
        self.db = db

    def create_promotion(self, promotion_data: PromotionCreate):
        """创建促销活动"""
        promotion = create_promotion(self.db, promotion_data)

        # 如果是立即开始的促销，更新状态
        if promotion.start_time <= datetime.now() <= promotion.end_time:
            promotion.status = PromotionStatus.ONGOING
            self.db.commit()

        logger.info(f"Created promotion: {promotion.name}")
        return promotion

    def get_product_promotions(self, product_id: int):
        """获取商品的有效促销活动"""
        promotions = get_valid_promotions(self.db, product_id=product_id)
        return promotions

    def apply_promotions_to_cart(self, cart_items: list, user_id: int = None):
        """应用促销活动到购物车"""
        total_amount = sum(item.product.price * item.quantity for item in cart_items)
        discount_amount = 0
        applied_promotions = []

        # 1. 检查商品促销
        for item in cart_items:
            promotions = self.get_product_promotions(item.product_id)
            for promo in promotions:
                if promo.type == 1:  # 折扣
                    item_discount = item.product.price * item.quantity * (1 - promo.discount_rate)
                    discount_amount += item_discount
                    applied_promotions.append({
                        'type': 'product_discount',
                        'promotion_id': promo.id,
                        'discount': item_discount,
                        'product_id': item.product_id
                    })

        # 2. 检查满减促销
        full_reduction_promos = get_valid_promotions(self.db, type=2)  # 满减类型
        for promo in full_reduction_promos:
            if total_amount >= promo.full_amount:
                discount_amount += promo.reduce_amount
                applied_promotions.append({
                    'type': 'full_reduction',
                    'promotion_id': promo.id,
                    'discount': promo.reduce_amount
                })
                break  # 只应用一个满减

        # 3. 检查用户优惠券
        if user_id:
            coupons = self.get_user_valid_coupons(user_id)
            for coupon in coupons:
                if total_amount >= coupon.min_order_amount:
                    discount_amount += coupon.discount_amount
                    applied_promotions.append({
                        'type': 'coupon',
                        'coupon_id': coupon.id,
                        'discount': coupon.discount_amount
                    })
                    break  # 只应用一张优惠券

        return {
            'original_amount': total_amount,
            'discount_amount': discount_amount,
            'final_amount': total_amount - discount_amount,
            'applied_promotions': applied_promotions
        }

    def generate_coupons(self, promotion_id: int, count: int, prefix: str = "COUPON"):
        """批量生成优惠券"""
        coupons = []
        for i in range(count):
            code = f"{prefix}_{promotion_id}_{datetime.now().strftime('%Y%m%d')}_{i}"
            coupon_data = CouponCreate(
                code=code,
                promotion_id=promotion_id,
                discount_amount=10,  # 示例金额
                min_order_amount=100,
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(days=30)
            coupon = create_coupon(self.db, coupon_data)
            coupons.append(coupon)
            self.db.commit()
        return coupons

    def get_user_valid_coupons(self, user_id: int):
        """获取用户有效优惠券"""
        now = datetime.now()
        return self.db.query(Coupon).filter(
            Coupon.user_id == user_id,
            Coupon.is_used == False,
            Coupon.start_time <= now,
            Coupon.end_time >= now
        ).all()

    def use_coupon(self, coupon_code: str, order_id: int):
        """使用优惠券"""
        coupon = get_coupon_by_code(self.db, coupon_code)
        if not coupon or coupon.is_used:
            raise ValueError("优惠券无效或已使用")

        coupon.is_used = True
        coupon.used_time = datetime.now()
        coupon.order_id = order_id
        self.db.commit()
        return coupon