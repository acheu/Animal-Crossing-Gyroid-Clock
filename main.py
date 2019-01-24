from __future__ import division
from datetime import datetime
from enum import Enum
from socket import error as SocketError
from time import sleep
import os
import sys
import signal
import pyowm
import random
import subprocess
import pygame
import config
from csv import reader as csvreader
import check_album
from gpio_handler import gpio_handler

class Weather(Enum):
    RAIN = 'rain_hour/'
    SNOW = 'snow_hour/'
    NONE = 'hour/'


class Festival(Enum):
    TOYDAY = 'toy day/'
    HALLOWEEN = 'halloween/'
    FIREWORKS = 'fireworks/'
    KKSLIDER = 'kk slider'
    CARNIVALE = 'carnivale/'
    HARVESTFESTIVAL = 'harvest festival/'
    BUNNYDAY = 'bunny day/'
    NEWYEAR = 'new year/'
    NEWYEARSEVE = 'new years eve/'
    NONE = 'none'


# Initialization parameters of the pygame.mixer
FREQ = 44100
BITSIZE = -16
CHANNELS = 2
BUFFER = 4096

global ch1  # global handle for channel 1 for music
global ch2  # global handle for channel 2 for music
global mus  # global music handler
global pigpio  # GPIO Object handle

# Notes:
# FIX ME: when ETC plays, title keeps getting reprinted over and over for length of song


def main():
    global pigpio
    try:
        pigpio = gpio_handler()
        pigpio.set_PIenable(True)  # Set running pin TRUE for daughter board
        pigpio.set_Speaker_SHTDWN(True)  # Turn on Speaker
        # signal.signal(pigpio.callback_SHTDWN, signal_handler)  # Signal interrupt if button on daughter board is pressed
    except:
        print 'Error: PI possibly not connected'
        print sys.exc_info()[0]
    musicloc = 'Music/'  # Location of the Musics folder with all the sounds
    cycle = 10  # Max time  between songs in seconds
    cts_play = True  # True for continuous play
    allow_albums = config.albums_allowable
    tvol = config.time_volume
    print 'Loaded in: ' + str(config.albums_allowable)
    pygame.mixer.init(FREQ, BITSIZE, CHANNELS, BUFFER)
    pygame.init()
    global ch1
    global ch2
    ch1 = pygame.mixer.Channel(0)  # for music and songs
    ch2 = pygame.mixer.Channel(1)  # for sound effects
    pygame.mixer.music.set_volume(tvol[datetime.now().hour]/10)
    #bootupSong()
    # TODO, play bootupsong as a sound effect, which will allow the bootup process to continue
    # Then add a wait condition for if/when bootupsong is done playing
    dto = datetime.now()
    #oldHour = dto.hour  # Starts with boot
    lastcheckWeather = False
    isWeather = Weather.NONE
    isFestival = Festival.NONE
    day_check = []  # Assumption: There'll never be a day []
    play_check = 0
    signal.signal(signal.SIGINT, signal_handler)
    play_check = check_play_triggers(True, dto.hour, 0)
    while 1:  # Infinite Main Loop
        dt = datetime.now()
        hour = dt.hour
        ch1.set_volume(tvol[hour]/10)
        ch2.set_volume(tvol[hour]/10)
        pygame.mixer.music.set_volume(tvol[hour]/10)
        minute = dt.minute        
        if play_check > 0:
            if dt.minute > 55 or not lastcheckWeather:
                # Checks Weather, returns 'none', 'snow', or 'rain'
                isWeather = checkWeather(config.location)  # Check weather at location
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
                check_rigid = True
                with open(songloc + 'album_config.txt','r+') as cf_file:
                    read = csvreader(cf_file, delimiter='=', quotechar='|')
                    for i in read:
                        comm_line = [i[0],i[1]]
                        if 'rigid' in i[0]:
                            check_rigid = i[1].strip()
                        if 'freq' in i[0]:
                            freq_set = int(i[1].strip())
                            _init = pygame.mixer.get_init()
                            if freq_set != _init[0]:
                                pygame.mixer.quit()  # Need to quit to reinitialize mixer
                                pygame.mixer.pre_init(freq_set, _init[1], _init[2])
                                pygame.mixer.init()
                                #print pygame.mixer.get_init()
                # FIX ME: A bit of a janky way of implementing album prefs
                if check_rigid == 'True':
                    played = chooseMusic_Rigid(songloc, hour, isWeather, isFestival, play_check)
                else:
                    played = chooseMusic_Flexible(songloc, hour, isWeather, isFestival, play_check)

                #print 'Loop Entered'
                while True:
                    sound_check_new = check_sound_triggers()
                    play_check_new = check_play_triggers(cts_play, hour, play_check)
                    if pigpio.SHTDWN:
                        signal_handler(signal.SIGINT, 0)
                    elif play_check > 0 and play_check_new != play_check:
                        fadeout_time = 3000  # milliseconds
                        pygame.mixer.music.fadeout(fadeout_time)
                        # Wait fadeout time + 100 ms
                        sleep(fadeout_time/1000 + .1)
                        played = False
                        # Possibly don't need thise played = False to accurately get the
                        # loop back to playing new music, I just don't want to wait the
                        # sleep cycle
                    else:
                        sleep(2)
                    play_check = play_check_new
                    if not pygame.mixer.music.get_busy():
                        # Emulate Do-while loop by going t hrough this at least once
                        #print played
                        #print 'Loop broken'
                        break
                    
                # If song did not play, new song will be chosen
            #oldHour = hour
            lastcheckWeather = False
        if play_check == 1:
            sleep(random.randint(1,cycle))  # Sleeps random integers seconds between 1 and cycle


