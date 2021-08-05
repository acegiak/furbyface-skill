from mycroft import MycroftSkill, intent_file_handler
from mycroft.messagebus import Message
import time
import RPi.GPIO as GPIO
import threading


class TalkingThread(threading.Thread):
    talk = False
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self,  *args, **kwargs):
        super(TalkingThread, self).__init__(*args, **kwargs)
        self.PWMA = 7
        self.AIN2 = 15
        self.AIN1 = 13
        self.STBY = 11
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        print("I am thread")
        TalkingThread.talk = True
#        GPIO.output(self.PWMA, GPIO.HIGH)
        while TalkingThread.talk:
            #print("I am thread {} doing something".format(id))            GPIO.output(15, GPIO.LOW)
#            GPIO.output(self.STBY, GPIO.LOW)
#            GPIO.output(13, GPIO.HIGH)
#            GPIO.output(15, GPIO.LOW)
#            GPIO.output(self.STBY, GPIO.HIGH)
#            time.sleep(0.15)
#            GPIO.output(11, GPIO.LOW)
#            GPIO.output(15, GPIO.HIGH)
#            GPIO.output(13, GPIO.LOW)
#            GPIO.output(11, GPIO.HIGH)
#            time.sleep(0.15)
            if self.stopped():
                print("  Exiting loop.")
                break
        print("Thread  signing off")
#        GPIO.output(self.PWMA, GPIO.HIGH)
#        GPIO.output(self.AIN1, GPIO.LOW)
#        GPIO.output(self.AIN2, GPIO.HIGH)
#        GPIO.output(self.STBY, GPIO.HIGH)
        #GPIO.output(15, GPIO.LOW)
        #GPIO.output(11, GPIO.LOW)
        #GPIO.output(12, GPIO.LOW)



class Furbyface(MycroftSkill):
    talkingthread = None
    def __init__(self):
        MycroftSkill.__init__(self)
        self.PWMA = 7
        self.AIN2 = 15
        self.AIN1 = 13
        self.STBY = 11
        self.openeyes = 0.25
        self.talktime = 0.25
        GPIO.setmode(GPIO.BOARD)   # Declare the GPIO settings
        GPIO.setup(self.PWMA, GPIO.OUT) # Connected to PWMA
        GPIO.setup(self.AIN2, GPIO.OUT) # Connected to AIN2
        GPIO.setup(self.AIN1, GPIO.OUT) # Connected to AIN1
        GPIO.setup(self.STBY, GPIO.OUT) # Connected to STBY
        self.stop = False
        GPIO.setup(12, GPIO.IN,pull_up_down=GPIO.PUD_UP)
        GPIO.remove_event_detect(12)
        GPIO.add_event_detect(12,GPIO.FALLING, callback=self.stopbutton)
        GPIO.setup(16, GPIO.IN,pull_up_down=GPIO.PUD_UP)
        GPIO.remove_event_detect(16)
        GPIO.add_event_detect(16,GPIO.FALLING, callback=self.bellybutton)
        GPIO.setup(18, GPIO.IN,pull_up_down=GPIO.PUD_UP)
        GPIO.remove_event_detect(18)
        GPIO.add_event_detect(18,GPIO.FALLING, callback=self.backbutton)
        self.bellytime = True

    def initialize(self):
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
#        if Furbyface.talkingthread is None:
#            print("furby start talking")
#            Furbyface.talkingthread = TalkingThread()
#            Furbyface.talkingthread.start()
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
#        TalkingThread.talk = False
#        if Furbyface.talkingthread is not None:
#            print("furby stop talking")
#            Furbyface.talkingthread.stop()
#            Furbyface.talkingthread.join()
#            Furbyface.talkingthread = None
        GPIO.output(self.AIN1, GPIO.LOW) # Set AIN1
        GPIO.output(self.AIN2, GPIO.HIGH) # Set AIN2
        GPIO.output(self.PWMA, GPIO.HIGH) # Set PWMA
        GPIO.output(self.STBY, GPIO.HIGH) # Disable STBY
        self.stop = True
        #while not GPIO.input(18):
        #    print("furby is trying to sleep")
        #time.sleep(1)
        #GPIO.output(self.AIN2, GPIO.LOW)
        #GPIO.output(self.PWMA, GPIO.LOW)
        #GPIO.output(self.STBY, GPIO.LOW)

    def stopbutton(self,pin):
        if self.stop:
            print("furby stop stop!")
            time.sleep(0.4)
            GPIO.output(self.STBY, GPIO.LOW)
            GPIO.output(self.AIN2, GPIO.LOW)
            GPIO.output(self.AIN1, GPIO.LOW)
            GPIO.output(self.PWMA, GPIO.LOW)
        self.stop = False


def create_skill():
    return Furbyface()

