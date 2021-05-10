import sqlite3
import logging
import sys
from RDconfig import rdstatus
from .rdutils import request_input, display_entry, get_hashed_key_from_config
from .rdencrypt import validate_hashed_key, get_hashed_key, sha_mod_key, decrypt_pass


rddb_logger = logging.getLogger('rdutil')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(name)s/%(levelname)s - %(message)s')
ch.setFormatter(formatter)
rddb_logger.addHandler(ch)



def create_new_db_gui(config_dir_path, db_dir_path, db_para_list):
    """
        Generate a database and its config file. For GUI.
    """
    # Only use lower case for the DB name
    # Also remove trailing spaces
    db_name = db_para_list[0].strip().lower()
    key = db_para_list[1]

    # Ask for another name if DB with the same name already exist
    # this test is done in createdbscreen for the GUI version

    # Hash the master key
    hashed_key = get_hashed_key(key)

    # Create the new template db and configuration file.
    try:
        db_full_path = db_dir_path+db_name+'.db'
        create_template_db(db_full_path)

        # Write the config file, hashed key
        with open(config_dir_path+db_name+'.config', mode='w') as f:
            f.write('#\n')
            f.write('# Config file '+db_name+'\n')
            f.write('#\n')
            f.write(hashed_key+'\n')
            f.write('# End of config file\n')

        return True
        # print(f'New database {db_name} and the configuration file are created successfully.')
    except:
        rddb_logger.warning('Error occured when creating a new template database')
        return False


def create_new_db(config_dir_path, db_dir_path, existing_db_list=[]):
    """
        Generate a database and its config file
    """
    print('Creating a new database and the corresponding config file.')
    db_name = request_input(msgtxt='Please enter the name of the database:', hidden=False)

    # Only use lower case for the DB name
    db_name = db_name.lower()

    # Ask for another name if DB with the same name already exist
    while db_name in existing_db_list:
        print('Error - Database with the same name already existed!')
        db_name = request_input(msgtxt='Please enter the name of the database:', hidden=False)
        db_name = db_name.lower()

    # Ask for the master key
    key = request_input(msgtxt='Please enter a new master key for logging in the database: ', hidden=True)
    hashed_key = get_hashed_key(key)

    # Create the new template db and configuration file.
    try:
        db_full_path = db_dir_path+db_name+'.db'
        create_template_db(db_full_path)

        # Write the config file, hashed key
        with open(config_dir_path+db_name+'.config', mode='w') as f:
            f.write('#\n')
            f.write('# Config file '+db_name+'\n')
            f.write('#\n')
            f.write(hashed_key+'\n')
            f.write('# End of config file\n')

        print(f'New database {db_name} and the configuration file are created successfully.')
    except:
        rddb_logger.warning('Error occured when creating a new template database')


def create_template_db(db_full_name_path):
    """
        Open a connection to a database and create a template table
    """
    try:
        conn = sqlite3.connect(db_full_name_path)
        c = conn.cursor()

        # Create a new table
        c.execute('''CREATE TABLE credentials
                 (entry_id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT UNIQUE, user TEXT, password TEXT, category TEXT, description TEXT, salt TEXT)''')

        # Insert a test row
        #c.execute("INSERT INTO credentials VALUES (0, 'TEST','jeffrdcs','password1234','EMAIL','Just a testing one')")
        #c.execute("INSERT INTO credentials(title, user, password, category, description) VALUES ('TESTAUTO','jeffrdcs','password1234','EMAIL','Just a testing one')")
        #c.close()

        # Save the change and close the cursor
        c.close()
        conn.commit()
        conn.close()

    except sqlite3.Error as err:
        rddb_logger.warning('Error occured when opening a new database')
        rddb_logger.warning(str(err))


def connect_existing_db(db_full_name_path):
    """
        Open a connection to an existing database
    """
    try:
        conn = sqlite3.connect(db_full_name_path)

        # Update the open connection to the status variable
        rdstatus.config_status['db_obj'].append(conn)
    except sqlite3.Error as err:
        rddb_logger.warning(f'Error occured when opening the database')
        rddb_logger.warning(str(err))


