import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import authentication, permissions
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from rest_framework.parsers import JSONParser, BaseParser
from rest_framework.renderers import JSONRenderer
from rest_framework import serializers
from tutorial.playground.models import HighSchore

from tutorial.playground.serializers import BookSerializer, HighScoreSerializer, UserSerializer
from tutorial.playground.auth import ExampleAuthentication

from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token


from datetime import datetime


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

class ExampleView(APIView):
    # authentication_classes = [SessionAuthentication, BasicAuthentication, TokenAuthentication,  ExampleAuthentication]
    authentication_classes = [ExampleAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        content = {
            'user': str(request.user),
            'auth': str(request.auth),
        }
        return Response(content)

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
