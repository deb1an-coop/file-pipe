from app.core.config import Settings
from datetime import timedelta, datetime, timezone
import jwt

class TokenManager:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._secret = self._get_secret()

    def _get_secret(self) -> str:
        secret = self.settings.jwt_secret_key
        if hasattr(secret, 'get_secret_value'):
            return secret.get_secret_value()
        return secret

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.settings.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        
        return jwt.encode(to_encode, self._secret, algorithm=self.settings.jwt_algorithm)