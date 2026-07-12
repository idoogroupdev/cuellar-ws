import graphene
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from graphene_django import DjangoObjectType

from branches.models import Category
from branches.services.category_service import CategoryService
from utils.decorators import permission_required, staff_member_required
from utils.exceptions import ValidationGraphQLError
from utils.graphql import BaseConnection, ConnectionField


class CategoryNode(DjangoObjectType):
    id = graphene.ID(source="pk", required=True)

    class Meta:
        model = Category
        exclude = []
        filter_fields = {
            "is_active": ["exact"],
            "name": ["icontains"],
        }
        interfaces = (graphene.relay.Node,)
        connection_class = BaseConnection


class CreateCategoryInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    sort_order = graphene.Int(required=False)
    is_active = graphene.Boolean(default_value=True)


class CreateCategory(graphene.Mutation):
    category = graphene.Field(CategoryNode)

    class Arguments:
        input = CreateCategoryInput(required=True)

    @staff_member_required
    @permission_required(Category, "add")
    def mutate(self, info, input: CreateCategoryInput):
        try:
            category = CategoryService.create(
                name=input.name,
                sort_order=input.sort_order or 0,
                is_active=input.is_active,
            )
        except ValidationError as exc:
            raise ValidationGraphQLError(fields=exc.message_dict)
        return CreateCategory(category=category)


class UpdateCategoryInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
    name = graphene.String(required=False)
    sort_order = graphene.Int(required=False)
    is_active = graphene.Boolean(required=False)


class UpdateCategory(graphene.Mutation):
    category = graphene.Field(CategoryNode)

    class Arguments:
        input = UpdateCategoryInput(required=True)

    @staff_member_required
    @permission_required(Category, "change")
    def mutate(self, info, input: UpdateCategoryInput):
        category = Category.objects.filter(pk=input.id).first()

        if not category:
            message = _("Category not found.")
            raise ValidationGraphQLError(fields={"id": [message]}, message=message)

        try:
            kwargs = dict(input.items())
            kwargs.pop("id", None)

            category = CategoryService.update(category, **kwargs)
        except ValidationError as exc:
            raise ValidationGraphQLError(fields=exc.message_dict)

        return UpdateCategory(category=category)


class ReorderCategoryInput(graphene.InputObjectType):
    ids = graphene.List(graphene.Int, required=True)


class ReorderCategory(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        input = ReorderCategoryInput(required=True)

    @staff_member_required
    @permission_required(Category, "change")
    def mutate(self, info, input: ReorderCategoryInput):
        try:
            CategoryService.reorder(input.ids)
        except ValidationError as exc:
            raise ValidationGraphQLError(fields=exc.message_dict)
        return ReorderCategory(success=True)


class Query(graphene.ObjectType):
    all_categories = ConnectionField(CategoryNode)

    @staff_member_required
    @permission_required(Category, "view")
    def resolve_all_categories(self, info, **kwargs):
        return Category.objects.all()


class Mutation(graphene.ObjectType):
    create_category = CreateCategory.Field()
    update_category = UpdateCategory.Field()
    reorder_category = ReorderCategory.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
