from rest_framework import routers
from django.contrib import admin
from django.urls import path, include
from  rest_framework.schemas import get_schema_view

from tutorial.quickstart import views

router = routers.DefaultRouter()
router.register('users', views.UserViewSet)
router.register('groups', views.GroupViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', include(router.urls)),
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # path('', include('tutorial.snippets.urls')),
    path('playground/', include('tutorial.playground.urls')),
    path('<version>/playground/', include('tutorial.playground.urls')),
    path('openapi/', get_schema_view(
        title="Your Project",
        description="API for all things …",
        version="1.0.0"
    ), name='openapi-schema'),
]
