import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

class Config:
    # openGauss 数据库连接配置
    DB_HOST = os.getenv('DB_HOST', '127.0.0.1')  # 使用 IPv4 地址避免 IPv6 认证问题
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'postgres')  # 先连接到 postgres 数据库
    DB_USER = os.getenv('DB_USER', 'gaussdb')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'Gauss@456')  # 使用 MD5 加密的密码
    
    # SQLAlchemy 配置 - 密码需要 URL 编码，添加 sslmode=disable 和 client_encoding
    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=disable&client_encoding=utf8'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask 配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True') == 'True'
