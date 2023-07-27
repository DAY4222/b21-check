import pandas as pd
import numpy as np
from datetime import datetime, timedelta , time
import time
start_time = time.time()
#--------------DATA_PREP----------------------------------------------------------------------------------------------
def row_selector_based_on_weekdayendwith_values(file_path,sheet_name,what_type_of_day):
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    columns_to_keep = ['Train_ID', 'Arrival Time', 'Departure Time', 'Cross Icon', 'Table', 'Bound', 'Star Icon', 'select_all', 'Train_Type']
    df_filtered = df[columns_to_keep]
    df_filtered = df_filtered[df_filtered['Train_Type'] == what_type_of_day]

    return df_filtered

def create_sub_data_frames_dict_for_input_file(df, key_column):
    unique_values = df[key_column].unique().tolist()
    data_dict = {}
    
    for value in unique_values:
        filter = df[key_column] == value
        sub_df = df[filter]
        data_dict[value] = sub_df
    
    return data_dict

def find_row_number(filename, search_string):
    row_number = None

    with open(filename, "r") as file:
        for i, line in enumerate(file, 1):
            if line.startswith(search_string):
                row_number = i
                break
    if row_number is None:
        return False
    else:           
        return row_number

def read_connection_data(filename, skiprows):
    columns_to_read = [0, 1, 2, 3, 4, 5, 6, 7]
   
    df_connection_og = pd.read_table(filename, header=None, skiprows=skiprows+2, usecols=columns_to_read)
    df_connection_og.columns = ["Train_ID", "ConnTrain_ID", "StationIndex", "ConnStation",
                                "ConnTime", "ConnChangeTime", "ConnMaxChangeTime", "ConnectionType"]
    dfConnection = df_connection_og.drop(['ConnMaxChangeTime'], axis=1)
    return dfConnection

def read_timetable_data(filename, skiprows, nrows):
    df_timetable = pd.read_table(filename, header=None, skiprows=skiprows, nrows=nrows)
    df_timetable.columns = ["Train_ID", "intervalCourseID", "timeToIntervalReference", "stationIndex",
                            'Station', "trackName", "arrTimeDayOffset", 'Arrival Time', "depTimeDayOffset",
                            'Departure Time', "useDepTime", "Dwell Time", "stopAtStation", "meanDelay", "Distribution", "deltaMass"]
    df_timetable = df_timetable.loc[:, ['Train_ID', 'Station', 'Arrival Time',
                                         'Departure Time', 'Dwell Time']]
    return df_timetable

def create_sub_data_frames_dict_from_dataframe(dataframe, key_column):
    sub_data_frames_dict = {}
    unique_keys = dataframe[key_column].unique()
    for key in unique_keys:
        sub_data_frames_dict[key] = dataframe[dataframe[key_column] == key]
    return sub_data_frames_dict

def filter_and_replace(df, search_word, replacement_dict):
    via_filter = df["Train_ID"].str.contains(search_word)
    via_df = df[via_filter]
    via_df.replace(replacement_dict)
    return via_df

def scenario_selector(scenario):
    if scenario == "S1":
        what_type_of_day = "BusinessDay"
        return what_type_of_day

    elif scenario == "S2":
        what_type_of_day = "WeekendDay"
        return what_type_of_day
    elif scenario == "S3":
        what_type_of_day = "BusinessDay"
        return what_type_of_day
    elif scenario == "S4":
        what_type_of_day = "WeekendDay"
        return what_type_of_day     
    elif scenario == "S5":
        #TODO: FIGURE IT OUT JUSTIN
        
           
        return what_type_of_day

    
#-------------Initialize_data_frames_set_scenario-----------------------------------------------------------------------------------------------

filename = "0710 network timetable 2023-07-13.txt"
#which timetable scenario? 
#S1: weekday, S2: weekend, S3: weekday.1, S4: weekend.2, S5: both weekday/weekend .1 .2
scenario = "S3"
#Is the timetable weekday?weeknd?both?


skip_rows_needed_for_time_table = find_row_number(filename, "// Connections:")

#Create DF of timetable
#Handle no conection table CASE
if skip_rows_needed_for_time_table == None:
    df_Timetable = read_timetable_data(filename, 13, None)
else:
    df_Timetable = read_timetable_data(filename, 13, skip_rows_needed_for_time_table-15)
    #Make a df and dict of the connection data at the end of the file only if it exsits.
    df_Connection = read_connection_data(filename, skip_rows_needed_for_time_table)
    connection_timetable_dict = create_sub_data_frames_dict_from_dataframe(df_VIA_Timetable, 'Train_ID')    
    
    
