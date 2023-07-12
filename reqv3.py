import pandas as pd
import numpy as np
from datetime import datetime, timedelta , time
import time
start_time = time.time()

def preprocess_timetable(file_path):

    # Read the timetable data from a text file into a DataFrame
    df_main = pd.read_table(file_path, skiprows=14)
    # Define a list of column indices to drop from the DataFrame
    columns_to_drop = [1, 2, 3, 5, 6, 8, 10, 12, 13, 14, 15]
    # Drop the specified columns from df_main
    df_main.drop(df_main.columns[columns_to_drop], axis=1, inplace=True)
    # Rename the columns of df_main
    column_names = ['Train_ID', 'Station', 'Arrival Time', 'Departure Time', 'Dwell Time']
    df_main.columns = column_names
    return df_main

def filter_and_replace(df, search_word, replacement_dict):
    # Filter df based on Train_ID containing the search word
    via_filter = df["Train_ID"].str.contains(search_word)
    via_df = df[via_filter]
    # Replace values in via_df using the replacement_dict
    via_df.replace(replacement_dict)
    return via_df

file_path = "2023-06-01 CS1 Network Timetable (OT Format).txt"
df_main = preprocess_timetable(file_path)
search_word = "VIA"
replacement_dict = {"HH:MM:SS": "00:00:00", "XX:XX:XX": "00:00:00"}
via_df = filter_and_replace(df_main, search_word, replacement_dict)

def dictionary_from_data_frame(dataframe, column_name):
    values = dataframe[column_name].unique().tolist()
    data_dict = {}

    for value in values:
        filter = dataframe[column_name] == value
        sub_df = dataframe[filter]
        data_dict[value] = sub_df

    return data_dict

def create_sub_data_frames_dict_for_input_file(excel_file_path, key_column):
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

VIA_dfs = dictionary_from_data_frame(via_df,"Train_ID")
VIA_Train_Input_criteria = pd.read_excel('InputExcel.xlsx')
VIA_Train_Input_criteria_dict = create_sub_data_frames_dict_for_input_file('InputExcel.xlsx', 'Train_ID')

def max_runtime_for_train(dictionary, station_start, station_end, max_run_time):
    
    if len(dictionary) == 0:
        return None
    
    for key in VIA_Train_Input_criteria_dict.keys():
        if key not in dictionary:
            print(f"Train {key} is not found in timetable given")
            continue
    
        df = dictionary[key]
        sub_dict_of_input_criteria = VIA_Train_Input_criteria_dict[key]
        end_df = df.loc[df['Station'] == station_end,"Arrival Time"]
        start_df = df.loc[df['Station'] == station_start,"Departure Time"]
        
        if len(end_df.index) == 0 or end_df.values[0] == "HH:MM:SS":
            end_df = df.loc[df['Station'] == station_end,"Departure Time"]
        
        if len(start_df.index) == 0 or  start_df.values[0] == "HH:MM:SS":
            start_df = df.loc[df['Station'] == station_start,"Arrival Time"]   
        
        if start_df.empty or end_df.empty:
            #print(f"{key} does not stop at one of the stations :(")
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
    return True

def test_max_runtime_for_train():
    assert max_runtime_for_train({}, "Aldershot Station", "Burlington Junction", "00:15:00") == None
    assert max_runtime_for_train(VIA_dfs,"Union Station","Burlington Junction","00:44:00") == True

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

#TODO: FINISH ???
def check_dwell_time_between_NRT_and_RT_at_Union():
    trains_to_check = VIA_Train_Input_criteria_dict.keys()
    for key in trains_to_check:
        if key not in dictionary:
            print(f" No matching key for {key} found in timetable")
            return 
        if df["Bound"] == "Inbound":
            return
    return

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

def station_stop_check(dictionary, *stations_to_check):
    for key in dictionary.keys():
        if key not in VIA_dfs:
            print(f"Train {key} is not found in the timetable given")
            continue
        
        df = VIA_dfs[key]
        
        for station_name_to_check in stations_to_check:
            if station_name_to_check == "":
                continue
            stops_at_station = station_name_to_check in df["Station"].values
        
            if stops_at_station:
                print(f"Train {key} does stop at {station_name_to_check}")   
            else :
                print(f"Train {key} does NOT stop at {station_name_to_check}")
    
    return True

def test_station_stop_check():
    assert station_stop_check(VIA_Train_Input_criteria_dict,"Guildwood Station") == True
    assert station_stop_check(VIA_Train_Input_criteria_dict,"Union Station") == True
    assert station_stop_check(VIA_Train_Input_criteria_dict,"Guildwood Station","Union Station","")  == True

#This function will check if a given value is within a range of 15 mins (900 seconds)
#value Colum is the criteria you want to check , arrival dep time ect..

def check_last_value_in_range_v2(df, value_column,bound_value):
    total_over_range = 0  # Variable to store the total time over the 15-minute range

    
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
            print(f"Punctuality for {name} is within the 15 min range of {range_mid} with time {input_given_time}")
        else:
            time_over_range = abs(input_given_time.total_seconds() - range_mid.total_seconds()) - 900
            total_over_range += time_over_range
            time_over_range_minutes = (time_over_range/60)
           
            print(f"Punctuality for {name} is NOT within the 15 min range of {range_mid}")
            print(input_given_time)
            print(name)
            print(f"The train is over the range by {time_over_range_minutes} minutes.")
            
    total_over_range_minutes = total_over_range / 60
    print(f"\nTotal time over the 15-minute range: {total_over_range_minutes} minutes.")

