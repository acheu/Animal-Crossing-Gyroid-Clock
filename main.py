from datetime import datetime
from enum import Enum
from socket import error as SocketError
from time import sleep
import os
import pyowm
import random
import subprocess
import pygame
import config
import yaml


class Weather(Enum):
    RAIN = 'rain_hour/'
    SNOW = 'snow_hour/'
    NONE = 'hour/'


class Festival(Enum):
    TOYDAY = 'toy day'
    HALLOWEEN = 'halloween'
    FIREWORKS = 'fireworks'
    KKSLIDER = 'kk slider'
    CARNIVALE = 'carnivale'
    HARVESTFESTIVAL = 'harvest festival'
    BUNNYDAY = 'bunny day'
    NEWYEAR = 'new year'
    NEWYEARSEVE = 'new years eve'
    NONE = 'none'

def main():
    musicloc = 'Music/'  # Location of the Musics folder with all the sounds
    cycle = 10  # Seconds for Checking
    cts_play = False  # True for continuous play
    allow_albums = config.albums_allowable
    print 'Loaded in: ' + str(config.albums_allowable)
    pygame.mixer.init(frequency=44000, size=-16, channels=2, buffer=4096)
    pygame.init()
    bootupSong(musicloc)
    dto = datetime.now()
    oldHour = dto.hour  # Starts with boot
    lastcheckWeather = False
    isWeather = Weather.NONE
    isFestival = Festival.NONE
    day_check = []  # Assumption: There'll never be a day []
    play_check = 0
    while 1:  # Infinite Main Loop
        dt = datetime.now()
        hour = dt.hour
        minute = dt.minute
        # play_check code:
        # 1: Cts Play
        # 2: Play the Top of the Hour
        # 3: Play the bottom of the Hour
        # 4: Ring bell toll
        # 5: onwards: Not yet used
        if cts_play:
            if oldHour != hour:
                play_check = 4
            else:
                play_check = 1
        else:
            if oldHour != hour:
                if config.hrly_preferences['ring_bell']:
                    play_check == 4
                else:
                    play_check = 2
            elif minute == 30:
                play_check = 3
            else:
                play_check = 0
            # Assumption: That cycle is < 60s and that a song length is >60s
        if play_check > 0:
            if dt.minute > 55 or not lastcheckWeather:
                # Checks Weather, returns 'none', 'snow', or 'rain'
                isWeather = checkWeather()
                lastcheckWeather = True
            if day_check != dt.day:
                # Checks for festivals like Christmas, KK, etc
                isFestival = checkFestival(dt)
                day_check = dt.day
            played = False
            while not played:
                # Keep choosing songs until something plays
                album = random.choice(allow_albums)
                songloc = musicloc + album + '/'
                #played = chooseMusic_Flexible(songloc, hour, isWeather, isFestival)
                played = chooseMusic_Rigid(songloc, hour, isWeather, isFestival, play_check)
                # If song did not play, new song will be chosen
            oldHour = hour
            lastcheckWeather = False
        sleep(cycle)  # Sleep 10 Seconds


def chooseMusic_Rigid(file_loc, hour, isWeather, isFestival, cts):
    """Check festival first, then check weather"""
    if cts == 4:
        ring_bell()
    if isFestival != Festival.NONE:
        if isFestival == Festival.KKSLIDER:
            musicFile = 'Music/KK/'
            kksong = random.choice(os.listdir(musicFile))
            musicFile = musicFile + kksong
        else:
            musicFile = file_loc + 'festival/' + isFestival.value + '.mp3'
    else:
        # Roll for random chance to play 'etc' song
        etcfol = file_loc + 'etc/'
        # Check if etc folder exists and there's music
        etcCheck = False
        if os.path.isdir(etcfol) and len(os.listdir(etcfol)) > 0:
            etcCheck = True
        # Chance arbitrarly set at 10% if etcCheck passes
        if (etcCheck and ((random.randint(0, 100) < 10) and cts == 1)) or cts == 3:
            musicFile = etcfol + random.choice(os.listdir(etcfol))
        else:
            musicFile = file_loc + isWeather.value + str(hour) + '.mp3'
    print musicFile
    # Double check if file exists
    if os.path.exists(musicFile):
        # subprocess.Popen(['mpg123', '-q', musicFile]).wait()
        pygame.mixer.music.load(musicFile)
        pygame.mixer.music.play(0)
        while pygame.mixer.music.get_busy():
            sleep(1)
        return True
    else:
        print 'Warning: ' + musicFile + ' Does not exist'
        return False


