"""
Security utilities for HF Token management
"""
import os
import json
import base64
import hashlib
import hmac
import time
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class TokenSecurity:
    """Advanced security for HF Token"""
    
    def __init__(self, settings_file='.xtools_secure.json'):
        self.settings_file = os.path.join(os.getcwd(), settings_file)
        self.lockout_file = os.path.join(os.getcwd(), '.xtools_lockout.json')
        self.audit_log_file = os.path.join(os.getcwd(), '.xtools_audit.log')
        self.max_attempts = 5
        self.lockout_duration = 300  # 5 minutes
        self._init_encryption()
    
    def _init_encryption(self):
        """Initialize encryption key"""
        # Use machine-specific data as salt
        machine_id = self._get_machine_id()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=machine_id.encode(),
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(b'xtools_secret_key_v1'))
        self.cipher = Fernet(key)
    
    def _get_machine_id(self):
        """Get machine-specific identifier"""
        try:
            # Try to get machine ID
            import uuid
            return str(uuid.getnode())
        except:
            # Fallback
            return 'xtools_default_salt'
    
    def encrypt_token(self, token):
        """Encrypt HF token"""
        if not token:
            return None
        return self.cipher.encrypt(token.encode()).decode()
    
    def decrypt_token(self, encrypted_token):
        """Decrypt HF token"""
        if not encrypted_token:
            return None
        try:
            return self.cipher.decrypt(encrypted_token.encode()).decode()
        except Exception:
            return None
    
    def check_lockout(self):
        """Check if system is locked due to failed attempts"""
        try:
            if os.path.exists(self.lockout_file):
                with open(self.lockout_file, 'r') as f:
                    lockout_data = json.load(f)
                
                attempts = lockout_data.get('attempts', 0)
                last_attempt = lockout_data.get('last_attempt', 0)
                
                # Check if lockout period has passed
                if attempts >= self.max_attempts:
                    time_passed = time.time() - last_attempt
                    if time_passed < self.lockout_duration:
                        remaining = int(self.lockout_duration - time_passed)
                        return True, remaining
                    else:
                        # Reset lockout
                        self._reset_lockout()
                        return False, 0
                return False, 0
        except Exception:
            pass
        return False, 0
    
    def _reset_lockout(self):
        """Reset lockout counter"""
        try:
            if os.path.exists(self.lockout_file):
                os.remove(self.lockout_file)
        except:
            pass
    
    def record_failed_attempt(self):
        """Record failed authentication attempt"""
        try:
            lockout_data = {'attempts': 1, 'last_attempt': time.time()}
            if os.path.exists(self.lockout_file):
                with open(self.lockout_file, 'r') as f:
                    lockout_data = json.load(f)
                lockout_data['attempts'] += 1
                lockout_data['last_attempt'] = time.time()
            
            with open(self.lockout_file, 'w') as f:
                json.dump(lockout_data, f)
        except:
            pass
    
    def audit_log(self, action, details=None):
        """Log security events"""
        try:
            timestamp = datetime.now().isoformat()
            log_entry = {
                'timestamp': timestamp,
                'action': action,
                'details': details or {}
            }
            with open(self.audit_log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except:
            pass
    
    def get_token_from_env(self):
        """Get token from environment variable"""
        return os.environ.get('HF_TOKEN') or os.environ.get('HUGGINGFACE_TOKEN')
    
    def validate_token_format(self, token):
        """Validate token format"""
        if not token:
            return False, "Token is empty"
        if not token.startswith('hf_'):
            return False, "Token must start with 'hf_'"
        if len(token) < 20:
            return False, "Token is too short"
        return True, "Valid"
    
    def hash_token(self, token):
        """Create hash of token for verification"""
        return hashlib.sha256(token.encode()).hexdigest()[:16]
    
    def verify_token_integrity(self, token, stored_hash):
        """Verify token hasn't been tampered with"""
        return self.hash_token(token) == stored_hash

# Global instance
token_security = TokenSecurity()
