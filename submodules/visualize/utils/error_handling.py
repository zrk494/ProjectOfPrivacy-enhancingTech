import streamlit as st
import traceback
import pandas as pd
from config import ERROR_MESSAGES

def handle_error(func):
    """错误处理装饰器"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            st.error(f"文件未找到: {str(e)}")
            return None
        except pd.errors.EmptyDataError:
            st.error(ERROR_MESSAGES.get('data_not_found', '数据为空'))
            return None
        except Exception as e:
            st.error(f"发生错误: {str(e)}")
            # 仅在开发模式下显示详细错误
            if st.get_option('client.showErrorDetails'):
                st.code(traceback.format_exc())
            return None
    return wrapper

def show_error(message):
    """显示错误消息"""
    st.error(message)

def show_warning(message):
    """显示警告消息"""
    st.warning(message)

def show_info(message):
    """显示信息消息"""
    st.info(message)