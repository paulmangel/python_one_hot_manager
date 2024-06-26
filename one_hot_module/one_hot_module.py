import pandas as pd
import numpy as np
import json
import os


# this class can split categorial columns using one-hot encoding, then merge them back to a single column.
class OneHotManager() : 
    def  __init__(self, dataFrame, inplace = False) :
        if inplace :
            self.df = dataFrame
        else : 
            self.df = dataFrame.copy()
        self._categorial_columns_data = {} # a dict to store data on the split columns needed to merge them back.
        self._quantitative_column_data = {}
        self.df_len = len(self.df)
    
    def add_cat_column_data(self, column_title): # add a column's data to the dictionnary. Doesn't need to be called by user. is automatically done before splitting a column.
        # Ensure column_title exists in the dataset
        if column_title not in self.df :
            print(f"Error, Column '{column_title}' does not exist in the dataset.")
            return
        else :
            column_data = self.df[column_title]  # Get data for the specified column

            # Compute categories and category counts
            categories = list(set(column_data))
            category_counts = column_data.value_counts().to_dict()

            # Add column data to the dictionary
            self._categorial_columns_data[column_title] = {
                'title': column_title,
                'categories': categories,
                'category_counts': category_counts,
                'status' : 'merged', # status merged or split , or split_rescaled
                'names_split_columns' : []
            }

  
    def add_multiple_columns_data(self, column_list) : 
        for column_title in column_list : 
            self.add_column_data(column_title)


    def nomrmalize_column(self, column_title) :
        if column_title in self._quantitative_column_data:
            if 'is normalized' in self._quantitative_column_data[column_title]['status']:
                raise ValueError(f"Column '{column_title}' is already normalized")
        
        previous_mean = self.df[column_title].mean()
        previous_std = self.df[column_title].std()
        self.df[column_title] = (self.df[column_title] - previous_mean) / previous_std
        self._quantitative_column_data[column_title] = {
                'title': column_title,
                'mean': previous_mean,
                'std': previous_std,
                'status' : 'is normalized'
            }

    def nomrmalize_multiple_columns(self, column_list) : 
        for column_title in column_list : 
            self.nomrmalize_column(column_title)


    def reverse_normalize_column(self, column_title):
        if column_title not in self._quantitative_column_data:
            raise ValueError(f"Column '{column_title}' has not been normalized yet.")
        if 'not normalized' in self._quantitative_column_data[column_title]['status']:
            raise ValueError(f"Column '{column_title}' is already denormalized")
        # Get previous mean and standard deviation from the stored information
        previous_mean = self._quantitative_column_data[column_title]['mean']
        previous_std = self._quantitative_column_data[column_title]['std']
        # Reverse normalization by multiplying by the previous standard deviation and adding the previous mean
        self.df[column_title] = (self.df[column_title] * previous_std) + previous_mean
        # Update the stored information to indicate that the column is no longer normalized
        self._quantitative_column_data[column_title]['status'] = 'not normalized'

    def reverse_nomrmalize_multiple_columns(self, column_list) : 
        for column_title in column_list : 
            self.reverse_normalize_column(column_title)

    def reverse_nomrmalize_all_columns(self) : 
        for column_title in self._quantitative_column_data : 
            self.reverse_normalize_column(column_title)

    # # use this function at your own risk : incorrect data will introduce bugs.
    # def manually_add_split_column_data(self, original_column_title, split_columns_titles_list, categories_list , is_rescaled = False):
    #     print("warning, method not operationnal yet")
    #     new_dict = {original_column_title : {}}
    #     new_dict[original_column_title]['categories'] = categories_list
    #     new_dict[original_column_title]['names_split_columns'] = split_columns_titles_list
    #     if is_rescaled :
    #         new_dict[original_column_title]['status'] = 'split_rescaled'
    #     else :
    #         new_dict[original_column_title]['status'] = 'split'



    def make_new_column_name(self, column_title, category):
        return "OneHot_" + str(column_title)+"_"+ str(category)

    def split_column(self,column_title, rescale = False) :  # adds the data of the column to the dictionary, then splits the column 
        self.add_cat_column_data(column_title)
        names_dict = {}
        for category in self._categorial_columns_data[column_title]['categories'] :
            new_name = self.make_new_column_name(column_title, category)
            if rescale :
                ratio = np.sqrt( self.df_len/self._categorial_columns_data[column_title]['category_counts'][category] )
            else :
                ratio = 1
            self.df[new_name] =  self.df[column_title].apply(lambda x: ratio if x == category else 0)
            names_dict[new_name] =  category
        self.df.drop(columns=[column_title], inplace = True)
        if rescale :
            self._categorial_columns_data[column_title]['status'] = 'split_rescaled'
        else :
            self._categorial_columns_data[column_title]['status'] = 'split'

        self._categorial_columns_data[column_title]['names_split_columns'] = names_dict
        
    def split_multiple_columns(self, column_list, rescale = False) : 
        for column_title in column_list : 
            self.split_column(column_title, rescale)

    # def category_choice(self, column_title, row_index) :
        
    #     for category in self.categorial_columns[column_title]['categories'] :
    #         inv_ratio = np.sqrt(self.categorial_columns[column_title]['category_counts'][category] / self.df_len )
    #         name =  self.make_new_name(self, column_title, category)

    #     df.loc[row_index, columns_list]

    def reconstruct_column(self, column_title) :
        name_map = self._categorial_columns_data[column_title]['names_split_columns']# dict mapping column names with categories
        status = self._categorial_columns_data[column_title]['status']
        if 'split' in status :
            if 'rescaled' in status  :
                for cat_column_name, category in name_map.items() :
                    inv_ratio = np.sqrt(self._categorial_columns_data[column_title]['category_counts'][category] / self.df_len )
                    self.df[cat_column_name] = self.df[cat_column_name] * inv_ratio  
            new_column = []
            for index, row in self.df.iterrows():
                values_dict = {} # used and reset for each row, to store the category associated with the value of the corresponding column until the best category is selected
                for cat_column_name, category in name_map.items() : 
                    values_dict[category] = row[cat_column_name]
                new_column.append(max(values_dict, key=values_dict.get))
            self.df[column_title] = new_column
            self.df.drop(columns=name_map.keys(), inplace = True)
            self._categorial_columns_data[column_title]['status'] = 'merged'
        else : 
            print(f"error : the column {column_title} isn't split, can't merge it.")

    def reconstruct_multiple_columns(self, column_list) : 
        for column_title in column_list : 
            self.reconstruct_column(column_title)

    def reconstruct_all_columns(self, verbose = False) : 
        for column_title, col_dict in self._categorial_columns_data.items() :
            is_split = 'split'  in self._categorial_columns_data[column_title]['status']
            if is_split  :
                self.reconstruct_column(column_title)
            if verbose : 
                print(f" column {column_title} : was split ? {is_split}")

    def make_unique_values_dictionary(self, column_list):
        unique_values_dict = {}
        for col in column_list:
            unique_values_dict[col] = pd.unique(self.df[col]).tolist()
        return unique_values_dict
    


    def save_state(self, base_name="my", path = "."): # path includes the begining of the name, and will 
        categorial_path = f"{path}/{base_name}_categorial_columns_data.json"
        quantitative_path = f"{path}/{base_name}_quantitative_column_data.json"
        with open(categorial_path, 'w') as json_file:
            json.dump(self._categorial_columns_data , json_file)
        with open(quantitative_path, 'w') as json_file:
            json.dump(self._quantitative_column_data , json_file)

    def load_state(self, base_name="my", path="."):
        categorial_path = f"{path}/{base_name}_categorial_columns_data.json"
        quantitative_path = f"{path}/{base_name}_quantitative_column_data.json"
        
        try:
            with open(categorial_path, 'r') as json_file:
                self._categorial_columns_data = json.load(json_file)
        except FileNotFoundError:
            print(f"File '{categorial_path}' not found. No categorical data loaded.")

        try:
            with open(quantitative_path, 'r') as json_file:
                self._quantitative_column_data = json.load(json_file)
        except FileNotFoundError:
            print(f"File '{quantitative_path}' not found. No quantitative data loaded.")




####################################                 EXAMPLE CODE :             ###########################################

# execute this file directly to execute this code :
if __name__ == "__main__":

    testdata = {
        'Column1': ['A', 'B', 'A', 'C', 'B'],
        'Column2': ['X', 'Y', 'X', 'Z', 'Y']
    }

    test_df = pd.DataFrame(testdata)

    manager1 = OneHotManager(test_df, inplace = False) # inplace is false by default.

    print(manager1._categorial_columns_data)

    manager1.split_multiple_columns(['Column1', 'Column2' ], rescale = True) # rescale is false by default

    print(manager1._categorial_columns_data)
    print()
    print(manager1.df)
    print()
    print(test_df)

    manager1.reconstruct_all_columns(verbose = True) # verbose is false by default

    print(manager1.df)



