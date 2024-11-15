# config.py
class Config:
    WELCOME = 'You are welcome, but it is nothing here!'

class DevelopmentConfig(Config):
    WELCOME = 'You are welcome, it is develop env'
    CKPT_PATH = r"D:\pyspaces\pth\jinghe_best.pth"
    TRAINING_PATH = r"D:\jinhe\training"

class ProductionConfig(Config):
    WELCOME = 'You are welcome, it is product env, please be careful'
    CKPT_PATH = r"D:\pyspaces\match\Result\2024-11-06_15-30-41\checkpoint_4.pth"
    TRAINING_PATH = r"D:\jinhe\training"
