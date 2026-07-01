from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from graphene_file_upload.django import FileUploadGraphQLView

from config.views import DownloadSchemaView, HealthCheckView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("graphql/", csrf_exempt(FileUploadGraphQLView.as_view(graphiql=True))),
    path("graphql/schema.json", DownloadSchemaView.as_view(), name="graphql-schema"),
    path("healthcheck/", HealthCheckView.as_view(), name="healthcheck"),
]
