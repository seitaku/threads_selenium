import spiderBot as threads_spiderBot  # 導入 SpiderBot_threads 模組
import threads_post_data_analysis as threads_analysis  


# 主程式
def main():
    post_file_name = threads_spiderBot.get_thread_post_save_local_by_time()  # 使用模組中的方法
    print(post_file_name)
    analysis_file_name = threads_analysis.analysis(post_file_name)
    print(analysis_file_name)

if __name__ == "__main__":
    main()