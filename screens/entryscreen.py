#
#  RDpass - Entryscreen (PEP8)
#

# Standard import requirements

# Kivy app requirements
# from kivy.lang import Builder
# from kivy.core.window import Window
from kivymd.app import MDApp
from kivy.core.clipboard import Clipboard
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty, ListProperty

# RD pass requirements
from RDconfig import rdconfig
#from RDutils import rddb
from RDutils.rdcomponents import SimpleHintTextField, Placeholder, \
                                 InTextPlaceholder



class EntryScreen(Screen):
    '''
        EntryScreen that displays the information of individual entry
    '''

    font_hn_medium = rdconfig.hn_medium
    font_hn_bold = rdconfig.hn_bold
    font_hn = rdconfig.hn
    #font_hn_light = rdconfig.hn_light

    title_text = StringProperty('Default Title')
    user_text = StringProperty('Default User')
    pswd_text = StringProperty('Default Password')
    cate_text = StringProperty('Default Category')
    desc_text = StringProperty('Default Description')
    icon_shadow_color = ListProperty([])
    fin_font_scale_fac = NumericProperty(0.1)

    def __init__(self, inputobj, **kwargs):
        super(EntryScreen, self).__init__(**kwargs)
        # Testing Phrases
        # self.title_text = 'Netflix'
        # self.user_text = 'jeffreyrdcs'        #in_user_text
        # self.pswd_text = 'This is a fake password'
        # self.cate_text = 'Media'
        # self.desc_text = "Hi I am a text field. This is supposed to be quite long and stupid." + \
        #                  "This is supposed to be quite long and stupid."
        self.title_text = inputobj[0][1]
        self.user_text = inputobj[0][2]
        self.pswd_text = inputobj[0][3]
        self.cate_text = inputobj[0][4]
        self.desc_text = inputobj[0][5]
        self.fin_font_scale_fac = inputobj[1]
        self.icon_shadow_color = inputobj[2]


    def copybutton_onpress(self, **kwargs):
        '''
            Function to put copy corresponding text into clipboard when the button is pressed
        '''
        # print('PRESS - COPY',kwargs['copyfield'])
        Clipboard.copy(self.ids[kwargs['copyfield']].text)


    def updatebutton_onpress(self, **kwargs):
        '''
            Function to move to the update screen when the update button is pressed
        '''
        # Package the entry into a list without querying the database again
        out_entry_list = [0, self.title_text, self.user_text, self.pswd_text,
                             self.cate_text, self.desc_text]

        app = MDApp.get_running_app()
        tmp_fin_font_scale_fac = app.root.get_screen('entryscreen').fin_font_scale_fac

        # Initiate the update screen
        app.init_updateentry_screen([out_entry_list, tmp_fin_font_scale_fac, self.icon_shadow_color])
        app.root.current = 'updateentryscreen'


    def on_fin_font_scale_fac(self, *args):
        '''
            When fin_font_scale_fac changes, propagate the fin_font_scale_fac
            to SimpleHintTextFields
        '''
        self.ids.user_simpfield.fin_font_scale_fac_propagate = self.fin_font_scale_fac
        self.ids.pswd_simpfield.fin_font_scale_fac_propagate = self.fin_font_scale_fac
        self.ids.cate_simpfield.fin_font_scale_fac_propagate = self.fin_font_scale_fac
        self.ids.desc_simpfield.fin_font_scale_fac_propagate = self.fin_font_scale_fac
