import streamlit as st
from config import CACHE_TTL

def cache_data(ttl=CACHE_TTL):
    """缓存数据装饰器"""
    def decorator(func):
        return st.cache_data(ttl=ttl)(func)
    return decorator

def clear_cache():
    """清除所有缓存"""
    st.cache_data.clear()
    st.cache_resource.clear()

def cache_resource():
    """缓存资源装饰器"""
    def decorator(func):
        return st.cache_resource()(func)
    return decorator