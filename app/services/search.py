#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: dengbanghan@gmail.com
# @Date: 2025/5/3

from sqlalchemy.orm import Session
from app.core.elasticsearch import es_service
from app.crud.product import get_product
from app.core.logging import logger


class SearchService:
    def __init__(self, db: Session):
        self.db = db

    def search_products(self, query: str, category_id: int = None,
                        min_price: float = None, max_price: float = None,
                        page: int = 1, page_size: int = 20):
        """搜索商品"""
        try:
            result = es_service.search_products(
                query=query,
                category_id=category_id,
                min_price=min_price,
                max_price=max_price,
                page=page,
                page_size=page_size
            )

            # 可以从数据库补充更多信息
            for product in result["products"]:
                db_product = get_product(self.db, product["id"])
                if db_product:
                    product["image_url"] = db_product.main_image_url
                    product["stock"] = db_product.stock

            return result
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            # 失败时回退到数据库搜索
            return self.fallback_search(
                query, category_id, min_price, max_price, page, page_size)

    def fallback_search(self, query: str, category_id: int = None,
                        min_price: float = None, max_price: float = None,
                        page: int = 1, page_size: int = 20):
        """数据库回退搜索"""
        from sqlalchemy import or_
        from app.models.product import Product

        query_obj = self.db.query(Product).filter(Product.status == 1)

        if query:
            query_obj = query_obj.filter(
                or_(
                    Product.name.like(f"%{query}%"),
                    Product.description.like(f"%{query}%")
                )
            )

        if category_id:
            query_obj = query_obj.filter(Product.category_id == category_id)

        if min_price is not None:
            query_obj = query_obj.filter(Product.price >= min_price)

        if max_price is not None:
            query_obj = query_obj.filter(Product.price <= max_price)

        total = query_obj.count()
        products = query_obj.offset((page - 1) * page_size).limit(page_size).all()

        return {
            "total": total,
            "products": [{
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "price": float(p.price),
                "image_url": p.main_image_url,
                "stock": p.stock,
                "highlight_name": p.name,
                "highlight_description": p.description
            } for p in products],
            "page": page,
            "page_size": page_size
        }

    def index_all_products(self):
        """索引所有商品"""
        from app.models.product import Product

        products = self.db.query(Product).all()
        for product in products:
            es_service.index_product(product)

        logger.info(f"Indexed {len(products)} products")