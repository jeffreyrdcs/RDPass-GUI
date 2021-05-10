#
#  RDpass - Menuscreen
#

# Standard import requirements
import weakref
import sys
import logging

# Kivy app requirements
from kivymd.app import MDApp
from kivymd.uix.button import MDIconButton
from kivymd.uix.card import MDCardSwipe
from kivymd.uix.toolbar import MDToolbar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.utils import get_color_from_hex

# RD pass requirements
from RDconfig import rdstatus, rdconfig
from RDutils.rdcomponents import SimpTextFieldRound, TwoLineIconListItemMod
from RDutils import rddb
#rdutils, rdmenu,

# RD pass - create the RDPass menu logger
rdpassmenu_logger = logging.getLogger('rdpassmenu')
rdpassmenu_logger.setLevel(logging.DEBUG)

# create console handler andset level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter and add to logger
formatter = logging.Formatter('%(name)s/%(levelname)s - %(message)s')
ch.setFormatter(formatter)
rdpassmenu_logger.addHandler(ch)



class TitleBar(MDToolbar):
    '''
        Title bar on the head of the screen
    '''
    font_hn_medium = rdconfig.hn_medium

    def __init__(self, **kwargs):
        super(TitleBar, self).__init__(**kwargs)
        Clock.schedule_once(lambda x: self.set_font(0))

    def set_font(self, value):
        self.ids.label_title.font_size  = dp(20)
        self.ids.label_title.font_name  = self.font_hn_medium


class SearchBarFieldRound(SimpTextFieldRound):
    '''
       Inherit from SimpTextFieldRound.
       Added set_clearbutton_color to change the search_clearbutton color
       Added on_text to connect with the search function
    '''
    def __init__(self, **kwargs):
        super(SearchBarFieldRound, self).__init__(**kwargs)

    def on_focus(self, instance, value):
        super(SearchBarFieldRound, self).on_focus(instance, value)
        self.set_clearbutton_color(value)

    def set_clearbutton_color(self,value):
        '''
            Set the color of the searchbar delete button depends on the focus
        '''
        app = MDApp.get_running_app()
        if value:
            app.root.get_screen('menuscreen').ids.searchbar_clearbutton.text_color = [0,0,0,0.75]
        else:
            app.root.get_screen('menuscreen').ids.searchbar_clearbutton.text_color = [0,0,0,0.4]

    def on_text(self, instance, value):
        '''
            Run the search function when the text field input changes
            if the text field is empty, reload all items
        '''
        app = MDApp.get_running_app()
        if value == "":
            # Reload the contentitem widgets
            app.root.get_screen('menuscreen').clear_all_item()
            app.root.get_screen('menuscreen').load_all_item()
        else:
            app.root.get_screen('menuscreen').clear_all_item()
            app.root.get_screen('menuscreen').search_item(value)


class TitleBarAddButton(MDIconButton):

    def on_press(self):
        '''
            Button to add new entry. On press:
            Initialize a new entry object and insert into database
            (Temporary, we need to design a different screen)
        '''
        app = MDApp.get_running_app()
        tmp_fin_font_scale_fac = app.root.get_screen('menuscreen').fin_font_scale_fac
        app.init_addentry_screen([tmp_fin_font_scale_fac])
        app.root.current = 'addentryscreen'


class SwipeToDeleteItem(MDCardSwipe):

    text = StringProperty(10)
    secondary_text = StringProperty(10)
    icon_shadow_color = ListProperty([])
    name = StringProperty(10)
    fin_font_scale_fac_propagate = NumericProperty(1)

    def __init__(self, input_font_scale_fac, **kwargs):
        super(SwipeToDeleteItem, self).__init__(**kwargs)
        self.icon_shadow_color = self.string_to_hex_rgb(self.text)
        self.icon_shadow_color[3] = 0.75
        self.fin_font_scale_fac_propagate = input_font_scale_fac


    def hash_code(self, in_str):
        '''
            Hash an input string to a number
        '''
        hashnum = 0
        for letter in in_str:
            hashnum = ord(letter) + ((hashnum << 5) - hashnum)
        return hashnum


    def int_to_RGB(self, in_hash):
        '''
            Convert a hashed number to a RGB code
        '''
        c = hex(in_hash & 0x00FFFFFF).upper()
        #print(c,len(c)-2)                         # Got to cut out the 0x
        return '#'+'00000'[0: 6-len(c)+2]+c[2:]


    def string_to_hex_rgb(self, in_string):
        return get_color_from_hex(self.int_to_RGB(self.hash_code(in_string)))


    def on_fin_font_scale_fac_propagate(self, *args):
        # Propagate the scale variable down to contentitem
        self.ids.contentitem._fin_font_scale_fac_propagate = self.fin_font_scale_fac_propagate
        self.ids.contentitem.ids._lbl_primary.font_size = dp(16 * self.fin_font_scale_fac_propagate)
        self.ids.contentitem.ids._lbl_secondary.font_size = dp(16 * self.fin_font_scale_fac_propagate)


