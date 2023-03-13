import json
from modulefinder import ReplacePackage
from tkinter import PAGES
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import authentication, permissions
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework import viewsets
from django.shortcuts import get_object_or_404, redirect
from rest_framework.parsers import JSONParser, BaseParser
from rest_framework.renderers import JSONRenderer
from rest_framework import serializers
from yaml import serialize
from tutorial.playground.models import Blocklist, HighSchore, Profile, Purchase

from tutorial.playground.serializers import BookSerializer, HighScoreSerializer, ProfileSerializer, PurchaseSerializer, UserSerializer
from tutorial.playground.auth import ExampleAuthentication

from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework.throttling  import UserRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.versioning import (
    NamespaceVersioning,
    QueryParameterVersioning,
    AcceptHeaderVersioning,
    HostNameVersioning,
    BaseVersioning,
    URLPathVersioning
)
from rest_framework.negotiation import BaseContentNegotiation
from rest_framework.metadata import BaseMetadata
from rest_framework.reverse import reverse, reverse_lazy
from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.renderers import TemplateHTMLRenderer


from datetime import datetime


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, MyError):
        return Response('666')

    if response is not None:
        response.data['status_code'] = response.status_code

    return response


class MinimalMetadata(BaseMetadata):
    def determine_metadata(self, request, view):
        return {
            "name": view.get_view_name(),
            "description": view.get_view_description()
        }


class IgnoreClientContentNegotiation(BaseContentNegotiation):

    def select_parser(self, request, parsers):
        """
        Select the first perser in the .parser_classes list
        """
        return parsers[1]

    def select_renderer(self, request, renderers, format_suffix=None):
        """
        Select the first renderer in the .renderer_classes list
        """
        return (renderers[0], renderers[0].media_type)


class XAPIVersionScheme(BaseVersioning):
    def determine_version(self, request, *args, **kwargs):
        return request.META.get('HTTP_X_API_VERSION', None)


class CustomPaagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 10000

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
            },
            'count': self.page.paginator.count,
            'results': data,
        })



class IsOwnerFilterBackend(filters.BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(pk=request.user.pk)



class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})

        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
        })

class MyError(Exception): ...


