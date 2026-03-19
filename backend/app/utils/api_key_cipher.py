"""
APIKey 加密工具类
使用 Fernet 对称加密存储敏感的 API Key
"""
from cryptography.fernet import Fernet
from app.core.config import settings
import base64
import hashlib


class APIKeyCipher:
    """APIKey 加解密工具类"""
    
    _instance = None
    _cipher = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(APIKeyCipher, cls).__new__(cls)
        return cls._instance
    
    def _get_key(self) -> bytes:
        """
        从环境变量获取加密密钥
        如果不存在则生成一个（仅用于开发环境）
        """
        # 优先使用配置的加密密钥
        encryption_key = getattr(settings, 'API_KEY_ENCRYPTION_KEY', None)
        
        if encryption_key:
            # 确保密钥格式正确（Fernet 需要 32 字节的 URL-safe base64 编码密钥）
            if isinstance(encryption_key, str):
                encryption_key = encryption_key.encode()
            
            # 如果是普通字符串，转换为合适的格式
            if len(encryption_key) < 32:
                # 使用 hash 生成固定长度的密钥
                key_hash = hashlib.sha256(encryption_key).digest()
                return base64.urlsafe_b64encode(key_hash)
            else:
                # 尝试直接使用，如果不是 valid Fernet key 会抛出异常
                try:
                    # 确保是 32 字节并正确编码
                    if len(encryption_key) >= 32:
                        return base64.urlsafe_b64encode(encryption_key[:32])
                except Exception:
                    pass
        
        # 开发环境：如果没有配置，使用固定的测试密钥（不推荐生产环境）
        test_key = b'test_encryption_key_for_development_only!'
        return base64.urlsafe_b64encode(hashlib.sha256(test_key).digest())
    
    def get_cipher(self) -> Fernet:
        """获取 Fernet 加密实例"""
        if self._cipher is None:
            key = self._get_key()
            self._cipher = Fernet(key)
        return self._cipher
    
    def encrypt(self, api_key: str) -> str:
        """
        加密 API Key
        
        Args:
            api_key: 原始 API Key 字符串
            
        Returns:
            加密后的字符串（base64 编码）
        """
        if not api_key:
            raise ValueError("API Key 不能为空")
        
        cipher = self.get_cipher()
        encrypted = cipher.encrypt(api_key.encode('utf-8'))
        return encrypted.decode('utf-8')
    
    def decrypt(self, encrypted_api_key: str) -> str:
        """
        解密 API Key
        
        Args:
            encrypted_api_key: 加密的 API Key 字符串
            
        Returns:
            解密后的原始 API Key
            
        Raises:
            ValueError: 解密失败时抛出异常
        """
        if not encrypted_api_key:
            raise ValueError("加密的 API Key 不能为空")
        
        try:
            cipher = self.get_cipher()
            decrypted = cipher.decrypt(encrypted_api_key.encode('utf-8'))
            return decrypted.decode('utf-8')
        except Exception as e:
            raise ValueError(f"API Key 解密失败：{str(e)}")
    
    def verify(self, api_key: str, encrypted_api_key: str) -> bool:
        """
        验证 API Key 是否匹配
        
        Args:
            api_key: 原始 API Key
            encrypted_api_key: 加密的 API Key
            
        Returns:
            是否匹配
        """
        try:
            decrypted = self.decrypt(encrypted_api_key)
            return decrypted == api_key
        except Exception:
            return False


# 全局单例
api_key_cipher = APIKeyCipher()


def encrypt_api_key(api_key: str) -> str:
    """
    便捷函数：加密 API Key
    
    Args:
        api_key: 原始 API Key
        
    Returns:
        加密后的字符串
    """
    return api_key_cipher.encrypt(api_key)


def decrypt_api_key(encrypted_api_key: str) -> str:
    """
    便捷函数：解密 API Key
    
    Args:
        encrypted_api_key: 加密的 API Key
        
    Returns:
        解密后的原始 API Key
    """
    return api_key_cipher.decrypt(encrypted_api_key)
