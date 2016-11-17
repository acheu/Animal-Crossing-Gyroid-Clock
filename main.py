from datetime import datetime
import subprocess
import pyowm
import os
from time import sleep
from socket import error as SocketError
import errno
import random
from enum import Enum


class Weather(Enum):
    RAIN = 'rain'
    SNOW = 'snow'
    NONE = 'none'


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
    WILDWORLD = 'Wild World'
    ORIGINAL = 'Oirginal'
    CITYFOLK = 'City Folk'


def main():
    musicloc = 'Music/'  # Location of the Musics folder with all the sounds
    cycle = 10  # Seconds for Checking
    allowAlbums = [ACS.NEWLEAF, ACS.CITYFOLK]
    bootupSong(musicloc)
    dto = datetime.now()
    oldHour = dto.hour  # Starts with boot
    checkWeather = False
    isWeather = Weather.NONE
    isFestival = Festival.NONE
    while 1:
        dt = datetime.now()
        hour = dt.hour
        # Check weather before the hour to allow time for API call
        if dt.minute > 55 and checkWeather is False:
            # Checks Weather, returns 'none', 'snow', or 'rain'
            isWeather = checkWeather()
            checkWeather = True
        # if oldHour != hour:
        if 1:
            album = random.choice(allowAlbums)
            songloc = musicloc + album.value + '/'
            # Checks for festivals like Christmas, KK, etc
            isFestival = checkFestival()
            print 'Weather is: ' + isWeather.value
            print 'Festival is: ' + isFestival.value
            played = playMusic(songloc, hour, isWeather, isFestival)
            if played:  # If opening the file was successfully called
                oldHour = hour
                checkWeather = False
        sleep(cycle)  # Sleep 10 Seconds


def playMusic(file_loc, hour, isWeather, isFestival):
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
        # Chance arbitrarly set at 5% if etcCheck passes
        if random.randint(0, 100) < 5 and etcCheck:
            musicFile = etcfol + random.choice(os.listdir(etcfol))
        elif isWeather == Weather.RAIN:
            musicFile = file_loc + 'rain_hour/' + str(hour) + '.mp3'
        elif isWeather == Weather.SNOW:
            musicFile = file_loc + 'snow_hour/' + str(hour) + '.mp3'
        else:
            musicFile = file_loc + 'hour/' + str(hour) + '.mp3'
    print musicFile
    # Double check if file exists
    if os.path.exists(musicFile):
        subprocess.Popen(['mpg123', '-q', musicFile]).wait()
        return True
    else:
        print 'Warning: ' + musicFile + ' Does not exist'
        return False


def bootupSong(file_loc):
    file_loc = file_loc + 'Menu/'
    start_song = file_loc + random.choice(os.listdir(file_loc))
    subprocess.Popen(['mpg123', '-q', start_song]).wait()


def checkWeather():
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
    if status == 'Drizzle' or status == 'Thunderstorm' or status == 'Rain':
        return Weather.RAIN
    elif status == 'Snow':
        return Weather.SNOW
    else:
        return Weather.NONE

def checkFestival():
    dt = datetime.now()
    weekday = dt.weekday()  # Returns 0-6 for Day of the Week
    month = dt.month
    day = dt.day
    hour = dt.hour
    holiday = Festival.NONE
    # Check for Halloween, Christmas and ...
    if day == 25 and month == 12:
        # It's Festival
        holiday = Holiday.TOYDAY
    elif day == 31 and month == 10:
        # It's Halloween
        holiday = Festival.HALLOWEEN
    elif weekday == 5 and hour > 20:
        # KK Slider
        holiday = Festival.KKSLIDER
    elif day == 31 and month == 12:
        holiday = Festival.NEWYEARSEVE
    elif day == 1 and month == 1:
        holiday = Festival.NEWYEAR
    elif day == 4 and month == 7:
        holiday = Festival.FIREWORKS
    return holiday


if __name__ == "__main__":
    main()
