# Skypebot 
#### This is simple python bot based on skypekit that can host conference call on a server side.
It can read commands from chat to up/hangup the call. 


## How to use

### 1) Download the Skypekit
You can download it from here http://developer.skype.com/ (cost $5) 

This code tested on sdp-distro-desktop-skypekit_4.5.0.105_2859374 but it work with 3.7 and later.

Put the skypebot.py into {skypekit_dir}/examples/python/tutorial/

### 2) Register skype account and get conference ID 


Don't create conference from username that you will use for bot!

Better way is to add bot into existing conference.

Check this by typing ```/get creator``` in conference chat. 

If creator == bot_skypename you will have error. 


Type ```/get name``` to get conference ID and put this string into skypebot line 37.

It must look like: ```conferenceID = '#username1/$username2;c7cddac89532bab3'```

