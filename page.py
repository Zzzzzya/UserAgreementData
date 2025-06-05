from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
# 改变这些导入
from selenium import webdriver
from selenium.webdriver.edge.service import Service  # 修改
from selenium.webdriver.edge.options import Options  # 修改
from webdriver_manager.microsoft import EdgeChromiumDriverManager  # 修改
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import os

def try_method_click(driver,text):
        # 尝试寻找并点击"《网易严选服务协议》"链接
    try:
        print("尝试寻找并点击"+text+"链接")
        # 使用多种定位方式尝试找到元素
        methods = [
            (By.LINK_TEXT, text)
            ,(By.PARTIAL_LINK_TEXT, text)
        ]
        
        for method, value in methods:
            try:
                # 使用显式等待，最多等待10秒
                element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((method, value))
                )
                print(f"找到元素，即将点击: {value}")
                element.click()
                print("点击成功!")
                # 点击后等待页面响应
                time.sleep(0.5)
                break
            except Exception as e:
                print(f"使用方法 {method} 和值 {value} 定位失败: {e}")
                continue
    except Exception as e:
        print(f"查找或点击链接时发生错误: {e}")

def open_url_with_chrome(url, headless=False, wait_time=5):
    """
    使用Chrome浏览器打开URL并返回JavaScript执行后的页面
    
    参数:
    url (str): 要打开的网址
    headless (bool): 是否使用无头模式，默认为False，即显示浏览器界面
    wait_time (int): 等待JavaScript执行的秒数
    
    返回:
    driver: Selenium WebDriver实例，可用于进一步操作
    """
    # 设置Chrome选项
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")  # 无头模式
    
    chrome_options.add_argument('--blink-settings=imagesEnabled=false')
    chrome_options.add_argument("--disable-gpu")  # 禁用GPU加速
    chrome_options.add_argument("--window-size=1920,1080")  # 设置窗口大小
    chrome_options.add_argument("--no-sandbox")  # 禁用沙箱模式
    chrome_options.add_argument("--disable-dev-shm-usage")  # 禁用/dev/shm使用
    chrome_options.add_argument('--log-level=3')

    # 初始化Chrome驱动
    driver = webdriver.Chrome(
        service=Service("E:/App/Anaconda/envs/jtr/chromedriver.exe"),
        options=chrome_options
    )
    
    # 打开URL
    print(f"正在打开网址: {url}")
    driver.get(url)
    
    # 等待JavaScript执行完成
    print(f"等待{wait_time}秒让JavaScript执行完成...")
    time.sleep(wait_time)

    

    
    
    # try_method(driver,"《网易严选服务协议》")

    
    # 也可以使用显式等待特定元素出现
    # from selenium.webdriver.common.by import By
    # from selenium.webdriver.support.ui import WebDriverWait
    # from selenium.webdriver.support import expected_conditions as EC
    # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "some-id")))
    
    print("页面加载完成")
    return driver


def open_url_with_chrome_gaode(url, headless=False, wait_time=5):
    """
    使用Chrome浏览器打开URL并返回JavaScript执行后的页面
    
    参数:
    url (str): 要打开的网址
    headless (bool): 是否使用无头模式，默认为False，即显示浏览器界面
    wait_time (int): 等待JavaScript执行的秒数
    
    返回:
    driver: Selenium WebDriver实例，可用于进一步操作
    """
    # 设置Chrome选项
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")  # 无头模式
    
    chrome_options.add_argument('--blink-settings=imagesEnabled=false')
    chrome_options.add_argument("--disable-gpu")  # 禁用GPU加速
    chrome_options.add_argument("--window-size=1920,1080")  # 设置窗口大小
    chrome_options.add_argument("--no-sandbox")  # 禁用沙箱模式
    chrome_options.add_argument("--disable-dev-shm-usage")  # 禁用/dev/shm使用
    chrome_options.add_argument('--log-level=3')

    # 初始化Chrome驱动
    driver = webdriver.Chrome(
        service=Service("E:/App/Anaconda/envs/jtr/chromedriver.exe"),
        options=chrome_options
    )
    
    # 打开URL
    print(f"正在打开网址: {url}")
    driver.get(url)
    
    # 等待JavaScript执行完成
    print(f"等待{wait_time}秒让JavaScript执行完成...")
    time.sleep(wait_time)

    

    
    
    # try_method(driver,"《网易严选服务协议》")

    
    # 也可以使用显式等待特定元素出现
    # from selenium.webdriver.common.by import By
    # from selenium.webdriver.support.ui import WebDriverWait
    # from selenium.webdriver.support import expected_conditions as EC
    # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "some-id")))
    
    print("页面加载完成")
    return driver

