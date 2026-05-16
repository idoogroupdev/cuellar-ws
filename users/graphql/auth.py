import graphene
import graphql_jwt
from django.core.exceptions import ValidationError

from roles.models import DefaultSystemRole
from users.graphql.user import UserNode
from users.services.user_service import UserService
from utils.exceptions import ValidationGraphQLError


class RegisterUserInput(graphene.InputObjectType):
    email = graphene.String(required=True)
    password = graphene.String(required=True)


class RegisterClient(graphene.Mutation):
    user = graphene.Field(UserNode)

    class Arguments:
        input = RegisterUserInput(required=True)

    def mutate(self, info, input: RegisterUserInput):
        try:
            user = UserService.create_user_with_roles(
                email=input.email.lower(),
                password=input.password,
                role_names=[DefaultSystemRole.CLIENT],
            )
        except ValidationError as exc:
            raise ValidationGraphQLError(fields=exc.message_dict)

        return RegisterClient(user=user)


class Mutation(graphene.ObjectType):
    login = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    revoke_token = graphql_jwt.Revoke.Field()
    register_client = RegisterClient.Field()


schema = graphene.Schema(mutation=Mutation)
