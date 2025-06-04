import pandas as pd
import numpy as np
import json
import time
from datetime import timedelta
import os
import sys
from datetime import datetime
from tkinter import Tk, messagebox
#from My_Utilities.utl_select_file_to_load_type02 import FileSelectorApp
from utl_select_file_to_load_type02 import FileSelectorApp
from my_logging import my_logging
from handle_params_class import HandleParams
import utl_functions_01 as func


def load_basic_args(file_name):
	script_dir = os.path.dirname(os.path.abspath(__file__))
	file_path = os.path.join(script_dir,file_name)
	try:
		with open(file_path, "r") as file:
			basic_args = json.load(file)  # Load the JSON file into a dictionary
	except FileNotFoundError:
		if gui_ind: messagebox.showerror('Fatal Error - Aborting', f'Basic args Error: File "{file_path}" was not found - Aborting')
		logging_app.print_message('F', f'Basic args Error: File "{file_path}" was not found')
	except PermissionError:
		if gui_ind: messagebox.showerror('Fatal Error - Aborting', f'Basic args Error: Permission denied - Trying to open file "{file_path}" ')
		logging_app.print_message('F', f'Basic args Error: Permission denied - Trying to open file "{file_path}" ')
	except Exception as e:
		if gui_ind: messagebox.showerror('Fatal Error - Aborting', f'Basic args Error: An unexpected error occurred when loading the "{file_path}" file - Aborting')
		tmp = f'Basic args Error: An unexpected error occurred when loading the "{file_path}" file \n'
		for x in e:
			tmp = tmp + x + '\n'
		if gui_ind: messagebox.showerror('Fatal Error - Aborting', f'tmp')
		logging_app.print_message('F', tmp)
	return basic_args

def basic_args_to_log_only(basic_args):
	logging_app.print_to_log_file_only(f'>>> Info - Basic arguments are:')
	for key, value in basic_args.items():
		if isinstance(value, dict):  # If the value is a dictionary
			logging_app.print_to_log_file_only(f"{key}:")
			for sub_key, sub_value in value.items():
				logging_app.print_to_log_file_only(f"  {sub_key}: {sub_value}")  # Preserve new lines
		else:
			logging_app.print_to_log_file_only(f"{key}: {value}")

def handle_basic_args_01(basic_args):
	logging_app.print_message('I', f'Basic arguments are:')
	for key, value in basic_args.items():
		if isinstance(value, dict):  # If the value is a dictionary
			print(f"{key}:")
			for sub_key, sub_value in value.items():
				print(f"  {sub_key}: {sub_value}")  # Preserve new lines
		else:
			print(f"{key}: {value}")
	
	# Handle True / False strings
	if basic_args['print_validation_info_ind'] == 'True':
		basic_args['print_validation_info_ind'] = True
	else:
		basic_args['print_validation_info_ind'] = False
	if basic_args['gui_ind'] == 'True':
		basic_args['gui_ind'] = True
	else:
		basic_args['gui_ind'] = False
		
#log file name
	log_file_name = basic_args['log_file_name']
	if log_file_name == '':
		logging_app.print_message('W', f'Basic args: log file name is empty, log file will not be created')
# param file name
	if basic_args['default_param_file'] in ('', 'm'):
		param_file_name = select_file_dialog_box('Select Param File')
		if param_file_name == '':
			if gui_ind: messagebox.showerror('Fatal Error - Aborting', f'Basic args Error: The name of the input param file is empty - Aborting')
			logging_app.print_message('F', 'Basic args Error: The name of the input param file is empty')
	else:
		param_file_name = basic_args['default_param_file']
# data file name
	if basic_args['default_data_file'] in ('', 'm'):
		data_file_name = select_file_dialog_box('Select Data File')
		if data_file_name == '':
			if gui_ind: messagebox.showerror('Fatal Error - Aborting', f'Basic args Error: The name of the input data file is empty - Aborting')
			logging_app.print_message('F', 'The name of the input data file is empty')
	elif basic_args['default_data_file'] == 'p':
			data_file_name = 'p'  # need to take the data file name from the param file, wil be done later
	else:
		data_file_name = basic_args['default_data_file']
