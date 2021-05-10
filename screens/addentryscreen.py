#
#  RDpass - Addentryscreen
#

# Standard import requirements

# Kivy app requirements
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty
from kivy.metrics import dp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

# RD pass requirements
from RDconfig import rdconfig, rdstatus
from RDutils.cred_entry import CredEntry
from RDutils import rddb



class AddEntryScreen(Screen):
    '''
        AddEntryScreen that allows user to add a new entry
    '''

    font_hn_medium = rdconfig.hn_medium
    #font_hn_bold = rdconfig.hn_bold
    #font_hn = rdconfig.hn
    #font_hn_light = rdconfig.hn_light

    heading_text = StringProperty('Default Heading')
    titl_text = StringProperty('Enter Title')
    user_text = StringProperty('Enter Username / email')
    pswd_text = StringProperty('Enter Password')
    repd_text = StringProperty('Re-enter Password')
    cate_text = StringProperty('Enter Category')
    desc_text = StringProperty('Enter Description')
    # base_font_size = dp(30)
    # test_font_size = NumericProperty("30dp")
    fin_font_scale_fac = NumericProperty(0.1)
    # dialog = None

    def __init__(self, inputobj, **kwargs):
        super(AddEntryScreen, self).__init__(**kwargs)
        self.heading_text = 'New Entry'
        self.initate_text_field()
        self.fin_font_scale_fac = inputobj[0]


    def on_enter(self):
        self.initate_text_field()


    def initate_text_field(self):
        '''
            Function to initiate the text field on the screen, set all to blank
        '''
        self.titl_text = ''
        self.user_text = ''
        self.pswd_text = ''
        self.repd_text = ''
        self.cate_text = ''
        self.desc_text = ''


    def field_valid_check(self, field_id):
        '''
            Function to check if the field text is valid, if not set color to error color
        '''
        if self.ids[field_id].check_valid_text():
            return True
        else:
            self.ids[field_id].set_line_color_to_error_color()
            # self.ids[field_id].corn_hint_text = 'Please fill in the field'
            return False


    def confirmbutton_onpress(self, **kwargs):
        '''
            Function to confirm the new entry input when the confirm button is pressed
            1. Check if the input are valid, mark them red if not
            2. If all valid, create an object storing all input and pass to add_entry_command
        '''
        # Check if title, username, category fields are valid
        if self.field_valid_check('titl_simpfield') and self.field_valid_check('user_simpfield') and \
            self.field_valid_check('pswd_simpfield') and self.field_valid_check('cate_simpfield'):

            # Check if the password input is equal to the re-enter input
            if self.ids.pswd_simpfield.text == self.ids.repd_simpfield.text:

                # Check if the title input is already in use
                if not self.ids.titl_simpfield.text in rdstatus.config_status['title_list']:

                    # Create a instance of the CredEntry object
                    new_entry = CredEntry(title=self.ids.titl_simpfield.text,
                        user=self.ids.user_simpfield.text, password=self.ids.pswd_simpfield.text,
                        description=self.ids.desc_simpfield.text, category=self.ids.cate_simpfield.text)
                    add_status = rddb.add_entry_command(new_entry)
                    if add_status:
                        print(f'Entry {self.ids.titl_simpfield.text} added!')

                    self.show_success_dialog('Accepted entry: '+self.ids.titl_simpfield.text)
                else:
                    self.ids.titl_simpfield.set_line_color_to_error_color()
                    self.show_error_dialog('This entry already exists. Please use a different title.')

            else:
                self.ids.pswd_simpfield.set_line_color_to_error_color()
                self.show_error_dialog('Password does not match. Please confirm your password.')
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
                    text="Close", text_color=[0,0,0,0.8], font_size=dp(8 * self.fin_font_scale_fac),
                    on_release=self.back_to_menu)
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


    def back_to_menu(self, instance):
        '''
            Callback function for the dialog button
        '''
        # Close the dialog
        self.dialog.dismiss(force=True)

        # Back to the menuscreen
        app = MDApp.get_running_app()
        app.root.current = 'menuscreen'


    def on_fin_font_scale_fac(self, *args):
        '''
            When fin_font_scale_fac changes, propagate the fin_font_scale_fac to SimpleHintTextFields
        '''
        self.ids.titl_simpfield.fin_font_scale_fac_propagate = self.fin_font_scale_fac
        self.ids.user_simpfield.fin_font_scale_fac_propagate = self.fin_font_scale_fac
        self.ids.pswd_simpfield.fin_font_scale_fac_propagate = self.fin_font_scale_fac
        self.ids.repd_simpfield.fin_font_scale_fac_propagate = self.fin_font_scale_fac
        self.ids.cate_simpfield.fin_font_scale_fac_propagate = self.fin_font_scale_fac
        self.ids.desc_simpfield.fin_font_scale_fac_propagate = self.fin_font_scale_fac
