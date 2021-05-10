#
#  RDpass - Createdbscreeen
#

# Standard import requirements
import sys

# Kivy app requirements
from kivymd.app import MDApp
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.metrics import dp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

# RD pass requirements
from RDconfig import rdconfig, rdstatus
from RDutils import rddb



class CreateDBScreen(Screen):

    screen_bg_color = [0.161, 0.439, 0.796, 0.05]    #2970cb  0.05 alpha

    font_hn_medium = rdconfig.hn_medium
    font_hn_bold = rdconfig.hn_bold
    font_hn = rdconfig.hn
    #font_hn_light = rdconfig.hn_light

    heading_text = StringProperty('Default Heading')
    dbnm_text = StringProperty('Enter Database name')
    dbmk_text = StringProperty('Enter Master key')
    remk_text = StringProperty('Re-enter Master key')
    db_avail_list = ListProperty([])
    fin_font_scale_fac = NumericProperty(0.1)

    def __init__(self, inputobj, **kwargs):
        super(CreateDBScreen, self).__init__(**kwargs)
        self.heading_text = 'New Database'
        self.dbnm_text = ''
        self.dbmk_text = ''
        self.remk_text = ''
        self.db_avail_list = inputobj[0]
        self.fin_font_scale_fac = inputobj[1]


    def field_valid_check(self, field_id):
        if self.ids[field_id].check_valid_text():
            return True
        else:
            self.ids[field_id].set_line_color_to_error_color()
            return False


    def db_valid_check(self, db_name, db_avail_list):
        '''
            Return True if the db_name is available (i.e. not in the list)
        '''
        # Only use lower case for the DB name
        # Also remove trailing spaces
        return not (db_name.strip().lower() in db_avail_list)


    def confirmbutton_onpress(self, **kwargs):
        '''
            Function to confirm the new database input when the confirm button is pressed
            1. Check if the input are valid, mark them red if not
            2. If all valid, create an object storing all input
        '''
        # Check if title, username, category fields are valid
        if self.field_valid_check('dbnm_simpfield') and \
            self.field_valid_check('dbmk_simpfield') and self.field_valid_check('remk_simpfield'):

            # Check if the master key input is equal to the re-enter input and
            if self.ids.dbmk_simpfield.text == self.ids.remk_simpfield.text:

                # Check if the name of the database is available
                if self.db_valid_check(self.ids.dbnm_simpfield.text, self.db_avail_list):

                    # Pass the input to create_new_db to create a new database
                    db_path = rdstatus.config_status['db_path']
                    config_path = rdstatus.config_status['config_path']
                    db_para = [self.ids.dbnm_simpfield.text, self.ids.dbmk_simpfield.text]
                    rddb.create_new_db_gui(config_path, db_path, db_para)

                    self.show_success_dialog('Created new database: '+self.ids.dbnm_simpfield.text+'\n\n'+
                                             'Please restart the app to access the new database.')
                else:
                    self.ids.dbnm_simpfield.set_line_color_to_error_color()
                    self.show_error_dialog('Database name already in use. Please provide a different name.')

            else:
                self.ids.dbmk_simpfield.set_line_color_to_error_color()
                self.show_error_dialog('Master key does not match. Please confirm your master key.')
        else:
            self.show_error_dialog('Please fill in the required fields.')


    def show_success_dialog(self, error_text):
        '''
            Show a popup with the accepted entry message and a button
        '''
        #if not self.dialog:
        self.dialog = MDDialog(
            text=error_text,
            pos_hint={'center_x': .5, 'center_y': .25},
            size_hint=(0.75,0.25),
            buttons=[
                MDFlatButton(
                    text="Quit", text_color=[0,0,0,0.8], font_size=dp(8 * self.fin_font_scale_fac),
                    on_release=self.quit_app)
                    # size_hint=(1,0.25),
                    # pos_hint={'center_x': .5, 'center_y': .25},
            ])
        self.dialog.ids.text.text_color = [0,0,0,0.8]
        self.dialog.ids.text.font_size = dp(16 * self.fin_font_scale_fac)
        self.dialog.open()


    def show_error_dialog(self, error_text):
        '''
            Show a popup with the error message
        '''
        #if not self.dialog:
        self.dialog = MDDialog(
            text=error_text,
            pos_hint={'center_x': .5, 'center_y': .25},
            size_hint=(0.75,0.25))
        self.dialog.ids.text.text_color = [0,0,0,0.8]
        self.dialog.ids.text.font_size = dp(16 * self.fin_font_scale_fac)
        self.dialog.open()


    def quit_app(self, instance):
        # Close the dialog
        self.dialog.dismiss(force=True)

        # Quit the app
        sys.exit()


    def on_fin_font_scale_fac(self, *args):
        '''
            When fin_font_scale_fac changes, propagate the fin_font_scale_fac to SimpleHintTextFields
        '''
        self.ids.dbnm_simpfield.fin_font_scale_fac_propagate = self.fin_font_scale_fac
        self.ids.dbmk_simpfield.fin_font_scale_fac_propagate = self.fin_font_scale_fac
        self.ids.remk_simpfield.fin_font_scale_fac_propagate = self.fin_font_scale_fac
