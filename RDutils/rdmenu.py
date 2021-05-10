import sys
from RDconfig import rdstatus
from .rdutils import clear, request_input
from .cred_entry import CredEntry
from .rddb import list_existing_category, add_entry_command, update_entry_command, delete_entry_command, list_entry_command, logout_db, login_db_gui, select_db_from_list, create_new_db



def load_login_menu(db_avail_list, in_command, in_sel_db_name='', in_sel_key=''):
	"""
		Show the login menu and get the input command
	"""
	command = in_command
	# command_list = ['l','c']

	# while command.lower() not in command_list:
	# 	command = request_input(msgtxt='Do you want to [l]og into an existing database or [c]reate a new database? ', hidden=False)

	# if command.lower() not in command_list:
	# 	print('Unknown command. Try again!')

	if command == 'l':
		if login_db_gui(in_sel_db_name, in_sel_key):
			return True
			#load_menu_command()

	elif command == 'c':
		db_path = rdstatus.config_status['db_path']
		config_path = rdstatus.config_status['config_path']
		create_new_db(config_path, db_path, existing_db_list=db_avail_list)
		print('Restart the manager to access the new database.')
		sys.exit()


def menu_command_list():
	"""
		List the menu commands
	"""
	print('##############################################')
	print('')
	print('         RD Password Manager Menu')
	print('')
	print('##############################################')
	print('')
	print('Please select an option: ')
	print('[A]dd an new entry')
	print('[U]pdate an existing entry')
	print('[D]elete an existing entry')
	print('[S]earch an entry by name and show password')
	print('[LA]List all entries in the database')
	print('[LC]List entries in a certain category')
	print('[DA]Delete all entries in the database')
	print('[E]xtract the database into file')
	#print('[L]ogout this database')
	print('[Q]uit')
	print('')


def load_menu_command():
	"""
		Show the command menu and get the input command
	"""
	command = ''

	while True:
		menu_command_list()
		command = request_input(msgtxt='Enter a command: ', hidden=False)
		command = command.lower()

		# Add an entry
		if command == 'a':
			print('[A]dd an new entry')

			# Initialize a new entry object and insert into database
			new_entry = CredEntry()
			new_entry.user_input(check_existing_title_flag=True, list_existing_category_flag=True, encrypt_password=True)
			add_entry_command(new_entry)

		# Update an entry
		elif command == 'u':
			print('[U]pdate an existing entry')

			# Initialize a new entry object
			updated_entry = CredEntry()
			updated_entry.user_input(check_existing_title_flag=True, list_existing_category_flag=True, encrypt_password=True)

			# Show existing titles
			title_list = list_existing_category('title')
			print(f'Existing Titles in the database: {title_list}')
			title = request_input(msgtxt='Enter the TITLE of the entry you would like to update: ', hidden=False)
			while title not in title_list:
				print('The title does not exist in the database. Try again!')
				title = request_input(msgtxt='Enter the TITLE of the entry you would like to update: ', hidden=False)

			ans = request_input(msgtxt=f'Are you sure you want to overwrite the entry {title}? [y/n]', hidden=False)
			if ans.lower() == 'y':
				update_entry_command(title, updated_entry)
			else:
				print('Not updating. Quitting ...')

		# Delete an entry
		elif command == 'd':
			print('[D]elete an existing entry')

			# Show existing titles
			title_list = list_existing_category('title')
			print(f'Existing Titles in the database: {title_list}')

			title = request_input(msgtxt='Enter the TITLE of the entry you would like to delete: ', hidden=False)
			while title not in title_list:
				print('The title does not exist in the database. Try again!')
				title = request_input(msgtxt='Enter the TITLE of the entry you would like to update: ', hidden=False)

			ans = request_input(msgtxt=f'Are you sure you want to delete the entry {title}? [y/n]', hidden=False)
			if ans.lower() == 'y':
				delete_entry_command('single',title)
			else:
				print('Not deleting. Quitting ...')

		# Search an entry by name
		elif command == 's':
			print('[S]earch an entry by name')

			# Show existing titles
			title_list = list_existing_category('title')
			print(f'Existing Titles in the database: {title_list}')

			title = request_input(msgtxt='Enter the TITLE of the entry you would like to query: ', hidden=False)
			while title not in title_list:
				print('The title does not exist in the database. Try again!')
				title = request_input(msgtxt='Enter the TITLE of the entry you would like to query: ', hidden=False)

			list_entry_command('title', in_name = title, decrypt_password=True)    # Only decrypt password in S

		# List all entries in the database
		elif command == 'la':
			print('[LA]List all entries in the database')
			list_entry_command('all')

		# List all entries in a category
		elif command == 'lc':
			print('[LC]List entries in a certain category')

			# Show existing categories
			category_list = list_existing_category('category')
			print(f'Existing Categories: {category_list}')

			cate = request_input(msgtxt='Enter the CATEGORY of the entries you would like to list: ', hidden=False)
			while cate not in category_list:
				print('The category does not exist in the database. Try again!')
				cate = request_input(msgtxt='Enter the CATEGORY of the entries you would like to list: ', hidden=False)

			list_entry_command('category', in_name = cate)

		# Delete all entries
		elif command == 'da':
			print('[DA]Delete all entries in the database')
			check_three_time = 0

			while check_three_time <= 2:
				if check_three_time == 0:
					ans = request_input(msgtxt=f'Are you sure you want to delete ALL entries? [y/n]', hidden=False)
				elif check_three_time == 1:
					ans = request_input(msgtxt=f'Are you really sure? [y/n]', hidden=False)
				elif check_three_time == 2:
					ans = request_input(msgtxt=f'I am going to ask yout one last time. Are you sure? [y/n]', hidden=False)

				if ans.lower() == 'n':
					break

				check_three_time = check_three_time + 1

			if check_three_time == 3:
				delete_entry_command('all')
			else:
				print('Not deleting. Quitting ...')

		# Quit
		elif command == 'q':
			print('')
			logout_db()
			sys.exit()


		# clear screen after completing a command
		# clear()