#Create DF of only VIA in timetable and dict
search_word = "VIA"
replacement_dict = {"HH:MM:SS": "00:00:00", "XX:XX:XX": "00:00:00"}
df_VIA_Timetable = filter_and_replace(df_Timetable, search_word, replacement_dict)
Via_df_Timetable_dict = create_sub_data_frames_dict_from_dataframe(df_VIA_Timetable, "Train_ID")

#Create Excel input df
VIA_Train_Input_criteria = row_selector_based_on_weekdayendwith_values('InputExcel.xlsx','Sheet1',scenario_selector(scenario))
VIA_Train_Input_criteria_dict = create_sub_data_frames_dict_for_input_file(VIA_Train_Input_criteria, 'Train_ID')


    

##-----------MAX_RUNTIME-------------------------------------------------------------------------------------------------
   
def max_runtime_for_train_S3_S4(dictionary, station_start, station_end, max_run_time,scenario):

    if len(dictionary) == 0:
        return None
    
    for key in VIA_Train_Input_criteria_dict.keys():
        if scenario == "S3":
            key = key + ".1"
        if  scenario == "S4":
            key = key + ".2"
        
        if key not in dictionary:
            print(f"Train {key} is not found in timetable given")
            continue
            
        df = dictionary[key]
        key = key[:-2]
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
            print(f"{key} failed Max Run Time of {max_run_time}, actual runtime: {time_diff}. Between {station_start} and {station_end}")
    return True

def max_runtime_for_train_S1_S2(dictionary, station_start, station_end, max_run_time):

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
            print(f"{key} failed Max Run Time of {max_run_time}, actual runtime: {time_diff}. Between {station_start} and {station_end}")
    return True

#---------------Dwell_recruitment check---------------------------------------------------------------------------------------------
def get_rows_with_column_value_true(dataframe, column_name, value):
    mask = dataframe[column_name] == value
    return dataframe[mask]  # Return the DataFrame slice where the mask is True

def check_dwell_time_at_station(train_df, station, dwell_time_desired_sec):
    mask = (train_df['Dwell Time'] == dwell_time_desired_sec) & (train_df['Station'] == station)
    filtered_df = train_df[mask]
    return not filtered_df.empty

def check_if_selected_category_dwells_on_station_based_on_icon_S3_S4(dictionary, icon, icon_valid_value, station,dwell_time_desired_sec,scenario):
    result = []
    sorted_df = get_rows_with_column_value_true(VIA_Train_Input_criteria, icon, icon_valid_value)
    trains_to_check = sorted_df['Train_ID'].unique().tolist()
    
    for key in trains_to_check:
        if scenario == "S3":
            key = key + ".1"
        if  scenario == "S4":
            key = key + ".2"
            
        if key in dictionary:
            train_df = dictionary[key]
            satisfies_condition = check_dwell_time_at_station(train_df, station, dwell_time_desired_sec)
            
            if satisfies_condition:
                print(f"The Train '{key}' satisfies the condition: Dwell Time is {dwell_time_desired_sec} seconds at {station}.")
            else:
                print(f"The Train '{key}' does NOT satisfy the condition: Dwell Time is {dwell_time_desired_sec} seconds at {station}.")
        else:
            print(f"The key '{key}' does not exist in the dictionary.")

def check_if_selected_category_dwells_on_station_based_on_icon_S1_S2(dictionary, icon, icon_valid_value, station,dwell_time_desired_sec):
    result = []
    sorted_df = get_rows_with_column_value_true(VIA_Train_Input_criteria, icon, icon_valid_value)
    trains_to_check = sorted_df['Train_ID'].unique().tolist()
    
    for key in trains_to_check:
        if key in dictionary:
            train_df = dictionary[key]
            satisfies_condition = check_dwell_time_at_station(train_df, station, dwell_time_desired_sec)
            
            if satisfies_condition:
                print(f"The Train '{key}' satisfies the condition: Dwell Time is {dwell_time_desired_sec} seconds at {station}.")
            else:
                print(f"The Train '{key}' does NOT satisfy the condition: Dwell Time is {dwell_time_desired_sec} seconds at {station}.")
        else:
            print(f"The key '{key}' does not exist in the dictionary.")

#this function retrieves a specific value from a DataFrame based on a search key and the corresponding key and value columns.                   

