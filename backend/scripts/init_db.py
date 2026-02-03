"""
数据库初始化脚本
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import engine
from sqlalchemy import text


def init_db():
    """初始化数据库"""
    print("开始初始化数据库...")
    
    # 先禁用外键约束检查
    with engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        conn.commit()
    
    # 重新创建所有表（不带外键约束）
    print("正在创建所有表...")
    from app.core.database import Base
    
    # 创建一个没有外键约束的元数据
    from sqlalchemy import MetaData
    metadata = MetaData()
    
    # 复制所有表结构但移除外键约束
    for table_name, table in Base.metadata.tables.items():
        # 创建新的表对象，移除外键约束
        columns = []
        for column in table.columns:
            # 复制列定义但移除外键信息
            col_args = []
            if hasattr(column, 'name'):
                col_args.append(column.name)
            if hasattr(column, 'type'):
                col_args.append(column.type)
            
            # 复制其他属性
            kwargs = {}
            if column.primary_key:
                kwargs['primary_key'] = True
            if column.autoincrement is not None:
                kwargs['autoincrement'] = column.autoincrement
            if column.nullable is not None:
                kwargs['nullable'] = column.nullable
            if column.default is not None:
                kwargs['default'] = column.default
            if column.server_default is not None:
                kwargs['server_default'] = column.server_default
            if column.comment is not None:
                kwargs['comment'] = column.comment
            if column.index:
                kwargs['index'] = True
            if column.unique:
                kwargs['unique'] = True
            
            from sqlalchemy import Column
            new_column = Column(*col_args, **kwargs)
            columns.append(new_column)
        
        # 创建新表（无外键约束）
        from sqlalchemy import Table
        new_table = Table(table_name, metadata, *columns)
    
    # 创建所有表
    metadata.create_all(bind=engine)
    print("✓ 所有表创建完成")
    
    # 重新启用外键约束检查
    with engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        conn.commit()
    
    print("\n✓ 数据库初始化完成！")
    print("\n数据库表已成功创建，您可以手动插入测试数据或使用API接口创建用户。")


if __name__ == "__main__":
    init_db()