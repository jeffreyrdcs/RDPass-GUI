import os
import re
import getpass
import logging
# from RDconfig import rdstatus

rdutil_logger = logging.getLogger('rdutil')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(name)s/%(levelname)s - %(message)s')
ch.setFormatter(formatter)
rdutil_logger.addHandler(ch)


def request_input(msgtxt='', hidden=False):
    """
        Request input from the user, add a function to hide the user input
    """
    try:
        if hidden:
            ans = getpass.getpass(msgtxt+' ')
        else:
            ans = input(msgtxt)
    except:
        return False

    return ans


def scan_db_dir(dir_path):
    """
        Returns the name of existing database in the given directory
    """
    db_list = [os.path.splitext(name)[0] for name in os.listdir(dir_path)]
    return db_list


def check_config_file(config_dir_path, db_dir_path):
    """
        Check the existence of the config file for existing databases
    """
    check_list = []
    config_list = [os.path.splitext(name)[0] for name in os.listdir(config_dir_path)]
    for name in scan_db_dir(db_dir_path):
        if os.path.isfile(config_dir_path+name+'.config'):
            rdutil_logger.debug(f'Config file for {name} exists.')
            check_list.append(1)
        else:
            rdutil_logger.warning(f'Config file for {name} missing.')
            check_list.append(0)
    return check_list


def get_hashed_key_from_config(config_file_path):
    """
        Get the hashed key from a config file
    """
    with open(config_file_path, mode='r') as f:
        contents = f.read()
    pattern = r'#\n([^#]+)\n#'
    return re.findall(pattern, contents)[0]


def clear():
    """
        Clear the screen output with the ANSI code
    """
    print('\x1b[1J')


def display_entry(in_col_names, in_result, truncate_data=True):
    """
        Display entry on screen
    """
    hori_line = ('+'+'-'*20) * (len(in_col_names)) +'+'
    row_format ="{:>20}|" * (len(in_col_names))
    row_col_line = "|"+row_format.format(*in_col_names)       #*list to unpack
    print('')
    print(hori_line)
    print(row_col_line)
    print(hori_line)

    for row in in_result:
        if truncate_data:
            trun_row_list = []
            for item in row:
                if isinstance(item, str):   # Check if it is a string

                    # Truncate the text if it is longer than 11 char
                    trun_row_list.append(  (item[:16] + '...') if len(item) > 16 else item )
                else:
                    trun_row_list.append(item)
            print("|"+ row_format.format(*trun_row_list))
        else:
            print("|"+ row_format.format(*row_list))

    print(hori_line)
    print('')


