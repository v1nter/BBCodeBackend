from django.contrib import admin
from .models import *

class EventAdmin(admin.ModelAdmin):
    list_display = ('event_name', 'event_is_current', 'event_url_thread', 'event_url_posting')


admin.site.register(Event)
admin.site.register(Imgur)
admin.site.register(Platform)
admin.site.register(Game)
admin.site.register(Trailer)
admin.site.register(BaseData)
