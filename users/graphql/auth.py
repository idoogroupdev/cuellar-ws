import graphene
import graphql_jwt
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from fcm_django.models import DeviceType, FCMDevice
from graphene.types.generic import GenericScalar

from roles.models import DefaultSystemRole
from users.graphql.user import UserNode
from users.services.auth_service import AuthService
from users.services.user_service import UserService
from utils.decorators import login_required
from utils.exceptions import PermissionDenied, UserNotVerified, ValidationGraphQLError

DeviceTypeEnum = graphene.Enum.from_enum(DeviceType)


class AuthCodeEnum(graphene.Enum):
    REGISTRATION = "REGISTRATION"
    PASSWORD_RECOVERY = "PASSWORD_RECOVERY"  # nosec


class RegisterUserInput(graphene.InputObjectType):
    email = graphene.String(required=True)
    password = graphene.String(required=True)
    first_name = graphene.String(required=True)
    phone = graphene.String(required=False)


class RegisterClient(graphene.Mutation):
    user = graphene.Field(UserNode)

    class Arguments:
        input = RegisterUserInput(required=True)

    def mutate(self, info, input: RegisterUserInput):
        try:
            user = UserService.create_user(
                email=input.email.lower(),
                password=input.password,
                role_name=DefaultSystemRole.CLIENT,
                first_name=input.first_name,
                phone=input.phone,
            )
        except ValidationError as exc:
            raise ValidationGraphQLError(fields=exc.message_dict)

        return RegisterClient(user=user)


class Login(graphql_jwt.ObtainJSONWebToken):
    user = graphene.Field(UserNode)

    class Arguments:
        firebase_registration_id = graphene.String()
        device_id = graphene.String()
        device_type = DeviceTypeEnum()
        is_mobile = graphene.Boolean()

    @classmethod
    def register_fmc_device(
        cls, user_id, firebase_registration_id, device_id, device_type
    ):

        if not firebase_registration_id:
            return None

        FCMDevice.objects.update_or_create(
            user_id=user_id,
            defaults={
                "registration_id": firebase_registration_id,
                "device_id": device_id,
                "type": device_type.value if device_type else None,
            },
        )

    @classmethod
    def resolve(cls, root, info, **kwargs):
        user = info.context.user

        if not user.is_verified:
            raise UserNotVerified

        if kwargs.get("is_mobile", False) and user.role.name not in (
            DefaultSystemRole.CLIENT,
            DefaultSystemRole.SALESPERSON,
            DefaultSystemRole.DELIVERY_DRIVER,
        ):
            raise PermissionDenied

        cls.register_fmc_device(
            user_id=user.id,
            firebase_registration_id=kwargs.get("firebase_registration_id"),
            device_id=kwargs.get("device_id"),
            device_type=kwargs.get("device_type"),
        )

        user.session_version += 1
        user.save(update_fields=["session_version"])

        return cls(user=user)


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


class ResetPasswordInput(graphene.InputObjectType):
    new_password = graphene.String(required=True)


class ResetPassword(graphene.Mutation):
    user = graphene.Field(UserNode)

    class Arguments:
        input = ResetPasswordInput(required=True)

    @login_required
    def mutate(self, info, input: ResetPasswordInput):
        try:
            user = AuthService.reset_password_after_recovery(
                email=info.context.user.email, new_password=input.new_password
            )
        except ValidationError as exc:
            raise ValidationGraphQLError(fields=exc.message_dict)

        return ResetPassword(user=user)


class Mutation(graphene.ObjectType):
    login = Login.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    revoke_token = graphql_jwt.Revoke.Field()
    register_client = RegisterClient.Field()
    request_auth_code = RequestAuthCode.Field()
    verify_auth_code = VerifyAuthCode.Field()
    reset_password = ResetPassword.Field()


schema = graphene.Schema(mutation=Mutation)
