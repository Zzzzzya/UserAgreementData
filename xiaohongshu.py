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

def try_click_user_agreement(driver, wait_time=10):
    """专门针对小红书用户协议链接的点击函数"""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    try:
        # 1. 使用链接文本精确匹配
        element = WebDriverWait(driver, wait_time).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "《用户协议》"))
        )
        element.click()
        print("成功通过链接文本点击《用户协议》")
        return True
    except Exception as e:
        print(f"方法1失败: {e}")
        
        try:
            # 2. 使用部分链接文本
            element = WebDriverWait(driver, wait_time).until(
                EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "用户协议"))
            )
            element.click()
            print("成功通过部分链接文本点击《用户协议》")
            return True
        except Exception as e:
            print(f"方法2失败: {e}")
            
            try:
                # 3. 使用XPath定位包含特定href的链接
                element = WebDriverWait(driver, wait_time).until(
                    EC.element_to_be_clickable((By.XPATH, 
                        "//a[contains(@href, 'agree.xiaohongshu.com/h5/terms') or contains(text(), '用户协议')]"))
                )
                element.click()
                print("成功通过XPath点击《用户协议》")
                return True
            except Exception as e:
                print(f"方法3失败: {e}")
                
                try:
                    # 4. 使用CSS选择器
                    element = WebDriverWait(driver, wait_time).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "a.links"))
                    )
                    if "用户协议" in element.text:
                        element.click()
                        print("成功通过CSS选择器点击《用户协议》")
                        return True
                except Exception as e:
                    print(f"方法4失败: {e}")
                    
                    try:
                        # 5. 使用JavaScript执行点击
                        links = driver.find_elements(By.XPATH, "//a[contains(text(), '用户协议')]")
                        if links:
                            driver.execute_script("arguments[0].click();", links[0])
                            print("成功通过JavaScript点击《用户协议》")
                            return True
                        else:
                            print("未找到《用户协议》链接")
                    except Exception as e:
                        print(f"方法5失败: {e}")
    
    # 所有方法都失败
    print("无法点击《用户协议》链接")
    return False
def process_snapshot(snapshot, index):
    try:
        archived_url = snapshot.archive_url
        print(f"处理第 {index+1} 条: {archived_url}")
        prefix = extract_wayback_prefix(archived_url)
        print(f"提取的前缀: {prefix}")
        
        driver = page.open_url_with_edge(archived_url, headless=True, wait_time=0)

        flag0 = False
         # 尝试点击"用户协议"元素 - 添加以下代码
        try:
            # 等待页面加载
            time.sleep(2)
            
            # 方法1: 通过CSS选择器
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            # 尝试使用CSS选择器
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "li.navigation-item.sign-up"))
                )
                element.click()
                print("成功点击用户协议按钮")
                flag0 = True
            except:
                # 尝试使用XPath
                try:
                    element = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//li[contains(text(), '用户协议')]"))
                    )
                    element.click()
                    print("成功通过XPath点击用户协议按钮")
                    flag0 = True
                except:
                    # 尝试JavaScript点击
                    try:
                        elements = driver.find_elements(By.XPATH, "//*[contains(text(), '用户协议')]")
                        if elements:
                            driver.execute_script("arguments[0].click();", elements[0])
                            print("成功通过JavaScript点击用户协议按钮")
                            flag0 = True
                        else:
                            print("未找到用户协议按钮")
                    except Exception as click_error:
                        print(f"点击用户协议失败: {click_error}")
                        
            # 等待新内容加载
            time.sleep(2)

        except Exception as e:
            print(f"尝试点击用户协议时发生错误: {e}")


        if not flag0:
            # 如果点击失败，尝试使用 try_click_user_agreement 函数
            if not try_click_user_agreement(driver):
                print("无法点击《用户协议》链接，跳过此快照")
                driver.quit()
                return False, f"第 {index+1} 条失败：无法点击《用户协议》链接"

        html_content = driver.page_source
        driver.quit()
        # print(res)
        soup = BeautifulSoup(html_content, 'html.parser') 
        text = soup.get_text(separator='\n')

        # 设置保存文件名（带时间戳）
        timestamp = snapshot.timestamp
        date_str = datetime.strptime(timestamp, "%Y%m%d%H%M%S").strftime("%Y-%m-%d")
        filename = f"xiaohongshu_agreement_{date_str}.txt"
        file_path = os.path.join(save_folder, filename)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)

        print(f"✅ 第 {index+1} 条保存成功：{filename}")
        
        # 处理保存逻辑...
        return True, index
    except Exception as e:
        return False, f"第 {index+1} 条失败：{e}"



# 1️⃣ 设置目标协议页面 URL
url = "https://www.xiaohongshu.com/explore"  # ← 你可以换成别的平台链接
user_agent = "Mozilla/5.0"


# 2️⃣ 在桌面新建保存文件夹
desktop_path = "./test/"
save_folder = os.path.join(desktop_path, "xiaohongshu_User_Agreements")
os.makedirs(save_folder, exist_ok=True)

# 3️⃣ 初始化 Wayback 抓取器，获取全部快照
wayback = WaybackMachineCDXServerAPI(url, user_agent)
snapshots = list(wayback.snapshots())
print(f"📦 共发现 {len(snapshots)} 条历史快照，开始抓取...\n")

# 按周分组，每周只保留第一条记录


weekable = True
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




begin = 100
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
#         filename = f"xiaohongshu_agreement_{date_str}.txt"
#         file_path = os.path.join(save_folder, filename)

#         with open(file_path, 'w', encoding='utf-8') as f:
#             f.write(text)

#         print(f"✅ 第 {i+1} 条保存成功：{filename}")
#         time.sleep(1.5)  # 限速防封

#     except Exception as e:
#         print(f"⚠️ 第 {i+1} 条失败：{e}")
#         time.sleep(2)

print(f"\n🎉 全部抓取完毕！共处理 {len(snapshots)} 条。\n📁 文件保存在桌面文件夹：{save_folder}")