from dataclasses import field, fields
import time
import re
from wsgiref.validate import validator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User

from tutorial.playground.models import Album, CustomerReportRecord, DataPoint, HighSchore, Profile, Purchase, Track
from rest_framework.validators import UniqueValidator

from tutorial.playground import validators


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'name',)

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


class Color:
    """
    Color reprensented in the RGB colorspace
    """

    def __init__(self, red, green, blue):
        assert(red >= 0 and green >= 0 and blue >=0)
        assert(red < 256 and green < 256 and blue < 256)
        self.red, self.green, self.blue = red, green, blue


class ColorField(serializers.Field):
    """
    Color objects are serialized into 'rgb(#, #, #)' notation.
    """

    default_error_messages = {
       'incorrect_type': 'Incorrect type. Expected a string, but got {input_type}',
        'incorrect_format': 'Incorrect format. Expected `rgb(#,#,#)`.',
        'out_of_range': 'Value out of range. Must be between 0 and 255.'
    }

    def to_representation(self, value):
        return "rgb(%d, %d, %d)" % (value.red, value.green, value.blue)

    # def to_internal_value(self, data):

    #     if not isinstance(data, str):
    #         msg = 'Incorrect type. Expected a string, but got %s'
    #         raise ValidationError(msg % type(data).__name__)

    #     if not re.match(r'^rgb\([0-9]+,[0-9]+,[0-9]+\)$', data):
    #         raise ValidationError('Incorrect format. Expected `rgb(#,#,#)`.')

    #     data =  data.strip('rgb(').rstrip(')')
    #     red, green, blue = [int(col) for col in data.split(',')]

    #     if any([col > 255 or col < 0 for col in (red, green, blue)]):
    #         raise ValidationError('Value out of range. Must be between 0 and 255.')

    #     return Color(red, green, blue)

    def to_internal_value(self, data):

        if not isinstance(data, str):
            self.fail('incorrect_type', input_type=type(data).__name__)

        if not re.match(r'^rgb\([0-9]+,[0-9]+,[0-9]+\)$', data):
            self.fail('incorrect_format')

        data =  data.strip('rgb(').rstrip(')')
        red, green, blue = [int(col) for col in data.split(',')]

        if any([col > 255 or col < 0 for col in (red, green, blue)]):
            self.fail('out_of_range')

        return Color(red, green, blue)



class ColorSerializer(serializers.Serializer):

    color = ColorField()


class ClassNameField(serializers.Field):

    def get_attribute(self, instance):
        return instance

    def  to_representation(self, value):
        """
        Serialize the value's class name
        """
        return value.__class__.__name__

class ClassNameSerializer(serializers.Serializer):

    class_name = ClassNameField()


class CoordinateField(serializers.Field):


    def to_representation(self, value):
        ret = {
            "x": value.x_coordinate,
            "y": value.y_coordinate
        }
        return ret

    def to_internal_value(self, data):
        ret = {
            "x_coordinate": data["x"],
            "y_coordinate": data["y"]
        }
        return ret


class DataPointSerializer(serializers.ModelSerializer):
    coordinates = CoordinateField(source="*")

    class Meta:
        model = DataPoint
        fields  = ['label', 'coordinates']


class NestedCoordinateSerializer(serializers.Serializer):
    x = serializers.IntegerField(source='x_coordinate')
    y = serializers.IntegerField(source='y_coordinate')


class DataPointSerializer(serializers.ModelSerializer):
    coordinates = NestedCoordinateSerializer(source='*')

    class Meta:
        model = DataPoint
        fields = ['label', 'coordinates']


class AlbumSerializer(serializers.ModelSerializer):
    # tracks = serializers.StringRelatedField(many=True)
    # tracks = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    tracks = serializers.SlugRelatedField(many=True, read_only=True, slug_field='title')

    class Meta:
        model = Album
        fields = ['album_name', 'artist', 'tracks']


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = ['order', 'title', 'duration']


class AlbumSerializerV2(serializers.ModelSerializer):
    tracks = TrackSerializer(many=True, read_only=True)

    class Meta:
        model = Album
        fields = ['album_name', 'artist', 'tracks']


class AlbumSerializerV3(serializers.ModelSerializer):
    tracks = TrackSerializer(many=True)

    class Meta:
        model = Album
        fields = ['album_name', 'artist', 'tracks']

    def create(self, validated_data):
        tracks_data = validated_data.pop('tracks')
        album = Album.objects.create(**validated_data)

        tracks_list =[ Track(album=album, **track_data) for track_data in tracks_data]

        Track.objects.bulk_create(tracks_list)

        return album


class TrackListingField(serializers.RelatedField):

    def to_representation(self, value):
        duration = time.strftime('%M:%S', time.gmtime(value.duration))
        return f"Track {value.order}: {value.title} ({duration})"


class AlbumSerializerV4(serializers.ModelSerializer):
    tracks = TrackListingField(many=True, read_only=True)

    class Meta:
        model = Album
        fields = ['album_name', 'artist', 'tracks']


class CustimerReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerReportRecord
        fields = '__all__'


class TestMyValidators(serializers.Serializer):

    number = serializers.IntegerField(validators=[validators.even_number])
    number2 = serializers.IntegerField(validators=[validators.MultipleOf(base=5)])


class PurchaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Purchase
        fields = ('user',)