# gui_ind
	gui_ind = basic_args['gui_ind']
	if gui_ind == '': gui_ind = False
# print_validation_info_ind
	print_validation_info_ind = basic_args['print_validation_info_ind']
	if print_validation_info_ind == '': print_validation_info_ind = False

	return log_file_name, param_file_name, data_file_name, gui_ind, print_validation_info_ind

def select_file_dialog_box(title):# Select File
	initial_directory=""
	root = Tk()
	app = FileSelectorApp(root, initial_directory, title)
	root.mainloop()
	if app.selected_file:
		return app.selected_file
	else:
		return ""

def set_output_file_names(data_file_name, log_file_name):
	if data_file_name:
		file_name_no_suffix, file_name_suffix = os.path.splitext(data_file_name) 	
		output_file_name = file_name_no_suffix + '_' + formatted_date + file_name_suffix
		output_report_name = file_name_no_suffix + '_' + formatted_date + '_REP' + file_name_suffix
	else:
		output_file_name = ''
		output_report_name = ''
	#log file name, add date stamp
	if log_file_name:
		file_name_no_suffix, file_name_suffix = os.path.splitext(log_file_name) 	
		log_file_name = file_name_no_suffix + '_' + formatted_date + file_name_suffix
	else:
		log_file_name = ''
	return output_file_name, output_report_name, log_file_name

def excel_to_dataframe(absolute_path, file_name):
	try:
		df = pd.read_excel(absolute_path)
	except FileNotFoundError:
		logging_app.print_message('F', f'Try openning the {file_name} - file was not found. File name: "{absolute_path}"')
	except Exception as e:
		logging_app.print_message('F', f'Try openning the {file_name} - An unexpected error occurred: {e.args[0]}')
	logging_app.print_message('V', f'\nFirst lines of the {file_name}:\n', lambda: print(df.head()))
	return df

def build_param_info2_helper(title, val, param_info_title, param_info_val):
	param_info_title = param_info_title.append(title)
	if isinstance(val, list):
		val = '  ;  '.join(map(str, val))
	param_info_val = param_info_val.append(val)

def build_param_info2():
	param_info_title = []
	param_info_val = []
	build_param_info2_helper('Detailed parameter description', 'Detailed description is in the parameter file, "instruction" tab', param_info_title, param_info_val)
	build_param_info2_helper('relevant_info_strings', relevant_info_strings, param_info_title, param_info_val)
	build_param_info2_helper('not_relevant_info_strings', not_relevant_info_strings, param_info_title, param_info_val)
	build_param_info2_helper('Strain columns range (first_strain_colix & last_strain_colix' , f'From {first_strain_colix} to {last_strain_colix}',
						   param_info_title, param_info_val)
	build_param_info2_helper('relevant_strains (identify that a stain is relevant)', relevant_strains, param_info_title, param_info_val)
	build_param_info2_helper('take_me_max_relevant_count', take_me_max_relevant_count, param_info_title, param_info_val)
	build_param_info2_helper('take_me_max_none_relevant_count', take_me_max_none_relevant_count, param_info_title, param_info_val)
	build_param_info2_helper('data_file_to_process', data_file_to_process, param_info_title, param_info_val)
	
	df = pd.DataFrame()
	df['Parameter Name'] = param_info_title
	df['Parameter Value'] = param_info_val
	return df


def save_into_excel(df1, df2, xl_file_name):	
	with pd.ExcelWriter(xl_file_name) as writer:
		df1.to_excel(writer, sheet_name='Data_Rsults', index=False)  # Save df1 to one Sheet
		df2.to_excel(writer, sheet_name='Params', index=False)  # Save df2 to another Sheet	

def create_final_report_df(colix_to_report):
	rep_df = pd.DataFrame(None)
	colix_to_report_2 = colix_to_report + [relevancy_info_col_name, strains_info_col_name, relevancy_ind_col_name, indle_col_name]
	for rep_col in colix_to_report_2:
		if rep_col in data_df.columns.tolist():
			rep_df[rep_col] = data_df[rep_col]
	rep_df[indle_col_name] = data_df[indle_col_name]
	rep_df = rep_df[rep_df[relevancy_ind_col_name] != 0]
	return rep_df

