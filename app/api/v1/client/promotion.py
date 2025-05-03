#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: dengbanghan@gmail.com
# @Date: 2025/5/3

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.promotion import CouponApply, PromotionOut
from app.services.promotion import PromotionService
from app.db.session import get_db
from app.core.security import get_current_user

router = APIRouter()

@router.get("/promotions/product/{product_id}", response_model=list[PromotionOut])
def get_product_promotions(
    product_id: int,
    db: Session = Depends(get_db)
):
    """获取商品促销活动"""
    service = PromotionService(db)
    return service.get_product_promotions(product_id)

@router.post("/coupons/apply")
def apply_coupon(
    data: CouponApply,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """应用优惠券到购物车"""
    service = PromotionService(db)
    try:
        result = service.apply_coupon_to_cart(
            user_id=current_user["id"],
            coupon_code=data.coupon_code,
            cart_items=data.cart_items
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/coupons/my", response_model=list[CouponOut])
def get_my_coupons(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取我的优惠券"""
    service = PromotionService(db)
    return service.get_user_valid_coupons(current_user["id"])