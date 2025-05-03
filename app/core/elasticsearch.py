#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: dengbanghan@gmail.com
# @Date: 2025/5/3

from elasticsearch import Elasticsearch
from app.core.config import settings
from app.models.product import Product
import logging

logger = logging.getLogger(__name__)


class ElasticSearchService:
    def __init__(self):
        self.es = Elasticsearch(settings.ELASTICSEARCH_URL)
        self.index_name = "products"

    def create_index(self):
        """创建Elasticsearch索引"""
        if not self.es.indices.exists(index=self.index_name):
            body = {
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0,
                    "analysis": {
                        "analyzer": {
                            "default": {
                                "type": "ik_max_word"
                            }
                        }
                    }
                },
                "mappings": {
                    "properties": {
                        "id": {"type": "keyword"},
                        "name": {
                            "type": "text",
                            "analyzer": "ik_max_word",
                            "search_analyzer": "ik_smart"
                        },
                        "description": {
                            "type": "text",
                            "analyzer": "ik_max_word",
                            "search_analyzer": "ik_smart"
                        },
                        "category_id": {"type": "keyword"},
                        "price": {"type": "float"},
                        "status": {"type": "integer"},
                        "attributes": {
                            "type": "nested",
                            "properties": {
                                "name": {"type": "keyword"},
                                "value": {"type": "keyword"}
                            }
                        }
                    }
                }
            }
            self.es.indices.create(index=self.index_name, body=body)
            logger.info(f"Created Elasticsearch index: {self.index_name}")

    def index_product(self, product: Product):
        """索引商品"""
        doc = {
            "id": str(product.id),
            "name": product.name,
            "description": product.description,
            "category_id": str(product.category_id) if product.category_id else None,
            "price": float(product.price),
            "status": product.status,
            "attributes": []
        }

        # 添加SKU属性
        for sku in product.skus:
            if sku.attributes:
                # 假设attributes是JSON字符串，如 {"颜色": "红色", "尺寸": "XL"}
                attrs = eval(sku.attributes) if isinstance(sku.attributes, str) else sku.attributes
                for name, value in attrs.items():
                    doc["attributes"].append({
                        "name": name,
                        "value": value
                    })

        self.es.index(index=self.index_name, id=str(product.id), body=doc)
        logger.debug(f"Indexed product: {product.id}")

    def search_products(self, query: str, category_id: int = None,
                        min_price: float = None, max_price: float = None,
                        page: int = 1, page_size: int = 20):
        """搜索商品"""
        start = (page - 1) * page_size

        # 构建查询条件
        must_conditions = []

        # 关键词查询
        if query:
            must_conditions.append({
                "multi_match": {
                    "query": query,
                    "fields": ["name^3", "description"],
                    "type": "best_fields"
                }
            })

        # 分类过滤
        if category_id:
            must_conditions.append({
                "term": {"category_id": str(category_id)}
            })

        # 价格范围
        price_range = {}
        if min_price is not None:
            price_range["gte"] = min_price
        if max_price is not None:
            price_range["lte"] = max_price
        if price_range:
            must_conditions.append({
                "range": {"price": price_range}
            })

        # 状态过滤(只显示上架商品)
        must_conditions.append({
            "term": {"status": 1}
        })

        body = {
            "query": {
                "bool": {
                    "must": must_conditions
                }
            },
            "from": start,
            "size": page_size,
            "sort": [
                {"_score": {"order": "desc"}},
                {"price": {"order": "asc"}}
            ],
            "highlight": {
                "fields": {
                    "name": {},
                    "description": {}
                }
            }
        }

        result = self.es.search(index=self.index_name, body=body)

        # 处理结果
        products = []
        for hit in result["hits"]["hits"]:
            source = hit["_source"]
            highlight = hit.get("highlight", {})
            products.append({
                "id": source["id"],
                "name": source["name"],
                "description": source["description"],
                "price": source["price"],
                "highlight_name": highlight.get("name", [source["name"]])[0],
                "highlight_description": highlight.get("description", [source["description"]])[0] if source[
                    "description"] else None
            })

        return {
            "total": result["hits"]["total"]["value"],
            "products": products,
            "page": page,
            "page_size": page_size
        }

    def delete_product(self, product_id: int):
        """删除商品索引"""
        self.es.delete(index=self.index_name, id=str(product_id), ignore=[404])
        logger.debug(f"Deleted product index: {product_id}")


# 全局实例
es_service = ElasticSearchService()