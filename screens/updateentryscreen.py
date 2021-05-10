#
#  RDpass - Updateentryscreen
#

# Standard import requirements

# Kivy app requirements
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.metrics import dp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

# RD pass requirements
from RDconfig import rdconfig
from RDutils.cred_entry import CredEntry
from RDutils import rddb



class UpdateEntryScreen(Screen):

    font_hn_medium = rdconfig.hn_medium
    font_hn_bold = rdconfig.hn_bold
    font_hn = rdconfig.hn
    #font_hn_light = rdconfig.hn_light

    title_text = StringProperty('Default Title')
    user_text = StringProperty('Default User')
    pswd_text = StringProperty('Default Password')
    repd_text = StringProperty('Re-enter Password')
    cate_text = StringProperty('Default Category')
    desc_text = StringProperty('Default Description')
    icon_shadow_color = ListProperty([])
    fin_font_scale_fac = NumericProperty(0.1)


    def __init__(self, inputobj, **kwargs):
        super(UpdateEntryScreen, self).__init__(**kwargs)
        self.title_text = inputobj[0][1]
        self.user_text = inputobj[0][2]
        self.pswd_text = inputobj[0][3]
        self.cate_text = inputobj[0][4]
        self.desc_text = inputobj[0][5]
        self.fin_font_scale_fac = inputobj[1]
        self.icon_shadow_color = inputobj[2]
        self.repd_text = ''


    def field_valid_check(self, field_id):
        if self.ids[field_id].check_valid_text():
            return True
        else:
            self.ids[field_id].set_line_color_to_error_color()
            # self.ids[field_id].corn_hint_text = 'Please fill in the field'
            return False


    def deletebutton_onpress(self, **kwargs):
        '''
            Function to show a popup with the confirm delete message and
            a confirm button when the delete button is pressed
        '''
        self.show_confirm_delete_dialog('Permanently delete this entry?')


    def savebutton_onpress(self, **kwargs):
        '''
            Function to check the updated entry input when the save button is pressed
            1. Check if the input are valid, mark them red if not
            2. If all valid, query the database and update the entry
        '''
        # Check if title, username, category fields are valid
        if self.field_valid_check('user_simpfield') and \
            self.field_valid_check('pswd_simpfield') and self.field_valid_check('cate_simpfield'):

            # Check if the password input is equal to the re-enter input
            if self.ids.pswd_simpfield.text == self.ids.repd_simpfield.text:

                # Create a instance of the CredEntry object (salt is also updated)
                new_entry = CredEntry(title=self.title_text,
                    user=self.ids.user_simpfield.text, password=self.ids.pswd_simpfield.text,
                    description=self.ids.desc_simpfield.text, category=self.ids.cate_simpfield.text)
                update_status = rddb.update_entry_command(self.title_text, new_entry)

                if update_status:
                    self.show_success_dialog('Updated entry: '+self.title_text)
                else:
                    self.show_error_dialog('Error in updating the entry. \n Please restart the app and try again')
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


    def show_confirm_delete_dialog(self, confirm_text):
        '''
            Show a popup with the confirm delete message and a button
        '''
        #if not self.dialog:
        self.dialog = MDDialog(
            text=confirm_text,
            pos_hint={'center_x': .5, 'center_y': .25},
            size_hint=(0.75,0.25),
            buttons=[
                MDFlatButton(
                    text="Delete", text_color=[1,0.2196,0.1372,0.9], font_size=dp(8 * self.fin_font_scale_fac),
                    on_release=self.confirm_delete_entry)
            ])
        self.dialog.ids.text.text_color = [1,0.2196,0.1372,1.0]
        self.dialog.ids.text.font_size = dp(16 * self.fin_font_scale_fac)
        self.dialog.open()


    def confirm_delete_entry(self, instance):
        '''
            Pass the title_text to delete_entry_command, then back_to_menu
        '''
        rddb.delete_entry_command('single', self.title_text)
        self.back_to_menu()


    def back_to_menu(self, *args):
        # Close the dialog
        self.dialog.dismiss(force=True)

        # Back to the menuscreen
        app = MDApp.get_running_app()
        app.root.current = 'menuscreen'


    def on_fin_font_scale_fac(self, *args):
        '''
            When fin_font_scale_fac changes, propagate the fin_font_scale_fac to SimpleHintTextFields
        '''
        self.ids.user_simpfield.fin_font_scale_fac_propagate = self.fin_font_scale_fac
        self.ids.pswd_simpfield.fin_font_scale_fac_propagate = self.fin_font_scale_fac
        self.ids.repd_simpfield.fin_font_scale_fac_propagate = self.fin_font_scale_fac
        self.ids.cate_simpfield.fin_font_scale_fac_propagate = self.fin_font_scale_fac
        self.ids.desc_simpfield.fin_font_scale_fac_propagate = self.fin_font_scale_fac
