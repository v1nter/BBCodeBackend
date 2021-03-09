from selenium import webdriver
import os
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from imgurpython import ImgurClient
from bbcapi.models import *

##################################################################
#
# Beinhaltet alle wichtigen Funktionen zu Kommunikation
# mit Imgur.
# => Authentifizierung
# => Album erstellen
# => Foto hochladen
#
##################################################################

def imgurUploadImage(URL, platform=False):

    ##################################################################
    #
    # Lädt Fotos nach Imgur.
    #
    # 1. Zwei Modi: Keyart für Spiel hochladen (=> platform=False) oder
    #    Icon für Plattform hochladen (=> platform=True).
    #    Unterschied: Fotos für Spiele werden in ein ALbum gespeichert,
    #    Fotos für Plattformen nicht. (=> Erweiterung: Stammdaten zentral
    #    speichern)
    #
    # 2. Wenn man sich bei Imgur neu anmeldet, wird ein neuer Datensatz
    #    aus Refresh- und Accesstoken angelegt. Der jeweils aktuellste
    #    Datensatz enthält current_login=True und wird zur Initialisierung
    #    des Clienten genutzt.
    #
    # 3. Client ID und Client Secret sind von Imgur zugewiesen und einmalig
    #    für die jeweilige App
    #
    ##################################################################

    ##################
    #
    # Initialisierung Client
    #
    ##################

    client_id = '4e9bcb4fb8cf695'
    client_secret = '2e5400af8caef2ff4e11c5bd11f917d8fc6a9ef6'

    # Hole aktuelles Refresh-Token/Access-Token-Paar
    imgur = Imgur.objects.filter(current_login=True)
    access_token = imgur.values()[0]['imgur_access_token']
    refresh_token = imgur.values()[0]['imgur_refresh_token']

    # Erstelle Client mit Client ID und Client Secret
    # Anschließend authentifiziere App mit Access- und Refresh-Token bei Imgur
    client = ImgurClient(client_id, client_secret)
    client.set_user_auth(access_token, refresh_token)

    ##################
    #
    # Upload
    #
    ##################

    # Moduswahl: Platformicons werden nicht in einem Album gespeichert
    if platform == True:
        # Platformicon hochladen
        img = client.upload_from_url(URL, anon=False)
    else:
        # Keyart zu Spiel in ein Album hochladen

        # Suche aktuelles Event heraus => Zu jedem Event gehört ein Album
        event = Event.objects.filter(event_is_current="True")


        if event:
            # Lese Album-ID (=> URL) aus Datenbank, dann lade
            # Bild aus dem Internet nach Imgur hoch.
            # Anschließend Bild dem passenden Album zuordnen.

            album_id = event.values()[0]['event_album']
            img = client.upload_from_url(URL, anon=False)
            client.album_add_images(album_id, img['id'])

    return img

def imgureDeleteAlbum(album_id):

    ###########################################################################
    #
    # Lösche ein ALbum
    #
    ###########################################################################

    client_id = '4e9bcb4fb8cf695'
    client_secret = '2e5400af8caef2ff4e11c5bd11f917d8fc6a9ef6'

    imgur = Imgur.objects.filter(current_login=True)
    access_token = imgur.values()[0]['imgur_access_token']
    refresh_token = imgur.values()[0]['imgur_refresh_token']

    client = ImgurClient(client_id, client_secret)
    client.set_user_auth(access_token, refresh_token)


    client.album_delete(album_id)



def imgurCreateAlbum(Title):

    ##################################################################
    #
    # Erstellt ein Album auf Imgur, passend zu jedem Event
    #
    ##################################################################

    client_id = '4e9bcb4fb8cf695'
    client_secret = '2e5400af8caef2ff4e11c5bd11f917d8fc6a9ef6'

    # Hole aktuelles Refresh-Token/Access-Token-Paar
    imgur = Imgur.objects.filter(current_login=True)
    access_token = imgur.values()[0]['imgur_access_token']
    refresh_token = imgur.values()[0]['imgur_refresh_token']

    # Erstelle Client mit Client ID und Client Secret
    # Anschließend authentifiziere App mit Access- und Refresh-Token bei Imgur
    client = ImgurClient(client_id, client_secret)
    client.set_user_auth(access_token, refresh_token)

    # Legt Album an. Der Titel wird übergeben und entspricht
    # dem Namen des Events.

    fields = {
    'title': Title,
    }

    album = client.create_album(fields)

    return album['id']

