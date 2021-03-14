from django.db import models
import datetime

###############################################################################
#
# Jeder Forenthread entspricht einem Event. Ein Event kann mehrere Spiele haben
# und ein Spiel kann zu mehreren Events gehören
#
###############################################################################
class Event(models.Model):
    event_name = models.CharField("Eventname", max_length=200, unique=True)
    event_is_current = models.BooleanField("Aktuelles Event", default=True)
    event_album = models.CharField("Album bei Imgur", max_length=200)
    event_url_thread = models.CharField("Thread URL", max_length=200) # URL zum Hauptbeitrag, der immer wieder aktualisiert wird
    event_url_posting = models.CharField("Posting URL", max_length=200) # URL für ein Updateposting

    def __str__(self):
        return self.event_name

    def get_absolute_url(self):
        """Returns the url to access a particular author instance."""
        return reverse('event-detail', args=[str(self.id)])

###############################################################################
#
# Speichert den Zugang zur Imgur API
#
###############################################################################
class Imgur(models.Model):
    imgur_access_token = models.CharField(max_length=200)
    imgur_refresh_token = models.CharField(max_length=200)
    current_login = models.BooleanField(default=False)

    def __str__(self):
        return self.access_token

###############################################################################
#
# Plattformen
#
###############################################################################

class Platform(models.Model):
    platform_name = models.CharField(max_length=200, help_text='Name der Plattform', unique=True)
    platform_image = models.CharField(max_length=200)
    platform_type = models.CharField(max_length=200)

    class Meta:
        ordering = ['platform_type', 'platform_name']

    def __str__(self):
        return self.platform_name

###############################################################################
#
# Spiele
#
###############################################################################
class Game(models.Model):
    game_name = models.CharField(max_length=200, help_text='Spieltitel', unique=True)
    game_release_date = models.CharField(max_length=200, help_text='Release', default="TBA")
    game_platforms = models.ManyToManyField('Platform', help_text='Spiel')
    game_events = models.ManyToManyField('Event')
    game_keyart = models.CharField(max_length=200, help_text='Keyart', default="https://i.imgur.com/9krYg4n.png")
    DeltaYesNo = models.BooleanField(default=False)
    game_description = models.CharField(max_length=200, default="")
    game_production = models.CharField(max_length=200, default="")
    game_needs_update = models.BooleanField(default=True)

    class Meta:
        ordering = ['game_name']

    def __str__(self):
        return self.game_name

###############################################################################
#
# Trailer
#
###############################################################################
class Trailer(models.Model):
    game_id = models.ForeignKey('Game', on_delete=models.CASCADE, null=True, related_name="game_trailers")
    trailer_url = models.CharField(max_length=200, help_text='Trailer URL')
    trailer_name = models.CharField(max_length=200, help_text='Trailer Name')
    DeltaYesNo = models.BooleanField(default = False)
    trailer_date = models.DateField('Date', default=datetime.date.today)

    class Meta:
        ordering = ['-trailer_date']

    def __str__(self):

        return self.trailer_name
