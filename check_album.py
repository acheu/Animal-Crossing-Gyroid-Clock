import os
from itertools import chain
from enum import Enum

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
    album = raw_input('Enter Album you want to check: /Music/')
    album = 'Music/' + album.split('/')[0] + '/'
    checkfor = ['hour', 'snow_hour', 'rain_hour', 'festival', 'etc']
    folder_error_msg = []
    all_error = []
    if not os.path.isdir(album):
        all_error.append(['ERROR: Album does not exit'])
    else:
        folder_error_msg = check_folders(album, checkfor)
        all_error.append(folder_error_msg)
        # print folder_error_msg
        for i, fol in enumerate(checkfor):
            if folder_error_msg[i] is None:
                msg = check_songs(fol, album + fol + '/')
                all_error.append(msg)
        # Print all error messages
    all_error = list(chain.from_iterable(all_error))
    print '*************************'
    for i in all_error:
        if i:
            print i
    print '*************************'


def check_songs(fol, loc):
    err_msg = []
    if fol is 'etc':
        lists = os.listdir(loc)
        if len(lists) == 0:
            err_msg.append('ERROR: Need songs in ETC folder')
        elif len(lists) < 5:
            err_msg.append('WARNING: Consider adding more songs to ETC')
    elif fol is 'festival':
        err_msg.append('FIXME: need to finish festival check')
    else:
        # We are now checking an 'hours' folder, ie snow_hour, hour, rain_hour
        for i in range(0, 23):
            f = loc + str(i) + '.mp3' 
            if not os.path.isfile(f):
                err_msg.append('ERROR: Missing file: ' + f)
    return err_msg
        
    

def check_folders(album_loc, checkfor):
    dirs = os.listdir(album_loc)
    error_msg = [None] * (len(checkfor) + 1)
    for i, fol in enumerate(checkfor):
        if not os.path.isdir(album_loc + fol):
            error_msg[i] = 'ERROR: Missing Album: ' + fol
    if len(dirs) > len(checkfor):
        error_msg[-1] = 'WARNING: Extra Albums'
    return error_msg


if __name__ == '__main__':
    main()
