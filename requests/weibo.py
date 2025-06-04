import os
import time
import requests
from bs4 import BeautifulSoup
from waybackpy import WaybackMachineCDXServerAPI
from tqdm import tqdm
from datetime import datetime
from collections import defaultdict

# 1️⃣ 设置目标协议页面 URL
url = "https://weibo.com/signup/v5/protocol"  # 腾讯新闻用户协议
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# 2️⃣ 在桌面新建保存文件夹 - 修改为腾讯新闻文件夹
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
save_folder = os.path.join(desktop_path, "weibo_User_Agreements")
os.makedirs(save_folder, exist_ok=True)

# 3️⃣ 初始化 Wayback 抓取器，获取全部快照
wayback = WaybackMachineCDXServerAPI(url, user_agent)
snapshots = list(wayback.snapshots())
print(f"📦 共发现 {len(snapshots)} 条历史快照")

# 按周分组，每周只保留第一条记录
weekly_snapshots = {}
for snapshot in snapshots:
    timestamp = snapshot.timestamp
    # 转换为日期对象以获取年和周数
    date_obj = datetime.strptime(timestamp, "%Y%m%d%H%M%S")
    # isocalendar() 返回 (年, 周, 星期几)，我们只取前两个
    year, week_num = date_obj.isocalendar()[:2]
    # 使用(年,周)作为键
    week_key = f"{year}_{week_num:02d}"
    
    # 如果这一周还没有记录，则添加该快照
    if week_key not in weekly_snapshots:
        weekly_snapshots[week_key] = snapshot

# 按时间顺序排序
filtered_snapshots = [weekly_snapshots[k] for k in sorted(weekly_snapshots.keys())]
print(f"📊 筛选后每周一条，共 {len(filtered_snapshots)} 条快照\n")

begin = 96
end = 10000

# 4️⃣ 循环抓取 + 防封 + 错误跳过 + 实时提示
for i, snapshot in enumerate(tqdm(filtered_snapshots, desc="抓取协议中（每周一条）")):
    if i < begin or i > end:
        continue  # 跳过不在范围内的快照
    try:
        archived_url = snapshot.archive_url
        res = requests.get(archived_url, timeout=50)
        soup = BeautifulSoup(res.text, 'html.parser')
        text = soup.get_text(separator='\n')

        # 设置保存文件名（带时间戳）
        timestamp = snapshot.timestamp
        date_str = datetime.strptime(timestamp, "%Y%m%d%H%M%S").strftime("%Y-%m-%d")
        # 更新为腾讯新闻协议文件名
        filename = f"weibo_agreement_{date_str}.txt"
        file_path = os.path.join(save_folder, filename)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)

        print(f"✅ 第 {i+1} 条保存成功：{filename}")
        time.sleep(2)  # 限速防封

    except Exception as e:
        print(f"⚠️ 第 {i+1} 条失败：{type(e).__name__} - {str(e)}")
        time.sleep(3)

print(f"\n🎉 全部抓取完毕！共处理 {len(filtered_snapshots)} 条。\n📁 文件保存在桌面文件夹：{save_folder}")