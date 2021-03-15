from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import views
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import *
from .models import *
from bbcapi.imgur import *
from bbcapi.constants import *
###############################################################################
#
# API-View für Events.
#
###############################################################################
@api_view(['GET', 'POST'])
def EventView(request):


    ###########################################################################
    #
    # GET wird benutzt, wenn der User Daten anfragt
    #
    ###########################################################################
    if request.method == 'GET':
        events = Event.objects.all()

        serializer = EventSerializerGet(
            events,
            context={'request': request},
            many = True
        )

        return Response(serializer.data)

    ###########################################################################
    #
    # POST wird benutzt, wenn der User Daten erstellt
    #
    ###########################################################################
    elif request.method == 'POST':
        serializer = EventSerializer(data=request.data)

        if serializer.is_valid():

            serializer.save()

            ###################################################################
            #
            # Hole nach dem Speichern die ID des gerade angelegten
            # Events und öffne damit ein Recordset, mit dem ein
            # neues Imgur Album angelegt wird
            #
            ###################################################################
            event = Event.objects.get(id=str(serializer.data["id"]))

            ###################################################################
            #
            # Es kann nur ein Event aktuell sein
            #
            ###################################################################
            check_for_current(event)

            ###################################################################
            #
            # Lege ein Album zum Event an
            #
            ###################################################################

            album = imgurCreateAlbum(event.event_name)

            if album is not None:
                event.event_album = album
                event.save()

                return Response(status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


###############################################################################
#
# Es kann immer nur ein Event aktuell sein. Falls das übergebene
# Event aktuell ist, entferne die Flag vom vorherigen Event.
#
###############################################################################
def check_for_current(event):

    if event.event_is_current:
        old_event = Event.objects.filter(event_is_current = True).exclude(id = event.id)

        for record in old_event:
            record.event_is_current = False;
            record.save()


###############################################################################
#
# API-View für Eventdetails.
#
###############################################################################
@api_view(['PUT', 'DELETE', 'GET'])
def EventDetailView(request, pk):
    try:
        events = Event.objects.get(pk=pk)
    except Event.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    ###########################################################################
    #
    # PUT wird benutzt, wenn der User Daten ändert
    #
    ###########################################################################
    if request.method == 'PUT':
        serializer = EventSerializer(
            events,
            data=request.data,
            context={'request': request}
            )
        if serializer.is_valid():
            serializer.save()

            ###################################################################
            #
            # Hole das gerade gespeicherte Objekt und überprüfe, ob es
            # aktuell geschaltet ist
            #
            ###################################################################
            event = Event.objects.get(id=str(serializer.data["id"]))
            check_for_current(event)

            ###################################################################
            #
            # HTTP 204 No Content bedeutet, ein Request war erfolgreich, aber
            # der Client muss nicht auf eine andere Seite navigieren.
            #
            ###################################################################
            return Response(status.HTTP_204_NO_CONTENT)

        return Response (status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':

        album = events.event_album

        if album:
            imgureDeleteAlbum(album)

        events.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    elif request.method == 'GET':
        events = Event.objects.get(pk=pk)
        serializer = EventSerializerGet(
            events,
            context={'request': request},
        )

        return Response(serializer.data)

###############################################################################
#
# API View für den BBCode Export
#
##############################################################################
@api_view(['GET'])
def BbcodeView(request, delta=False):
    # BBCODE_TABLE_TOP
    # BBCODE_TABLE_BOTTOM
    # BBCODE_EMPTY_ROW

    if request.method == 'GET':

        bbcode = ''

        delta = request.GET['delta']

        rows = [] #Enthält jedes Spiel
        formatted_rows = [] #Enthält jedes Spiel in formatiertem BBCode

        event = Event.objects.get(event_is_current=True)
        games = Game.objects.filter(game_events = event.id)

        ###########################################################################
        #
        # Es gibt zwei Modi: Poste ALLE Spiele des Events oder poste nur die Spiele,
        # die ein Update erhalten haben. Falls Flag delta gesetzt, filtere alle
        # Spiele und reduziere auf die mit Update
        #
        ###########################################################################
        if delta=="true":
            games = games.filter(DeltaYesNo=True)

        for game in games.order_by('game_name'):
            #######################################################################
            #
            # Gehe jedes Spiel im Queryset durch und speichere eine formatierte
            # Variante in game_row
            #
            #######################################################################

            game_row = []
            game_header = []
            game_desc = []

            # Grundlegende Informationen zum Spiel
            game_name = game.game_name
            game_id = game.id
            game_release = game.game_release_date
            game_description = game.game_description
            game_production = game.game_production

            # Keyart in kleiner Größe
            keyart = game.game_keyart
            url, suffix = keyart.rsplit('.', 1)
            keyart_url = '{}m.{}'.format(url, suffix)

            # Plattformen, in drei Reihen formatiert
            game_platforms = platformsinthree(game)

            # ALle Trailer zum Spiel holen
            game_trailers = Trailer.objects.filter(game_id = game_id).order_by('-DeltaYesNo', '-trailer_date')
            all_trailer = []

            for trailer in game_trailers:

                # Wenn Modus Delta und Trailer hat Flag DeltaYesNo=True => Trailer in Rot markieren
                new = '[color=#FF0000]NEU: [/color]' if delta=="true" and trailer.DeltaYesNo else ''

                # Liste aller Trailer als formatierter BBCode
                all_trailer.append('[url={}]{}{}[/url]\n'.format(trailer.trailer_url, new, trailer.trailer_name))

            # Sammle alle Spieldaten in game_row

            game_row.append('[img]{}[/img]'.format(keyart_url))
            game_row.append(' ')
            game_row.append('{}\n\n{}\n{}\n{}\n{}'.format('[u]' + game_name + '[/u]', '→ ' + game_description, '→ ' + game_release, '→ ' + game_production, BBCODE_EMPTY_ROW))#"".join(all_trailer), BBCODE_EMPTY_ROW))
            game_row.append(' ')
            game_row.append('{}\n{}\n'.format("".join(all_trailer), BBCODE_EMPTY_ROW))
            game_row.append(' ')
            game_row.append(game_platforms)

            # Hänge Spieldaten an

            rows.append('[tr]')
            for header in game_header:
                rows.append('[table=0][align=left]{}[/align][/table]\n'.format(''.join(header)))
            rows.append('[/tr]\n')

            rows.append('[tr]')
            for desc in game_desc:
                rows.append('[table=0][align=left]{}[/align][/table]\n'.format(''.join(desc)))
            rows.append('[/tr]\n')

            rows.append('[tr]')
            for row in game_row:
                rows.append('[table=0][align=left]{}[/align][/table]\n'.format(''.join(row)))
            rows.append('[/tr]\n')
            #rows.append('[tr][th=7] [/th][/tr]\n')

        # Füge alle Spiele zusammen
        bbcode = '{}{}{}'.format(BBCODE_TABLE_TOP, ''.join(rows), BBCODE_TABLE_BOTTOM)

        return Response(bbcode)


    return Response(status=status.HTTP_204_NO_CONTENT)

def platformsinthree(current_game):
    # For current game, look up all the platforms
    current_platforms = current_game.game_platforms.all().order_by('platform_name')

    # Write down every platform
    blank_image_url= "https://i.imgur.com/KOn6BRI.png"
    count = 0

    all_platforms  = '[tblo]\n[tbody][tr]'
    for j in range(current_platforms.count()):

        platform_url = current_platforms.values()[j]['platform_image']
        #url_split = platform_url.rsplit('.',1)
        #platform_url = url_split[0] + url_split[1]

        all_platforms = (all_platforms +
        '[table=0][img]' +
        platform_url +
        '[/img][/table]\n'
        )

        #if j == 1 or j == 3 or j == 5 or j == 7:
        if j == 2 or j == 5 or j == 8 or j == 11:
            all_platforms = all_platforms + '[/tr][tr]'

        count = count + 1

    #if count % 2 != 0:
    if count == 2 or count == 5 or count == 8 or count == 11:
        all_platforms = (all_platforms +
        '[table=0][img]' +
        blank_image_url +
        '[/img][/table]\n'
        )

    if count == 1 or count == 4 or count == 7 or count == 10:
        all_platforms = (all_platforms +
        '[table=0][img]' +
        blank_image_url +
        '[/img][/table]' +
        '[table=0][img]' +
        blank_image_url +
        '[/img][/table]\n'
        )

    all_platforms = all_platforms #+ '[/tr]'#'[/tbody]\n[/tblo]'

    return all_platforms


###############################################################################
#
# API View zum Imgur-login
#
###############################################################################
@api_view(['GET'])
def ImgurGet(request):

    if request.method == 'GET':

        client_id = CLIENT
        client_secret = SECRET
        client = ImgurClient(client_id, client_secret)
        authorization_url = client.get_auth_url('pin')

        return Response(authorization_url)

    return Response(status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def ImgurPost(request):

    if request.method == 'POST':

        client_id = CLIENT
        client_secret = SECRET
        client = ImgurClient(client_id, client_secret)

        pin = request.data['pin']

        credentials = client.authorize(pin, 'pin')
        client.set_user_auth(credentials['access_token'], credentials['refresh_token'])

        imgur = Imgur()
        imgur.imgur_access_token = credentials['access_token']
        imgur.imgur_refresh_token = credentials['refresh_token']
        imgur.current_login = True

        check_for_current = Imgur.objects.filter(current_login="True")

        if check_for_current:

            for record in check_for_current:
                record.current_login = False
                record.save()

        imgur.save()


        return Response(status = status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
def PlatformView(request):


    ###########################################################################
    #
    # GET wird benutzt, wenn der User Daten anfragt
    #
    ###########################################################################
    if request.method == 'GET':
        platforms = Platform.objects.all()

        serializer = PlatformSerializer(
            platforms,
            context={'request': request},
            many = True
        )

        return Response(serializer.data)

    ###########################################################################
    #
    # POST wird benutzt, wenn der User Daten erstellt
    #
    ###########################################################################
    elif request.method == 'POST':
        serializer = PlatformSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            platform = Platform.objects.get(id=str(serializer.data["id"]))
            platform_image = platform.platform_image

            platform_image = imgurUploadImage(platform_image, True)
            platform.platform_image = platform_image['link']
            platform.save()

            return Response(status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'DELETE', 'GET'])
def PlatformDetailView(request, pk):
    try:
        platforms = Platform.objects.get(pk=pk)
    except platforms.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    ###########################################################################
    #
    # PUT wird benutzt, wenn der User Daten ändert
    #
    ###########################################################################
    if request.method == 'PUT':
        serializer = PlatformSerializer(
            platforms,
            data=request.data,
            context={'request': request}
            )
        if serializer.is_valid():
            old_platform_image = platforms.platform_image
            serializer.save()
            new_platform_image = platforms.platform_image

            if not old_platform_image == new_platform_image:

                new_platform_image = imgurUploadImage(new_platform_image, True)
                platforms.platform_image = new_platform_image['link']
                platforms.save()

            ###################################################################
            #
            # HTTP 204 No Content bedeutet, ein Request war erfolgreich, aber
            # der Client muss nicht auf eine andere Seite navigieren.
            #
            ###################################################################
            return Response(status.HTTP_204_NO_CONTENT)

        return Response (status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':

        platforms.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
def GameView(request):


    ###########################################################################
    #
    # GET wird benutzt, wenn der User Daten anfragt
    #
    ###########################################################################
    if request.method == 'GET':

        try:
            delta = request.GET['delta']
        except:
            delta= ""

        try:
            search = request.GET['search']
        except:
            search = ""

        try:
            needs_update = request.GET['needs_update']
        except:
            needs_update = ""

        if delta=="true":
            games = Game.objects.filter(DeltaYesNo="True")
        else:
            games = Game.objects.all()

        if search != "":
            games = games.filter(game_name__icontains = search)

        if needs_update == "true":
            games = games.filter(game_needs_update = True)

        serializer = GameSerializerGet(
            games,
            context={'request': request},
            many = True
        )

        return Response(serializer.data)

    ###########################################################################
    #
    # POST wird benutzt, wenn der User Daten erstellt
    #
    ###########################################################################
    elif request.method == 'POST':
        serializer = GameSerializerPost(data=request.data)

        if serializer.is_valid():
            serializer.save()

            ###################################################################
            #
            # Hole das gerade gespeicherte Spiel und füge die Referenz
            # zum aktuellen Event hinzu
            #
            ###################################################################
            game = Game.objects.get(id=str(serializer.data["id"]))
            event = Event.objects.get(event_is_current = True)
            game.game_events.add(event)
            game.save()

            return Response(status.HTTP_204_NO_CONTENT)

        #print(serializer.errors)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['Get','DELETE', 'PUT'])
def GameDetailView(request, pk):
    try:
        games = Game.objects.get(pk=pk)
    except games.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)



    ###########################################################################
    #
    # GET
    #
    ###########################################################################
    if request.method == 'GET':

        serializer = GameSerializerGet(
            games,
            context={'request': request},
        )

        return Response(serializer.data)

    ###########################################################################
    #
    # DELETE
    #
    ###########################################################################
    elif request.method == 'DELETE':

        games.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    ###########################################################################
    #
    # PUT
    #
    ###########################################################################
    elif request.method == 'PUT':

        serializer = GameSerializerPut(
            games,
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():


            old_keyart = games.game_keyart
            serializer.save()
            new_keyart = games.game_keyart


            ###################################################################
            #
            # Upload des Keyarts nach Imgur und speichern des neuen Links
            #
            ###################################################################

            if not old_keyart == new_keyart:

                keyart = imgurUploadImage(new_keyart)
                games.game_keyart = keyart['link']
                games.save()

            ###################################################################
            #
            # Füge das Spiel dem aktuellen Event hinzu
            #
            ###################################################################

            game = Game.objects.get(id=str(serializer.data["id"]))
            event = Event.objects.get(event_is_current = True)
            game.game_events.add(event)
            game.save()

            return Response(status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET', 'POST'])
def TrailerView(request):

    ###########################################################################
    #
    # GET
    #
    ###########################################################################
    if request.method == 'GET':

        delta = request.GET['delta']

        if delta=="true":
            trailers = Trailer.objects.filter(DeltaYesNo="True")
        else:
            trailers = Trailer.objects.all()

        serializer = TrailerSerializer(
            trailers,
            context={'request': request},
            many = True
        )

        return Response(serializer.data)

    if request.method == 'POST':
            serializer = TrailerSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(status.HTTP_204_NO_CONTENT)

            ###################################################################
            #
            # Füge das Spiel dem aktuellen Event hinzu
            #
            ###################################################################
            game = Game.objects.get(id=str(serializer.data["game_id_id"]))
            event = Event.objects.get(event_is_current = True)
            game.game_events.add(event)
            game.save()

            return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT', "DELETE"])
def TrailerDetailView(request, pk):

    try:
        trailers = Trailer.objects.get(pk=pk)
    except games.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':

        serializer = TrailerSerializer(
            trailers,
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()

            return Response(status.HTTP_204_NO_CONTENT)


        return Response(status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'DELETE':

        trailers.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


### KOMMENTAR, DAMIT BEIM SPEICHERN NICHT IMMER DIE LEEREN ZEILEN GELÖSCHT WERDEN ####
