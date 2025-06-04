import os
import time
import requests
from bs4 import BeautifulSoup
from waybackpy import WaybackMachineCDXServerAPI
from tqdm import tqdm
from datetime import datetime
from collections import defaultdict

import PyPDF2
import io

# 新增：PDF文本提取函数
def extract_text_from_pdf(pdf_content):
    """从PDF二进制内容提取文本"""
    try:
        # 创建PDF文件对象
        pdf_file = io.BytesIO(pdf_content)
        
        # 创建PDF阅读器
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # 提取所有页面文本
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text() + "\n\n"
            
        return text
    except Exception as e:
        print(f"PDF解析错误: {str(e)}")
        return f"[PDF解析失败: {str(e)}]"


# 1️⃣ 设置目标协议页面 URL
url = "https://cdn.cnbj1.fds.api.mi-img.com/mi-mall/0c8a291dbc2491de7b9fc98afd8c0039.pdf"  # 腾讯新闻用户协议
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# 2️⃣ 在桌面新建保存文件夹 - 修改为腾讯新闻文件夹
desktop_path = "./test/"
save_folder = os.path.join(desktop_path, "xiaomiyoupin_User_Agreements")
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

begin = 0
end = 10000




# 循环抓取部分修改如下:
for i, snapshot in enumerate(tqdm(filtered_snapshots, desc="抓取协议中（每周一条）")):
    if i < begin or i > end:
        continue  # 跳过不在范围内的快照
    try:
        archived_url = snapshot.archive_url
        
        # 修改：使用stream=True以支持二进制内容
        res = requests.get(archived_url, timeout=50, stream=True)
        
        # 确定内容类型
        content_type = res.headers.get('Content-Type', '').lower()
        is_pdf = 'application/pdf' in content_type
        
        # 设置保存文件名（带时间戳）
        timestamp = snapshot.timestamp
        date_str = datetime.strptime(timestamp, "%Y%m%d%H%M%S").strftime("%Y-%m-%d")
        filename = f"xiaomiyoupin_agreement_{date_str}.txt"
        file_path = os.path.join(save_folder, filename)
        
        if is_pdf:
            # PDF处理
            pdf_content = res.content
            
            # 可选：同时保存原始PDF
            # pdf_path = os.path.join(save_folder, f"xiaomiyoupin_agreement_{date_str}.pdf")
            # with open(pdf_path, 'wb') as f:
            #     f.write(pdf_content)
                
            # 提取文本
            text = extract_text_from_pdf(pdf_content)
            print(f"✅ 已处理PDF: {filename}")
        else:
            # HTML处理（原有逻辑）
            soup = BeautifulSoup(res.text, 'html.parser')
            text = soup.get_text(separator='\n')
        
        # 保存为TXT
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)

        print(f"✅ 第 {i+1} 条保存成功：{filename}")
        time.sleep(2)  # 限速防封

    except Exception as e:
        print(f"⚠️ 第 {i+1} 条失败：{type(e).__name__} - {str(e)}")
        time.sleep(3)

print(f"\n🎉 全部抓取完毕！共处理 {len(filtered_snapshots)} 条。\n📁 文件保存在桌面文件夹：{save_folder}")