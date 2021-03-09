from rest_framework import serializers
from .models import *

###############################################################################
#
# Serializer übersetzen Django Models in JSON und JSON in Django Models
# Dient zur Kommunikation von Front- und Backend
#
###############################################################################
class EventSerializerGet(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = ('id', 'event_name', 'event_is_current', 'event_url_thread', 'event_url_posting', 'event_album')

class EventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = ('id', 'event_name', 'event_is_current', 'event_url_thread', 'event_url_posting')

class ImgurSerializer(serializers.ModelSerializer):

    class Meta:
        model = Imgur
        fields = ('pin',)

class PlatformSerializer(serializers.ModelSerializer):

    class Meta:
        model = Platform
        fields = ('id', 'platform_name', 'platform_image', 'platform_type')

class TrailerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Trailer
        fields = ('id', 'game_id', 'trailer_name', 'trailer_url', 'trailer_date', 'DeltaYesNo')

class GameSerializerGet(serializers.ModelSerializer):


    ###########################################################################
    #
    # Nur-Lesen Many-to-Many-Relation
    #
    ###########################################################################
    game_platforms = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='platform_name'
    )

    ###########################################################################
    #
    # Nur-Lesen Many-to-Many-Relation
    #
    ###########################################################################
    game_events = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='event_name'
    )

    ###########################################################################
    #
    # Nur-Lesen Many-to-One Relation
    #
    ###########################################################################
    game_trailers = TrailerSerializer(many=True, read_only=True)


    ###########################################################################
    #
    # Nur-Lesen One-to-One Relation
    #
    ###########################################################################
    # game_keyart = KeyartSerializer(read_only=True)

    class Meta:
        model = Game
        fields = ('id',
                  'game_name',
                  'game_release_date',
                  'game_platforms',
                  'game_events',
                  'game_trailers',
                  'game_keyart',
                  'DeltaYesNo',
                  'game_description',
                  'game_production',
                  )

class GameSerializerPost(serializers.ModelSerializer):

    class Meta:
        model = Game
        fields = ('id', 'game_name', 'DeltaYesNo')

class GameSerializerPut(serializers.ModelSerializer):

    ###########################################################################
    #
    # Updatefähige Many-to-Many-Relation
    #
    ###########################################################################
    game_platforms = serializers.SlugRelatedField(
        many=True,
        slug_field='platform_name',
        queryset=Platform.objects.all()
    )

    class Meta:
        model = Game
        fields = ('id',
                  'game_name',
                  'game_release_date',
                  'game_platforms',
                  'game_keyart',
                  'DeltaYesNo',
                  'game_description',
                  'game_production',
                  )

        extra_kwargs = {
                'game_release_date': {
                    'required': False,
                    'allow_blank': True,
                 },
                 'game_description': {
                     'required': False,
                     'allow_blank': True,
                  },
                  'game_production': {
                      'required': False,
                      'allow_blank': True,
                   },

             }
