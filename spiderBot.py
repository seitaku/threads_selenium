from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os
import time
import json
from datetime import datetime

###
# threads 爬蟲
###

def load_config(file_path='config.json'):
    with open(file_path, 'r') as file:
        return json.load(file)
    
config = load_config()

# 設定 ChromeDriver 路徑
CHROMEDRIVER_PATH = config["proj_path"] + config["chromeDriver_path"]
# 找到每篇貼文的外框
post_article_class = 'x1a2a7pz x1n2onr6'
# 取得貼文文字內容
post_content_class ='x1a6qonq x6ikm8r x10wlt62 xj0a0fe x126k92a x6prxxf x7r5mf7'
# 取得讚、回覆、轉發、分享等操作項
post_sharing_class = 'x4vbgl9 xp7jhwk x1k70j0n'
#保存post的id 檢查防止重複
post_id_set = set()
# 平台
threads_plant = "https://www.threads.net/"
# 滾動刷新頁面次數
rolling_index = config["rolling_index"]


# 等待網頁加載完成並獲取內容
def fetch_webpage_no_rolling(url):
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # 無頭模式，若不需要 GUI，可以啟用這行

    options.add_argument('--disable-gpu')  # 禁用 GPU 硬體加速
    options.add_argument('--disable-software-rasterizer')  # 禁用軟體光柵化
    options.add_argument('--disable-dev-shm-usage')  # 避免共享記憶體使用錯誤
    options.add_argument('--disable-features=VizDisplayCompositor')  # 禁用視覺渲染功能
    options.add_argument('--blink-settings=imagesEnabled=false')  # 禁止加載圖片

    # 設定 WebDriver
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            # EC.presence_of_element_located((By.TAG_NAME, 'span'))  # 等待 span 標籤出現
            # EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.content')) # 等待特定內容或元素可見
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )

        html = driver.page_source
        return html
    except Exception as e:
        # print(f"Error fetching webpage: {e}")
        print(f"Error type: {type(e).__name__}")
        return None
    finally:
        driver.quit()

def fetch_webpage_rolling(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 無頭模式，若不需要 GUI，可以啟用這行

    options.add_argument('--disable-gpu')  # 禁用 GPU 硬體加速
    options.add_argument('--disable-software-rasterizer')  # 禁用軟體光柵化
    options.add_argument('--disable-dev-shm-usage')  # 避免共享記憶體使用錯誤
    options.add_argument('--disable-features=VizDisplayCompositor')  # 禁用視覺渲染功能
    options.add_argument('--blink-settings=imagesEnabled=false')  # 禁止加載圖片

    # 設定 WebDriver
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )

        time.sleep(3)
        posts_data_json = []
        get_posts_immediate(driver.page_source, posts_data_json)

        # # 模擬滾動頁面兩次並等待內容載入
        for _ in range(rolling_index):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
            get_posts_immediate(driver.page_source, posts_data_json)
        

        return posts_data_json
    except Exception as e:
        print(f"Error fetching webpage: {e}")
        if driver.get is None:
            print("driver.get 已被設為 None!")
        return None
    finally:
        driver.quit()

# 解析並提取 thread 中的文章
def get_posts_local_html(html_file_name):
    # 假設本地端的 HTML 檔案路徑
    html_file_path = html_file_name  # 請將此處替換為您本地 HTML 檔案的路徑

    # 打開並讀取本地 HTML 檔案
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    # 找到每篇貼文的外框
    posts = soup.find_all('div', class_= post_article_class)

    posts_data_json = []
    analyze_data_json = {}
    # 遍歷每篇貼文
    post_count = 0
    for post in posts:
        post_data_json = {}
        post_count += 1

        # 取得使用者名稱
        user = post.find('a', href=True, string=True)
        if user:
            post_data_json["user"] = user['href'][1:]  # 假設 href="/@" 開頭，去除 "/@"

        # 取得文字內容
        content_element = post.find('div', class_ = post_content_class)
        if content_element:
            content = ' '.join([span.get_text() for span in content_element.find_all('span')])
            post_data_json["content"] = content

        # 取得讚、回覆、轉發、分享等操作項
        flag_element = post.find('div', class_ = post_sharing_class)
        if flag_element:
            post_data_json["flag"] = flag_element.get_text()
        # print(post_data_json) #log 列出
        posts_data_json.append(post_data_json)
            

        # 查找符合條件的 link 標籤
        links = post.find("a", href=lambda x: x and "/post" in x)
        post_data_json["post_href"] = threads_plant + links["href"]

    return post_data_json

