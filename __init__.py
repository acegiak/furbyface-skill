from mycroft import MycroftSkill, intent_file_handler


class Furbyface(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('furbyface.intent')
    def handle_furbyface(self, message):
        self.speak_dialog('furbyface')


def create_skill():
    return Furbyface()

