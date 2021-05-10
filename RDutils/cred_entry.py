from .rdutils import request_input
from .rddb import list_existing_category
from .rdencrypt import gen_salt, encrypt_pass



# Credential Entry Object
class CredEntry():
    
    def __init__(self, title='dummy', user='dummy', password='dummy', description='dummy', category='dummy', encrypt_password=True):
        self.title = title
        self.user = user
        self.description = description
        self.category = category
        self.salt = gen_salt(5)         #Salt is generated when the object is created
        self.encrypt_password = encrypt_password

        if self.encrypt_password:
            self.password = encrypt_pass(password.encode(), self.salt.encode())
        else:
            self.password = password


    def __str__(self):                            #String representation of the object
        return f"Credential Entry - {self.title}: {self.description}"

    def message(self):
        return (self.title, self.user, self.password, self.category, self.description, self.salt)
    
    def user_input(self, check_existing_title_flag=False, list_existing_category_flag=False):
        # Title 
        if check_existing_title_flag:
            title_list = list_existing_category('title')
            print(f'Existing Titles: {title_list}')
            title = request_input(msgtxt='Enter the TITLE of the entry: ', hidden=False)
            while title in title_list:
                print('The title already exists in the database. Try again!')
                title = request_input(msgtxt='Enter the TITLE of the entry: ', hidden=False)
        else:
            title = request_input(msgtxt='Enter the TITLE of the entry: ', hidden=False)
        self.title = title
        
        # Category
        if list_existing_category_flag:
            category_list = list_existing_category('category')
            print(f'Existing Categories: {category_list}')        
        category = request_input(msgtxt='Enter the CATEGORY that the entry belongs to: ', hidden=False)
        self.category = category
        
        # User
        user_double_pass = True
        while user_double_pass:
            user = request_input(msgtxt='Enter the USER of the entry: ', hidden=False)
            user_dp = request_input(msgtxt='Please enter that again:  ', hidden=False)
            if user == user_dp:
                user_double_pass = False
            else:
                print('Does not match. Try again!')
        self.user = user
        
        # Password
        pw_double_pass = True
        while pw_double_pass:
            pw = request_input(msgtxt='Enter the PASSWORD of the entry: ', hidden=True)
            pw_dp = request_input(msgtxt='Please enter that again:  ', hidden=True)
            if pw == pw_dp:
                pw_double_pass = False
            else:
                print('Does not match. Try again!')

        if self.encrypt_password:
            self.password = encrypt_pass(pw.encode(), self.salt.encode())
        else:
            self.password = pw
        
        # Description
        description = request_input(msgtxt='Enter the DESCRIPTION for the entry: ', hidden=False)
        self.description = description

