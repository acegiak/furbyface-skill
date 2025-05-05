
from ovos_workshop.skills import OVOSSkill
from ovos_bus_client import MessageBusClient, Message
import time
import RPi.GPIO as GPIO
import threading



class Furbyface(OVOSSkill):
	talkingthread = None
	def __init__(self):
		OVOSSkill.__init__(self)

	def initialize(self):
		self.bellytime = True
		self.stop = False
		self.add_event('recognizer_loop:audio_output_start',
				   self.handler_talk_start)
		self.add_event('recognizer_loop:audio_output_end',
				   self.handler_talk_end)
		self.add_event('recognizer_loop:wakeword',
				   self.handler_wakeword)
		self.add_event('recognizer_loop:sleep',
				   self.handler_sleep)
		self.add_event('mycroft.speech.recognition.unknown',
				   self.handler_unknown)
		self.settings_change_callback = self.on_settings_changed
		self.on_settings_changed()  # Also run immediately on start

	def on_settings_changed(self):
		self.PWMA = self.settings.get('pwma_pin')
		self.AIN2 = self.settings.get('ain2_pin')
		self.AIN1 = self.settings.get('ain1_pin')
		self.STBY = self.settings.get('stby_pin')
		self.openeyes = self.settings.get('eye_open_time')
		self.talktime = self.settings.get('eye_close_time')
		GPIO.setmode(GPIO.BOARD)   # Declare the GPIO settings
		GPIO.setup(self.PWMA, GPIO.OUT) # Connected to PWMA
		GPIO.setup(self.AIN2, GPIO.OUT) # Connected to AIN2
		GPIO.setup(self.AIN1, GPIO.OUT) # Connected to AIN1
		GPIO.setup(self.STBY, GPIO.OUT) # Connected to STBY
		
		GPIO.setup(self.settings.get('timer_input_pin'), GPIO.IN,pull_up_down=GPIO.PUD_UP)
		GPIO.remove_event_detect(self.settings.get('timer_input_pin'))
		GPIO.add_event_detect(self.settings.get('timer_input_pin'),GPIO.FALLING, callback=self.stopbutton)
		
		GPIO.setup(self.settings.get('belly_input_pin'), GPIO.IN,pull_up_down=GPIO.PUD_UP)
		GPIO.remove_event_detectself.settings.get('belly_input_pin')
		GPIO.add_event_detect(self.settings.get('belly_input_pin'),GPIO.FALLING, callback=self.bellybutton)

		GPIO.setup(self.settings.get('back_input_pin'), GPIO.IN,pull_up_down=GPIO.PUD_UP)
		GPIO.remove_event_detect(self.settings.get('back_input_pin'))
		GPIO.add_event_detect(self.settings.get('back_input_pin'),GPIO.FALLING, callback=self.backbutton)

	def handler_wakeword(self, message):
		print("Furby got Wakeword")
		GPIO.output(self.AIN1, GPIO.HIGH) # Set AIN1
		GPIO.output(self.AIN2, GPIO.LOW) # Set AIN2
		GPIO.output(self.PWMA, GPIO.HIGH) # Set PWMA
		GPIO.output(self.STBY, GPIO.HIGH) # Disable STBY
		time.sleep(self.openeyes)
		GPIO.output(self.STBY, GPIO.LOW)
		GPIO.output(self.AIN2, GPIO.LOW)
		GPIO.output(self.AIN1, GPIO.LOW)
		GPIO.output(self.PWMA, GPIO.LOW)
		
	def handler_talk_start(self,message):
		print("Furby got talk start")
#		if Furbyface.talkingthread is None:
#			print("furby start talking")
#			Furbyface.talkingthread = TalkingThread()
#			Furbyface.talkingthread.start()
		GPIO.output(self.AIN1, GPIO.LOW) # Set AIN1
		GPIO.output(self.AIN2, GPIO.HIGH) # Set AIN2
		GPIO.output(self.PWMA, GPIO.HIGH) # Set PWMA
		GPIO.output(self.STBY, GPIO.HIGH) # Disable STBY

	def handler_talk_end(self,message):
		print("furby got talk end")
		self.gotosleep()
		
	def handler_sleep(self,message):
		print("furby got Sleep")
		self.gotosleep()
		
	def bellybutton(self,pin):
		print("got belly button")
		if self.bellytime:
			self.bellytime = False
			self.bus.emit(Message('mycroft.stop'))
			self.bus.emit(Message('speak', {"utterance": "oh! haha!", "lang": "en-GB"}))
			time.sleep(1)
			self.bellytime = True
	def backbutton(self,pin):
		print("got back button")
	def handler_unknown(self,message):
		print("I didn't understand")
		self.bus.emit(Message('speak', {"utterance": "pardon?", "lang": "en-GB"}))
	def gotosleep(self):
		print("trying to sleep")
#		TalkingThread.talk = False
#		if Furbyface.talkingthread is not None:
#			print("furby stop talking")
#			Furbyface.talkingthread.stop()
#			Furbyface.talkingthread.join()
#			Furbyface.talkingthread = None
		self.stop = True
		#while not GPIO.input(18):
		#	print("furby is trying to sleep")
		#time.sleep(1)
		#GPIO.output(self.AIN2, GPIO.LOW)
		#GPIO.output(self.PWMA, GPIO.LOW)
		#GPIO.output(self.STBY, GPIO.LOW)

	def stopbutton(self,pin):
		if self.stop:
			print("furby stop stop!")
			GPIO.output(self.AIN1, GPIO.HIGH) # Set AIN1
			GPIO.output(self.AIN2, GPIO.LOW) # Set AIN2
			GPIO.output(self.PWMA, GPIO.HIGH) # Set PWMA
			GPIO.output(self.STBY, GPIO.HIGH) # Disable STBY
			time.sleep(0.4)
			GPIO.output(self.STBY, GPIO.LOW)
			GPIO.output(self.AIN2, GPIO.LOW)
			GPIO.output(self.AIN1, GPIO.LOW)
			GPIO.output(self.PWMA, GPIO.LOW)
		self.stop = False


def create_skill():
	return Furbyface()