def add_entry_command(c_entry):
    """
        Add entry into the database
    """
    if rdstatus.config_status['login'] == 'N':
        print('You are not logged in.')
        return False
    else:
        # Get the object
        conn = rdstatus.config_status['db_obj'][0]
        nc = conn.cursor()

        try:
            # Insert a new entry
            #test = ('TESTAUTO','jeffrdcs','password1234','EMAIL','Just a testing description')
            #nc.execute("INSERT INTO credentials(title, user, password, category, description) VALUES (?,?,?,?,?)", test)
            nc.execute("INSERT INTO credentials (title, user, password, category, description, salt) VALUES (?,?,?,?,?,?)", c_entry.message())

            # Close the cursor object and commit
            nc.close()
            conn.commit()

            # print('Entry added.')
            return True
        except sqlite3.Error as err:
            rddb_logger.warning(f'Error occured when adding entry into the database')
            rddb_logger.warning(str(err))


def update_entry_command(title, c_entry):
    """
        Modify an existing entry in the database
    """
    if rdstatus.config_status['login'] == 'N':
        print('You are not logged in.')
        return False
    else:
        # Get the object
        conn = rdstatus.config_status['db_obj'][0]
        nc = conn.cursor()

        try:
            c_list = list(c_entry.message())
            c_list.append(title)
            c_tuple = tuple(c_list)

            # Modify an existing entry
            nc.execute("UPDATE credentials SET title=?, user=?, password=?, category=?, description=?, salt=? WHERE title=?", c_tuple)

            # Close the cursor object and commit
            nc.close()
            conn.commit()

            # print('Entry updated.')
            return True
        except sqlite3.Error as err:
            rddb_logger.warning(f'Error occured when updating entry in the database')
            rddb_logger.warning(str(err))


def delete_entry_command(command_choice, title='dummy'):
    """
        Delete an existing entry in the database
        all = all entries in the database
        single = a single entry by title
    """
    if rdstatus.config_status['login'] == 'N':
        print('You are not logged in.')
        return False
    else:
        # Get the object
        conn = rdstatus.config_status['db_obj'][0]
        nc = conn.cursor()

        try:
            if command_choice == 'all':
                # Delete all entries
                nc.execute("DELETE FROM credentials")
            elif command_choice == 'single':
                # Delete a single entry
                nc.execute("DELETE FROM credentials WHERE title=?", (title,))

            # Close the cursor object and commit
            nc.close()
            conn.commit()

            # print('Entry deleted.')
            return True
        except sqlite3.Error as err:
            rddb_logger.warning(f'Error occured when deleting entry in the database')
            rddb_logger.warning(str(err))


def list_entry_command(command_choice, in_name='dummy', decrypt_password=False):
    """
        List existing entry in the database
        all = all entries in the database
        category = all entries in certain category
    """
    if rdstatus.config_status['login'] == 'N':
        print('You are not logged in.')
        return False
    else:
        # Get the object
        conn = rdstatus.config_status['db_obj'][0]
        nc = conn.cursor()

        try:
            if command_choice == 'all':
                # List all entries
                cursor = nc.execute("SELECT * FROM credentials")
            elif command_choice == 'category':
                # List entries for a category
                cursor = nc.execute("SELECT * from credentials WHERE category=?", (in_name,))
            elif command_choice == 'title':
                # List entry with a certain title
                cursor = nc.execute("SELECT * from credentials WHERE title=?", (in_name,))

            # Get column names and the results
            out_col_names = list(map(lambda x: x[0], cursor.description))
            out_result = nc.fetchall()

            # Descrypt the password for a title query
            # We need to change values in the result tuples
            if decrypt_password:

                out_result_decrypt = []

                for row in out_result:
                    row_list = list(row)
                    de_pw = decrypt_pass(row_list[3].encode(), row_list[6].encode())
                    row_list[3] = de_pw
                    row_list_tuple = tuple(row_list)
                    out_result_decrypt.append(row_list_tuple)

                # Print the entries out
                # display_entry(out_col_names, out_result_decrypt)
                return (out_col_names, out_result_decrypt)
            else:
                # display_entry(out_col_names, out_result)
                return (out_col_names, out_result)

            # Close the cursor object and commit
            nc.close()
            conn.commit()

            return True
        except sqlite3.Error as err:
            rddb_logger.warning(f'Error occured when querying entry in the database')
            rddb_logger.warning(str(err))


