# """
# 数据库初始化脚本
# 用于创建所有数据表
# """
# from models import init_db

# if __name__ == '__main__':
#     print("🚀 开始初始化数据库...")
#     try:
#         init_db()
#         print("✅ 数据库初始化成功！")
#         print("💡 提示: 运行 'python seed_data.py' 可以添加测试数据")
#     except Exception as e:
#         print(f"❌ 数据库初始化失败: {e}")


# init_db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from models import Base  # 你的ORM基类和所有模型都在这里

from config import Config as AppConfig

class Config:
    # 使用 config.py 中的配置
    SQLALCHEMY_DATABASE_URI = AppConfig.SQLALCHEMY_DATABASE_URI

def init_db():
    print("🚀 开始初始化数据库...")
    
    # 创建数据库引擎，禁用连接池避免版本检测缓存问题
    engine = create_engine(
        Config.SQLALCHEMY_DATABASE_URI,
        echo=True,
        poolclass=NullPool,
        isolation_level="AUTOCOMMIT",
    )
    
    # 绕过版本检测，将 openGauss 伪装成 PostgreSQL 12
    engine.dialect.server_version_info = (12, 0)
    
    # 创建所有表（如果表已经存在，则不会覆盖）
    Base.metadata.create_all(engine)
    
    # 创建Session对象
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        # 这里可以执行一些初始化数据写入操作
        # 例如：
        # new_user = User(username="admin", password="123456")
        # session.add(new_user)
        # session.commit()
        
        session.commit()
        print("✅ 数据库初始化成功！")
    except Exception as e:
        session.rollback()
        print(f"❌ 数据库初始化失败: {e}")
        raise
    finally:
        session.close()

if __name__ == '__main__':
    init_db()

