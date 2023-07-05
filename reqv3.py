import pandas as pd
import numpy as np
from datetime import datetime, timedelta , time
import time

#Prep data
# Read the text file into a DataFrame, skipping the first 14 rows
df_main = pd.read_table("2023-06-01 CS1 Network Timetable (OT Format).txt", skiprows=14)
# Define a list of column indices to drop from the DataFrame
columns_to_drop = [1, 2, 3, 5, 6, 8, 10, 12, 13, 14, 15]
# Drop the specified columns from df_main
df_main.drop(df_main.columns[columns_to_drop], axis=1, inplace=True)
# Rename the columns of df_main
df_main.columns = ['Train_ID', 'Station', 'Arrival Time', 'Departure Time', "Dwell Time"]
# Define the search word
search_word = "VIA"
# Filter df_main based on Train_ID containing the search word
via_filter = df_main["Train_ID"].str.contains(search_word)
# Create a new DataFrame containing only the filtered rows
via_df = df_main[via_filter]

#print(via_df)

replacement_dict = {"HH:MM:SS": "00:00:00", "XX:XX:XX": "00:00:00"}
via_df.replace(replacement_dict)
unique_values_trains = via_df['Train_ID'].unique().tolist()
values = unique_values_trains
unique_columns_name = df_main.columns.values

# Initialize a dictionary to store sub-dataframes
VIA_dfs = {}

# Iterate over each value
for value in values:
    # Create a filter to check if the value matches the text_column exactly
    filter = via_df['Train_ID'] == value

    # Apply the filter to create the sub-dataframe
    sub_df = via_df[filter]

    # Store the sub-dataframe in the dictionary with the value as the key
    VIA_dfs[value] = sub_df

# Access the sub-dataframes by value
#test333 = VIA_dfs["VIA50/60"]
#print(VIA_dfs["VIA50/60"])


VIA_Train_Input_criteria = pd.read_excel('InputExcel.xlsx')

def create_subdataframes_dict(excel_file_path, key_column):
    df = pd.read_excel(excel_file_path)
    unique_values = df[key_column].unique().tolist()
    data_dict = {}
    
    for value in unique_values:
        # Create a filter to check if the value matches the key_column exactly
        filter = df[key_column] == value

        # Apply the filter to create the sub-dataframe
        sub_df = df[filter]

        # Store the sub-dataframe in the dictionary with the value as the key
        data_dict[value] = sub_df
    
    return data_dict

VIA_Train_Input_criteria_dict = create_subdataframes_dict('InputExcel.xlsx', 'Train_ID')


def create_subdataframes_dict_frome_dataframe(df, key_column):
    unique_values = df[key_column].unique().tolist()
    data_dict = {}
    
    for value in unique_values:
        # Create a filter to check if the value matches the key_column exactly
        filter = df[key_column] == value

        # Apply the filter to create the sub-dataframe
        sub_df = df[filter]

        # Store the sub-dataframe in the dictionary with the value as the key
        data_dict[value] = sub_df
    
    return data_dict


# TODO: FIX MIDNIGHT EDGE CASE
#POSSIBLE FIX TO MIDNIGHT RANGE ISSUE.... PLAYAROUND MORE
#time_format = "%H:%M:%S"  # 24-hour format with seconds

#time1 = datetime.strptime("23:30:00", time_format)
#time2 = datetime.strptime("01:00:00", time_format)
#check_time = datetime.strptime("23:45:00", time_format)

# Adjust time2 if it is before time1 (crosses midnight)
#if time2 < time1:
#   time2 = time2 + datetime.timedelta(days=1)

#if time1 <= check_time <= time2:
#    print("23:45 PM is between 23:30 PM and 1 AM")
#else:
#    print("23:45 PM is not between 23:30 PM and 1 AM")


#TODO: CHECK EDGE CASE FOR NON UNION CORRIDORS.

#TODO: value = 90
# time=timedelta(seconds=value)
start_time = time.time()

def maxruntime_for_train(dictionary, station_start, station_end, max_run_time):
    
    if len(dictionary) == 0:
        return None
    trains_to_check = set(VIA_Train_Input_criteria_dict.keys())
    for key in trains_to_check:
        if key not in dictionary:
            print(f"Train {key} is not found in timetable given")
            continue
        
        df = dictionary[key]
        sub_dict_of_input_criteria = VIA_Train_Input_criteria_dict[key]
                
        end_df = df.loc[df['Station'] == station_end,"Arrival Time"]
        start_df = df.loc[df['Station'] == station_start,"Departure Time"]
        print(key)
        print(start_df)
        if len(end_df.index) == 0 or end_df.values[0] == "HH:MM:SS":
            end_df = df.loc[df['Station'] == station_end,"Departure Time"]
        if len(start_df.index) == 0 or  start_df.values[0] == "HH:MM:SS":
            start_df = df.loc[df['Station'] == station_start,"Arrival Time"]   
        
        if start_df.empty and end_df.empty:
            continue
        
        Departure_Time = start_df.values[0]
        Arrival_Time = end_df.values[0]
    
        start_time = datetime.strptime(Departure_Time, "%H:%M:%S")
        end_time = datetime.strptime(Arrival_Time, "%H:%M:%S")

        time_diff = abs(end_time - start_time)
        max_run_time_converted = datetime.strptime(max_run_time,"%H:%M:%S") - datetime.strptime("00:00:00", "%H:%M:%S")
        
        if time_diff <= max_run_time_converted:
            print(f"The Train {key} runtime for the stations selected is below the the max, {time_diff}")
        else:
            print(f"{key} failed Max Run Time of {max_run_time}, actual runtime: {time_diff}")
  