def find_iframe_src(html_content, iframe_id="service_item_frame"):
    """
    从HTML中查找指定ID的iframe并提取其src属性
    
    参数:
    html_content (str): HTML内容字符串
    iframe_id (str): 要查找的iframe的ID，默认为"service_item_frame"
    
    返回:
    str or None: iframe的src属性值，如果未找到则返回None
    """
    from bs4 import BeautifulSoup
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 方法1: 使用ID精确查找
    div = soup.find('div', id=iframe_id)
    if div:
        # 在找到的div中查找iframe
        iframe = div.find('iframe')
        if iframe and 'src' in iframe.attrs:
            return iframe['src']
    
    return None

def find_iframe_src(html_content, iframe_id="service_item_frame"):
    """
    从HTML中查找指定ID的iframe并提取其src属性
    
    参数:
    html_content (str): HTML内容字符串
    iframe_id (str): 要查找的iframe的ID，默认为"service_item_frame"
    
    返回:
    str or None: iframe的src属性值，如果未找到则返回None
    """
    from bs4 import BeautifulSoup
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 方法1: 使用ID精确查找
    div = soup.find('div', id=iframe_id)
    if div:
        # 在找到的div中查找iframe
        iframe = div.find('iframe')
        if iframe and 'src' in iframe.attrs:
            return iframe['src']
    
    return None

def find_and_click_div_by_text(driver, text="注册协议"):
    """
    查找并点击包含指定文本的div元素
    
    参数:
    driver: Selenium WebDriver实例
    text: 要查找的文本内容，默认为"注册协议"
    """
    print(f"尝试查找并点击文本为'{text}'的div元素")
    
    # 多种定位策略
    locators = [
        # XPath策略 - 查找包含指定文本的div
        (By.XPATH, f"//div[contains(text(), '{text}')]"),
        (By.XPATH, f"//div[text()='{text}']"),
        (By.XPATH, f"//*[contains(text(), '{text}')]"),
        
        # 一些网站可能会有特定类名
        (By.CSS_SELECTOR, f"div.protocol"),
        (By.CSS_SELECTOR, f"div.agreement"),
        (By.CSS_SELECTOR, f"div.terms"),
        
        # 查找包含该文本的任何可点击元素
        (By.XPATH, f"//a[contains(text(), '{text}')]"),
        (By.XPATH, f"//span[contains(text(), '{text}')]"),
        (By.XPATH, f"//p[contains(text(), '{text}')]")
    ]
    
    # 尝试每种定位策略
    for method, value in locators:
        try:
            # 首先检查元素是否存在
            elements = driver.find_elements(method, value)
            if elements:
                print(f"找到{len(elements)}个匹配元素，使用 {method}: {value}")
                
                # 遍历所有找到的元素，尝试点击第一个可见且可点击的
                for element in elements:
                    if element.is_displayed():
                        print(f"找到可见元素: {element.text or '无文本'}")
                        # 尝试滚动到元素位置再点击
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                        time.sleep(0.5)  # 等待滚动完成
                        
                        # 尝试点击
                        element.click()
                        print(f"成功点击了元素!")
                        return True
        except Exception as e:
            print(f"使用 {method}: {value} 定位/点击失败: {e}")
    
    # 所有方法都失败后，尝试使用JavaScript点击
    print("尝试使用JavaScript查找并点击元素...")
    try:
        # 通过文本内容查找元素
        js_result = driver.execute_script(f"""
            var elements = document.querySelectorAll('div, a, span, p');
            for (var i = 0; i < elements.length; i++) {{
                if (elements[i].textContent.includes('{text}')) {{
                    elements[i].click();
                    return true;
                }}
            }}
            return false;
        """)
        
        if js_result:
            print("使用JavaScript成功点击元素!")
            return True
    except Exception as e:
        print(f"JavaScript点击失败: {e}")
    
    print(f"⚠️ 未找到文本为'{text}'的可点击元素")
    return False

