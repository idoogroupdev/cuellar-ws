from graphql import GraphQLError
from graphql_jwt.settings import jwt_settings
from django.utils.translation import gettext_lazy as _


class SingleSessionJWTMiddleware:
    def resolve(self, next, root, info, **kwargs):
        request = info.context
        user = request.user

        if not user.is_authenticated:
            return next(root, info, **kwargs)

        if not hasattr(request, "_session_checked"):
            request._session_checked = True

            auth = request.META.get("HTTP_AUTHORIZATION", "")

            if auth:
                token = auth.split(" ")[1]

                payload = jwt_settings.JWT_DECODE_HANDLER(token)

                token_session_id = payload.get("session_version")

                if token_session_id != user.session_version:
                    raise GraphQLError(_("Your session has been closed."))

        return next(root, info, **kwargs)
