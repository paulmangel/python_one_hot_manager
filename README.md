################   Purpose   ########################

This module helps you manage one-hot encoding and decoding.
Give it your pandas dataframe, and the list of columns you want to split with one-hot encoding. It creates new columns and store the data needed to merge them later.
You can them merge them all back together after treating them however you need.


################   Install    ########################

You only need to use the one_hot_module.py file and import it from your main program.



################   Use    ########################

see example code at the end of the readme.

The module contains one class named OneHotManager, that manages all operations.
First,import and initialize your manager with your dataframe (use the inplace option to choose to work on your original dataframe or on a copy)

Then use :
split_column(column_title: str, rescale: bool = False)   
or 
split_multiple_columns(self, column_list, rescale = False)
to split the categorial columns in your dataframe. (original column is deleted, but can be rebuilt from the new columns)

When you're done and want to merge the columns back, use :
reconstruct_column( column_title (str) ),   
reconstruct_multiple_columns( column_list (list) ),   
or 
reconstruct_all_columns(verbose: bool = False) 
to merge them back together



If you used inplace=False during initialization, the manager makes a copy of the dataframe and modify it instead of working on your original dataframe
use self.df to access the dataframe.






################   Methods    ########################

split_column
def split_column(column_title: str, rescale: bool = False):
    """
	Split a column with one-hot encoding. Data needed for the reconstruction is stored in the dictionnary self.categorial_columns_data
	the names of the new columns are made as : 
	"OneHot_" + str(column_title)+"_"+ str(category)
	The categorial column is then deleted to prevent duplicate data and potential conflict.
	

    Args:
        column_title (str): The name of the column to be split.
        rescale (bool, optional): Whether to rescale the resulting one-hot encoded columns. Default is `False`.
    """



split_multiple_columns
def split_multiple_columns(column_list (list), rescale: bool = False) :
	"""
	calls split_column for each column in the list.
	
	Args : 
	column_list (list of str) : a list of the names of the columns to split.
	the other arguments are the same as split_column()
	"""
	
	
reconstruct_column
def reconstruct_column( column_title (str) ) :
	"""
	Reconstructs a column that was split by this object. Data needed for the reconstruction is taken from the dictionnary self.categorial_columns_data (split_column fills it)
	If rescaled option was False during the split : 
	For each line, the category selected is the one with the highest value (if data didn't change since the split, the column of the original category should have a 1 , and the other 0 )
	If rescaled was true, the scaling is reversed before selecting the highest value
	The OneHot columns are then deleted to prevent duplicate data and potential conflict.	
	

	Args:
	column_title (str): The name of the column (before the split, which is also part of the new columns names).
	"""

 
reconstruct_multiple_columns    	
def reconstruct_multiple_columns( column_list (list) ) : 
	"""
	calls reconstruct_column for each column in the list
	
	Args:
	column_list (list of str): The name of the column (before the split, which is also part of the new columns names).
	"""

    
reconstruct_all_columns
def reconstruct_all_columns(verbose: bool = False) : 
   	"""
	calls reconstruct_column for each column  that is currently split 
	(the status split or merged of each column is stored in self.categorial_columns_data, and updated by split_column and reconstruct_column)
	
	Args:
	verbose (bool, optional) : default is false. Will print the name of the columns documented in categorial_columns_data , and tell for each of them if it was split (and therefore are reconstructed by this function)
	"""



################   Example code    ########################

Example code is included in the module (after the class declaration). Execute the module directly to test it.

Code : 

from one_hot_module import OneHotManager
import pandas as pd

testdata = {
    'Column1': ['A', 'B', 'A', 'C', 'B'],  
    'Column2': ['X', 'Y', 'X', 'Z', 'Y']
}

test_df = pd.DataFrame(testdata)

manager1 = OneHotManager(test_df, inplace = False) # inplace is false by default.

print(manager1.categorial_columns_data)

manager1.split_multiple_columns(['Column1', 'Column2' ], rescale = True) # rescale is false by default

print(manager1.categorial_columns_data)
print()
print(manager1.df)
print()
print(test_df)

manager1.reconstruct_all_columns(verbose = True) # verbose is false by default

print(manager1.df)



















