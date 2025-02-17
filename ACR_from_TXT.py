#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import re
import requests
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


# ---- SOURCE FILE DEPENDENCIES
# Required files within the same directory
# ACR_Projects.txt
# ACR_RetiredCredits.txt
# country_codes.csv


# --- HELPER FUNCTIONS ----

# Returns a dictionary of country code and country name mappings
def pull_local_country_dict():
    organized_country_data = {}
    country_df=pd.read_csv('country_codes.csv', header=0, index_col=0)
    organized_country_data = country_df.to_dict()['0']
    
    return organized_country_data

# Fetches country code and name mappings
# if the webpage is unavailable, it pulls from the local file country_codes.csv
def populate_country_dict():
    
    
    loc_url = 'https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/countries-codes/records?limit=100&offset=0'  
    data_list = {}
    organized_country_data = {}
    prior_failure = False
    
    for i in range(3):
        
        # there are ~250 countries and the webpage has a view limit of 100
        # offset is the starting point
            
        try:
            response = requests.get(loc_url[:-1]+str(i*100))
            
            if response.status_code == 200:
                data_list = response.json()
                
                for item in data_list.get('results'): 
                    new_key = item.get('iso2_code')
                    new_value = item.get('label_en')
                    organized_country_data[new_key] = new_value
        
        except:
            if not prior_failure:
                print('We could not update the list of country codes, so we will use a local version.')
                prior_failure = True 
                
            organized_country_data = pull_local_country_dict()
            
            
    return organized_country_data

    

def rename_file_in_directory(old_name, new_name, directory=os.getcwd()):
    # Construct full file paths
    old_file_path = os.path.join(directory, old_name)
    new_file_path = os.path.join(directory, new_name)
    
    try:
        # Rename the file
        os.rename(old_file_path, new_file_path)
        print(f"File renamed from '{old_name}' to '{new_name}' in directory '{directory}'")
    except FileNotFoundError:
        print(f"Error: The file '{old_name}' does not exist in '{directory}'.")
    except FileExistsError:
        print(f"Error: The file '{new_name}' already exists in '{directory}'.")
    except Exception as e:
        print(f"An error occurred: {e}")


# download a txt file, which the site calls temp
def download_temp_txt_file(url):
    # Set up Chrome options
    my_chrome_options = webdriver.ChromeOptions()
    my_chrome_options.add_experimental_option("prefs", {
        "download.default_directory": os.getcwd(),  # download to current directory
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    
    driver = webdriver.Chrome(options=my_chrome_options)

    try:
        # Navigate to the URL
        driver.get(url)

        # Wait for the page to load
        time.sleep(5)  

        txt_link = driver.find_element(By.ID, 'downloadtxtIcon')
        txt_link.click()

        # Wait for the file to download
        time.sleep(10)  # long wait, to be sure
    
    except Exception as e:
        print(f'An error occurred: {e}')
    finally:
        driver.quit()
        
# --- MAIN FUNCTION ----
# Call with no argument if you do not want to update local ACR files
# Call with argument True to update local files (will take about 30 seconds)
# Returns a dataframe with the data from ACR 

def runall(fresh_data=False):
    
    projects_url = 'https://acr2.apx.com/myModule/rpt/myrpt.asp?r=111'
    retired_credits_url = 'https://acr2.apx.com/myModule/rpt/myrpt.asp?r=206'
    
    # These are the default local files
    acr_projects = 'ACR_Projects.txt'
    acr_ret_credits = 'ACR_RetiredCredits.txt'
    
    organized_country_data = pull_local_country_dict()
    
    # update if user wants new data
    if fresh_data:
        download_temp_txt_file(projects_url)
        rename_file_in_directory('temp.txt', acr_projects)
        download_temp_txt_file(retired_credits_url)
        rename_file_in_directory('temp.txt', acr_ret_credits)

        organized_country_data = populate_country_dict()
    
    
    # --- Get retired credits
    fin_ret = open(acr_ret_credits, 
               'rt', #read text
              encoding='latin-1'
              )
    
    # file contains special characters inside content that brings content out of order
    # one problem is that the ID doesn't always list the retired credits (vacuous entry)
    # another is that there are random linebreaks from non \n characters
    
    header = fin_ret.readline() # pop the header line
    credits_retired = {}
    
    for line in fin_ret:
        # create a list of objects contained in each line
        # first object is an empty string, so we remove it
        line_objs = re.split('","|"',line.strip('\n'))[1:]
        # ensure that we have a line for each ID
        if re.search('^ACR.*', line_objs[0]):
            id_items = re.split('-| ', line_objs[0])
            # ignore vacuous entries
            if len(id_items) > 6:    
                id = line_objs[0][:3]+line_objs[0][7:10]
                number = int(id_items[-1]) - int(id_items[-3])+1
                if id in credits_retired:
                    number += credits_retired[id]
                credits_retired[id] = number
        
    fin_ret.close()
    
    
    # ----- Then populate the list of ID objects
    
    fin = open(acr_projects, 
               'rt', #read text
              encoding='latin-1'
              )
    
    
    list_of_projects = []
    
    # pops and returns the header line from fin
    header = fin.readline()
    
    
    
    for line in fin: 
        line_objs = line[:-1].split('","')
        id = line_objs[0][1:]
        
        if id not in credits_retired:
            ret = 0
        else:
            ret = credits_retired[id]
        
        credits_issued = 0
        if line_objs[-3] != '': 
            credits_issued += int(line_objs[-3])
            
        location = ''
        try:
            location = organized_country_data[line_objs[14]]
        except:
            location = 'Undefined Location'
            
        
        id_obj = {'Registry':'ACR', 
                  'ID': id,
                  'Name': line_objs[3],
                  'Type': line_objs[4],
                  'Location': location,
                  'SDGs': [int(sdg[0:2]) for sdg in line_objs[15].split(';') if sdg[0:2] != ''],
                  'Project Start Date': line_objs[6],
                  'Credits Issued': credits_issued,
                  'Credits Retired': ret,
                  'Project Website': line_objs[20]}
        list_of_projects.append(id_obj)
        
    fin.close()
    
    acr_df = pd.DataFrame(list_of_projects)
    
#    fout = open('ACR_CSV.csv', 
#                'wt', 
#                encoding="utf-8")
#    
#    acr_df.to_csv(fout, index=False)    
#    fout.close()
    
    return acr_df















