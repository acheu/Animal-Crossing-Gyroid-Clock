from datetime import datetime
from enum import Enum
from socket import error as SocketError
from time import sleep
import os
import pyowm
import random
import subprocess


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


class ACS(Enum):
    NEWLEAF = 'New Leaf'
    ORIGINAL = 'Oirginal'
    CITYFOLK = 'City Folk'


def main():
    musicloc = 'Music/'  # Location of the Musics folder with all the sounds
    cycle = 10  # Seconds for Checking
    cts_play = True  # True for continuous play
    allowAlbums = [ACS.NEWLEAF, ACS.CITYFOLK]
    bootupSong(musicloc)
    dto = datetime.now()
    oldHour = dto.hour  # Starts with boot
    lastcheckWeather = False
    isWeather = Weather.NONE
    isFestival = Festival.NONE
    while 1:  # Infinite Main Loop
        dt = datetime.now()
        hour = dt.hour
        # Check weather before the hour to allow time for API call
        if dt.minute > 55 and lastcheckWeather is False:
            # Checks Weather, returns 'none', 'snow', or 'rain'
            isWeather = checkWeather()
            lastcheckWeather = True
        if oldHour != hour or cts_play:
            played = False
            while not played:
                # Keep choosing songs until something plays
                album = random.choice(allowAlbums)
                songloc = musicloc + album.value + '/'
                # Checks for festivals like Christmas, KK, etc
                isFestival = checkFestival(dt)
                print 'Weather is: ' + isWeather.value
                print 'Festival is: ' + isFestival.value
                played = playMusic(songloc, hour, isWeather, isFestival, cts_play)
                # If song did not play, new song will be chosen
            oldHour = hour
            lastcheckWeather = False
        sleep(cycle)  # Sleep 10 Seconds


def playMusic(file_loc, hour, isWeather, isFestival, cts):
    # Check festival first, then check weather
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
        if (random.randint(0, 100) < 10 and etcCheck) or (cts and random.randint(0, 100) < 40):
            musicFile = etcfol + random.choice(os.listdir(etcfol))
        else:
            musicFile = file_loc + isWeather.value + str(hour) + '.mp3'
    print musicFile
    # Double check if file exists
    if os.path.exists(musicFile):
        subprocess.Popen(['mpg123', '-q', musicFile]).wait()
        return True
    else:
        print 'Warning: ' + musicFile + ' Does not exist'
        return False


def bootupSong(file_loc):
    # Plays a random song in the Menu folder
    file_loc = file_loc + 'Menu/'
    start_song = file_loc + random.choice(os.listdir(file_loc))
    subprocess.Popen(['mpg123', '-q', start_song]).wait()


def checkWeather():
    # Python Open Weather Map
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
    weekday = dt.weekday()  # Returns 0-6 for Day of the Week
    month = dt.month
    day = dt.day
    hour = dt.hour
    #date = str(datetime.date.today())
    #print date
    carnivale_dates = []
    # Check for Halloween, Christmas and ...
    if day == 25 and month == 12:
        # It's Festival
        return Festival.TOYDAY
    elif day == 31 and month == 10:
        # It's Halloween
        return Festival.HALLOWEEN
    elif weekday == 5 and hour > 20:
        # KK Slider
        return Festival.KKSLIDER
    elif day == 31 and month == 12:
        return Festival.NEWYEARSEVE
    elif day == 1 and month == 1:
        return Festival.NEWYEAR
    elif day == 4 and month == 7:
        return Festival.FIREWORKS
    else:
        return Festival.NONE
#27th February 2017
#12th February 2018
#4th March 2019
#24th February 2020
#15th February 2021
#28th February 2022
#20th February 2023
#12th February 2024 

if __name__ == "__main__":
    main()