def check_play_triggers(cts_play, oldHour, old_play_check):
    """ play_check returns:
    0: 0 is no mode, skip to sleep cycle
    1: Cts Play
    2: Play the Top of the Hour  <----- not fully supported yet
    3: Play etc Song
    4: Ring bell toll
    5: onwards: Not yet used
    """
    dt = datetime.now()
    hour = dt.hour
    minute = dt.minute
    play_check = 0
    if cts_play:  # decide on song for continuous play
        #print oldHour
        #print hour
        #print '---'
        if oldHour != hour and minute == 0:  # Top of the hour
            if config.hrly_preferences['ring_bell']:
                play_check = 4
            else:
                play_check = 3
                # play_check = 2  # To be enabled with supported with additional music options
        elif minute in [15, 30, 45]:
            play_check = 3
        else:
            play_check = 1
    else:  # Non-continuous play song decision
        if minute == 0:
            if config.hrly_preferences['ring_bell']:
                play_check = 4
            else:
                play_check = 2
        if minute in [15, 30, 45]:
            play_check = 3
        else:
            play_check = 0
        # Assumption: That cycle is < 60s and that a song length is >60s
    return play_check
    

def check_sound_triggers():
    minute = datetime.now().minute
    fx_fold = 'Music/Resources/effects/'
    #if True:  # play test, ignore
    #    crits = fx_fold + 'critters/'
    #    ff = [crits + '066.wav', crits + '066.wav', crits + '067.wav', crits + '068.wav']
    #    print 'playing'
    #    play_sound(ff)
    return False


def play_sound(music_file):
    # Function call to play sounds in addition to the main music e.g. cicada
    played = False
    for i in music_file:
        if os.path.exists(i):
            #print i
            soundobj = pygame.mixer.Sound(i)
            length = soundobj.get_length()
            soundobj.play()
            sleep(length + .15)
            played = True
            print music_file
    return played


def play_music(f):
    # Play main mixer music function
    played = False
    try:
        if os.path.exists(f):
            #print f
            pygame.mixer.music.load(f)
            # subprocess.Popen(['mpg123', '-q', f]).wait()
            pygame.mixer.music.play(0)
            played = True
        else:
            print 'Warning: ' + f + ' Does not exist'
            played = False
    except:
        played = False
    return played


