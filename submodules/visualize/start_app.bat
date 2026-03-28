@echo off

REM 启动Visualize应用
cd /d "%~dp0"

echo 正在启动Visualize应用...
echo 请确保已安装所需依赖：pip install streamlit plotly pandas

echo 启动Streamlit应用...
streamlit run app.py