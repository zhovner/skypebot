#coding:utf-8
print '*****************************'
print 'Skypekit conference host bot'
print '*****************************'

#
# This file must be run from ./examples/python/tutorial/ from skypekit package.
# 
#

import sys
import keypair
from time import sleep
import signal

sys.path.append(keypair.distroRoot + '/ipc/python');
sys.path.append(keypair.distroRoot + '/interfaces/skype/python');

try:
	import Skype;
except ImportError:
    raise SystemExit('Program requires Skype and skypekit modules');

#----------------------------------------------------------------------------------
# Taking skypename and password arguments from command-line.
# ConferenceID must be hardcoded (type '/get name' in existed conference)
# 


if len(sys.argv) < 3:
	print('Usage: python autoanswer.py <skypename> <password>');
	sys.exit();

accountName = sys.argv[1]
accountPsw  = sys.argv[2]

# don't work if #accountName/...
conferenceID = 'TYPE_HERE_CONFERENCE_ID'

# /golive token (not necessarily)
conferenceToken = 'confa'

Admins = ['skypename1','skypename2','skypename3']



if conferenceID == 'TYPE_HERE_CONFERENCE_ID':
	print 'You must set conference ID in this file line 36.\nType "/get name" in conference to get ID.'
	sys.exit()
	
loggedIn	= False
isCallFinished	= False

#----------------------------------------------------------------------------------
# Stop when press Ctrl+C  
# 

def shutdown(signal, frame):
	print ' Aborted.'
	if not isCallFinished:
		liveConversation.LeaveLiveSession(False)
	while not isCallFinished:
		sleep(1)
	MySkype.stop()
	sys.exit()

signal.signal(signal.SIGINT, shutdown)



#----------------------------------------------------------------------------------
# Defining our own Account property change callback and assigning it to the
# SkyLib.Account class.

def AccountOnChange (self, property_name):
	global loggedIn;
	if property_name == 'status':
		if self.status == 'LOGGED_IN':
			loggedIn = True;
			print('Login complete.');

Skype.Account.OnPropertyChange = AccountOnChange;

Skype.isLiveSessionUp = False;
Skype.liveSession = 0;


#----------------------------------------------------------------------------------
# Creating our main Skype object

try:
	MySkype = Skype.GetSkype(keypair.keyFileName);	
	MySkype.Start();
except Exception:
	raise SystemExit('Unable to create Skype instance');


#----------------------------------------------------------------------------------
# Retrieving account and logging in with it. Then waiting in loop.

account = MySkype.GetAccount(accountName);

print('Logging in with ' + accountName);
account.LoginWithPassword(accountPsw, False, False);

while loggedIn == False:
	sleep(1);

#----------------------------------------------------------------------------------
# Create conversation object 

# global liveConversation
print 'MySkype.GetConversationByIdentity'

#global liveConversation
liveConversation = MySkype.GetConversationByIdentity(conferenceID)


ForceCallFinished = False


#----------------------------------------------------------------------------------
# Defining our own Participant property change callback

def ParticipantOnChange (self, property_name):
	if property_name == 'voice_status':

		# It makes sense to only display 'joined call' and 'left call'
		# feedback messages for people other than ourselves.
		if self.identity != accountName:
			if self.voice_status == 'SPEAKING':
				print(self.identity + ' has joined the call.');

			if self.voice_status == 'VOICE_STOPPED':
				print(self.identity + ' has left the call.');

		if (self.identity == accountName) and (self.voice_status == 'VOICE_STOPPED'):
			global isCallFinished;
			isCallFinished = True;

	# This property enables you to have neat voice activity indicators in your UI.
	if property_name == 'sound_level':
		print(self.identity + ' sound level: ' + str(self.sound_level));

Skype.Participant.OnPropertyChange = ParticipantOnChange;



#----------------------------------------------------------------------------------
# Incoming messages looking
#

def OnMessage(self, message, changesInboxTimestamp, supersedesHistoryMessage, conversation):

	if message.author != accountName:
		print(message.author_displayname + ': ' + message.body_xml);

	if conversation.identity == conferenceID:
		# Stop and start conf (only by Admins)
		# можно сломать глаза
		if message.body_xml.startswith("!down") or message.body_xml.startswith(u"!лежать"):
			if message.author in Admins: 
				global ForceCallFinished
				if not ForceCallFinished:
					print message.author + ': Call forced shutdown.'
					ForceCallFinished = True
					conversation.PostText(message.author + ': Call forced shutdown.', False)
				else:
					conversation.PostText('Call already down. Do nothing.', False)
			else:
				conversation.PostText(u'Недостаточно прав.', False)
		if message.body_xml.startswith("!up") or message.body_xml.startswith(u"!сидеть"):
			if message.author in Admins: 
				if ForceCallFinished:
					ForceCallFinished = False
					conversation.PostText(message.author + ': Call forced up.', False)
				else:
					conversation.PostText('Call already up. Do nothing.', False)
			else:
				conversation.PostText(u'Недостаточно прав.', False)

	if message.body_xml.startswith("!mute"):
		print 'liveConversation.type: ' + liveConversation.type 
		print 'liveConversation.identity: ' + liveConversation.identity
		liveConversation.MuteMyMicrophone()

Skype.Skype.OnMessage = OnMessage;


#----------------------------------------------------------------------------------
# Main loop
#


# We need the Participant list to get Participant property change events firing.
# If we don't have the participant objects - no events for us.
callParticipants = liveConversation.GetParticipants('ALL');

sleep(1)


# Start dummy conference (like /golive)
print 'Starting conference ID: ' + conferenceID

isCallFinished = False;
liveConversation.JoinLiveSession(conferenceToken)

sleep(1)

# mute microphone
liveConversation.MuteMyMicrophone()


sleep(3)


while True: 
	if not ForceCallFinished:
		if isCallFinished:
			print 'Conference STOPED. Restarting...'
			liveConversation.JoinLiveSession(conferenceToken)
			sleep(1)
			liveConversation.MuteMyMicrophone()
			isCallFinished = False
	elif not isCallFinished:
		liveConversation.LeaveLiveSession(False)
	sleep(1)