#------------------------------------------------------------------------------------------------------------
def station_stop_check(dictionary, *stations_to_check):
    for key in dictionary.keys():
        if key not in Via_df_Timetable_dict:
            print(f"Train {key} is not found in the timetable given")
            continue
        
        df = Via_df_Timetable_dict[key]
        
        for station_name_to_check in stations_to_check:
            if station_name_to_check == "":
                continue
            stops_at_station = station_name_to_check in df["Station"].values
        
            if stops_at_station:
                print(f"Train {key} does stop at {station_name_to_check}")   
            else :
                print(f"Train {key} does NOT stop at {station_name_to_check}")
    
    return True
#------------------------------------------------------------------------------------------------------------

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

#This function will check if a given value is within a range of 15 mins (900 seconds)
#value Colum is the criteria you want to check , arrival dep time ect..
#TODO: abstract 900 use the range to make the range no need 900 seconds.

def check_last_value_in_range_S3_S4(df, value_column,bound_value):
    total_over_range = 0  # Variable to store the total time over the 15-minute range

    for name, df in df.items():
        # Access the last row of the DataFrame
        row_needed = get_correct_row_(df, value_column)
        input_timetable_time = row_needed[value_column].values[0]
        # Access the last value of a specific column
        name = name[:-2]
        if 'E' in name:
            continue
        
        
        criteria_from_table_1_input = get_data_by_search(VIA_Train_Input_criteria, name, "Train_ID", value_column)
        if criteria_from_table_1_input == 1:
            subdf = VIA_Train_Input_criteria_dict[name]
            if subdf["Bound"].item() == bound_value:
                print(f"check this one,{name}")
                continue
            continue
        
        
        if criteria_from_table_1_input is None:
            if name not in VIA_Train_Input_criteria_dict.keys():
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
            print(f"The train is over the range by {time_over_range_minutes} minutes.")
            
    total_over_range_minutes = total_over_range / 60
    print(f"\nTotal time over the 15-minute range: {total_over_range_minutes} minutes.")
    return True

def check_last_value_in_range_S1_S2(df, value_column,bound_value):
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
        if 'E' in name:
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
            print(f"The train is over the range by {time_over_range_minutes} minutes.")
            
    total_over_range_minutes = total_over_range / 60
    print(f"\nTotal time over the 15-minute range: {total_over_range_minutes} minutes.")
    return True

#------------------------------------------------------------------------------------------------------------

def keys_with_values(df,column_true_value1,column_name1,column_true_value2, column_name2):
    keys_with_yes_value = []
    for key, dataframe in df.items():
        if column_true_value1 in dataframe[column_name1].values and column_true_value2 in dataframe[column_name2].values :
            keys_with_yes_value.append(key)
    
    return keys_with_yes_value 

#TODO: FIX THE CASE WITH / IN THE TRAIN ID, THEY ARE NOT FOUND AS THE FINAL PART, EG: possible error with VIA50/60.1 possible error with VIA52/62.1  
def filter_nrt_connection_S3_S4(criteria_dict, col_name_of_identifier, col_true_value, bound_direction,Bound,scenario):
    keys_to_check = keys_with_values(criteria_dict, col_true_value, col_name_of_identifier, bound_direction, Bound)
    nrt_connection_dictionary = {}
    if bound_direction == "Outbound":
        connection_type = 2
        column_nrt_found = 'Train_ID'
        column_to_look_for_key = 'ConnTrain_ID'
    elif bound_direction == "Inbound":
        connection_type = 2
        column_nrt_found = "ConnTrain_ID"
        column_to_look_for_key = 'Train_ID'

    for train_id in keys_to_check:
        if scenario == "S3":
            modified_train_id = train_id + ".1"
        if  scenario == "S4":
            modified_train_id = train_id + ".2"
        
        nrt_that_matches = df_Connection.loc[(df_Connection[column_to_look_for_key] == modified_train_id) &
                                             (df_Connection['ConnectionType'] == connection_type), column_nrt_found]
        if nrt_that_matches.empty:
            print(f"No matching NRT found for train {train_id}.")
            continue
        if 'E' not in nrt_that_matches.iat[0]:
            print(f"No matching NRT found for train {train_id}, connection 2 is train: {nrt_that_matches.iat[0]}.")
            continue
        if not nrt_that_matches.empty and nrt_that_matches.iat[0] in connection_timetable_dict.keys():
            nrt_connection_dictionary[train_id] = nrt_that_matches.iat[0]
        
    return nrt_connection_dictionary

