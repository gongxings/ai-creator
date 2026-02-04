"""
OAuth凭证加密服务
"""
import os
from cryptography.fernet import Fernet
from typing import Optional
from loguru import logger


class EncryptionService:
    """凭证加密服务"""
    
    def __init__(self):
        """初始化加密服务"""
        self.encryption_key = self._get_encryption_key()
        self.cipher = Fernet(self.encryption_key)
    
    def _get_encryption_key(self) -> bytes:
        """
        获取加密密钥
        从环境变量获取，如果不存在则生成新的
        """
        # 延迟导入避免循环依赖
        from app.core.config import settings
        
        key_str = settings.OAUTH_ENCRYPTION_KEY
        
        # 检查是否使用默认值
        if key_str == "your-oauth-encryption-key-change-in-production":
            # 生成新密钥
            logger.warning("OAUTH_ENCRYPTION_KEY using default value, generating new key")
            key = Fernet.generate_key()
            logger.info(f"Generated new encryption key: {key.decode()}")
            logger.info("Please update OAUTH_ENCRYPTION_KEY in your .env file")
            return key
        
        if not key_str:
            # 生成新密钥
            logger.warning("OAUTH_ENCRYPTION_KEY not found, generating new key")
            key = Fernet.generate_key()
            logger.info(f"Generated new encryption key: {key.decode()}")
            logger.info("Please add this key to your .env file as OAUTH_ENCRYPTION_KEY")
            return key
        
        # 直接使用环境变量中的密钥
        try:
            # 验证密钥格式是否正确
            Fernet(key_str.encode())
            logger.info("Using encryption key from configuration")
            return key_str.encode()
        except Exception as e:
            logger.error(f"Invalid encryption key format: {e}")
            # 如果密钥格式不正确，生成新的密钥
            logger.warning("Generating new key due to invalid format")
            key = Fernet.generate_key()
            logger.info(f"Generated fallback encryption key: {key.decode()}")
            return key
    
    def encrypt(self, data: str) -> str:
        """
        加密数据
        
        Args:
            data: 要加密的字符串
            
        Returns:
            加密后的字符串（Base64编码）
        """
        try:
            encrypted = self.cipher.encrypt(data.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise ValueError(f"Failed to encrypt data: {e}")
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        解密数据
        
        Args:
            encrypted_data: 加密的字符串（Base64编码）
            
        Returns:
            解密后的字符串
        """
        try:
            decrypted = self.cipher.decrypt(encrypted_data.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise ValueError(f"Failed to decrypt data: {e}")
    
    def encrypt_credentials(self, credentials: dict) -> str:
        """
        加密凭证字典
        
        Args:
            credentials: 凭证字典（如Cookie、Token等）
            
        Returns:
            加密后的字符串
        """
        import json
        credentials_str = json.dumps(credentials)
        return self.encrypt(credentials_str)
    
    def decrypt_credentials(self, encrypted_credentials: str) -> dict:
        """
        解密凭证字符串
        
        Args:
            encrypted_credentials: 加密的凭证字符串
            
        Returns:
            凭证字典
        """
        import json
        credentials_str = self.decrypt(encrypted_credentials)
        return json.loads(credentials_str)


# 全局加密服务实例
encryption_service = EncryptionService()


def encrypt_credentials(credentials: dict) -> str:
    """加密凭证（便捷函数）"""
    return encryption_service.encrypt_credentials(credentials)


def decrypt_credentials(encrypted_credentials: str) -> dict:
    """解密凭证（便捷函数）"""
    return encryption_service.decrypt_credentials(encrypted_credentials)