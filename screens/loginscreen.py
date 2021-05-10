#
#  RDpass - LoginScreen
#

# Standard import requirements
import logging
# import sys

# Kivy app requirements
from kivy.uix.textinput import TextInput
from kivy.properties import NumericProperty, ListProperty
from kivy.uix.spinner import SpinnerOption
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from kivy.metrics import dp
from kivymd.app import MDApp

# RD pass requirements
from RDconfig import rdstatus, rdconfig
from RDutils import rdutils, rdmenu

# RD pass - create the RDPass login logger
rdpasslogin_logger = logging.getLogger('rdpasslogin')
rdpasslogin_logger.setLevel(logging.DEBUG)

# create console handler andset level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter and add to logger
formatter = logging.Formatter('%(name)s/%(levelname)s - %(message)s')
ch.setFormatter(formatter)
rdpasslogin_logger.addHandler(ch)

# Fonts (Set in rdconfig)
# hn_medium = './font/HelveticaNeue-Medium-11.ttf'
# hn_bold = './font/HelveticaNeue-Bold-02.ttf'
# hn = './font/HelveticaNeue-01.ttf'
# hn_light = './font/HelveticaNeue-Light-08.ttf'



class LsPWInput(TextInput):
    touch_count = 0

    def on_touch_down(self, touch):
        # Only change these on the first time touch down
        if self.collide_point(*touch.pos) and self.touch_count == 0 and self.disabled != True:
            self.text = ''
            self.password = True
            self.foreground_color = [1,1,1,1]
            self.touch_count = self.touch_count + 1
        #    self.foreground_color = [1,1,1,1] #root.button_press_color
        elif self.collide_point(*touch.pos) and self.touch_count == 1 and self.disabled != True:
            self.parent.status_label.text = ''

        return super(LsPWInput, self).on_touch_down(touch)


class LsSpinnerOption(SpinnerOption):
    trans_font_scale = 1.0
    font_hn_medium = rdconfig.hn_medium
    button_norm_color = [0.125, 0.224, 0.631, 1]  #2039a1
    spinner_norm_color =  [0.298, 0.545, 0.859, 1] # 4c8bdb #[0.075, 0.133, 0.38, 1]  #132261

    def __init__(self, **kwargs):
        self.font_size = dp(self.trans_font_scale*13)
        super(LsSpinnerOption, self).__init__(**kwargs)


