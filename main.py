#
#  RD Pass
#

# Standard import requirements
import os
import logging

# Kivy app requirements
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager
from screens.loginscreen import LoginScreen
from screens.menuscreen import MenuScreen
from screens.entryscreen import EntryScreen
from screens.addentryscreen import AddEntryScreen
from screens.updateentryscreen import UpdateEntryScreen
from screens.createdbscreen import CreateDBScreen

# RD pass requirements
# from RDconfig import rdstatus, rdconfig
# from RDutils import rdutils, rdmenu, rddb

# Text rendering
os.environ['KIVY_TEXT'] = 'pil'

# Window properties
# Window.size = (750, 1334)      # Mimic iPhone 8 resolution
# wininit = (450,650)
# Window.size = wininit

# RD pass - create the RDPass logger
rdpass_logger = logging.getLogger('rdpass')
rdpass_logger.setLevel(logging.INFO)

# create console handler and set level to INFO
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# create formatter and add to logger
formatter = logging.Formatter('%(name)s/%(levelname)s - %(message)s')
ch.setFormatter(formatter)
rdpass_logger.addHandler(ch)



class RDScreenManager(ScreenManager):
    pass


class RdpassApp(MDApp):
    '''
        The main RD Pass app
    '''
    wininit = (450, 650)
    #Window.size = wininit
    #Window.minimum_width = wininit[0]
    #Window.minimum_height = wininit[1]

    def build(self):
        '''
            Entry-related screens are now created when called
        '''

        # Create the screen manager
        global sm
        sm = RDScreenManager()

        # Add the required screens
        sm.add_widget(LoginScreen())
        sm.add_widget(MenuScreen())
        # sm.add_widget(AddEntryScreen())
        # sm.add_widget(UpdateEntryScreen())
        # sm.add_widget(CreateDBScreen())
        return sm


    def init_entry_screen(self, input_obj):
        '''
          Entry screen are generated when called to limit the number of
          screens opened simultaneously. The existing entry screen is
          deleted when a new one is called.
        '''
        try:
            sm.remove_widget(self.entryscreen)
            rdpass_logger.debug("Deleted existing Entry Screen")
        except:
            rdpass_logger.debug("No existing Entry Screen")
        self.entryscreen = EntryScreen(inputobj=input_obj)
        sm.add_widget(self.entryscreen)


    def init_addentry_screen(self, input_obj):
        '''
          Add entry screen are generated when called to avoid the information
          that the user enters are retained on the screen
        '''
        try:
            sm.remove_widget(self.addentryscreen)
            rdpass_logger.debug("Deleted existing Add Entry Screen")
        except:
            rdpass_logger.debug("No existing Add Entry Screen")
        self.addentryscreen = AddEntryScreen(inputobj=input_obj)
        sm.add_widget(self.addentryscreen)


    def init_updateentry_screen(self, input_obj):
        '''
          Update entry screen are generated when called to avoid the information
          that the user enters are retained on the screen
        '''
        try:
            sm.remove_widget(self.updateentryscreen)
            rdpass_logger.debug("Deleted existing Update Entry Screen")
        except:
            rdpass_logger.debug("No existing Update Entry Screen")
        self.updateentryscreen = UpdateEntryScreen(inputobj=input_obj)
        sm.add_widget(self.updateentryscreen)


    def init_createdb_screen(self, input_obj):
        '''
          Create db screen are generated when called
        '''
        try:
            sm.remove_widget(self.createdbscreen)
            rdpass_logger.debug("Deleted existing Create DB Screen")
        except:
            rdpass_logger.debug("No existing Create DB Screen")
        self.createdbscreen = CreateDBScreen(inputobj=input_obj)
        sm.add_widget(self.createdbscreen)


# Start the App
if __name__ == "__main__":
    RdpassApp().run()
