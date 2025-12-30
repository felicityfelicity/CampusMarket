"""
openGauss 兼容性补丁
用于解决 SQLAlchemy 无法识别 openGauss 版本字符串的问题
"""
from sqlalchemy.dialects.postgresql import base as postgresql_base

# 保存原始的版本解析函数
_original_get_server_version_info = postgresql_base.PGDialect._get_server_version_info

def patched_get_server_version_info(self, connection):
    """
    修补后的版本解析函数，兼容 openGauss
    """
    try:
        return _original_get_server_version_info(self, connection)
    except (AssertionError, ValueError):
        # 如果解析失败（openGauss 的情况），返回一个兼容的版本号
        # 模拟 PostgreSQL 12.0
        return (12, 0)

# 应用补丁
postgresql_base.PGDialect._get_server_version_info = patched_get_server_version_info

print("✅ openGauss 兼容性补丁已应用")
