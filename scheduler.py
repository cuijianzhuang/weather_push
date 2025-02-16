import schedule
import time
from datetime import datetime
import logging
from weather_push import main

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def job():
    """执行天气推送任务"""
    logger.info(f"开始执行定时任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        main()
        logger.info("定时任务执行完成")
    except Exception as e:
        logger.error(f"定时任务执行失败: {str(e)}", exc_info=True)

def run_scheduler():
    """启动定时任务调度器"""
    # 设置定时任务
    schedule.every().day.at("07:00").do(job)
    schedule.every().day.at("12:00").do(job)
    schedule.every().day.at("21:00").do(job)
    
    logger.info("定时任务调度器已启动")
    logger.info("预定的运行时间: 每天 07:00, 12:00, 21:00")
    
    # 立即执行一次
    logger.info("执行首次运行...")
    job()
    
    # 持续运行定时任务
    while True:
        try:
            schedule.run_pending()
            time.sleep(30)  # 每30秒检查一次是否有待执行的任务
        except Exception as e:
            logger.error(f"调度器运行异常: {str(e)}", exc_info=True)
            time.sleep(60)  # 发生异常时等待60秒后继续

if __name__ == "__main__":
    run_scheduler() 