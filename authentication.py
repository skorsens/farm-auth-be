import datetime
import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext


class AuthHandler:
    security = HTTPBearer()
    # Password hashing library that uses bcrypt's Blowfish hashing algorithm
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    # The secret used for JWT. Would be stored in an env var in prod environment
    secret = "FARMSTACKsecretString"

    def get_password_hash(self, password: str) -> str:
        """Generate the hash for the password"""
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify the plain_password against the hashed one"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def encode_token(self, user_id: str, username: str) -> str:
        payload = {
            # Expiration - how long is the tocken valid
            "exp": datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(minutes=30),
            # Issued at time - when the tocken was issued
            "iat": datetime.datetime.now(datetime.timezone.utc),
            # Subscription - the user details
            "sub": f"{user_id}:{username}",
        }
        return jwt.encode(payload, self.secret, algorithm="HS256")

    def decode_token_and_get_sub(self, token: str) -> str:
        """Decode token and return the `sub` claim from the token payload

        The `sub` is returned as a string `f"{user_id}:{username}"`
        """
        try:
            payload = jwt.decode(token, self.secret, algorithms=["HS256"])
            return payload["sub"]
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Signature has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

    def auth_wrapper(
        self, auth: HTTPAuthorizationCredentials = Security(security)
    ) -> str:
        """The dependency to be injected for the routes that need authentication"""
        return self.decode_token_and_get_sub(auth.credentials)
