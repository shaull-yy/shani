import pandas as pd
import numpy as np
from my_logging import my_logging
import utl_functions_01 as func

class HandleParams():
	def __init__(self,param_df, must_param_columns, data_df_columns, param_lists_with_1_value_only_param_col_name, main_my_logging, gui_ind=False):
		self.gui_ind = gui_ind
		self.relevant_info_colix = 0
		self.first_strain_colix = 0
		self.last_strain_colix = len(data_df_columns) - 1 # We assume that the last column in the data excel is the last strain column
		self.relevant_info_strings = []
		self.not_relevant_info_strings = []
		self.colix_to_report = []
		self.take_me_max_relevant_count = 0
		self.take_me_max_none_relevant_count = 0
		self.relevant_strains = []
		self.param_df = param_df
		self.must_param_columns = must_param_columns
		self.data_df_columns = data_df_columns.tolist()
		self.param_lists_with_1_value_only_param_col_name = param_lists_with_1_value_only_param_col_name
		self.actual_data_columns_to_report = []
		self.data_file_to_process = ''
		self.param_file_load_mode = ''
		self.data_file_load_mode = ''
		self.logging_app = main_my_logging

	def update_instance_args_param_df(self, param_df):
		self.param_df = param_df
	def update_instance_args_data_df_col(self, data_df_columns):
		self.data_df_columns = data_df_columns.tolist()


	def get_file_load_mode(self):  # Not in use
		tmp = (
			f'Loading Data & Param Files: \n'
			f'    Type 0 to manually select both files (paramet & data file) \n'
			f'    Type 1 to take default paramer file and take the data file from the parameter file \n'
			f'    Type 2 to manually select the paramer file and take the data file from the parameter file \n'
			f'    Type any other character for running with the both default files'
			)
		self.logging_app.print_message('A',tmp)
		default_files_ind = input("  Enter Value...")
		if default_files_ind == '0':
			self.param_file_load_mode = 'm'  # modes: m- select manually, d - take default file, p - take from param file (relevant to data file only)
			self.data_file_load_mode = 'm'
		elif default_files_ind == '1':
			self.param_file_load_mode = 'd'
			self.data_file_load_mode = 'p'
		elif default_files_ind == '2':
			self.param_file_load_mode = 'm'
			self.data_file_load_mode = 'p'
		else:
			self.param_file_load_mode = 'd'
			self.data_file_load_mode = 'd'
		return self.param_file_load_mode, self.data_file_load_mode

	def validate_param_df_columns(self):
		if func.are_lists_same(self.param_df.columns.tolist(), self.must_param_columns, False):  #if self.param_df.columns.tolist() == self.must_param_columns:
			self.logging_app.print_message('I','Params file columns are as expected')
		else:
			tmp = (
			f'Params columns are not as expected' 
			f'\nactual columns in the "param_df" dataframe are:\n{self.param_df.columns.tolist()}' 
			f'\nComparing against hardcoded list:\n{self.must_param_columns}'
			)
			self.logging_app.print_message('F', tmp)

	def clean_check_params_data(self, lst, lst_name):
		self.final_lst = []
		for x in lst:
			if isinstance(x, (float, int)) == True:
				if np.isnan(x) == False:
					self.final_lst.append(x)
			elif x is not np.nan:
				self.final_lst.append(x)
		
		set_param_to_empty = False
		if lst_name in self.param_lists_with_1_value_only_param_col_name:
			if len(self.final_lst) == 0:
				if lst_name == 'data_file_to_process':
					set_param_to_empty = True  # this parameter can be empty
				else:
					self.logging_app.print_message('F', f'The following paramer is empty "{lst_name}"')
			elif len(self.final_lst) > 1:
				tmp = (f'Parameters set-up: The "{lst_name}" paramer should have single value but it has more then one value \n' 
		              f'  Parameter values are: {self.final_lst}  ---  Progam uses the first value')
				self.logging_app.print_message('W', tmp)
			if not set_param_to_empty:
				self.final_lst = self.final_lst[0]
			else:
				self.final_lst = ''
			if isinstance(self.final_lst, float):
				self.final_lst = int(self.final_lst)
		self.logging_app.print_message('I', f'Parameters set-up: The value of the "{lst_name}" parameter is: {self.final_lst}')
		return self.final_lst

	def create_params_for_analysing(self): #creating parameters for analyzing the data file (some are lists, some are acalars)
		self.logging_app.print_message('I', '\n----- Start of parameter set up and validation ------')
		self.relevant_info_colix = self.clean_check_params_data(self.param_df['relevant_info_colix'], 'relevant_info_colix')
		self.first_strain_colix = self.clean_check_params_data(self.param_df['first_strain_colix'], 'first_strain_colix')
		self.relevant_info_strings = self.clean_check_params_data(self.param_df['relevant_info_strings'], 'relevant_info_strings')
		self.not_relevant_info_strings = self.clean_check_params_data(self.param_df['not_relevant_info_strings'], 'not_relevant_info_strings')
		self.colix_to_report = self.clean_check_params_data(self.param_df['colix_to_report'], 'colix_to_report')
		self.take_me_max_relevant_count = self.clean_check_params_data(self.param_df['take_me_max_relevant_count'], 'take_me_max_relevant_count')
		self.take_me_max_none_relevant_count = self.clean_check_params_data(self.param_df['take_me_max_none_relevant_count'], 'take_me_max_none_relevant_count')
		self.relevant_strains = self.clean_check_params_data(self.param_df['relevant_strains'], 'relevant_strains')
		self.data_file_to_process = self.clean_check_params_data(self.param_df['data_file_to_process'], 'data_file_to_process')
		self.logging_app.print_message('I', '----- End of parameter set up and validation --------\n')


	def set_up_columns_ix_for_data_fd(self):
		self.logging_app.print_message('I', '----- Start of setting up the data frame indexes --------')
		tmp = min(15, len(self.data_df_columns))
		self.logging_app.print_message('I', f'The first 15 Data File columns are: \n {self.data_df_columns[0:tmp]}')
		
		self.relevant_info_colix -=1
		tmp = self.data_df_columns[self.relevant_info_colix]
		self.logging_app.print_message('I', f'Data File Columns: Column Name "{tmp}", DataFrame-Index {self.relevant_info_colix} is used for check if the line is relevant')
		
		self.first_strain_colix -=1
		tmp = self.data_df_columns[self.first_strain_colix]
		self.logging_app.print_message('I', f'Data File Columns: Column Name "{tmp}", DataFrame-Index {self.first_strain_colix} is the firts column of "STRAINS"')

		#Check that columns to report exists (colix_to_report list):
		for col_name in self.colix_to_report:
			if col_name in self.data_df_columns:
				self.actual_data_columns_to_report.append(col_name)
				self.logging_app.print_message('I', f'Data File Columns to be on final report: Column Name "{col_name}" exists and will be on the final report')
			else:
				self.logging_app.print_message('W', f'Data File Columns to be on final report: Column Name "{col_name}" NOT exists and will NOT be on the final report')
		
		self.logging_app.print_message('I', '----- End of setting up the data frame indexes ----------\n')

	def get_parameters(self): # send to the calling program all the parameters
		return (
		self.relevant_info_colix,
		self.first_strain_colix,
		self.last_strain_colix,
		self.relevant_info_strings,
		self.not_relevant_info_strings,
		self.colix_to_report,
		self.take_me_max_relevant_count,
		self.take_me_max_none_relevant_count,
		self.relevant_strains,
		self.data_file_to_process
		)
	def get_data_file_name_from_params(self): 
		return 	self.data_file_to_process
		

if __name__ == '__main__':
	param_df = pd.DataFrame(None)
	data_df_columns = ['a','b']
	must_param_columns = []
	handle_params = HandleParams(param_df, data_df_columns, must_param_columns)
	handle_params.validate_param_df()
	print('end prog')