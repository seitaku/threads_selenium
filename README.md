# 必要套件
```bash
pip3 install selenium
pip3 install beautifulsoup4
```

# 設定config.json
```bash
"post_save_default_path": "./post/json/ori",   //posts ori 儲存位置
"analysis_file_path": "./post/json/analysis",  //analysis 儲存位置
"proj_path": "C:/workspace/python/threads",    //專案位於電腦位置
"chromeDriver_path": "/chromedriver-win64/chromedriver.exe",  //chromeDriver模擬器的位置
"rolling_index": 3    // spiderBot.py 爬取文章時往下滾動刷新文章的次數
```

# 使用方法，請參考
```bash
main.py

import spiderBot as threads_spiderBot  # 導入 SpiderBot_threads 模組
import threads_post_data_analysis as threads_analysis  


# 主程式
def main():
    post_file_name = threads_spiderBot.get_thread_post_save_local_by_time()  # 使用模組中的方法
    print(post_file_name)
    analysis_file_name = threads_analysis.analysis(post_file_name)
    print(analysis_file_name)
```

# 主要功能
```bash
###
# 取得thread 連線保存至本地，並解析本地文件得出json
# 提供使用者輸入ID
###
get_thread_post_save_local_by_time()

###
# 取得thread 連線保存至本地，並解析本地文件得出json
# para user_input = threads user ID 或是傳""(空值)為直接查詢當下首頁的文章posts
# para rolling = True 滾動查詢
# return fileName 儲存於 config.json 參數"post_save_default_path" 位置
###
get_threads_v1_byId(user_input, True)

###
# threads posts 文章分析
# para json_file = spiderBot.py爬出的檔案名稱
# return fileName 儲存於 config.json 參數"analysis_file_path" 位置
###
analysis(json_file)
```