def list_existing_category(in_column):
    """
        List all unique column (e.g. categories, titles) in the database. Return as a list
    """
    if rdstatus.config_status['login'] == 'N':
        print('You are not logged in.')
        return False
    else:
        # Get the object
        conn = rdstatus.config_status['db_obj'][0]
        nc = conn.cursor()

        try:
            # Pick the correct SQL command
            if in_column == 'category':
                nc.execute("SELECT DISTINCT category FROM credentials")
            elif in_column == 'title':
                nc.execute("SELECT DISTINCT title FROM credentials")
            elif in_column == 'description':
                nc.execute("SELECT DISTINCT description FROM credentials")
            out_result = nc.fetchall()

            # Close the cursor object and commit
            nc.close()

            out_result_list = [item[0] for item in out_result]
            return out_result_list

        except sqlite3.Error as err:
            rddb_logger.warning(f'Error occured when querying {in_column}')
            rddb_logger.warning(str(err))


def select_db_from_list(available_db_list):
    """
        Allow user to pick a DB from DB list
    """
    db_text = ', '.join(str(item) for item in available_db_list)
    print('Available Database: '+db_text)

    # Ask the user to select a database if more than one available
    if len(available_db_list) == 1:
        db_name = available_db_list[0]
    else:
        db_name = ''

        while db_name not in available_db_list:
            db_name = request_input(msgtxt='Select a database to login: ', hidden=False)

            if db_name not in available_db_list:
                print('Please select a database that is available')

    rddb_logger.info(f'Selected database: {db_name}')
    return db_name


def login_db_gui(db_name, in_key=''):
    """
        Log in a given database, given three trials. For GUI.
    """
    db_path = rdstatus.config_status['db_path']
    config_path = rdstatus.config_status['config_path']

    # Read in the hashed key for this database
    try:
        hashed_key = get_hashed_key_from_config(config_path+db_name+'.config')
        rddb_logger.debug(f'Hashed Key: {hashed_key}')
    except:
        print('Error reading Config File. Exiting!')
        sys.exit()

    if hashed_key == '':
        print('No Hashed Key found! Exiting!')
        sys.exit()

    # Return True if already logged in
    if rdstatus.config_status['login'] == 'Y':
        print(f'You have logged in already. Accessing database {rdstatus.config_status["database_access"]}')
        return True

    # Check if password is correct:
    if rdstatus.config_status['login'] == 'N':
        if in_key == '':
            master_key = request_input(msgtxt=f'Please enter the master key for database {db_name}: ', hidden=True)
        else:
            master_key = in_key

        if validate_hashed_key(master_key, hashed_key):
            db_full_path = db_path+db_name+'.db'
            connect_existing_db(db_full_path)
            rdstatus.config_status['login'] = 'Y'
            rdstatus.config_status['database_access'] = db_name
            print(f'Login success. Accessing database - {db_name}:')

            # if the master key is correct, hash it to the config_status
            rdstatus.config_status['gen_key'] = sha_mod_key(master_key.encode())

            return True
        else:
            return False



def login_db(db_name, in_key=''):
    """
        Log in a given database, given three trials.
    """
    db_path = rdstatus.config_status['db_path']
    config_path = rdstatus.config_status['config_path']

    # Read in the hashed key for this database
    try:
        hashed_key = get_hashed_key_from_config(config_path+db_name+'.config')
        rddb_logger.debug(f'Hashed Key: {hashed_key}')
    except:
        print('Error reading Config File. Exiting!')
        sys.exit()

    if hashed_key == '':
        print('No Hashed Key found! Exiting!')
        sys.exit()

    # Return True if already logged in
    if rdstatus.config_status['login'] == 'Y':
        print(f'You have logged in already. Accessing database {rdstatus.config_status["database_access"]}')
        return True

    # Three attempts
    try_count = 0
    while try_count < 3 and rdstatus.config_status['login'] == 'N':
        if in_key == '':
            master_key = request_input(msgtxt=f'Please enter the master key for database {db_name}: ', hidden=True)
        else:
            master_key = in_key

        if validate_hashed_key(master_key, hashed_key):
            db_full_path = db_path+db_name+'.db'
            connect_existing_db(db_full_path)
            rdstatus.config_status['login'] = 'Y'
            rdstatus.config_status['database_access'] = db_name
            print(f'Login success. Accessing database - {db_name}:')

            # if the master key is correct, hash it to the config_status
            rdstatus.config_status['gen_key'] = sha_mod_key(master_key.encode())

            return True
        else:
            try_count += 1

        if try_count == 3:
            print('Too many wrong password attempts. Exiting.')
            sys.exit()
        else:
            print(f'Wrong password! You have {3-try_count} attempts left.')


def logout_db():
    """
        Log out from the database
    """
    rdstatus.config_status['login'] = 'N'
    rdstatus.config_status['database_access'] = ''
    rdstatus.config_status['db_obj'] = []
