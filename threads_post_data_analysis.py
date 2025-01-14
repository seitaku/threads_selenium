import json
import re
from datetime import datetime
import os

###
# threads posts 文章分析
###

# 定義正規表達式模式
pattern = r"讚([\d\.]+)(萬|千)?|留言([\d,]+)(萬|千)?|轉發([\d,]+)(萬|千)?|分享([\d,]+)(萬|千)?"

def load_config(file_path='config.json'):
    with open(file_path, 'r') as file:
        return json.load(file)
    
config = load_config()
load_config()
    
# 讀取 JSON 文件
def get_json_data_to_obj(json_file, default_path=config["post_save_default_path"]):
    if not os.path.isabs(json_file):  # 檢查是否已經是完整路徑
        json_file = os.path.join(default_path, json_file)

    # 檢查文件是否存在
    if not os.path.exists(json_file):
        raise FileNotFoundError(f"文件 {json_file} 不存在。請確認文件路徑是否正確。")

    print(f'json_file:{json_file}')
    with open(json_file, "r", encoding="utf-8") as file:
        data = json.load(file)  # 載入 JSON 數據
    return data

# 主程式
def main():
    # 取出 posts 陣列
    analysis("20250104_162715_Posts.json")
    
def analysis(json_file):
    json_str = get_json_data_to_obj(json_file)

    posts = json_str.get("posts", [])  # 使用 .get() 確保即使沒有 posts 屬性也不會報錯
    # 輸出每篇文章的標題與內容
    for post in posts:
        matches = re.findall(pattern, post['flag'])
        # 整理數據並補 0
        flag_data = {
            'like': 0,
            'reMsg': 0,
            'forward': 0,
            'share': 0
        }
        for match in matches:
            # 根據匹配結果，match 是一個元組，選擇其中不為空的元素
            like_value, like_unit, remsg, remsg_unit, forward, forward_unit, share, share_unit = match

            if like_value:
                flag_data['like'] = convert_to_number(like_value, like_unit)
            if remsg:
                flag_data['reMsg'] = convert_to_number(remsg, remsg_unit)
            if forward:
                flag_data['forward'] = convert_to_number(forward, forward_unit)
            if share:
                flag_data['share'] = convert_to_number(share, share_unit)

        post["flag"] = flag_data

    sorted_posts = sorted(posts, key=lambda post: int(post['flag']['like']), reverse=True)
    # for post in sorted_posts:
    #     print(f"Post URL: {post['post_href']}, Likes: {post['flag']['like']}")
    return save_json_to_file(sorted_posts)

# 取得當前時間當格式年月日時分秒
def curr_time():
    # 取得當前時間並格式化為 "YYYYMMDD_HHMMSS" 格式
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    return current_time

def save_json_to_file(json_str):
    # 取得當前時間並格式化為 "YYYYMMDD_HHMMSS" 格式
    current_time = curr_time()
    # 使用當前時間作為檔案名稱
    analysis_file_path = config["analysis_file_path"]
    file_name = f"{current_time}_Posts_analysis.json"
    with open(f"{analysis_file_path}/{file_name}", 'w', encoding='utf-8') as json_file:
        json.dump(json_str, json_file, ensure_ascii=False, indent=4)
    return file_name

def convert_to_number(value, unit=None):
    """根據單位將數字轉換成實際數值"""
    value = float(value.replace(',', ''))
    if unit == '萬':
        return int(value * 10000)
    elif unit == '千':
        return int(value * 1000)
    else:
        return int(value)
    
if __name__ == "__main__":
    main()
