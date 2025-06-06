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
import page


import concurrent.futures

def extract_wayback_prefix(url):
    # 找到第一个http出现的位置
    first_http_index = url.find('http')
    if first_http_index == -1:
        return None  # 未找到http
    
    # 从第一个http之后开始查找第二个http
    second_http_index = url.find('http', first_http_index + 1)
    if second_http_index == -1:
        return None  # 未找到第二个http
    
    # 提取直到第二个http之前的部分
    return url[:second_http_index]

def process_snapshot(snapshot, index):
    try:
        archived_url = snapshot.archive_url
        print(f"处理第 {index+1} 条: {archived_url}")
        prefix = extract_wayback_prefix(archived_url)
        print(f"提取的前缀: {prefix}")
        
        driver = page.open_url_with_edge(archived_url, headless=True, wait_time=0)

        html_content = driver.page_source
        driver.quit()
        # print(res)
        soup = BeautifulSoup(html_content, 'html.parser') 
        text = soup.get_text(separator='\n')

        # 设置保存文件名（带时间戳）
        timestamp = snapshot.timestamp
        date_str = datetime.strptime(timestamp, "%Y%m%d%H%M%S").strftime("%Y-%m-%d")
        filename = f"meituan_agreement_{date_str}.txt"
        file_path = os.path.join(save_folder, filename)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)

        print(f"✅ 第 {index+1} 条保存成功：{filename}")
        
        # 处理保存逻辑...
        return True, index
    except Exception as e:
        return False, f"第 {index+1} 条失败：{e}"



# 1️⃣ 设置目标协议页面 URL
url = "https://rules-center.meituan.com/rules-detail/4"  # ← 你可以换成别的平台链接
user_agent = "Mozilla/5.0"


# 2️⃣ 在桌面新建保存文件夹
desktop_path = "./test/"
save_folder = os.path.join(desktop_path, "meituan_User_Agreements")
os.makedirs(save_folder, exist_ok=True)

# 3️⃣ 初始化 Wayback 抓取器，获取全部快照
wayback = WaybackMachineCDXServerAPI(url, user_agent)
snapshots = list(wayback.snapshots())
print(f"📦 共发现 {len(snapshots)} 条历史快照，开始抓取...\n")

# 按周分组，每周只保留第一条记录


weekable = False
filtered_snapshots = []
if weekable:
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
else:
    monthly_snapshots = {}
    for snapshot in snapshots:
        timestamp = snapshot.timestamp
        # 提取年月作为键，格式为 "YYYYMM"
        month_key = timestamp[:6]
        
        # 如果这个月份还没有记录，则添加该快照
        if month_key not in monthly_snapshots:
            monthly_snapshots[month_key] = snapshot
            # 按时间顺序排序
    filtered_snapshots = [monthly_snapshots[k] for k in sorted(monthly_snapshots.keys())]
    print(f"📊 筛选后每月一条，共 {len(filtered_snapshots)} 条快照\n")




begin = 0
end = 1000


# 使用线程池并行处理
with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
    futures = {executor.submit(process_snapshot, snapshot, i): i 
               for i, snapshot in enumerate(filtered_snapshots) 
               if begin <= i <= end}
    
    for future in concurrent.futures.as_completed(futures):
        success, result = future.result()
        if success:
            print(f"✅ 第 {result+1} 条处理成功")
        else:
            print(f"⚠️ {result}")

# # 4️⃣ 循环抓取 + 防封 + 错误跳过 + 实时提示
# for i, snapshot in enumerate(tqdm(filtered_snapshots, desc="抓取协议中（每周一条）")):
#     if i < begin or i > end:
#         continue  # 跳过不在范围内的快照
#     try:
#         archived_url = snapshot.archive_url
#         print(archived_url)

#             # 打开浏览器并加载页面
#         driver = page.open_url_with_chrome(archived_url, headless=False, wait_time=0)
        
#         page.try_method_click(driver,"服务协议")

#         # 获取渲染后的HTML
#         html_content = driver.page_source
#         # 使用完后关闭
#         driver.quit()
#         # print(res)
#         soup = BeautifulSoup(html_content, 'html.parser') 
#         text = soup.get_text(separator='\n')

#         # 设置保存文件名（带时间戳）
#         timestamp = snapshot.timestamp
#         date_str = datetime.strptime(timestamp, "%Y%m%d%H%M%S").strftime("%Y-%m-%d")
#         filename = f"meituan_agreement_{date_str}.txt"
#         file_path = os.path.join(save_folder, filename)

#         with open(file_path, 'w', encoding='utf-8') as f:
#             f.write(text)

#         print(f"✅ 第 {i+1} 条保存成功：{filename}")
#         time.sleep(1.5)  # 限速防封

#     except Exception as e:
#         print(f"⚠️ 第 {i+1} 条失败：{e}")
#         time.sleep(2)

print(f"\n🎉 全部抓取完毕！共处理 {len(snapshots)} 条。\n📁 文件保存在桌面文件夹：{save_folder}")