def chooseMusic_Rigid(file_loc, hour, isWeather, isFestival, cts):
    """Check festival first, then check weather"""
    # FIX ME: Need to organize to respond more accurately to cts states
    song_loc = ''
    played = False
    print file_loc
    if cts == 4:
        played = ring_bell()
        #return played
        #FIX ME; Should exit after ring bell or not? Is it find to proceed?
    if cts == 3:
        etcfol = file_loc + 'etc/'
        # Consider: adding a play_sound here
        song_loc = etcfol + random.choice(os.listdir(etcfol))
    else:
        # Else, play main music selection
        if isFestival != Festival.NONE:
            if isFestival == Festival.KKSLIDER:
                musicFile = 'Music/KK/'
                kksong = random.choice(os.listdir(musicFile))
                musicFile = musicFile + kksong
            else:
                musicfol = file_loc + 'festival/' + isFestival.value
                musicFile = musicfol + random.choice(os.listdir(musicfol))
        else:
        # Chance arbitrarly set at 10% if etcCheck passes
        #-------------------------------------------------------
        # Commented out because I didn't like the random chance of other music playing
        # I changed it so cts == 3 means play random music on its own timer
        # not just randomly within every call
            #etcfol = file_loc + 'etc/'
            # Check if etc folder exists and there's music
            #etcCheck = False
            #if os.path.isdir(etcfol) and len(os.listdir(etcfol)) > 0:
            #    etcCheck = True
        #if (etcCheck and ((random.randint(0, 100) < 10) and cts == 1)) or cts == 3:
        #    musicFile = etcfol + random.choice(os.listdir(etcfol))
        #else:
        #    # musicFile = file_loc + isWeather.value + str(hour) + '.mp3'
        #    music_fol = file_loc + isWeather.value + str(hour) + '/'
        #    musicFile = music_fol + random.choice(os.listdir(music_fol))
        #-------------------------------------------------------
            music_fol = file_loc + isWeather.value + str(hour) + '/'
            song_loc = music_fol + random.choice(os.listdir(music_fol))
    played = play_music(song_loc)
    return played


def chooseMusic_Flexible(song_loc, hour, isWeather, isFestival, cts):
    _times = config.flexible_defs
    # flexible_defs are the definitions for how the exact hour correlates to
    # 'Afternoon', 'Morning', 'Noon', etc
    songfile = ''
    if cts == 3:
        #song_loc = song_loc + 'etc/'
        # Consider: adding a play_sound here
        songfile = random.choice(os.listdir(song_loc + 'etc/'))
    elif cts == 4:
        played = ring_bell()
        #return played
    #elif
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
    played = play_music(song_loc)
    return played
    

def ring_bell():
    """Plays bell tone """
    file_loc = "Music/Resources/Menu/"
    bell_song = file_loc + "belltone.mp3"
    play_music(bell_song)
    #pygame.mixer.music.load(bell_song)
    #pygame.mixer.music.play(0)
    while pygame.mixer.music.get_busy():
        sleep(1)
    return True


def bootupSong():
    """Plays a random song in the Menu folder"""
    file_loc = 'Music/Resources/Menu/'
    start_song = file_loc + 'Nintendo.mp3'
    # start_song = file_loc + 'Train_Departure.mp3'
    pygame.mixer.music.load(start_song)
    pygame.mixer.music.play(0)
    while pygame.mixer.music.get_busy():
        sleep(1)


def checkWeather(city):
    """Python Open Weather Map, pass it string of city,country"""
    
    #city = 'Jersey City,us'
    try:
        # Key provided free on openweathermap.org
        owm = pyowm.OWM('7fcf1a61a3f873475c5d8ea070c6454b')
        weather = owm.weather_at_place(city).get_weather()
        status = weather.get_status()
    except:
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
    #harvest_dates = ['2016-11-24']
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
    elif day == 24 and month == 11:  # Hardcoded thanksgiving
    #elif date in harvest_dates:
        festival = Festival.HARVESTFESTIVAL
    else:
        festival = Festival.NONE
    return festival

def signal_handler(signal, frame):
    global pigpio
    print 'SIGINT Received, quitting program...'
    #pygame.mixer.music.fadeout(3000)  # Fade music out at 3000 ms
    pygame.mixer.quit()
    print 'Quiting Pygame Mixer...'
    try:
        pigpio.cleanup()  # Release GPIO before quitting
    except:
        print 'No GPIO to access'
    if frame == 0:
        # Frame == 0 is specially passed by daughter board
        os.system("sudo shutdown now -h")
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
