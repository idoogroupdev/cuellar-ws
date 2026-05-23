import graphene
import graphql_jwt
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from graphene.types.generic import GenericScalar

from roles.models import DefaultSystemRole
from users.graphql.user import UserNode
from users.services.auth_service import AuthService
from users.services.user_service import UserService
from utils.exceptions import UserNotVerified, ValidationGraphQLError


class AuthCodeEnum(graphene.Enum):
    REGISTRATION = "REGISTRATION"
    PASSWORD_RECOVERY = "PASSWORD_RECOVERY"  # nosec


class RegisterUserInput(graphene.InputObjectType):
    email = graphene.String(required=True)
    password = graphene.String(required=True)


class RegisterClient(graphene.Mutation):
    user = graphene.Field(UserNode)

    class Arguments:
        input = RegisterUserInput(required=True)

    def mutate(self, info, input: RegisterUserInput):
        try:
            user = UserService.create_user_with_role(
                email=input.email.lower(),
                password=input.password,
                role_name=DefaultSystemRole.CLIENT,
            )
        except ValidationError as exc:
            raise ValidationGraphQLError(fields=exc.message_dict)

        return RegisterClient(user=user)


class Login(graphql_jwt.ObtainJSONWebToken):
    user = graphene.Field(UserNode)

    @classmethod
    def resolve(cls, root, info, **kwargs):
        if not info.context.user.is_verified:
            raise UserNotVerified
        return cls(user=info.context.user)


class RequestAuthCodeInput(graphene.InputObjectType):
    email = graphene.String(required=True)
    auth_code = AuthCodeEnum(required=True)


class RequestAuthCode(graphene.Mutation):
    message = graphene.String()

    class Arguments:
        input = RequestAuthCodeInput(required=True)

    def mutate(self, info, input: RequestAuthCodeInput):
        try:
            AuthService.send_auth_code(
                email=input.email.lower(),
                auth_code=input.auth_code,
            )
        except ValidationError as exc:
            raise ValidationGraphQLError(fields=exc.message_dict)

        return RequestAuthCode(message=_("Code sent"))


class VerifyAuthCodeInput(RequestAuthCodeInput):
    code = graphene.String(required=True)


class VerifyAuthCode(graphene.Mutation):
    user = graphene.Field(UserNode)
    token = graphene.String()
    refresh_token = graphene.String()
    payload = GenericScalar()
    refresh_expires_in = graphene.Int()

    class Arguments:
        input = VerifyAuthCodeInput(required=True)

    def mutate(self, info, input: VerifyAuthCodeInput):

        try:
            user, auth_info = AuthService.verify_auth_code(
                email=input.email.lower(),
                code=input.code,
                auth_code=input.auth_code,
                request=info.context,
            )

        except ValidationError as exc:
            raise ValidationGraphQLError(fields=exc.message_dict)

        return VerifyAuthCode(
            user=user,
            token=auth_info.token,
            refresh_token=auth_info.refresh_token,
            payload=auth_info.payload,
            refresh_expires_in=int(auth_info.refresh_expires_in.timestamp()),
        )


class Mutation(graphene.ObjectType):
    login = Login.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    revoke_token = graphql_jwt.Revoke.Field()
    register_client = RegisterClient.Field()
    request_auth_code = RequestAuthCode.Field()
    verify_auth_code = VerifyAuthCode.Field()


schema = graphene.Schema(mutation=Mutation)
