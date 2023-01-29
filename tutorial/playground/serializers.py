from rest_framework import serializers
from django.contrib.auth.models import User

from tutorial.playground.models import HighSchore


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class UserSerializerUrl(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class BookSerializer(serializers.Serializer):
    title = serializers.CharField()
    author = serializers.CharField()

    def create(self, validated_data):
        print('create', validated_data)
        return validated_data


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self,  validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class HighScoreSerializer(serializers.BaseSerializer):

    def to_internal_value(self, data):
        score = data.get('score')
        player_name = data.get('player_name')

        if not score:
            raise serializers.ValidationError({
                'score': 'This field is required'
            })

        if not player_name:
            raise serializers.ValidationError({
                'player_name': 'This field is required'
            })

        if len(player_name) > 10:
            raise serializers.ValidationError({
                'player_name': 'May not be more than 10 characters.'
            })

        return {
            'score': int(score),
            'player_name': player_name
        }


    def to_representation(self, instance):
        return {
            'score': instance.score,
            'player_name': instance.player_name
        }

    def create(self, validated_data):
        return HighSchore.objects.create(**validated_data)
