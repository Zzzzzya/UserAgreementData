import os
import time
import requests
from bs4 import BeautifulSoup
from waybackpy import WaybackMachineCDXServerAPI
from tqdm import tqdm
from datetime import datetime




# 1️⃣ 设置目标协议页面 URL
url = "https://in.m.jd.com/help/app/register_info.html"  # ← 你可以换成别的平台链接
user_agent = "Mozilla/5.0"


# 2️⃣ 在桌面新建保存文件夹
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
save_folder = os.path.join(desktop_path, "jingdong_User_Agreements")
os.makedirs(save_folder, exist_ok=True)

# 3️⃣ 初始化 Wayback 抓取器，获取全部快照
wayback = WaybackMachineCDXServerAPI(url, user_agent)
snapshots = list(wayback.snapshots())
print(f"📦 共发现 {len(snapshots)} 条历史快照，开始抓取...\n")

# 4️⃣ 循环抓取 + 防封 + 错误跳过 + 实时提示
for i, snapshot in enumerate(tqdm(snapshots, desc="抓取协议中（全量）")):
    try:
        archived_url = snapshot.archive_url
        res = requests.get(archived_url, timeout=10)
        # print(res)
        soup = BeautifulSoup(res.text, 'html.parser',from_encoding='ISO-8859-1')
        text = soup.get_text(separator='\n')

        # 设置保存文件名（带时间戳）
        timestamp = snapshot.timestamp
        date_str = datetime.strptime(timestamp, "%Y%m%d%H%M%S").strftime("%Y-%m-%d")
        filename = f"jingdong_agreement_{date_str}.txt"
        file_path = os.path.join(save_folder, filename)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)

        print(f"✅ 第 {i+1} 条保存成功：{filename}")
        time.sleep(1.5)  # 限速防封

    except Exception as e:
        print(f"⚠️ 第 {i+1} 条失败：{e}")
        time.sleep(2)

print(f"\n🎉 全部抓取完毕！共处理 {len(snapshots)} 条。\n📁 文件保存在桌面文件夹：{save_folder}")