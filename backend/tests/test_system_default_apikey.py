"""
系统默认APIKey 功能测试脚本
用于验证 Phase 1 核心功能的实现
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.services.api_key_service import APIKeyService
from app.utils.api_key_cipher import encrypt_api_key, decrypt_api_key
from app.models import User


def test_encryption():
    """测试加密解密功能"""
    print("=" * 60)
    print("测试 1: APIKey 加密解密功能")
    print("=" * 60)
    
    test_key = "sk-test123456789abcdefghijklmnopqrstuvwxyz"
    
    # 加密
    encrypted = encrypt_api_key(test_key)
    print(f"✓ 原始 Key: {test_key}")
    print(f"✓ 加密后：{encrypted[:50]}...")
    
    # 解密
    decrypted = decrypt_api_key(encrypted)
    print(f"✓ 解密后：{decrypted}")
    
    # 验证
    assert decrypted == test_key, "解密结果与原始 Key 不一致"
    print("✅ 加密解密测试通过\n")


def test_create_system_default_key():
    """测试创建系统默认APIKey"""
    print("=" * 60)
    print("测试 2: 创建系统默认APIKey")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # 查找第一个管理员用户（user_id=1）
        admin_user = db.query(User).filter(User.id == 1).first()
        if not admin_user:
            print("⚠ 未找到管理员用户，跳过此测试")
            return
        
        from app.schemas.api_key import APIKeyCreate
        
        # 创建系统默认APIKey
        key_data = APIKeyCreate(
            key_name="系统默认 - GPT-4",
            set_as_system_default=True,
            system_default_order=1,
            provider="openai",
            model_name="gpt-4",
            base_url="https://api.openai.com/v1",
            rate_limit=60
        )
        
        response = APIKeyService.create_api_key(
            db=db,
            user_id=admin_user.id,
            key_data=key_data
        )
        
        print(f"✓ 创建成功:")
        print(f"  - ID: {response.id}")
        print(f"  - 名称：{response.key_name}")
        print(f"  - API Key: {response.api_key}")
        print(f"  - 显示：{response.key_display}")
        
        # 验证数据库中的记录
        from app.models import APIKey
        db_key = db.query(APIKey).filter(APIKey.id == response.id).first()
        
        assert db_key.is_system_default == True, "is_system_default 应为 True"
        assert db_key.system_default_order == 1, "system_default_order 应为 1"
        assert db_key.provider == "openai", "provider 应为 openai"
        assert db_key.model_name == "gpt-4", "model_name 应为 gpt-4"
        assert db_key.encrypted_key is not None, "encrypted_key 不应为 None"
        
        # 验证可以解密
        decrypted = decrypt_api_key(db_key.encrypted_key)
        assert decrypted == response.api_key, "解密的 Key 应与创建的 Key 一致"
        
        print(f"✓ 数据库验证通过")
        print(f"✓ 加密存储验证通过")
        print("✅ 创建系统默认APIKey 测试通过\n")
        
    except Exception as e:
        print(f"❌ 测试失败：{str(e)}\n")
        raise
    finally:
        db.close()


def test_get_system_default_keys():
    """测试获取系统默认APIKey 列表"""
    print("=" * 60)
    print("测试 3: 获取系统默认APIKey 列表")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # 获取所有系统默认 Key
        keys = APIKeyService.get_system_default_api_keys(db)
        
        print(f"✓ 找到 {len(keys)} 个系统默认APIKey")
        
        for key in keys:
            print(f"  - {key.key_name} (排序：{key.system_default_order})")
        
        # 验证按排序排序
        if len(keys) > 1:
            for i in range(len(keys) - 1):
                assert keys[i].system_default_order <= keys[i+1].system_default_order, \
                    "系统默认 Key 应按排序升序排列"
            print("✓ 排序验证通过")
        
        print("✅ 获取系统默认APIKey 列表测试通过\n")
        
    except Exception as e:
        print(f"❌ 测试失败：{str(e)}\n")
        raise
    finally:
        db.close()


def test_assign_models_to_user():
    """测试为用户分配系统默认模型"""
    print("=" * 60)
    print("测试 4: 为用户分配系统默认模型")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # 查找一个测试用户
        test_user = db.query(User).filter(User.id == 2).first()
        if not test_user:
            print("⚠ 未找到测试用户，跳过此测试")
            return
        
        print(f"✓ 测试用户：{test_user.username} (ID: {test_user.id})")
        
        # 分配系统默认模型
        models = APIKeyService.assign_system_default_models_to_user(db, test_user.id)
        
        print(f"✓ 新创建了 {len(models)} 个模型:")
        for model in models:
            print(f"  - {model.name} ({model.model_name})")
            print(f"    来源：system_default_source={model.system_default_source}")
            print(f"    APIKey ID: {model.source_api_key_id}")
        
        # 验证再次调用不会重复创建
        models_again = APIKeyService.assign_system_default_models_to_user(db, test_user.id)
        assert len(models_again) == 0, "再次调用不应创建新模型"
        print("✓ 防重复创建验证通过")
        
        print("✅ 为用户分配系统默认模型测试通过\n")
        
    except Exception as e:
        print(f"❌ 测试失败：{str(e)}\n")
        raise
    finally:
        db.close()


def test_usage_logging():
    """测试使用日志记录（带用户追踪）"""
    print("=" * 60)
    print("测试 5: 使用日志记录（带用户追踪）")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # 获取第一个系统默认 Key
        sys_key = APIKeyService.get_system_default_api_keys(db)[0]
        test_user = db.query(User).filter(User.id == 2).first()
        
        if not test_user:
            print("⚠ 未找到测试用户，跳过此测试")
            return
        
        # 记录使用日志（指定 used_by_user_id）
        log = APIKeyService.log_api_key_usage(
            db=db,
            api_key_id=sys_key.id,
            model_id="gpt-4",
            model_name="GPT-4",
            endpoint="/v1/chat/completions",
            method="POST",
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            used_by_user_id=test_user.id  # 关键：记录实际使用者
        )
        
        print(f"✓ 日志记录成功:")
        print(f"  - APIKey ID: {log.api_key_id}")
        print(f"  - 使用用户 ID: {log.used_by_user_id}")
        print(f"  - Token 数：{log.total_tokens}")
        
        # 验证可以通过 used_by_user_id 查询
        from app.models import APIKeyUsageLog
        user_logs = db.query(APIKeyUsageLog).filter(
            APIKeyUsageLog.used_by_user_id == test_user.id
        ).all()
        
        print(f"✓ 该用户共有 {len(user_logs)} 条使用记录")
        
        # 测试统计功能
        stats = APIKeyService.get_user_usage_for_api_key(
            db=db,
            api_key_id=sys_key.id,
            user_id=test_user.id,
            days=30
        )
        
        print(f"✓ 用户使用情况统计:")
        print(f"  - 总请求：{stats['total_requests']}")
        print(f"  - 总 Token: {stats['total_tokens']}")
        
        print("✅ 使用日志记录测试通过\n")
        
    except Exception as e:
        print(f"❌ 测试失败：{str(e)}\n")
        raise
    finally:
        db.close()


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("系统默认APIKey 功能测试 - Phase 1")
    print("=" * 60 + "\n")
    
    tests = [
        ("加密解密功能", test_encryption),
        ("创建系统默认APIKey", test_create_system_default_key),
        ("获取系统默认列表", test_get_system_default_keys),
        ("分配模型给用户", test_assign_models_to_user),
        ("使用日志记录", test_usage_logging),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} 测试失败，继续下一项\n")
    
    print("=" * 60)
    print(f"测试总结:")
    print(f"  ✅ 通过：{passed} 项")
    print(f"  ❌ 失败：{failed} 项")
    print("=" * 60)
    
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
