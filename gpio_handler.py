try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print 'RuntimeError: Error accessing RPi Library. Retry as Sudo'
except ImportError:
    print 'ImportError: Error accessing RPi Library'

# Pins:
# 29, GPIO 21 --> (0) Spare (Read)
# 31, GPIO 22 --> (1) Volume Wiper (Read)
# 33, GPIO 23 --> (2) RUN reset (Read)
# 35, GPIO 24 --> (3) SHTDWN Comamnd (Read)
# 37, GPIO 25 --> (4) PIenable (Set)


class gpio_handler(object):
    

    def get_Spare(self):
        io = GPIO.input(self.chanlist[0])
        return io

    def get_Volume(self):
        io = GPIO.input(self.chanlist[1])
        return io

    def get_RUN(self):
        print 'Error: RUN pin was not intended to be accessed'

    def get_SHTDWN(self):
        io = GPIO.input(self.chanlist[3])
        return io

    def callback_SHTDWN(self,channel):
        print 'SHTDWN Command Toggled'
        # raise KeyboardInterrupt
        self.SHTDWN = True
    

    def set_PIenable(self,highlow):
        """ Set to Enabled with a highlow == True when program is running """ 
        GPIO.output(self.chanlist[4], highlow)


    def cleanup(self):
        """ closeout function, releases all gpio resources """
        GPIO.cleanup(self.chanlist)

    def get_chanlist(self):
        """ Return the chanlist """
        return self.chanlist

    def set_chanlist(self,loc,newchannel):
        """ reformat a channel to another channel """
        # TODO, add checks and illegal arguments to protect Pi
        # TODO actually add the functionality
        # self.chanlist(loc) = newchannel
            
    def __init__(self):
        """ Create object handle for interfacing with RPi Model B GPIO """
        GPIO.setmode(GPIO.BOARD)  # Set's GPIO referencing to RPi Board Refdes
        self.chanlist = [29, 31, 33, 35, 37]  # chanlist 0, 1, 2, 3, 4
        GPIO.setup(29, GPIO.IN)  # Setup as input to pi
        GPIO.setup(31, GPIO.IN)  # Setup as input
        GPIO.setup(33, GPIO.IN)  # Setup as input
        GPIO.setup(35, GPIO.IN)  # Setup as input
        GPIO.setup(37, GPIO.OUT)  # Setup as output from pi
        self.SHTDWN = False

        GPIO.add_event_detect(self.chanlist[1], GPIO.BOTH)  
        GPIO.add_event_detect(self.chanlist[3], GPIO.FALLING, self.callback_SHTDWN, bouncetime=200)


    