def chooseMusic_Flexible(song_loc, hour, isWeather, isFestival):
    _times = config.flexible_defs
    songfile = ''
    if isFestival is not Festival.NONE:
        song_loc = song_loc + 'Festival/'
        songfile = random.choice(os.listdir(song_loc))
    elif hour in _times['Morning']:
        song_loc = song_loc + 'Morning/'
        songfile = random.choice(os.listdir(song_loc))
    elif hour in _times['Noon']:
        song_loc = song_loc + 'Noon/'
        songfile = random.choice(os.listdir(song_loc))
    elif hour in _times['Afternoon']:
        song_loc = song_loc + 'Afternoon/'
        songfile = random.choice(os.listdir(song_loc))
    elif hour in _times['Evening']:
        song_loc = song_loc + 'Evening/'
        songfile = random.choice(os.listdir(song_loc))
    elif hour in _times['Night']:
        song_loc = song_loc + 'Night/'
        songfile = random.choice(os.listdir(song_loc))
    song_loc += songfile
    if os.path.exists(song_loc):
        pygame.mixer.music.load(song_loc)
        pygame.mixer.music.play(0)
        print 'Playing: ' + songfile
        while pygame.mixer.music.get_busy():
            sleep(1)
        return True
    else:
        print 'Warning: ' + song_loc + ' Does not exist'
        return False


def ring_bell():
    """Plays bell tone """
    file_loc = "Music/Menu/"
    bell_song = file_loc + "belltone.mp3"
    pygame.mixer.music.load(bell_song)
    pygame.mixer.music.play(0)
    while pygame.mixer.music.get_busy():
        sleep(1)


def bootupSong(file_loc):
    """Plays a random song in the Menu folder"""
    file_loc = file_loc + 'Menu/'
    start_song = file_loc + 'Nintendo.mp3'
    #start_song = file_loc + random.choice(os.listdir(file_loc))
    # subprocess.Popen(['mpg123', '-q', start_song]).wait()
    #sound = pygame.mixer.Sound(start_song)
    pygame.mixer.music.load(start_song)
    pygame.mixer.music.play(0)
    while pygame.mixer.music.get_busy():
        sleep(1)


def checkWeather():
    """Python Open Weather Map"""
    # City Hardcoded into this. Can change later with API call
    city = 'Atlanta,us'
    try:
        # Key provided free on openweathermap.org
        owm = pyowm.OWM('7fcf1a61a3f873475c5d8ea070c6454b')
        weather = owm.weather_at_place(city).get_weather()
        status = weather.get_status()
    except SocketError:
        print 'Socket Closed Error'
        status = Weather.NONE
        return status
    if status in ['Drizzle', 'Thunderstorm', 'Rain']:
        return Weather.RAIN
    elif status == 'Snow':
        return Weather.SNOW
    else:
        return Weather.NONE


def checkFestival(dt):
    """Checks festival dates"""
    weekday = dt.weekday()  # Returns 0-6 for Day of the Week
    month = dt.month
    day = dt.day
    hour = dt.hour
    date = str(dt.date())
    carnivale_dates = ['2017-2-27','2018-2-12','2019-3-4','2020-2-24','2021-3-15','2022-2-28']
    bunnyday_dates = []
    harvest_dates = ['2016-11-24']
    festival = Festival.NONE
    # Check for Halloween, Christmas and ...
    
    if day == 25 and month == 12:
        # It's Festival
        festival = Festival.TOYDAY
    elif day == 31 and month == 10:
        # It's Halloween
        festival = Festival.HALLOWEEN
    elif weekday == 5 and hour > 20:
        #  Slider
        festival = Festival.KKSLIDER
    elif day == 31 and month == 12:
        return Festival.NEWYEARSEVE
    elif day == 1 and month == 1:
        festival = Festival.NEWYEAR
    elif day == 4 and month == 7:
        festival = Festival.FIREWORKS
    elif date in carnivale_dates:
        festival = Festival.CARNIVALE
    elif date in harvest_dates:
        festival = Festival.HARVESTFESTIVAL
    else:
        festival = Festival.NONE
    return festival

if __name__ == "__main__":
    main()
