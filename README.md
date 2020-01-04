# Animal-Crossing-Gyroid-Clock version 2A
A Raspberry PI music player that attempts to recreate the animal crossing soundtrack by playing music associated with the time and weather, by Alex Cheu

Version Gyroid_2A corresponds to development version for Raspberry Pi Zero W adding additional functions of user turning on/off custom album settings as well as improvements to the music selection
2A corresponds to breadboard while Gyroid 2B will correspond to printed board


Setup gpio pwm function 2 for audio
>sudo nano /boot/config.txt
	add line dtoverlay=pwm-2chan,pin=18,func=2,pin2=13,func2=4 

Setup new user

>sudo addgroup <username> audio
>logout
>login
>sudo raspi-config
	3. boot options, B1 Desktop / CLI, B2 Console Autologin Text console, automatically logged in as <username> user
	Ensure that the new username is the new account or else it'll remain the default pi usr

Test Audio
>aplay /usr/share/sounds/alsa/Front_Center.wav


Clone Github Directory
>sudo git clone https://github.com/acheu/Animal-Crossing-Gyroid-Clock.git


Install Dependancies
>sudo apt update
>sudo apt install python3-pip
>sudo pip install pyowm
>sudo apt-get install mpg123
>sudo pip install pyyaml
>sudo apt-get install python-pygame