class ProfileDetail(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'profile_detail.html'

    def get(self, request, pk):
        profile = get_object_or_404(Profile, pk=pk)
        serializer = ProfileSerializer(profile)
        return Response({'serializer': serializer, 'profile': profile})

    def post(self, request, pk):
        profile = get_object_or_404(Profile, pk=pk)
        serializer = ProfileSerializer(profile, data=request.data)
        if not serializer.is_valid():
            return Response({'serializer': serializer, 'profile': profile})
        serializer.save()
        return redirect('profile-list')


class ProfileList(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'profile_list.html'

    def get(self, request):
        queryset = Profile.objects.all()
        return Response({'profiles': queryset})


class ErrorView(APIView):

    def get(self, reuqest):

        raise MyError()

        return Response('OK')


class APIRoot(APIView):
    # metadata_class = MinimalMetadata

    def get(self, request, format=None):
        return Response(reverse("version", request=request))


class NoNegotiationView(APIView):
    """
    An exemple view that does not perform content negotiation
    """
    content_negotiation_class = IgnoreClientContentNegotiation

    def get(self, request):
        return Response({
            'accepted media type': request.accepted_renderer.media_type
        })




class APIVersion(APIView):

    versioning_class = URLPathVersioning
    def get(self, request, version):
        return Response(request.version)


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPaagination
    # authentication_classes = [ExampleAuthentication]
    # filter_backends = [filters.OrderingFilter]
    # filter_backends = [IsOwnerFilterBackend]
    # filterset_fields = ['username', 'email']
    # search_fields = ['username', 'email']
    # ordering_fields = ['username']



class PurchaseList(generics.ListAPIView):
    # permission_classes = [IsAuthenticated]
    # authentication_classes = [ExampleAuthentication]
    serializer_class = PurchaseSerializer

    # def get_queryset(self):
    #     username = self.kwargs['username']
    #     return Purchase.objects.filter(user__username=username)

    def get_queryset(self):
        queryset = Purchase.objects.all()
        username = self.request.query_params.get('username')
        if  username is not None:
            queryset = queryset.filter(user__username=username)
        return queryset


class ThrottleView(APIView):
    throttle_classes = [UserRateThrottle]

    def get(self, request, format=None):
        content = {
            "status": "request was permitted"
        }
        return Response(content)


class PostView(APIView):
    @method_decorator(cache_page(60))
    @method_decorator(vary_on_headers('X-MEUCACHE'))
    def get(self, request, format=None):
        content = {
            'title': 'Post title',
            "body": datetime.now(),
        }
        return Response(content)


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class BlockListPermission(BasePermission):
    """
    Global permission check for blocked Ips
    """

    def has_permission(self, request, view):
        ip_addr = request.META['REMOTE_ADDR']
        blocked = Blocklist.objects.filter(ip_addr=ip_addr).exists()
        return not blocked



class ExampleView(APIView):
    # permission_classes = [IsAuthenticated|ReadOnly]
    permission_classes = [BlockListPermission]

    def get(self, request, format=None):
        ip_addr = request.META['REMOTE_ADDR']
        Blocklist.objects.update_or_create(ip_addr=ip_addr)
        content = {
            'status': 'request was permitted'
        }
        return Response(content)



# class ExampleView(APIView):
#     # authentication_classes = [SessionAuthentication, BasicAuthentication, TokenAuthentication,  ExampleAuthentication]
#     authentication_classes = [ExampleAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request, format=None):
#         content = {
#             'user': str(request.user),
#             'auth': str(request.auth),
#         }
#         return Response(content)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def example_view(request, format=None):
    content = {
        "user": str(request.user),
        "auth": str(request.auth)
    }
    return Response(content)


# class UserSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     username = serializers.CharField(max_length=100)


# class Comment:
#     def __init__(self, email, content, created=None):
#         self.email = email
#         self.content = content
#         self.created = created or datetime.now()


# class CommentSerializer(serializers.Serializer):
#     user = UserSerializer()
#     email = serializers.EmailField()
#     content = serializers.CharField(max_length=200)
#     created = serializers.DateTimeField(required=False)

#     def create(self, validated_data):
#         return Comment(**validated_data)

#     def update(self, instance, validated_data):
#         instance.email = validated_data.get('email', instance.email)
#         instance.content = validated_data.get('content', instance.content)
#         instance.created = validated_data.get('created', instance.created)
#         return instance

#     def validate_content(self, value):

#         if 'django' == value:
#             raise serializers.ValidationError("Erro atributo")

#         return value

#     def validate(self, data):
#         if data['content'] == 'django2':
#             raise serializers.ValidationError("Error object-level")
#         return data


# class TestSerizalizer(APIView):

#     def post(self, request):
#         serializer = CommentSerializer(data=request.data)

#         serializer.is_valid(raise_exception=True)

#         return Response(serializer.data)


#     def get(self, request):

#         books = [
#             {'title': 'oi1', 'author': 'au1'},
#             {'title': 'oi2', 'author': 'au2'},
#         ]

#         serializer = BookSerializer(data=books, many=True)

#         serializer.is_valid()

#         serializer.save()
#         return Response(serializer.data)


# @api_view(['GET'])
# def high_score(request, pk):
#     instance = HighSchore.objects.get(pk=pk)
#     serializer = HighScoreSerializer(instance)
#     return Response(serializer.data)


# @api_view(['GET'])
# def all_high_scores(request):

#     queryset = HighSchore.objects.order_by('-score')
#     serializer = HighScoreSerializer(queryset, many=True)
#     return Response(serializer.data)


# @api_view(['POST'])
# def high_score_create(request):
#     serializer = HighScoreSerializer(data=request.data)
#     serializer.is_valid(raise_exception=True)
#     serializer.save()
#     return Response(serializer.data)



# class UserCountView(APIView):
#     """
#     A view that retuns the count of  active users is JSON.
#     """

#     renderer_classes = [JSONRenderer]

#     def get(self, request, format=None):
#         user_count = User.objects.filter().count()
#         content = {'user_count': user_count}
#         return Response(content)

# class MinhaView(APIView):

#     renderer_classes = [JSONRenderer]
#     parser_classes = [JSONParser]

#     def post(self, request):
#         return  Response({'received data': request.data})


# class MeuParser(BaseParser):
#     media_type = 'application/json'
#     def parse(self, stream, media_type=None, parser_context=None):
#         return stream.read()


# class ExampleView(APIView):
#     """
#     A view taht can accept POST requests with JSON content.
#     """

#     parser_classes = [MeuParser]

#     def post(self, request, format=None):
#         data = request.data
#         return Response({'received data': data})


# class UserViewSet(viewsets.ViewSet):
#     """
#     A simple ViewSet fot listing or retrieving users.
#     """

#     def list(self, request):
#         queryset = User.objects.all()
#         serializer = UserSerializer(queryset, many=True)
#         return Response(serializer.data)

#     def retrieve(self, request, pk=None):
#         queryset = User.objects.all()
#         user = get_object_or_404(queryset, pk=pk)
#         serializer = UserSerializer(user)
#         return Response(serializer.data)


# class MultipleFieldLookupMixin:
#     def get_object(self):
#         queryset = self.get_queryset()
#         queryset = self.filter_queryset(queryset)
#         filter = {}

#         for field in self.lookup_fields:
#             if self.kwargs.get(field):
#                 filter[field] = self.kwargs[field]

#         obj = get_object_or_404(queryset, **filter)
#         self.check_object_permissions(self.request, obj)
#         return obj


# class Users(MultipleFieldLookupMixin, generics.RetrieveUpdateDestroyAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     lookup_fields = ['username', 'id']



# class UserList(generics.ListCreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     # permission_classes = [IsAdminUser]
#     lookup_field = 'name'

#     def list(self, request):
#         queryset = self.get_queryset()
#         serializer = UserSerializer(queryset, many=True)
#         return Response(serializer.data)



# class ListUsers(APIView):
#     """
#     View  to list all users in the system.

#     * Requires token authentication
#     * Only admin usrers are able to acesse this view
#     """

#     authentication_classes = [authentication.TokenAuthentication]
#     permission_classes = [permissions.IsAdminUser]

#     def get(self, request, format=None):
#         """
#         Return a list of all users
#         """

#         usernames = [user.username for user in User.objects.all()]

#         return Response(usernames)


# from rest_framework.decorators import api_view, throttle_classes
# from rest_framework.throttling import UserRateThrottle

# class OncePerDayUserThrottle(UserRateThrottle):
#     rate = '1/day'

# @api_view(['GET'])
# @throttle_classes([OncePerDayUserThrottle])
# def view(request):
#     return Response({"message": "Hello for today! See you tomorrow!"})
