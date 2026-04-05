"""Unit tests for secrets_service (local envelope encryption)"""

import pytest
from src.services.secrets_service import SecretsService


class TestSecretsService:
    """Tests for SecretsService encryption methods"""

    def setup_method(self):
        """Create a new secrets service for each test"""
        self.service = SecretsService()

    def test_generate_master_key_length(self):
        """Test master key is 32 bytes (256 bits)"""
        master_key = self.service.generate_master_key()
        assert len(master_key) == 32

    def test_generate_master_key_randomness(self):
        """Test master keys are different each time"""
        key1 = self.service.generate_master_key()
        key2 = self.service.generate_master_key()
        assert key1 != key2

    def test_generate_data_key_length(self):
        """Test data key is 32 bytes (256 bits)"""
        data_key = self.service.generate_data_key()
        assert len(data_key) == 32

    def test_encrypt_decrypt_with_data_key(self):
        """Test encrypt and decrypt with data key"""
        plaintext = "my secret password"
        data_key = self.service.generate_data_key()

        encrypted = self.service.encrypt_with_data_key(plaintext, data_key)
        decrypted = self.service.decrypt_with_data_key(encrypted, data_key)

        assert decrypted == plaintext

    def test_encrypt_produces_required_fields(self):
        """Test encrypted data contains iv, ciphertext, auth_tag"""
        plaintext = "test"
        data_key = self.service.generate_data_key()

        encrypted = self.service.encrypt_with_data_key(plaintext, data_key)

        assert "iv" in encrypted
        assert "ciphertext" in encrypted
        assert "auth_tag" in encrypted

    def test_decrypt_wrong_key_fails(self):
        """Test decryption with wrong key fails"""
        plaintext = "secret"
        data_key1 = self.service.generate_data_key()
        data_key2 = self.service.generate_data_key()

        encrypted = self.service.encrypt_with_data_key(plaintext, data_key1)

        with pytest.raises(ValueError):
            self.service.decrypt_with_data_key(encrypted, data_key2)

    def test_encrypt_data_key(self):
        """Test encrypting a data key with master key"""
        data_key = self.service.generate_data_key()
        master_key = self.service.generate_master_key()

        encrypted = self.service.encrypt_data_key(data_key, master_key)

        assert "iv" in encrypted
        assert "encrypted_data_key" in encrypted
        assert "auth_tag" in encrypted

    def test_decrypt_data_key(self):
        """Test decrypting a data key with master key"""
        data_key = self.service.generate_data_key()
        master_key = self.service.generate_master_key()

        encrypted = self.service.encrypt_data_key(data_key, master_key)
        decrypted = self.service.decrypt_data_key(encrypted, master_key)

        assert decrypted == data_key

    def test_envelope_encrypt_decrypt(self):
        """Test full envelope encryption and decryption"""
        plaintext = "my database password"
        master_key = self.service.generate_master_key()

        # Encrypt
        encrypted_data = self.service.encrypt_secret(plaintext, master_key)

        assert "encrypted_data_key" in encrypted_data
        assert "encrypted_secret" in encrypted_data
        assert "created_at" in encrypted_data

        # Decrypt
        decrypted = self.service.decrypt_secret(encrypted_data, master_key)

        assert decrypted == plaintext

    def test_envelope_decrypt_wrong_master_key_fails(self):
        """Test envelope decryption with wrong master key fails"""
        plaintext = "secret"
        master_key1 = self.service.generate_master_key()
        master_key2 = self.service.generate_master_key()

        encrypted = self.service.encrypt_secret(plaintext, master_key1)

        with pytest.raises(ValueError):
            self.service.decrypt_secret(encrypted, master_key2)

    def test_encrypt_empty_string(self):
        """Test encrypting empty string"""
        plaintext = ""
        data_key = self.service.generate_data_key()

        encrypted = self.service.encrypt_with_data_key(plaintext, data_key)
        decrypted = self.service.decrypt_with_data_key(encrypted, data_key)

        assert decrypted == plaintext

    def test_encrypt_long_string(self):
        """Test encrypting long string"""
        plaintext = "a" * 10000
        data_key = self.service.generate_data_key()

        encrypted = self.service.encrypt_with_data_key(plaintext, data_key)
        decrypted = self.service.decrypt_with_data_key(encrypted, data_key)

        assert decrypted == plaintext

    def test_encrypt_unicode(self):
        """Test encrypting unicode characters"""
        plaintext = "中文密码 🔐"
        data_key = self.service.generate_data_key()

        encrypted = self.service.encrypt_with_data_key(plaintext, data_key)
        decrypted = self.service.decrypt_with_data_key(encrypted, data_key)

        assert decrypted == plaintext

    def test_each_encryption_unique(self):
        """Test each encryption produces unique ciphertext"""
        plaintext = "secret"
        data_key = self.service.generate_data_key()

        encrypted1 = self.service.encrypt_with_data_key(plaintext, data_key)
        encrypted2 = self.service.encrypt_with_data_key(plaintext, data_key)

        # IV should be different (random)
        assert encrypted1["iv"] != encrypted2["iv"]
        # Ciphertext might differ due to different IV
        assert encrypted1["ciphertext"] != encrypted2["ciphertext"]


class TestGetSecretsService:
    """Tests for get_secrets_service singleton"""

    def test_returns_instance(self):
        """Test get_secrets_service returns a SecretsService"""
        from src.services.secrets_service import get_secrets_service

        service = get_secrets_service()
        assert isinstance(service, SecretsService)

    def test_returns_same_instance(self):
        """Test get_secrets_service returns same instance"""
        from src.services.secrets_service import get_secrets_service, _secrets_service

        # Clear existing instance
        import src.services.secrets_service as module
        module._secrets_service = None

        service1 = get_secrets_service()
        service2 = get_secrets_service()

        assert service1 is service2

    def test_clear_secret_cache(self):
        """Test clear_secret_cache clears caches"""
        from src.services.secrets_service import clear_secret_cache, _decrypted_cache, _master_key_cache

        # Add some data to cache
        import src.services.secrets_service as module
        module._decrypted_cache = {"test": "value"}
        module._master_key_cache = bytes(32)

        clear_secret_cache()

        assert module._decrypted_cache == {}
        assert module._master_key_cache is None