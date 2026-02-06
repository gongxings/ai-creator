"""
创建管理员账号脚本
"""
import sys
import io
from pathlib import Path
from datetime import datetime, timedelta

# 设置Windows控制台编码为UTF-8
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到Python路径
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from app.core.database import engine, SessionLocal
from app.models.user import User, UserRole, UserStatus


def create_admin():
    """创建管理员账号"""
    db = SessionLocal()
    try:
        # 检查是否已存在管理员账号
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("[X] 管理员账号已存在！")
            print(f"   用户名: {existing_admin.username}")
            print(f"   邮箱: {existing_admin.email}")
            print(f"   角色: {existing_admin.role}")
            return
        
        # 使用预生成的密码哈希值 (admin123456)
        password_hash = "$2b$12$GeSP7DrBzGF9JqkdNS6Iqu6GViKpd2qafYLuT732omjDrRjzj38Uu"
        
        # 创建管理员账号
        admin_user = User(
            username="admin",
            email="admin@example.com",
            password_hash=password_hash,
            nickname="系统管理员",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            daily_quota=999999,
            used_quota=0,
            total_creations=0,
            credits=1000,  # 初始1000积分
            is_member=1,   # 会员
            member_expired_at=datetime.now() + timedelta(days=365),  # 会员有效期1年
            last_login_at=None,
            last_login_ip=None
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("[OK] 管理员账号创建成功！")
        print("\n" + "="*50)
        print("管理员账号信息：")
        print("="*50)
        print(f"用户名: admin")
        print(f"密码: admin123456")
        print(f"邮箱: admin@example.com")
        print(f"角色: {admin_user.role}")
        print(f"积分: {admin_user.credits}")
        print(f"会员状态: {'是' if admin_user.is_member else '否'}")
        print(f"会员到期时间: {admin_user.member_expired_at.strftime('%Y-%m-%d') if admin_user.member_expired_at else 'N/A'}")
        print("="*50)
        print("\n[!] 请在生产环境中修改默认密码！")
        
    except Exception as e:
        db.rollback()
        print(f"[X] 创建管理员账号失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