class MyRowListItem(TwoLineIconListItemMod):
    '''
        Inherit from TwoLineIconListItemMod.
        Added support on distinguishing different mouse actions
    '''
    mouse_dpos = [0,0]
    drag_threshold = 50
    highlight_color = ListProperty([0,0,0,0])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_touch_down = False
        self.activate_item_down = ''
        self.activate_item_up = ''


    def on_touch_down(self, touch):
        '''
            Function that works together with touch_up
            Distinguish between scrolling, drag and clicks on contentitem
        '''
        self.is_touch_down = True
        self.mouse_dpos = [touch.x, touch.y]

        if self.collide_point(*touch.pos):
            self.activate_item_down = self.text

            # Change color
            self.highlight_color = [0,0,0,0.06]
            return True

        return super(MyRowListItem, self).on_touch_down(touch)


    def on_touch_up(self, touch):
        '''
            Function that works together with touch_down
            Distinugish between scrolling, drag and clicks on contentitem
        '''
        self.highlight_color = [0,0,0,0.0]
        if self.is_touch_down == False and self.collide_point(*touch.pos):
            # print(' Scrolling at boundaries ')
            return super(MyRowListItem, self).on_touch_up(touch)
        elif self.is_touch_down == True and self.collide_point(*touch.pos):
            self.activate_item_up = self.text
            if abs(touch.x - self.mouse_dpos[0]) > self.drag_threshold:
                # Dragging
                # print(f' Drag: {touch.x} , {self.mouse_dpos[0]}')
                self.is_touch_down = False
                return super(MyRowListItem, self).on_touch_up(touch)

            elif self.activate_item_up == self.activate_item_down:
                # Clicking
                self.is_touch_down = False
                # print(f' Click: {touch.x} , {self.mouse_dpos[0]}')
                self.open_content_entry()
                return super(MyRowListItem, self).on_touch_up(touch)


    def open_content_entry(self):
        '''
            Fire when click on a contentitem label
            1. Query for the title name from the database
            2. Generate a new entry screen
        '''
        # Grab the icon color and scale fac
        app = MDApp.get_running_app()
        icon_shadow_color = self.parent.parent.icon_shadow_color
        tmp_fin_font_scale_fac = app.root.get_screen('menuscreen').fin_font_scale_fac

        # Query for the entry
        out_entry_list = rddb.list_entry_command('title', in_name=self.text, decrypt_password=True)[1][0]

        # Inputobj format: [Entry, the_scale_fac, the_icon_color]
        app.init_entry_screen([out_entry_list, tmp_fin_font_scale_fac, icon_shadow_color])
        app.root.current = 'entryscreen'


