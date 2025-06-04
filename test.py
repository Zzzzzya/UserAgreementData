import os
import time
import requests
from bs4 import BeautifulSoup
from waybackpy import WaybackMachineCDXServerAPI
from tqdm import tqdm
from datetime import datetime
from selenium import webdriver  # 添加此行
from selenium.webdriver.edge.options import Options  # 添加此行
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager



# 1️⃣ 设置目标协议页面 URL
url = "https://you.163.com/help/new#36"  # ← 你可以换成别的平台链接
user_agent = "Mozilla/5.0"



archived_url = url


options = Options()
options.headless = True  # 无界面模式
driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()),options=options)
driver.get(archived_url)
# 等待JS执行完成
driver.implicitly_wait(5000)