#------------------------- analyze data of one row FUNCTIONS --------------------

def get_indle_data(info_string):
	final_rslt = ''
	for relevant_str in relevant_info_strings:
		ix = 0
		while ix > -1:
			ix = info_string.find(relevant_str)
			if ix > 0:
				intrim_string = info_string[0:ix]
				ix_start = intrim_string.rfind(delimiter2)
				if ix_start > 0:
					rslt = info_string[ix_start + 1:ix] + relevant_str
					final_rslt = final_rslt + delimiter1 + rslt
				else: 
					rslt = relevant_str
					final_rslt = final_rslt + delimiter1 + 'Error-No-Left-"|" ' + relevant_str
				info_string = info_string.replace(rslt, '')	
					
	final_rslt = final_rslt.replace(delimiter1, '', 1)
	return final_rslt

def relevancy_indicator(count_relevant_str, count_none_relevant_str):
	if (count_relevant_str      > 0                             and
		count_relevant_str      <= take_me_max_relevant_count   and 
		count_none_relevant_str <= take_me_max_none_relevant_count):
		return 1
	else:
		return 0

def analyze_data_row(row):
	global data_lines_processed_count, data_lines_relevant_count
	count_relevant_str = 0
	count_none_relevant_str = 0
	relevancy_info=''
	strains_info = ''
	for x in relevant_info_strings:
		count_relevant_str = count_relevant_str + row.iloc[relevant_info_colix].count(x)
	for x in not_relevant_info_strings:
		count_none_relevant_str = count_none_relevant_str + row.iloc[relevant_info_colix].count(x)
	
	if count_relevant_str > 0 and count_none_relevant_str == 0:
		relevancy_info = f'Relevancy-OnlyYES'
	elif count_relevant_str > 0 and count_none_relevant_str > 0:
		relevancy_info = f'Relevancy-YES-NO'
	elif count_relevant_str == 0 and count_none_relevant_str > 0:
		relevancy_info = f'Relevancy-OnlyNO'
	else:
		relevancy_info = f'Relevancy-None-Found'
	relevancy_info = relevancy_info + f' count: {count_relevant_str} / {count_none_relevant_str}'
	
	# ----- Building the lists of relevant properiws
	for k in range(first_strain_colix, last_strain_colix + 1):
		for x in relevant_strains:
			if x == row.iloc[k][:len(x)]:
				if strains_info == '':
					strains_info = data_df.columns[k]
				else:
					strains_info = strains_info + delimiter1 + data_df.columns[k]
	
	relevancy_ind = relevancy_indicator(count_relevant_str, count_none_relevant_str) # get value of 1 or 0
	if relevancy_ind == 1:
		data_lines_relevant_count += 1
	if count_relevant_str > 0:
		indle = get_indle_data(row.iloc[relevant_info_colix])
	else:
		indle = ''
	
	data_lines_processed_count += 1
	
	return relevancy_info, strains_info, relevancy_ind, indle
#------------------------- END of analyze data of one row FUNCTIONS --------------------


#----------------- MAIN Program ------------------------------------------------

#----- Init ------------------------

formatted_date = datetime.now().strftime("%Y-%m-%d_%H%M") 
delimiter1 = '; '
delimiter2 = '|'
gui_ind = False # to move to basic args
basic_args_json_file = "basic_args.json"

logging_app = my_logging(__file__)
logging_app.start_program_msg()

basic_args = load_basic_args(basic_args_json_file)
log_file_name, param_file_name, data_file_name, gui_ind, print_validation_info_ind = handle_basic_args_01(basic_args)
logging_app.update_show_validation_info(print_validation_info_ind) #why no printing df.hhead()
_, _, log_file_name = set_output_file_names('', log_file_name)
logging_app.open_log_file(log_file_name)
basic_args_to_log_only(basic_args)
logging_app.print_message('I', f'Printing Data Validation indicator is set in the program to: {print_validation_info_ind}')
must_param_columns = ['relevant_info_colix', 'first_strain_colix', 'relevant_info_strings', 
					  'not_relevant_info_strings', 'relevant_strains', 'take_me_max_relevant_count', 
					  'take_me_max_none_relevant_count', 'colix_to_report', 'data_file_to_process']
