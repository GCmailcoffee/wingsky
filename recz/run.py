# run.py

import os
from app import create_app

# 从环境变量获取 Flask 运行环境，默认是开发环境
env = os.getenv("FLASK_ENV", "development")

# 根据环境创建应用实例
app = create_app()

if __name__ == "__main__":
    # 根据环境变量决定是否启用调试模式
    debug = env == "development"
    app.run(debug=debug)