def test_maxruntime_for_train():
    assert maxruntime_for_train({}, "Aldershot Station", "Burlington Junction", "00:15:00") == None
   

#test_maxruntime_for_train()
#maxruntime_for_train(VIA_dfs,"Union Station","Burlington Junction","00:15:00")
print("Process finished --- %s seconds ---" % (time.time() - start_time))

def get_rows_with_column_value_true(dataframe, column_name, value):
    # Create a boolean mask based on the condition
    mask = dataframe[column_name] == value
    return dataframe[mask]  # Return the DataFrame slice where the mask is True



def check_if_selected_category_dwells_on_station_based_on_icon(dictionary, icon, icon_valid_value, station,dwell_time_desired_sec):
    result = []
    sorted_df = get_rows_with_column_value_true(VIA_Train_Input_criteria, icon, icon_valid_value)
    trains_to_check = sorted_df['Train_ID'].unique().tolist()
    
    for key in trains_to_check:
        if key in dictionary:
            train_df = dictionary[key]
            satisfies_condition = check_dwell_time_at_station(train_df, station, dwell_time_desired_sec)
            
            if satisfies_condition:
                print(f"The Train '{key}' satisfies the condition: Dwell Time is 60 seconds at {station}.")
            else:
                print(f"The Train '{key}' does not satisfy the condition: Dwell Time is 60 seconds at {station}.")
        else:
            print(f"The key '{key}' does not exist in the dictionary.")


def check_dwell_time_at_station(train_df, station, dwell_time_desired_sec):
    mask = (train_df['Dwell Time'] == dwell_time_desired_sec) & (train_df['Station'] == station)
    filtered_df = train_df[mask]
    return not filtered_df.empty


#this function retrieves a specific value from a DataFrame based on a search key and the corresponding key and value columns.                   
def get_data_by_search(df, search_key, key_column, value_column):
    filtered_df = df.loc[df[key_column] == search_key, value_column]
    # Check if the filtered DataFrame is not empty
    if not filtered_df.empty:
        matched_value = filtered_df.iloc[0]
        
        # Check if the matched value is not null
        if pd.isna(matched_value):
            get_data_by_search.failedkey_nan = search_key
            return 1
        if pd.notnull(matched_value):
            return str(matched_value)
    # If no matching value or null value is found, return None
    get_data_by_search.failedkey_nan = 1
    return None


def get_correct_row_(df,value_column):
    value = str(value_column)
    if value == "Arrival Time":
        info_row = df.iloc[[-1]]
        
    elif value == "Departure Time":
        info_row  = df.iloc[[0]]
        
    else:
        info_row = "Column not found! doesn't match any cases"
        
    return info_row

#TODO:CHECK ERORR make it check up to 5
def station_stop_check(df,station_name_to_check):
    for name, df in df.items():
        df_of_matching_inputout_entries = df.loc[df["Train_ID"] == name, 'Station']
        if not df_of_matching_inputout_entries.empty:
            print(f"The train {name} does stop at {station_name_to_check}")
        else: print(f"The train {name} does NOT stop at {station_name_to_check}")
station_stop_check(VIA_dfs,"Guildwood Station")   
#print(get_data_by_search(VIA_Train_Input_criteria,"VIA40", "Train_ID","Arrival Time"))
# Example usage
#print(get_data_by_search(VIA_Train_Input_criteria, "VIA651" ,"Train_ID", "Arrival Time"))

#This function will check if a given value is within a range of 15 mins (900 seconds)
#value Colum is the criteria you want to check , arrival dep time ect..

#uses 15 min range hence 900 seconds

#TODO: Potentially add in outbound in bound logic???? to function below




def check_last_value_in_range_v2(df, value_column,bound_value):
    for name, df in df.items():
        # Access the last row of the DataFrame
        row_needed = get_correct_row_(df, value_column)
        input_timetable_time = row_needed[value_column].values[0]
        # Access the last value of a specific column
        criteria_from_table_1_input = get_data_by_search(VIA_Train_Input_criteria, name, "Train_ID", value_column)
        if criteria_from_table_1_input == 1:
            subdf = VIA_Train_Input_criteria_dict[name]
            if subdf["Bound"].item() == bound_value:
                print(f"check this one,{name}")
                continue
            continue
        if criteria_from_table_1_input is None:
            print("No matching entry found for {} in VIA_Train_Input_criteria.".format(name))
            continue 
        
        input_given_time = datetime.strptime(input_timetable_time, "%H:%M:%S") - datetime.strptime("00:00:00", "%H:%M:%S")
        range_mid = datetime.strptime(criteria_from_table_1_input, "%H:%M:%S") - datetime.strptime("00:00:00", "%H:%M:%S")
        # Check if the last value is within the desired range
        is_in_range = (range_mid.total_seconds() - 900) <= input_given_time.total_seconds() <= (range_mid.total_seconds() + 900)

        # Display messages based on the comparison
        if is_in_range:
            print("Arrival Time for {} is within the 15 min range of {}.".format(name, range_mid))
        else:
            print("Arrival Time for {} is not within the 15 min range of {}.".format(name, range_mid))

