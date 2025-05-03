#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: dengbanghan@gmail.com
# @Date: 2025/5/3

from sqlalchemy import Column, String, Integer, Numeric, Text, Boolean, ForeignKey
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship
from app.models.base import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    original_price = Column(Numeric(10, 2), nullable=True)
    stock = Column(Integer, default=0, nullable=False)
    sold_count = Column(Integer, default=0)
    category_id = Column(BIGINT, ForeignKey("categories.id"), nullable=True)
    main_image_url = Column(String(255), nullable=True)
    status = Column(Integer, default=1)  # 1-上架, 0-下架
    # 商品属性
    weight = Column(Numeric(10, 2), nullable=True)  # 重量(kg)
    volume = Column(String(50), nullable=True)  # 体积
    # SEO信息
    seo_title = Column(String(100), nullable=True)
    seo_keywords = Column(String(255), nullable=True)
    seo_description = Column(String(255), nullable=True)

    category = relationship("Category", back_populates="products")
    images = relationship("ProductImage", back_populates="product")
    skus = relationship("ProductSku", back_populates="product")

    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name}, price={self.price})>"


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    product_id = Column(BIGINT, ForeignKey("products.id"), nullable=False)
    image_url = Column(String(255), nullable=False)
    sort_order = Column(Integer, default=0)

    product = relationship("Product", back_populates="images")

    def __repr__(self):
        return f"<ProductImage(id={self.id}, product_id={self.product_id})>"


class ProductSku(Base):
    __tablename__ = "product_skus"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    product_id = Column(BIGINT, ForeignKey("products.id"), nullable=False)
    sku_code = Column(String(50), nullable=False, unique=True)
    price = Column(Numeric(10, 2), nullable=False)
    original_price = Column(Numeric(10, 2), nullable=True)
    stock = Column(Integer, default=0, nullable=False)
    sold_count = Column(Integer, default=0)
    attributes = Column(String(255), nullable=True)  # JSON格式的属性组合

    product = relationship("Product", back_populates="skus")

    def __repr__(self):
        return f"<ProductSku(id={self.id}, sku_code={self.sku_code}, price={self.price})>"