#check_last_value_in_range_v2(VIA_dfs, "Arrival Time","Inbound")
#check_last_value_in_range_v2(VIA_dfs, "Departure Time","Outbound")

def find_row_number(filename, search_string):
    row_number = None

    with open(filename, "r") as file:
        for i, line in enumerate(file, 1):
            if line.startswith(search_string):
                row_number = i
                break
            
    return row_number

def read_connection_data(filename, skiprows):
    df_connection_og = pd.read_table(filename, header=None, skiprows=skiprows+2)
    df_connection_og.columns = ["Train_ID", "ConnTrain_ID", "StationIndex", "ConnStation",
                                "ConnTime", "ConnChangeTime", "ConnMaxChangeTime", "ConnectionType"]
    dfConnection = df_connection_og.drop(['ConnMaxChangeTime'], axis=1)
    return dfConnection

def read_timetable_data(filename, skiprows, nrows):
    df_timetable = pd.read_table(filename, header=None, skiprows=skiprows, nrows=nrows)
    df_timetable.columns = ["courseID", "intervalCourseID", "timeToIntervalReference", "stationIndex",
                            "stationSign", "trackName", "arrTimeDayOffset", "arrTime", "depTimeDayOffset",
                            "depTime", "useDepTime", "dwell", "stopAtStation", "meanDelay", "Distribution", "deltaMass"]
    df_timetable = df_timetable.loc[:, ['courseID', 'stationIndex', 'stationSign', 'arrTime',
                                         'depTime', 'dwell']]
    return df_timetable

def create_sub_data_frames_dict_from_dataframe(dataframe, key_column):
    sub__data_frames_dict = {}
    unique_keys = dataframe[key_column].unique()
    for key in unique_keys:
        sub__data_frames_dict[key] = dataframe[dataframe[key_column] == key]
    return sub__data_frames_dict

filename = "CS2 Network Timetable 1125.txt"
skiprows_needed = find_row_number(filename, "// Connections:")
dfConnection = read_connection_data(filename, skiprows_needed)
df_timetable_that_has_connection_data = read_timetable_data(filename, 13, skiprows_needed-15)
connection_timetable_dict = create_sub_data_frames_dict_from_dataframe(df_timetable_that_has_connection_data, 'courseID')

def keys_with_values(df,column_true_value1,column_name1,column_true_value2, column_name2):
    keys_with_yes_value = []
    for key, dataframe in df.items():
        if column_true_value1 in dataframe[column_name1].values and column_true_value2 in dataframe[column_name2].values :
            keys_with_yes_value.append(key)
    
    return keys_with_yes_value 

#TODO: FIX THE CASE WITH / IN THE TRAIN ID, THEY ARE NOT FOUND AS THE FINAL PART, EG: possible error with VIA50/60.1 possible error with VIA52/62.1
def nrt_check(criteria_dict,connection_df,col_name_of_identifier,col_true_value,bound_Direction):
    keys_to_check = keys_with_values(criteria_dict,col_true_value,col_name_of_identifier,bound_Direction,"Bound")
    nrt_connection_dictionary = {}
    
    if bound_Direction == "Outbound":
        connection_type = 2
        column_nrt_found = 'Train_ID'
        column_to_look_for_key = 'ConnTrain_ID'
        
    elif bound_Direction == "Inbound":
        connection_type = 2
        column_nrt_found = "ConnTrain_ID"
        column_to_look_for_key = 'Train_ID'
        
    for Train_Id in keys_to_check:
        modified_Train_ID = Train_Id +".1"
        nrt_that_matches = connection_df.loc[(connection_df[column_to_look_for_key] == modified_Train_ID) &
                                            (connection_df['ConnectionType'] == connection_type),column_nrt_found]
       
        if nrt_that_matches.empty:
            print(f"possible error with {modified_Train_ID}")
            
        else:
            if nrt_that_matches.iat[0] in connection_timetable_dict.keys():
                nrt_connection_dictionary[Train_Id] = nrt_that_matches.iat[0]
                print(f"{modified_Train_ID} has a matching NRT")
                #print(f"The matching NRT for {Train_Id} is : {nrt_that_matches.iat[0]}")
    #print(nrt_connection_dictionary)            
    return True  
        
def test_nrt_check():
    assert nrt_check(VIA_Train_Input_criteria_dict, dfConnection,"Star Icon", "yes","Outbound") == True
    assert nrt_check(VIA_Train_Input_criteria_dict, dfConnection,"Star Icon", "yes","Inbound") == True
    
test_nrt_check()
    
#TODO: DWELL TIME CHECK E TO NON E TABLE 9
#TODO:655,VIA60 exception need to be coded in SAME WITH THE / TRAINS
#TODO:CHECK FOR VIA 78 RANGE ERROR AS MIDNIGHT thing
#TODO:2b iv)eception 88 which may bypass malton station
#TODO: FIX MIDNIGHT EDGE CASE
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

#station_stop_check(VIA_dfs,"Guildwood")
#check_if_selected_category_dwells_on_station_based_on_icon(VIA_dfs, "Cross Icon", "yes", "Guildwood Station",60)



print("Process finished --- %s seconds ---" % (time.time() - start_time))