# Example usage of function tools:

#TODO:655,VIA60 exception need to be coded in SAME WITH THE / TRAINS
#TODO:CHECK FOR VIA 78 RANGE ERROR AS MIDNIGHT thing
#TODO:exception 2b ii) 97 and 98 create sub section for b iii)
#TODO:2b iv)eception 88 which may bypass malton station

#check_last_value_in_range_v2(VIA_dfs, "Arrival Time","Inbound")
#check_last_value_in_range_v2(VIA_dfs, "Departure Time")
#station_stop_check(VIA_dfs,"Guildwood")
#check_if_selected_category_dwells_on_station_based_on_icon(VIA_dfs, "Cross Icon", "yes", "Guildwood Station",60)
#check_if_selected_cgatagory_dwells_on_staion_based_on_icon(VIA_dfs,"Table","Table 2", "Oakville Station")


#find connections we must first find connection.

def find_row_number(filename, search_string):
    row_number = None

    with open(filename, "r") as file:
        for i, line in enumerate(file, 1):
            if line.startswith(search_string):
                row_number_connections = i
                break
            
    return row_number_connections

skiprows_needed = find_row_number("CS2 Network Timetable 1125.txt", "// Connections:")
# Example usage

df_connection_og = pd.read_table("CS2 Network Timetable 1125.txt", header=None, skiprows= skiprows_needed+2 )
df_connection_og.columns = ["Train_ID", "ConnTrain_ID","StationIndex","ConnStation",
                            "ConnTime","ConnChangeTime","ConnMaxChangeTime", "ConnectionType"]
dfConnection = df_connection_og.drop(['ConnMaxChangeTime'], axis=1)


df_timetable_that_has_connection_data = pd.read_table("CS2 Network Timetable 1125.txt", header=None, skiprows=13, nrows= skiprows_needed-15)
df_timetable_that_has_connection_data.columns = ["courseID","intervalCourseID","timeToIntervalReference","stationIndex",
                                                 "stationSign","trackName","arrTimeDayOffset","arrTime","depTimeDayOffset",
                                                 "depTime","useDepTime","dwell","stopAtStation","meanDelay","Distribution","deltaMass"]
df_timetable_that_has_connection_data = df_timetable_that_has_connection_data.loc[:,['courseID','stationIndex','stationSign','arrTime',
                                                                                     'depTime','dwell']]


connection_timetable_dict = create_subdataframes_dict_frome_dataframe(df_timetable_that_has_connection_data, 'courseID')


def keys_with_values(df,column_true_value1,column_name1,column_true_value2, column_name2):
    keys_with_yes_value = []
    for key, dataframe in df.items():
        if column_true_value1 in dataframe[column_name1].values and column_true_value2 in dataframe[column_name2].values :
            keys_with_yes_value.append(key)
    
    return keys_with_yes_value

    

# print(get_rows_with_column_value_true(VIA_Train_Input_criteria,"Star Icon","yes"))


def nrt_check(criteria_dict,connection_df,col_name_of_identifier,col_true_value,outbound_or_inbound):
    keys_to_check = keys_with_values(criteria_dict,col_true_value,col_name_of_identifier,outbound_or_inbound,"Bound")
    if outbound_or_inbound == "Outbound":
        connection_type = 2
        column_nrt_found = 'Train_ID'
    elif outbound_or_inbound == "Inbound":
        connection_type = 0
        column_nrt_found = "ConnTrain_ID"
        
    for Train_Id in keys_to_check:
        modified_Train_ID = Train_Id +".1"

        nrt_that_matches = connection_df.loc[(connection_df['ConnTrain_ID'] == modified_Train_ID) &
                                            (connection_df['ConnectionType'] == connection_type),column_nrt_found]
        if nrt_that_matches.empty:
            print(f"possible error with {modified_Train_ID}")
        else:
            if nrt_that_matches.iat[0] in connection_timetable_dict.keys():
                print(f"{modified_Train_ID} has a matching NRT")
        
        
#nrt_check(VIA_Train_Input_criteria_dict, dfConnection,"Star Icon", "yes","Outbound")
# print("----------------------------------------------------------------")
# nrt_check(VIA_Train_Input_criteria_dict, dfConnection,"Star Icon", "yes","Inbound")

     
#TODO: 300 MIN, DWELL TIME CHECK E TO NON E TABLE 9, Check the station stop function.
#maxruntime_for_train(VIA_dfs,"Union Station","Burlington Junction","00:44:00")
#def tmc_check_inbound(dfConnection,Train_ID,):
#change wording to punctuality