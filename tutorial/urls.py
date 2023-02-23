from rest_framework import routers
from django.contrib import admin
from django.urls import path, include

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
]