def filter_nrt_connection_S1_S2(criteria_dict, col_name_of_identifier, col_true_value, bound_direction,Bound):
    keys_to_check = keys_with_values(criteria_dict, col_true_value, col_name_of_identifier, bound_direction, Bound)
    nrt_connection_dictionary = {}
    if bound_direction == "Outbound":
        connection_type = 2
        column_nrt_found = 'Train_ID'
        column_to_look_for_key = 'ConnTrain_ID'
    elif bound_direction == "Inbound":
        connection_type = 2
        column_nrt_found = "ConnTrain_ID"
        column_to_look_for_key = 'Train_ID'

    for train_id in keys_to_check:
        nrt_that_matches = df_Connection.loc[(df_Connection[column_to_look_for_key] == train_id) &
                                             (df_Connection['ConnectionType'] == connection_type), column_nrt_found]
        if nrt_that_matches.empty:
            print(f"No matching NRT found for train {train_id}.")
            continue
        if 'E' not in nrt_that_matches.iat[0]:
            print(f"No matching NRT found for train {train_id}, connection 2 is train: {nrt_that_matches.iat[0]}.")
            continue
        if not nrt_that_matches.empty and nrt_that_matches.iat[0] in connection_timetable_dict.keys():
            nrt_connection_dictionary[train_id] = nrt_that_matches.iat[0]
        
    return nrt_connection_dictionary

def nrt_check_S3_S4(criteria_dict, col_name_of_identifier, col_true_value, bound_direction, Bound,scenario):
    nrt_connection_dictionary = filter_nrt_connection_S3_S4(criteria_dict, col_name_of_identifier,col_true_value, bound_direction, Bound,scenario)
    for train_id, nrt_value in nrt_connection_dictionary.items():
        if scenario == "S3":
            modified_train_id = train_id + ".1"
        if  scenario == "S4":
            modified_train_id = train_id + ".2"
        print(f"{train_id} has a matching NRT. The matching NRT for {train_id} is: {nrt_value}")
    return True

def nrt_check_S1_S2(criteria_dict, col_name_of_identifier, col_true_value, bound_direction, Bound):
    nrt_connection_dictionary = filter_nrt_connection_S3_S4(criteria_dict, col_name_of_identifier,col_true_value, bound_direction, Bound)
    for train_id, nrt_value in nrt_connection_dictionary.items():
        print(f"{train_id} has a matching NRT. The matching NRT for {train_id} is: {nrt_value}")
    return True

#------------------------------------------------------------------------------------------------------------

def connection_check_for_dwell_S3_S4(criteria_time,scenario):
    
    for index,row in VIA_Train_Input_criteria.iterrows():
        Train_ID = row["Train_ID"]
       
        if row["Bound"] == "Outbound":
            connection_type = 2
            column_nrt_found = 'Train_ID'
            column_to_look_for_key = 'ConnTrain_ID'
        elif row["Bound"] == "Inbound":
            connection_type = 2
            column_nrt_found = "ConnTrain_ID"
            column_to_look_for_key = 'Train_ID'
        
        if scenario == "S3":
            modified_train_id = Train_ID + ".1"
        if  scenario == "S4":
            modified_train_id = Train_ID + ".2"    
        dwell_time = df_Connection.loc[(df_Connection[column_to_look_for_key] == modified_train_id) & 
                                    (df_Connection['ConnectionType'] == connection_type), :]
        if dwell_time.empty:
            print(f"No matching Connection train found for train {Train_ID}.")
            continue
        
        time_string = dwell_time["ConnChangeTime"].values[0]
        time_object = datetime.strptime(time_string,"%H:%M:%S").time()
        connection_Train_ID = dwell_time[column_nrt_found].values[0]
        criteria = datetime.strptime(criteria_time,"%M:%S").time()
        if 'E' not in connection_Train_ID:
            if time_object < criteria :
                print(f"{Train_ID} with connection {connection_Train_ID} does not meet minimum dwell time at union of {criteria} MINS with {time_object}")
            continue
