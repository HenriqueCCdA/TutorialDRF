from django.urls import path
from rest_framework.routers import DefaultRouter, SimpleRouter
from rest_framework.authtoken.views import obtain_auth_token

from . import views

# user_list = views.UserViewSet.as_view({'get' : 'list'})
# user_detail = views.UserViewSet.as_view({'get' : 'retrieve'})

# router = DefaultRouter()
# router.register(r'rota1', views.UserViewSet, basename='user')

# urlpatterns = router.urls

urlpatterns = [
    # path('', views.ExampleView.as_view())
    # path('', views.MinhaView.as_view())
    # path('', views.TestSerizalizer.as_view())
    # path('high-score/<int:pk>/', views.high_score),
    # path('high-score-list/', views.all_high_scores),
    # path('high-score-add/', views.high_score_create)
    path('auth/', views.ExampleView.as_view()),
    path('api-token-auth/', views.CustomAuthToken.as_view())
]

# urlpatterns = [
#     path('', views.index),
#     path('list_user/', views.ListUsers.as_view()),
#     path('', views.view),
#     path('', views.UserList.as_view()),
#     path('<int:id>/<username>', views.Users.as_view())
#     path('', user_list),
#     path('<int:pk>', user_detail)
# ]
