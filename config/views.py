from django.http import JsonResponse
from django.views import View
from graphene_django.settings import graphene_settings


class DownloadSchemaView(View):
    def get(self, request, *args, **kwargs):
        schema = graphene_settings.SCHEMA
        schema_dict = {"data": schema.introspect()}
        return JsonResponse(
            schema_dict,
            headers={"Content-Disposition": 'attachment; filename="schema.json"'},
        )
