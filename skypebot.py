# -*- coding: utf8 -*-
print('****************************************************************************');
print('SkypeKit Python Wrapper Tutorial: Making outgoing (conference) calls');
print('****************************************************************************');

# This example demonstrates, how to:
# 1. Make outgoing (multi-target) calls.
# 2. Catch voice activity events during calls.

# NB! You will need to launch the SkypeKit runtime before running this example.

#----------------------------------------------------------------------------------
# Importing necessary libraries. Note that you will need to set the keyFileName value
# in the keypair.py file.

import sys;
import keypair;
import signal
from time import sleep;
from random import random
import pickle
import random

sys.path.append(keypair.distroRoot + '/ipc/python');
sys.path.append(keypair.distroRoot + '/interfaces/skype/python');

try:
	import Skype;
except ImportError:
    raise SystemExit('Program requires Skype and skypekit modules');

#----------------------------------------------------------------------------------
# Taking skypename and password arguments from command-line.

if len(sys.argv) < 5:
	print('Usage: python hostconvo.py <skypename> <password> <conference identity> <token random word>');
	sys.exit();

accountName = sys.argv[1]
accountPsw  = sys.argv[2]
ConvoID     = '#sergey.brin1/$zhovner;c7cddac89532bab3'
ConvoToken  = sys.argv[4]


print 'ConvoID: ' + ConvoID
print 'ConvoToken: ' + ConvoToken


# help message (!help !рудз)
global HelpMessage
HelpMessage='''Привет, я робот Эльза.
!down  --- завершить звонок
!up    --- возобновить звонок
!who   --- показать свои права
!whois <login> --- показать права login
'''



# Personal welcomes
global PersonalWelcome
PersonalWelcome = pickle.load(open("PersonalWelcome.txt", "rb"))



# Bot owners (super users, can set Operators and Admins and everything, can't kick other owners) 
global Owners
Owners = pickle.load(open("Owners.txt", "rb"))

global OwnersWelcome
OwnersWelcome = pickle.load(open("OwnersWelcome.txt", "rb"))


# Operators 
# Can setrole to Adims
# Can't can't kick/change role of Owners/Operators
global Operators
Operators = pickle.load(open("Operators.txt", "rb"))


# Admins
# Can add/kick regular users
# Can set listener to regular users
global Admins
Admins = pickle.load(open("Admins.txt", "rb"))


# Listeners (who can listen and read chat but can't write and speak)
global Listeners
Listeners = pickle.load(open("Listeners.txt", "rb"))


# Banned 
# Can't join into conference from outside
global Banned
Banned = pickle.load(open("Banned.txt", "rb"))



#
# 
#
#


# kill when press Ctrl+C
def signal_handler(signal, frame):
	print ' Aborted.'
	liveConversation.LeaveLiveSession(False)
	MySkype.stop();
signal.signal(signal.SIGINT, signal_handler)


# Collecting call target list from command-line arguments.
# 3rd and subsequent arguments are our call targets.
#callTargets = [];
#for i in range(3, len(sys.argv)):
#	callTargets.append(sys.argv[i]);
	
loggedIn		= False;
isCallFinished	= False;

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


###
###  create main Conversation object with ConvoID
###

# global need for visible inside OnMessage and ParticipantOnChange
global liveConversation

liveConversation = MySkype.GetConversationByIdentity(ConvoID)


# possible to hangup conference manually 
ForceCallFinished = False


#----------------------------------------------------------------------------------
# Defining our own Participant property change callback
# Unlike with incoming calls - we can assume that we already have the Conversation
# object - as we retrieved it ourselves when initiating the call. This makes our life
# much easier. So much so that we can make do without any Conversation callback 
# at all and put all our logic into Participant class.
#
# We can use the self.voice_status == 'SPEAKING' property change to detect when 
# any given participant reached live status and 'VOICE_STOPPED' for detecting when 
# they left the call.
# 
# When the self.voice_status == 'VOICE_STOPPED' fires for ourselves - the call has 
# ended. Note that in case of conference call, the rest of the participants will 
# drop too - when the conference host (us) went non-live.

def ParticipantOnChange (self, property_name):
	if property_name == 'voice_status':
		if self.identity != accountName:
			if self.voice_status == 'SPEAKING':
				print(self.identity + ' has joined the call.');
				if self.identity in PersonalWelcome:
					liveConversation.PostText(PersonalWelcome[self.identity], False)
				if self.identity in Owners:
					rlen = len(OwnersWelcome) - 1 
					liveConversation.PostText(OwnersWelcome[random.randint(0,rlen)], False)
			if self.voice_status == 'VOICE_STOPPED':
				print(self.identity + ' has left the call.');
		if (self.identity == accountName) and (self.voice_status == 'VOICE_STOPPED'):
			print 'STOPED'
			global isCallFinished;
			isCallFinished = True;
	if property_name == 'sound_level':
		print(self.identity + ' sound level: ' + str(self.sound_level));

Skype.Participant.OnPropertyChange = ParticipantOnChange;
	

#
# incoming messages
#


def OnMessage(self, message, changesInboxTimestamp, supersedesHistoryMessage, conversation):
#	if message.author != accountName and conversation.identity == ConvoID and message.body_xml == u'значение знаешь?':
#		print(message.author_displayname + ': ' + message.body_xml);
#		conversation.PostText(u'кон фач', False);
	if conversation.identity == ConvoID:

		# !help
		if message.body_xml.startswith("!help") or message.body_xml.startswith(u"!рудз"):
			conversation.PostText(HelpMessage, False)

		# Stop and start conf (only by Owners and Operators)
		# можно сломать глаза
		if message.body_xml.startswith("!down") or message.body_xml.startswith(u"!лежать"):
			if message.author in Owners or message.author in Operators: 
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
			if message.author in Owners or message.author in Operators: 
				if ForceCallFinished:
					ForceCallFinished = False
					conversation.PostText(message.author + ': Call forced up.', False)
				else:
					conversation.PostText('Call already up. Do nothing.', False)
			else:
				conversation.PostText(u'Недостаточно прав.', False)


		# Who am I
		if message.body_xml.startswith("!who ") or message.body_xml.startswith(u"!кто я"):
			if message.author in Owners:
				conversation.PostText(u'Вы находитесь в группе владелецы (OWNER).', False)
			elif message.author in Operators:
				conversation.PostText(u'Вы находитесь в группе операторы (OP).', False)
			elif message.author in Admins:
				conversation.PostText(u'Вы находитесь в группе администраторы (ADMIN).', False)
			else:
				conversation.PostText(u'Вы никто.', False)

		# Whois
		if message.body_xml.startswith("!whois ") or message.body_xml.startswith(u"!кто "):
			sp_message = message.body_xml.split(' ')
			if len(sp_message) != 2:
				 conversation.PostText(u'Неправильный синтаксис.\n!whois skypename', False)
			elif 
	




Skype.Skype.OnMessage = OnMessage


###
###
###

sleep(2)
print 'Get GetConversationByIdentity...'

# We need the Participant list to get Participant property change events firing.
# If we don't have the participant objects - no events for us.
callParticipants = liveConversation.GetParticipants('ALL');

sleep(1)

# Start dummy conference (like /golive)
print 'Starting conference ID: ' + ConvoID

isCallFinished = False;
liveConversation.JoinLiveSession(ConvoToken)


sleep(3)


while True: 
	if not ForceCallFinished:
		if isCallFinished:
			print 'Conference STOPED. Restarting...'
			liveConversation.JoinLiveSession(ConvoToken)
			isCallFinished = False
	elif not isCallFinished:
		liveConversation.LeaveLiveSession(False)
	sleep(1)