class MenuScreen(Screen):

    font_hn_medium = rdconfig.hn_medium
    font_hn_bold = rdconfig.hn_bold
    font_hn = rdconfig.hn
    #font_hn_light = rdconfig.hn_light

    fin_font_scale_fac = NumericProperty(1)

    def __init__(self, **kwargs):
        self.trash_widget =[]
        self.title_list = []
        self.category_list = []
        self.search_list = []
        super(MenuScreen, self).__init__(**kwargs)


    def on_enter(self):

        # Check if we are logged in into a database
        if rdstatus.config_status['login'] == 'N':
            rdpassmenu_logger.info('You are not logged in.')
            sys.exit()
        else:
            # Check if it is the first time we visit the menuscreen
            if rdstatus.config_status['menu_visit_count'] == 0:
                rdpassmenu_logger.info('Welcome!')

                # Fetch the list of category names and update rdstatus.config_status
                rdstatus.config_status['category_list'] = rddb.list_existing_category('category')

                # Fetech the list of titles and update rdstatus.config_status
                rdstatus.config_status['title_list'] = rddb.list_existing_category('title')

                # Fetch all the records and add the contentitem widgets
                self.load_all_item()
            else:
                # Fetch the list of category names and update rdstatus.config_status
                rdstatus.config_status['category_list'] = rddb.list_existing_category('category')

                # Fetch the title of the entries and update rdstatus.config_status
                entry_title = rddb.list_existing_category('title')
                rdstatus.config_status['title_list'] = entry_title

                # Check if the existing swipe list is identical to the database, if not, reload all contentitem widgets
                existing_swipe_ids = [k for k in self.ids.keys() if k[0:5] == 'swipe']
                database_swipe_ids = ['swipe_'+item.replace(" ","").lower() for item in entry_title]

                if set(existing_swipe_ids) != set(database_swipe_ids):
                    # Reload the contentitem widgets
                    self.clear_all_item()
                    self.load_all_item()
                else:
                    # print('No update needed')
                    pass

            # Add 1 to the visit counter
            rdstatus.config_status['menu_visit_count'] += 1

            # Testing code
            # pri_text_list = ['Test1', 'Test2', 'Test3', 'Twitter', 'Gundam', 'Facebook', 'Instagram', 'Youtube', 'Poop', 'Test10']
            # second_text_list = ['test', 'test', 'test', 'Social Media', 'Website', 'Social Media', 'Social Media', 'Website', 'Poop', 'test']
            # swipe_id_list = ['swipe1', 'swipe2', 'swipe3', 'swipe4', 'swipe5','swipe6', 'swipe7', 'swipe8', 'swipe9', 'swipe10']
            # name_list = [x.title() for x in swipe_id_list]
            # for i in range(len(pri_text_list)):
            #     new_cardswipe_widget = SwipeToDeleteItem(text=pri_text_list[i], secondary_text=second_text_list[i], name=name_list[i]) #, id=swipe_id_list[i])
            #     self.ids.md_list.add_widget(new_cardswipe_widget)
            #     # Add it into the self.ids
            #     self.ids[swipe_id_list[i]] = weakref.ref(new_cardswipe_widget)


    def search_item(self, in_text):
        '''
            Filter the search_list with in_text and pass them to display_item
        '''
        # Filter the list according to in_text
        search_result_list = list(filter((lambda x: in_text.lower() in x[1]), enumerate(self.search_list)))
        tmp_title_list = [self.title_list[ind] for ind,_  in search_result_list]
        tmp_category_list = [self.category_list[ind] for ind,_  in search_result_list]

        self.display_item(tmp_title_list, tmp_category_list)


    def load_all_item(self):
        '''
            Fetch all the records, update the title_list and category_list and search_list
            pass them to display_item
        '''
        entry_result = rddb.list_entry_command('all')

        self.title_list = [item[1] for item in entry_result[1]]
        self.category_list = [item[4] for item in entry_result[1]]

        # Search list only use lower_case
        self.search_list =[item1.lower() +'*'+ item2.lower() for item1, item2 in zip(self.title_list, self.category_list)]

        self.display_item(self.title_list, self.category_list)


    def clear_all_item(self):
        '''
            Fetch all the swipe item using md_list.children, pass them to remove_item
        '''
        while len(self.ids.md_list.children) > 0:
            for child in self.ids.md_list.children:
                self.remove_item(child)


    def display_item(self, text_list, second_text_list):
        '''
            Format two list of input text (title, category), pass them to add_item to add widget
        '''
        swipe_id_list = [self.title_to_id(item) for item in text_list]
        name_list = [x.title() for x in swipe_id_list]

        for i, (text, second_text, name) in enumerate(zip(text_list, second_text_list, name_list)):
            new_cardswipe_widget = SwipeToDeleteItem(input_font_scale_fac=self.fin_font_scale_fac, text=text, secondary_text=second_text, name=name)
            self.add_item(new_cardswipe_widget)
            # Add it into the self.ids using weakref
            self.ids[swipe_id_list[i]] = weakref.ref(new_cardswipe_widget)


    def remove_item(self, instance):
        self.ids.md_list.remove_widget(instance)
        self.ids.pop(self.title_to_id(instance.text))


    def add_item(self, instance):
        self.ids.md_list.add_widget(instance)


    def title_to_id(self, intext):
        '''
            Convert the title of the entry to the swipe_ id format
        '''
        return 'swipe_'+intext.replace(" ","").lower()


    def show_confirm_delete_dialog_menu(self, instance, in_title_text):
        '''
            Show a popup with the confirm delete message and a button
            Also store the to-be-deleted widget into the self.trash_widget list
        '''
        # Store the title and the reference of the to-be-deleted widget into a list
        self.trash_widget = [in_title_text, instance]

        #if not self.dialog:
        self.dialog = MDDialog(
            text='Permanently delete this entry?',
            pos_hint={'center_x': .5, 'center_y': .25},
            size_hint=(0.75,0.25),
            buttons=[
                MDFlatButton(
                    text="Delete", text_color=[1,0.2196,0.1372,0.9], font_size=dp(8 * self.fin_font_scale_fac),
                    on_release=self.confirm_delete_entry_menu)
            ])
        self.dialog.ids.text.text_color = [1,0.2196,0.1372,1.0]
        self.dialog.ids.text.font_size = dp(16 * self.fin_font_scale_fac)
        self.dialog.open()


    def confirm_delete_entry_menu(self, instance):
        '''
            Pass the title_text to delete_entry_command
            then pass the widget to remove_item and close the dialog box
        '''
        rddb.delete_entry_command('single', self.trash_widget[0])
        self.remove_item(self.trash_widget[1])
        self.dialog.dismiss(force=True)

        # Empty the trash_widget list
        self.trash_widget = []


    def on_fin_font_scale_fac(self, *args):
        '''
            When fin_font_scale_fac changes, modify the label size of the toolbar
            Also modify the fin_font_scale_fac_propagate, which changes the text size and secondary text size of the swipe Listitem
        '''
        self.ids.toolbar.ids.label_title.font_size = dp(self.fin_font_scale_fac * 20)
        self.ids.searchbar_field.fin_font_scale_fac_propagate = self.fin_font_scale_fac

        for itemid in self.ids.keys():
            if 'swipe' in itemid:
                exec('self.ids.'+itemid+'.fin_font_scale_fac_propagate = self.fin_font_scale_fac')
