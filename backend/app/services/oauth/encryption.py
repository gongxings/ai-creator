"""
OAuth凭证加密服务
"""
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
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
        key_str = os.getenv("OAUTH_ENCRYPTION_KEY")
        
        if not key_str:
            # 生成新密钥
            logger.warning("OAUTH_ENCRYPTION_KEY not found, generating new key")
            key = Fernet.generate_key()
            logger.info(f"Generated new encryption key: {key.decode()}")
            logger.info("Please add this key to your .env file as OAUTH_ENCRYPTION_KEY")
            return key
        
        # 如果密钥不是标准的Fernet格式，使用PBKDF2派生
        try:
            # 尝试直接使用
            Fernet(key_str.encode())
            return key_str.encode()
        except Exception:
            # 使用PBKDF2从密码派生密钥
            logger.info("Deriving encryption key from password")
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'oauth_encryption_salt',  # 固定salt，确保密钥一致
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(key_str.encode()))
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