def connection_check_for_dwell_S1_S2(criteria_time):
    
    for index,row in VIA_Train_Input_criteria.iterrows():
        Train_ID = row["Train_ID"]
       
        if row["Bound"] == "Outbound":
            connection_type = 2
            column_nrt_found = 'Train_ID'
            column_to_look_for_key = 'ConnTrain_ID'
        elif row["Bound"] == "Inbound":
            connection_type = 2
            column_nrt_found = "ConnTrain_ID"
            column_to_look_for_key = 'Train_ID'
            
        dwell_time = df_Connection.loc[(df_Connection[column_to_look_for_key] == Train_ID) & 
                                    (df_Connection['ConnectionType'] == connection_type), :]
        if dwell_time.empty:
            print(f"No matching Connection train found for train {Train_ID}.")
            continue
        
        time_string = dwell_time["ConnChangeTime"].values[0]
        time_object = datetime.strptime(time_string,"%H:%M:%S").time()
        connection_Train_ID = dwell_time[column_nrt_found].values[0]
        criteria = datetime.strptime(criteria_time,"%M:%S").time()
        if 'E' not in connection_Train_ID:
            if time_object < criteria :
                print(f"{Train_ID} with connection {connection_Train_ID} does not meet minimum dwell time at union of {criteria} MINS with {time_object}")
            continue

#------------------------------------------------------------------------------------------------------------

def connection_time_check_for_NRT_S3_S4(criteria_time_NRT_to_Outbound,criteria_time_Inbound_to_NRT,scenario):
        
    for index,row in VIA_Train_Input_criteria.iterrows():
        Train_ID = row["Train_ID"]
       
        if row["Bound"] == "Outbound":
            connection_type = 2
            column_nrt_found = 'Train_ID'
            column_to_look_for_key = 'ConnTrain_ID'
            criteria = criteria_time_NRT_to_Outbound
        elif row["Bound"] == "Inbound":
            connection_type = 2
            column_nrt_found = "ConnTrain_ID"
            column_to_look_for_key = 'Train_ID'
            criteria = criteria_time_Inbound_to_NRT
        if scenario == "S3":
            modified_train_id = Train_ID + ".1"
        if  scenario == "S4":
            modified_train_id = Train_ID + ".2"    
            
        dwell_time = df_Connection.loc[(df_Connection[column_to_look_for_key] == modified_train_id) & 
                                    (df_Connection['ConnectionType'] == connection_type), :]
        if dwell_time.empty:
            print(f"No matching Connection train found for train {Train_ID}.")
            continue
        
        time_string = dwell_time["ConnChangeTime"].values[0]
        time_object = datetime.strptime(time_string,"%H:%M:%S").time()
        connection_Train_ID = dwell_time[column_nrt_found].values[0]
        criteria = datetime.strptime(criteria,"%M:%S").time()
        if 'E' not in connection_Train_ID:
            continue 
        if  time_object < criteria:
            print(f"{Train_ID} with connection {connection_Train_ID} does not meet minimum dwell time at union of {criteria} MINS with {time_object}")
    return True

def connection_time_check_for_NRT_S1_S2(criteria_time_NRT_to_Outbound,criteria_time_Inbound_to_NRT):
        
    for index,row in VIA_Train_Input_criteria.iterrows():
        Train_ID = row["Train_ID"]
       
        if row["Bound"] == "Outbound":
            connection_type = 2
            column_nrt_found = 'Train_ID'
            column_to_look_for_key = 'ConnTrain_ID'
            criteria = criteria_time_NRT_to_Outbound
        elif row["Bound"] == "Inbound":
            connection_type = 2
            column_nrt_found = "ConnTrain_ID"
            column_to_look_for_key = 'Train_ID'
            criteria = criteria_time_Inbound_to_NRT
            
        dwell_time = df_Connection.loc[(df_Connection[column_to_look_for_key] == Train_ID) & 
                                    (df_Connection['ConnectionType'] == connection_type), :]
        if dwell_time.empty:
            print(f"No matching Connection train found for train {Train_ID}.")
            continue
        
        time_string = dwell_time["ConnChangeTime"].values[0]
        time_object = datetime.strptime(time_string,"%H:%M:%S").time()
        connection_Train_ID = dwell_time[column_nrt_found].values[0]
        criteria = datetime.strptime(criteria,"%M:%S").time()
        if 'E' not in connection_Train_ID:
            continue 
        if  time_object < criteria:
            print(f"{Train_ID} with connection {connection_Train_ID} does not meet minimum dwell time at union of {criteria} MINS with {time_object}")
    return True

#------------------------------------------------------------------------------------------------------------

def test_check_last_value_in_range():
    assert check_last_value_in_range_S3_S4(Via_df_Timetable_dict, "Arrival Time","Inbound") == True
    assert check_last_value_in_range_S3_S4(Via_df_Timetable_dict, "Departure Time","Outbound") == True