def imgurAuth():

    ##################################################################
    #
    # Gewährt BBCode-Generator Zugriff auf den Useraccount bei Imgur.
    #
    # 1. Dazu wird der Imgur-Login in einem Chrome-Fenster geöffnet
    #    Anschließend werden in die passenden Felder automatisch
    #    Login und Passwort eingetragen und abgeschickt. Der User
    #    erhält von Imgur eine PIN im Webbrowser, die automatisch
    #    ausgelesen wird. Mit dem PIN wird ein Access- und Refresh-Token
    #    erzeugt, die fortan zur Identifikation dienen.
    #
    # 2. Die Tokens werden in der DB gespeichert, damit man später
    #    nicht mehr vor jedem Upload einen Authenfizierungsprozesss
    #    vornehmen muss. Stattdessen werden die gültigen Tokens
    #    aus der Datenbank genutzt.
    #
    ##################################################################

    client_id = '4e9bcb4fb8cf695'
    client_secret = '2e5400af8caef2ff4e11c5bd11f917d8fc6a9ef6'
    client_user = 'V1nter'
    client_pw = '0N1hWHMKpIMGcwT9'

    ##################
    #
    # Authenfizierung
    #
    ##################


    # Erstelle Clienten und erhalte URL zur Authentifizierung
    client = ImgurClient(client_id, client_secret)
    authorization_url = client.get_auth_url('pin')

    # Öffne Chrome-Fenster mit URL zum Login im Useraccount

    #chrome_exec_shim = "/app/.apt/opt/google/chrome/chrome"
    # chrome_exec_shim = "/app/.apt/usr/bin/google-chrome"
    # opts = webdriver.ChromeOptions()
    # opts.binary_location = chrome_exec_shim
    # opts.add_argument("--no-sandbox");
    # opts.add_argument("--disable-gpu");
    # driver = webdriver.Chrome(executable_path=chrome_exec_shim, chrome_options=opts)

    chrome_bin = os.environ.get('GOOGLE_CHROME_SHIM', None)
    opts = ChromeOptions()
    opts.binary_location = chrome_bin
    driver = webdriver.Chrome(executable_path="chromedriver", chrome_options=opts)

    #driver = webdriver.Chrome(ChromeDriverManager().install())
    #driver.get(authorization_url)


    # Finde die passenden Felder für Username und Passwort auf der Login-Seite
    # von Imgur, fülle sie aus und schicke sie anschließend automatisch ab.

    # Finde Felder
    username = driver.find_element_by_xpath('//*[@id="username"]')
    password = driver.find_element_by_xpath('//*[@id="password"]')

    # Fülle Felder
    username.clear()
    password.clear()
    username.send_keys(client_user)
    password.send_keys(client_pw)

    # Bestätige Login durch Click auf Button
    driver.find_element_by_name("allow").click()

    timeout = 5

    # Lese PIN zur Authenfizierung
    try:
        element_present = EC.presence_of_element_located((By.ID, 'pin'))
        WebDriverWait(driver, timeout).until(element_present)
        pin_element = driver.find_element_by_id('pin')
        pin = pin_element.get_attribute("value")

    except TimeoutException:
        exceptionYN = True
        exception = "TimeOut"
    driver.close()

    # Erhalte Refresh- und Accesstoken im Eintausch gegen PIN.
    credentials = client.authorize(pin, 'pin')
    client.set_user_auth(credentials['access_token'], credentials['refresh_token'])

    ##################
    #
    # Authenfizierung abgeschlossen
    #
    ##################

    ##################
    #
    # Speichere Refresh- und Accesstoken in Datenbank,
    # um sie später erneut benutzen zu können.
    #
    ##################

    # Schreibe Tokens in Datenbank und markiere sie
    # als aktuellen Datensatz (current_login = True)
    imgur = Imgur()
    imgur.imgur_access_token = credentials['access_token']
    imgur.imgur_refresh_token = credentials['refresh_token']
    imgur.current_login = True

    # Hole den bisherigen aktuellen Datensatz
    check_for_current = Imgur.objects.filter(current_login="True")

    # Falls Queryset nicht leer ist, setze current_login des bisherigen
    # aktuellen Datensatzes auf falsch.
    if check_for_current:

        for record in check_for_current:
            record.current_login = False
            record.save()

    imgur.save()

    return client
