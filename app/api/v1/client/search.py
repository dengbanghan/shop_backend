#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: dengbanghan@gmail.com
# @Date: 2025/5/3

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.search import SearchResult
from app.services.search import SearchService
from app.db.session import get_db

router = APIRouter()

@router.get("/search", response_model=SearchResult)
def search_products(
    q: str = "",
    category_id: int = None,
    min_price: float = None,
    max_price: float = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """搜索商品接口"""
    service = SearchService(db)
    return service.search_products(
        query=q,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        page=page,
        page_size=page_size
    )