def test_nrt_check():
    assert nrt_check_S3_S4(VIA_Train_Input_criteria_dict,"Star Icon", "yes","Outbound","Bound") == True
    assert nrt_check_S3_S4(VIA_Train_Input_criteria_dict,"Star Icon", "yes","Inbound","Bound") == True

def test_connection_time_check_for_NRT():
    assert connection_time_check_for_NRT_S3_S4("1:00","1:00")== True

def test_max_runtime_for_train():
    assert max_runtime_for_train_S3_S4({}, "Aldershot Station", "Burlington Junction", "00:15:00") == None
    assert max_runtime_for_train_S3_S4(Via_df_Timetable_dict,"Union Station","Burlington Junction","00:44:00") == True

def test_station_stop_check():
    assert station_stop_check(VIA_Train_Input_criteria_dict,"Guildwood Station") == True
    assert station_stop_check(VIA_Train_Input_criteria_dict,"Union Station") == True
    assert station_stop_check(VIA_Train_Input_criteria_dict,"Guildwood Station","Union Station","")  == True

#------------------------------------------------------------------------------------------------------------
#TODO:655,VIA60 exception need to be coded in SAME WITH THE / TRAINS, potential only issue for old datafile,
#investigate when new timetable is here.
#TODO:2b iv)exception 88 which may bypass malton station, will be fixed in bus logic output writing

def test_box1():
    test_max_runtime_for_train()
    test_nrt_check()
    test_station_stop_check()
    test_check_last_value_in_range()

#NOTE: Durham Jct/Pickering Jct is Pickering Jct

#------------------------------------------------------------------------------------------------------------
#station_stop_check(Via_df_Timetable_dict,"Guildwood")

#S3 commands to run

connection_check_for_dwell_S3_S4("40:00",scenario)
connection_time_check_for_NRT_S3_S4("30:00","10:00",scenario)
check_if_selected_category_dwells_on_station_based_on_icon_S3_S4(Via_df_Timetable_dict, "Cross Icon", "yes", "Guildwood Station",60,scenario)
check_if_selected_category_dwells_on_station_based_on_icon_S3_S4(Via_df_Timetable_dict, "Table", "Table 2", "Oakville Station",60,scenario)
check_if_selected_category_dwells_on_station_based_on_icon_S3_S4(Via_df_Timetable_dict, "Table", "Table 2", "Aldershot Station",60,scenario)
check_last_value_in_range_S3_S4(Via_df_Timetable_dict, "Arrival Time","Inbound")
check_last_value_in_range_S3_S4(Via_df_Timetable_dict, "Departure Time","Outbound")
max_runtime_for_train_S3_S4(Via_df_Timetable_dict,"Union Station","Burlington Junction","00:44:00",scenario)
max_runtime_for_train_S3_S4(Via_df_Timetable_dict,"Union Station","Durham Jct/Pickering Jct","00:35:00",scenario)
max_runtime_for_train_S3_S4(Via_df_Timetable_dict,"Union Station","Agincourt Junction","00:20:00",scenario)
max_runtime_for_train_S3_S4(Via_df_Timetable_dict,"Burlington Junction","Aldershot Station","00:15:00",scenario)
max_runtime_for_train_S3_S4(Via_df_Timetable_dict,"Aldershot Station","Bayview Jct","00:10:00",scenario)
max_runtime_for_train_S3_S4(Via_df_Timetable_dict,"Union Station","Halwest Junction","00:29:00",scenario)
max_runtime_for_train_S3_S4(Via_df_Timetable_dict,"Georgetown Station","Kitchener Station","00:55:00",scenario)
max_runtime_for_train_S3_S4(Via_df_Timetable_dict,"Union Station","Snider North Turnback","00:35:00",scenario)
max_runtime_for_train_S3_S4(Via_df_Timetable_dict,"Snider North Turnback","Doncaster","00:04:00",scenario)
max_runtime_for_train_S3_S4(Via_df_Timetable_dict,"Glencrest Loop","Union Station","00:30:00",scenario)



print("Process finished --- %s seconds ---" % (time.time() - start_time))

#------------------------------------------------------------------------------------------------------------

#TODO:FIX MIDNIGHT EDGE CASE I don't think this is an issue, module takes care of it but worth a test!VIA 78
#POSSIBLE FIX TO MIDNIGHT RANGE ISSUE....
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

#------------------------------------------------------------------------------------------------------------

#TODO: Write a a startign senario where there is no connection table S1 OR S2
#TODO: fix test boxes.


#if the train appears in both weekday and weekend, record the information, use the same train name but set day to weekend or weekday