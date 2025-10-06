from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from urllib.parse import parse_qs
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class JWTAuthMiddleware:
    """JWT authentication middleware for WebSocket connections"""
    
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # Получаем токен из query parameters
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]

        if token:
            try:
                # Аутентификация через JWT
                user = await self.get_user_from_token(token)
                scope['user'] = user
            except Exception as e:
                logger.error(f"JWT authentication failed: {e}")
                scope['user'] = AnonymousUser()
        else:
            scope['user'] = AnonymousUser()

        return await self.inner(scope, receive, send)

    @database_sync_to_async
    def get_user_from_token(self, token):
        """Получить пользователя из JWT токена"""
        try:
            jwt_auth = JWTAuthentication()
            validated_token = jwt_auth.get_validated_token(token)
            user = jwt_auth.get_user(validated_token)
            return user
        except (InvalidToken, TokenError) as e:
            logger.error(f"Invalid token: {e}")
            return AnonymousUser()
        except Exception as e:
            logger.error(f"Error validating token: {e}")
            return AnonymousUser()


def JWTAuthMiddlewareStack(inner):
    """Stack with JWT authentication middleware"""
    return JWTAuthMiddleware(AuthMiddlewareStack(inner))