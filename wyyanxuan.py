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
url = "https://hc.suning.com/privacy/index.htm?channelId=158196196466980997"  # ← 你可以换成别的平台链接
user_agent = "Mozilla/5.0"


# 2️⃣ 在桌面新建保存文件夹
desktop_path = "./test/"
save_folder = os.path.join(desktop_path, "wyyanxuan_User_Agreements")
os.makedirs(save_folder, exist_ok=True)

# 3️⃣ 初始化 Wayback 抓取器，获取全部快照
wayback = WaybackMachineCDXServerAPI(url, user_agent)
snapshots = list(wayback.snapshots())
print(f"📦 共发现 {len(snapshots)} 条历史快照，开始抓取...\n")

# 4️⃣ 循环抓取 + 防封 + 错误跳过 + 实时提示
for i, snapshot in enumerate(tqdm(snapshots, desc="抓取协议中（全量）")):
    try:
        archived_url = snapshot.archive_url
        print(archived_url)

        options = Options()
        options.headless = True  # 无界面模式
        driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()),options=options)
        driver.get(archived_url)
        # 等待JS执行完成
        driver.implicitly_wait(500)

        # 获取渲染后的HTML
        html_content = driver.page_source
        # 使用完后关闭
        driver.quit()
        # print(res)
        soup = BeautifulSoup(html_content, 'html.parser') 
        text = soup.get_text(separator='\n')

        # 设置保存文件名（带时间戳）
        timestamp = snapshot.timestamp
        date_str = datetime.strptime(timestamp, "%Y%m%d%H%M%S").strftime("%Y-%m-%d")
        filename = f"wyyanxuan_agreement_{date_str}.txt"
        file_path = os.path.join(save_folder, filename)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)

        print(f"✅ 第 {i+1} 条保存成功：{filename}")
        time.sleep(1.5)  # 限速防封

    except Exception as e:
        print(f"⚠️ 第 {i+1} 条失败：{e}")
        time.sleep(2)

print(f"\n🎉 全部抓取完毕！共处理 {len(snapshots)} 条。\n📁 文件保存在桌面文件夹：{save_folder}")