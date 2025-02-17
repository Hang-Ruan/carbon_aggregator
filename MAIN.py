#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 21:29:41 2024


"""
import pandas as pd
from SdgDict import SdgDict

#import each scraper app
import ACR_from_TXT as acr
import VerraScrape1_2 as verra
import CAR as car
import markit as mkt


# uncomment if we want to force the user to run main
# remove if just running the file is sufficient
#def main():
    
refresh_data = False

# Check if the user wants to update the data
# 0 input is the only one that should prompt refreshing the data
try:
    refresh_data = not int(input('Do you want to update the data and overwrite the available datafiles?\n'
                               'Note: this operation will take around 2 to 3 hours to complete and will download new files into your local folder.\n'
                                   'Type 0 to get new data. Type another number to proceed without refreshing data(check README 9 for what file will be used): '))
    
    if refresh_data: 
        print ('Sit tight, we are scraping new data, just for you!')
    else: print('OK! We are going to use local data files and a subset of HTML data.')
    
    # --- Run all formatting (and optionally, scraping) functions to generate combined CSV files: 
    # create a list of all project dataframes

    project_dfs =[project.runall(refresh_data) for project in [acr,car,verra,mkt]] # note that the name comes from the import list    
    all_project=pd.concat(project_dfs,axis=0).reset_index(drop=True)
    
    #Map inferred SDGs to projects without SDGs pre-assigned
    #The SDG map was created by assigning defualt SDG sets to all project types based on other similar projects types with SDGs assigned, and market knowledge/understanding
    map=SdgDict()
    for i in range(len(all_project)):
        all_project.at[i,'SDGs']=map[str(all_project.loc[i,'Type'])]

    #write merged and updated DF to csv output
    fout = open('all_Markets.csv', 
                'wt', 
                encoding="utf-8")
        
    all_project.to_csv(fout,index=False)
    
    print('You now have a CSV file in your local folder, called all_Markets.\n'
          +'This file contains all public information we could find on the carbon credit market.\n')
                       
except:
      print('You seem to have entered something we do not understand.\n'
            'We hope you actually wanted to know all there is to know about the carbon credit market.\n'
            'If so, please run the program again.')

finally:
    print('We also create a website for this project: ')
    print("https://carbonoffsetregistries.streamlit.app")

