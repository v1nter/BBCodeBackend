"""Backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from rest_framework import routers
from bbcapi import views

urlpatterns = [
    path('admin/', admin.site.urls),

    ###########################################################################
    #
    # Events
    #
    ###########################################################################
    re_path(r'^bbcapi/events/$', views.EventView),
    re_path(r'^bbcapi/events/([0-9]+)$', views.EventDetailView),

    ###########################################################################
    #
    # Imgur
    #
    ###########################################################################
    re_path(r'^bbcapi/imgurget/$', views.ImgurGet),
    re_path(r'^bbcapi/imgurpost/$', views.ImgurPost),

    ###########################################################################
    #
    # Plattformen
    #
    ###########################################################################
    re_path(r'^bbcapi/platforms/$', views.PlatformView),
    re_path(r'^bbcapi/platforms/([0-9]+)$', views.PlatformDetailView),

    ###########################################################################
    #
    # Spiele
    #
    ###########################################################################
    re_path(r'^bbcapi/games/$', views.GameView),
    re_path(r'^bbcapi/games/([0-9]+)$', views.GameDetailView),

    ###########################################################################
    #
    # Trailer
    #
    ###########################################################################
    re_path(r'^bbcapi/trailer/$', views.TrailerView),
    re_path(r'^bbcapi/trailer/([0-9]+)$', views.TrailerDetailView),

    ###########################################################################
    #
    # BBCode
    #
    ###########################################################################
    re_path(r'^bbcapi/bbcode/$', views.BbcodeView),

    ###########################################################################
    #
    # Stammdaten
    #
    ###########################################################################
    re_path(r'^bbcapi/base/$', views.BaseViewGet),
    re_path(r'^bbcapi/base/([0-9]+)$', views.BaseViewPut),
]