class LoginScreen(Screen):

    font_hn_medium = rdconfig.hn_medium
    font_hn_bold = rdconfig.hn_bold
    font_hn = rdconfig.hn
    font_hn_light = rdconfig.hn_light

    login_button_color = ListProperty([0.125, 0.224, 0.631, 1])
    cdb_button_color = ListProperty([0.125, 0.224, 0.631, 1])

    screen_bg_color = [0.161, 0.439, 0.796, 1]    #2970cb

    password_field_color = [0.643, 0.769, 0.929, 0.25]  #a4c4ed

    button_text_norm_color = [1,1,1, 1]
    button_text_grayout_color = [0.545, 0.545, 0.545, 1]  #8b8b8b

    button_norm_color = [0.125, 0.224, 0.631, 1]  #2039a1
    button_press_color = [0.075, 0.133, 0.38, 1]  #132261
    button_grayout_color = [0.847, 0.847, 0.847, 0.8]  #d8d8d8

    fin_font_scale_fac = NumericProperty(1)
    base_font_scale_fac = NumericProperty(1)
    db_avail_list = ListProperty([])


    def __init__(self, *args):
        super(LoginScreen, self).__init__()
        self.window_size_safe = [0, 0]
        self.window_pixel_dim_safe = [0, 0]
        Window.bind(on_resize = self.resolution_check_update)

        self.window_width_min = MDApp.get_running_app().wininit[0]
        self.window_height_min = MDApp.get_running_app().wininit[1]

        # Initialize parameters
        db_path = rdstatus.config_status['db_path']
        config_path = rdstatus.config_status['config_path']

        # Print the initization
        print('##############################################')
        print('')
        print('         RD Password Manager - v1.0')
        print('')
        print('##############################################')

        # Check if database exist and return an available list for login
        self.db_avail_list = []
        db_list = rdutils.scan_db_dir(db_path)

        # If no DB exist, disable the login button
        if len(db_list) == 0:
            rdpasslogin_logger.info('Found no DB.')
            self.login_button_color = self.button_grayout_color
            self.ids['login_button'].disabled = True
            self.ids['login_button'].color = self.button_text_grayout_color
            self.ids['db_selector'].disabled = True
            self.ids['db_selector'].color = self.button_text_grayout_color
            self.ids['password_input'].disabled = True

        else:
            rdpasslogin_logger.info(f'Found {len(db_list)} DB.')

            # Check if the config file exists for each db
            config_avail_list = rdutils.check_config_file(config_path, db_path)

            for db_item, config_flag in zip(db_list, config_avail_list):
                if config_flag == 1:
                    self.db_avail_list.append(db_item)


    def option_select_db_login(self, *args):
        sel_db_name = self.ids['db_selector'].text
        sel_key = self.ids['password_input'].text

        if sel_db_name == 'Press to select a database':
            self.ids['db_selector'].color = [1,0,0,1]     # Red to warn user to select a database
        else:
            rdpasslogin_logger.info(f'User selected DB: {sel_db_name}')
            if rdmenu.load_login_menu(self.db_avail_list, 'l', sel_db_name, sel_key):
                # Switch to menu screen if login successful
                self.manager.current='menuscreen'
                # rddb.list_entry_command('all')
                # rdmenu.load_menu_command()
            else:
                self.ids['status_label'].text = 'Wrong password. Try again!'


    def option_create_new_db(self, *args):
        '''
            Function to switch to create db screen when create_new_db button is pressed
            Pass the db_avail_list and fin_font_scale_fac to create db screen
        '''
        app = MDApp.get_running_app()
        app.init_createdb_screen([self.db_avail_list, self.fin_font_scale_fac])
        app.root.current = 'createdbscreen'


    def multiply_list(self, in_list, value):
        '''
            Simple function multiply values in a whole list
        '''
        return [element * value for element in in_list]


    def on_fin_font_scale_fac(self, *args):
        '''
            When fin_font_scale_fac changes, modify the dropdown list of the spinner
            and trigger the rebuild of the option_cls of the dropdown
        '''
        LsSpinnerOption.trans_font_scale = self.fin_font_scale_fac

        # trigger rebuild of dropdown by changing option_cls
        self.ids.db_selector.option_cls = 'SpinnerOption'
        self.ids.db_selector.option_cls = 'LsSpinnerOption'


    def resolution_update_otherscreen(self, scale_fac):
        try:
            MDApp.get_running_app().root.get_screen('menuscreen').fin_font_scale_fac = self.fin_font_scale_fac
            rdpasslogin_logger.debug("Changed fin_font_scale_fac on menuscreen")
        except:
            rdpasslogin_logger.debug("No existing Menu Screen")

        try:
            MDApp.get_running_app().root.get_screen('entryscreen').fin_font_scale_fac = self.fin_font_scale_fac
            rdpasslogin_logger.debug("Changed fin_font_scale_fac on entryscreen")
        except:
            rdpasslogin_logger.debug("No existing Entry Screen")

        try:
            MDApp.get_running_app().root.get_screen('addentryscreen').fin_font_scale_fac = self.fin_font_scale_fac
            rdpasslogin_logger.debug("Changed fin_font_scale_fac on addentryscreen")
        except:
            rdpasslogin_logger.debug("No existing AddEntry Screen")

        try:
            MDApp.get_running_app().root.get_screen('updateentryscreen').fin_font_scale_fac = self.fin_font_scale_fac
            rdpasslogin_logger.debug("Changed fin_font_scale_fac on updateentryscreen")
        except:
            rdpasslogin_logger.debug("No existing UpdateEntry Screen")

        try:
            MDApp.get_running_app().root.get_screen('createdbscreen').fin_font_scale_fac = self.fin_font_scale_fac
            rdpasslogin_logger.debug("Changed fin_font_scale_fac on createdbscreen")
        except:
            rdpasslogin_logger.debug("No existing CreateDB Screen")


    def resolution_check_update(self, instance, x, y):
        '''
            Check and update the resolution of the text on screen
        '''
        # Initialize
        if self.window_size_safe == [0, 0]:
            self.window_size_safe = Window._get_system_size()
            self.window_pixel_dim_safe = [x, y]
            self.display_num = 0
            rdpasslogin_logger.debug(f'Saved the initiated size_safe: {self.window_size_safe}')
            rdpasslogin_logger.debug(f'Pixel_dim_safe: {self.window_pixel_dim_safe}, Size_safe: {self.window_size_safe}')
            #print(f'Pixel_dim_safe: {self.window_pixel_dim_safe}, Size_safe: {self.window_size_safe}, Current_pixel_dim: {window_current_pixel_dim}')
            return True

        # Check whether the resize is caused by switching monitors or resizing
        if Window._get_system_size() == self.window_size_safe:
            window_current_pixel_dim = [x, y]

            # Check if the window pixel dimensions suddenly changes (in my retina display it is 2x less when move to external)
            if self.window_pixel_dim_safe == self.multiply_list(window_current_pixel_dim, 2):
                rdpasslogin_logger.info('Resizing font for External Display')
                # Update the font_size, x,y change should be identical
                scale_fac = window_current_pixel_dim[0]/self.window_pixel_dim_safe[0]
                self.fin_font_scale_fac = self.fin_font_scale_fac * scale_fac
                self.base_font_scale_fac = 0.5
                self.display_num = 1

                # Also update other screens
                self.resolution_update_otherscreen(self.fin_font_scale_fac)

            # Check if the window pixel dimensions suddenly changes (in my retina display it is 2x more when move to retina)
            elif self.window_pixel_dim_safe == self.multiply_list(window_current_pixel_dim, 0.5):
                rdpasslogin_logger.info('Resizing font for Retina Display')
                # Update the font_size, x,y change should be identical
                scale_fac = window_current_pixel_dim[0]/self.window_pixel_dim_safe[0]
                self.fin_font_scale_fac = self.fin_font_scale_fac * scale_fac
                #self.base_font_scale_fac = self.fin_font_scale_fac
                #print(self.base_font_scale_fac, self.fin_font_scale_fac)
                self.base_font_scale_fac = 1
                self.display_num = 0

                # Also update other screens
                self.resolution_update_otherscreen(self.fin_font_scale_fac)

            # Saved the current window pixel dimensions
            self.window_pixel_dim_safe = window_current_pixel_dim
        else:
            window_current_pixel_dim = [x, y]

            # Update the font size (Enlarge font size after window resize)
            # https://www.reddit.com/r/kivy/comments/86okok/update_font_sizes_in_a_layoutwidget_after_window/
            if self.display_num == 0:
                scale_fac_display = 2
            elif self.display_num == 1:
                scale_fac_display = 1
            scale_fac = min(Window.width/(scale_fac_display * self.window_width_min), Window.height/(scale_fac_display * self.window_height_min))
            self.fin_font_scale_fac = self.base_font_scale_fac * scale_fac
#            print(self.base_font_scale_fac, self.fin_font_scale_fac, scale_fac)
            self.window_pixel_dim_safe = window_current_pixel_dim
            self.window_size_safe = Window._get_system_size()

            # Also update other screens
            self.resolution_update_otherscreen(self.fin_font_scale_fac)

