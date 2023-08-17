import logging

# 创建并配置日志记录
logging.basicConfig(
    level=logging.INFO,  # 设置日志级别为 DEBUG
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # 输出到控制台
        logging.FileHandler("app.log"),  # 写入日志到文件 app.log
    ],
)

# 获取一个名为 "logger" 的日志记录器
logger = logging.getLogger("logger")
