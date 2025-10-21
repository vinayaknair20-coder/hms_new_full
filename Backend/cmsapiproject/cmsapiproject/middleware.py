from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)

class TokenDebugMiddleware(MiddlewareMixin):
    def process_request(self, request):
        try:
            if request.path.endswith('/api/token/'):
                logger.warning('--- Token request headers: %s', dict(request.headers))
                try:
                    body = request.body.decode('utf-8')
                except Exception:
                    body = '<unreadable>'
                logger.warning('--- Token request body: %s', body)
        except Exception as e:
            logger.exception('TokenDebugMiddleware error: %s', e)
        return None