def open_url_with_edge(url, headless=False, wait_time=5):
    """
    使用Edge浏览器打开URL并返回JavaScript执行后的页面
    
    参数:
    url (str): 要打开的网址
    headless (bool): 是否使用无头模式，默认为False，即显示浏览器界面
    wait_time (int): 等待JavaScript执行的秒数
    
    返回:
    driver: Selenium WebDriver实例，可用于进一步操作
    """
    # 设置Edge选项
    edge_options = Options()
    if headless:
        edge_options.add_argument("--headless")  # 无头模式
    
    # 这些选项与Chrome兼容，因为Edge也是基于Chromium的
    # edge_options.add_argument('--blink-settings=imagesEnabled=false')
    edge_options.add_argument("--disable-gpu")
    edge_options.add_argument("--window-size=1920,1080")
    # edge_options.add_argument("--no-sandbox")
    # edge_options.add_argument("--disable-dev-shm-usage")
    # edge_options.add_argument('--log-level=3')

    # 初始化Edge驱动
    driver = webdriver.Edge(
        service=Service(EdgeChromiumDriverManager().install()),
        options=edge_options
    )
    
    # 打开URL
    print(f"正在使用Edge打开网址: {url}")
    driver.get(url)
    
    # 等待JavaScript执行完成
    print(f"等待{wait_time}秒让JavaScript执行完成...")
    time.sleep(wait_time)
    
    print("页面加载完成")
    return driver

def open_url_with_edge_gaode(url, headless=False, wait_time=5):
    """
    使用Edge浏览器打开URL并返回JavaScript执行后的页面
    
    参数:
    url (str): 要打开的网址
    headless (bool): 是否使用无头模式，默认为False，即显示浏览器界面
    wait_time (int): 等待JavaScript执行的秒数
    
    返回:
    driver: Selenium WebDriver实例，可用于进一步操作
    """
    # 设置Edge选项
    edge_options = Options()
    if headless:
        edge_options.add_argument("--headless")
    
    edge_options.add_argument('--blink-settings=imagesEnabled=false')
    edge_options.add_argument("--disable-gpu")
    edge_options.add_argument("--window-size=1920,1080")
    edge_options.add_argument("--no-sandbox")
    edge_options.add_argument("--disable-dev-shm-usage")
    edge_options.add_argument('--log-level=3')

    # 初始化Edge驱动
    driver = webdriver.Edge(
        service=Service(EdgeChromiumDriverManager().install()),
        options=edge_options
    )
    
    # 打开URL
    print(f"正在使用Edge打开网址: {url}")
    driver.get(url)
    
    # 等待JavaScript执行完成
    print(f"等待{wait_time}秒让JavaScript执行完成...")
    time.sleep(wait_time)
    
    print("页面加载完成")
    return driver

if __name__ == "__main__":
    # 示例URL
    target_url = "https://web.archive.org/web/20151124230948/http://you.163.com/help"
    
    # 打开浏览器并加载页面
    driver = open_url_with_chrome(target_url, headless=False, wait_time=5)
    
    try_method_click(driver,"服务协议")


    # 2️⃣ 在桌面新建保存文件夹
    desktop_path = "./test/"
    save_folder = os.path.join(desktop_path, "wyyanxuan_User_Agreements")
    os.makedirs(save_folder, exist_ok=True)

    # 获取页面标题
    print(f"页面标题: {driver.title}")
    
    # 获取渲染后的HTML源码
    html_content = driver.page_source
    print(f"HTML源码长度: {len(html_content)}字符")
    
    # 截图保存
    screenshot_path = "page_screenshot.png"
    driver.save_screenshot(screenshot_path)
    print(f"截图已保存到: {screenshot_path}")
    
    # 可以继续进行其他操作，例如查找元素、点击按钮等
    
    # 关闭浏览器（执行完所需操作后）
    input("按Enter键关闭浏览器...")
    driver.quit()