# 解析並提取 thread 中的文章
def get_posts_immediate(html_content, posts_data_json):

    soup = BeautifulSoup(html_content, 'html.parser')
    # 找到每篇貼文的外框
    posts = soup.find_all('div', class_= post_article_class)
    # 遍歷每篇貼文
    post_count = 0
    for post in posts:
        post_data_json = {}

        # 查找符合條件的 link 標籤
        post_id = post.find("a", href=lambda x: x and "/post" in x)["href"]
        if post_id in post_id_set:
            # print(f'重複的文章 post_id:{post_id}')
            continue
        else:
            print(f'新的文章 post_id:{post_id}')

        # 取得文章UID
        post_id_set.add(post_id)
        post_data_json["post_href"] = threads_plant + post_id

        # 取得使用者名稱
        user = post.find('a', href=True, string=True)
        if user:
            post_data_json["user"] = user['href'][1:]  # 假設 href="/@" 開頭，去除 "/@"

        # 取得文字內容
        content_element = post.find('div', class_ = post_content_class)
        if content_element:
            content = ' '.join([span.get_text() for span in content_element.find_all('span')])
            post_data_json["content"] = content

        # 取得讚、回覆、轉發、分享等操作項
        flag_element = post.find('div', class_ = post_sharing_class)
        if flag_element:
            post_data_json["flag"] = flag_element.get_text()
        
        # 有照片的文章
        picture_tags = post.find_all('picture')
        post_data_json["picture"] = 'T' if picture_tags else "F"

        # 記錄有影片的文章
        picture_tags = post.find_all('video')
        post_data_json["video"] = 'T' if picture_tags else "F"

        posts_data_json.append(post_data_json)
        print(post_data_json) #log 列出
    # return analyze_data_json


# 匯出 HTML 檔案
def save_html_to_file(html, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(html)

# 保存json字串到本地匯出檔案
def save_json_to_file(json_str):
    # 取得當前時間並格式化為 "YYYYMMDD_HHMMSS" 格式
    current_time = curr_time()
    # 使用當前時間作為檔案名稱
    post_save_default_path = config["post_save_default_path"]
    file_name = f"{current_time}_Posts.json"
    with open(f"{post_save_default_path}/{file_name}", 'w', encoding='utf-8') as json_file:
        json.dump(json_str, json_file, ensure_ascii=False, indent=4)
    return file_name

# 取得當前時間當格式年月日時分秒
def curr_time():
    # 取得當前時間並格式化為 "YYYYMMDD_HHMMSS" 格式
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    return current_time

# 取得thread html
def get_threads_rolling():
    url = threads_plant  # 替換為需要爬取的 thread 網址
    html = fetch_webpage_rolling(url)
    return html

# 取得thread html
def get_threads_no_rolling():
    url = threads_plant  # 替換為需要爬取的 thread 網址
    html = fetch_webpage_no_rolling(url)
    return html

# 取得thread 連線保存至本地，並解析本地文件得出json
def get_threads_v1():
    url = threads_plant  # 替換為需要爬取的 thread 網址
    current_time = curr_time()
    html_file_name =  f"{current_time}_html.html" 
    html = fetch_webpage_no_rolling(url)
    if html:
        # 匯出 HTML 檔案到根目錄
        save_html_to_file(html, html_file_name)

    posts_json = get_posts_local_html(html_file_name)
    save_json_to_file(posts_json)

    print('finsh')

# 取得thread 連線保存至本地，並解析本地文件得出json
def post_data_to_json(posts_data_json):
    analyze_data_json = {}
    analyze_data_json["posts"] = posts_data_json
    analyze_data_json["post_count"] = len(posts_data_json)
    return analyze_data_json

# 取得thread 連線保存至本地，並解析本地文件得出json
def get_threads_v1_byId(thread_id, rolling : bool = True):
    url = threads_plant
    if thread_id:
        url = url + '@' + thread_id  # 替換為需要爬取的 thread 網址
        current_time = curr_time()
        html_file_name =  f"{current_time}_html.html" 

    if rolling:
        posts_data_json = fetch_webpage_rolling(url)
    else:
        html = fetch_webpage_no_rolling(url)
        if html:
            # 匯出 HTML 檔案到根目錄
            save_html_to_file(html, html_file_name)
        posts_data_json = get_posts_local_html(html_file_name)
    
    print(f'finsh rolling:{rolling}')
    # print(f'post post_id_set:{post_id_set}, size:{len(post_id_set)}')
    analyze_data_json = post_data_to_json(posts_data_json)
    return save_json_to_file(analyze_data_json)

# 取得thread 連線保存至本地，並解析本地文件得出json
def get_thread_post_save_local_by_time():
    user_input = input("請輸入id：")
    if not user_input:
        user_input = ""
    return get_threads_v1_byId(user_input, True)

# 主程式
def main():
    get_thread_post_save_local_by_time()


if __name__ == "__main__":
    main()
