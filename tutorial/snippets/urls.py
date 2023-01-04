from django.urls import path, include
from rest_framework.routers import DefaultRouter

from tutorial.snippets import views

breakpoint()
router = DefaultRouter()
router.register(r'snippets', views.SnippetViewSet, basename='snippet')
router.register(r'urers', views.UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls))
]