param_lists_with_1_value_only_param_col_name = ['relevant_info_colix', 'first_strain_colix','take_me_max_relevant_count', 
												'take_me_max_none_relevant_count', 'data_file_to_process']
# Default data & params files names
#data_file_name = "C:\\_Shaul\\Python\\_My_Code\\Shani\\data\\synthetic_genome_data_v01.xlsx"
#param_file_name = "C:\\_Shaul\\Python\\_My_Code\\Shani\\params\\genome_data_params_v01.xlsx"

data_lines_processed_count = 0
data_lines_relevant_count = 0
# Data analysis is kept in the following new columns (columns created by this program) of data_df
relevancy_info_col_name, strains_info_col_name, relevancy_ind_col_name, indle_col_name = 'relevancy_info', 'strains_info', 'relevancy_ind', 'indle'

#----- End Init --------------------


data_df = pd.DataFrame(None)  # create empty data frames for the first call of the handle_params class, later we will load the data file into a data frame
param_df = pd.DataFrame(None)
handle_params = HandleParams(param_df, must_param_columns, data_df.columns, param_lists_with_1_value_only_param_col_name, logging_app, gui_ind)
#param_file_load_mode, data_file_load_mode = handle_params.get_file_load_mode() # modes: m- select manually, d - take default file, 
																			   #p - take from param file (relevant to data file only)

param_df = excel_to_dataframe(param_file_name, 'Param file') # Load parameters excel into data frame
handle_params.update_instance_args_param_df(param_df) # here we send data_df.columns
handle_params.validate_param_df_columns()
handle_params.create_params_for_analysing()

if data_file_name == 'p':
	data_file_name = handle_params.get_data_file_name_from_params()
else:
	pass # if not == 'p' then the data file was set 
if data_file_name == '':
	if gui_ind: messagebox.showerror('Fatal Error - Aborting', 'The name of the input data file is empty - Aborting')
	logging_app.print_message('F', 'The name of the input data file is empty')

output_file_name, output_report_name, _ = set_output_file_names(data_file_name, '')


data_df = excel_to_dataframe(data_file_name, 'Data file')  # Loading the data into a data frame
handle_params.update_instance_args_data_df_col(data_df.columns)
handle_params.set_up_columns_ix_for_data_fd()
(		relevant_info_colix,
		first_strain_colix,
		last_strain_colix,
		relevant_info_strings,
		not_relevant_info_strings,
		colix_to_report,
		take_me_max_relevant_count,
		take_me_max_none_relevant_count,
		relevant_strains,
		data_file_to_process
		) = handle_params.get_parameters()


# Run the analysis and insert the info into 2 new columns
data_df[[relevancy_info_col_name, strains_info_col_name, relevancy_ind_col_name, indle_col_name]] = data_df.apply(
	lambda row: pd.Series(analyze_data_row(row)), axis=1)

info_df = build_param_info2()
logging_app.print_message('V', '\nFirst lines of the Parameters list that will be added to the output files:\n', lambda: print(info_df.head()))
# Save results (including original excel) in a new excel f
save_into_excel(data_df, info_df, output_file_name)

# Generate final reprt and keep it with parameter in excel
rep_df = create_final_report_df(colix_to_report)
logging_app.print_message('V', '\nFirst lines of the Final Report file:\n', lambda: print(rep_df.head()))
save_into_excel(rep_df, info_df, output_report_name)


logging_app.print_message('I',f'Files in this run..............')
logging_app.print_message('just_print', f'>>  Param file        :  {param_file_name}')
logging_app.print_message('just_print', f'>>  Output file       :  {output_file_name}')
logging_app.print_message('just_print', f'>>  Output report file:  {output_report_name}')
logging_app.print_message('just_print', f'>>  Lof file          :  {log_file_name}')

# data for printing statistics
list_of_text = ['Number of processed data lines', 'Number of RELEVANT data lines'] 
list_of_Values = [data_lines_processed_count,data_lines_relevant_count]
logging_app.print_running_statistics(list_of_text, list_of_Values, 40)
logging_app.stop_program_msg()

