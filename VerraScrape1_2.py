
#general imports
from tabulate import tabulate
import csv
import pandas as pd
import io
#selenium imports for downloading csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

#move files from downloads folder
import os
import shutil

#---------------EXTRACT--------------------
#download VCU CSV from Verra and pull relevant columns and data including 'Registry', 'ID', 'Name', 'Project Type', 'Country/Area', 'Sustainable Development Goals', 'Quantity Issued', 'Retirement/Cancellation Date' (if date then retired)
#return a list of dicts, with column/value pairs
def retreiveVcuCsv(): #paramenters for url, I will call this twice for each data source
    #utilized chat to help learn about and how to use selenium for this purpose, and troubleshooting errors

    #Set up the WebDriver 
    #if you dont have chrome, install it, or switch this to .Safari() or .Firefox()
    driver = webdriver.Chrome()  

    #nav to the website
    driver.get("https://registry.verra.org/app/search/VCS")

    #wait for website to load, intentionally long wait
    wait = WebDriverWait(driver, 10)

    #set and click the vcus button
    vcus_button = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'VCUs')))
    vcus_button.click()
    time.sleep(5)

    #set and click the search button
    search_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="verra-application"]/div/apx-search-page/div/apx-search-container/div/div[2]/div/div[1]/apx-search-selection-criteria/div/form/div[2]/div/button[1]')))
    search_button.click()
    #sleep time intentionnaly long
    time.sleep(40)

    # Set and click the download button
    download_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="verra-application"]/div/apx-search-page/div/apx-search-container/div/div[2]/div/div[2]/apx-issuance-search-results/div/apx-search-results-header/div/button[1]/i')))
    download_button.click()
    #sleep time intentionally long
    time.sleep(60)

    #close browser
    driver.quit()


def retreiveAllProjCsv(): #paramenters for url, I will call this twice for each data source
    #Set up the WebDriver 
    #if you dont have chrome, install it, or switch this to .Safari() or .Firefox()
    driver = webdriver.Chrome()  

    #nav to the website
    driver.get("https://registry.verra.org/app/search/VCS")

    #wait for website to load, intentionally long wait
    wait = WebDriverWait(driver, 10)

    #set and click the vcus button
    vcus_button = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'All Projects')))
    vcus_button.click()
    time.sleep(5)

    #set and click the search button
    search_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="verra-application"]/div/apx-search-page/div/apx-search-container/div/div[2]/div/div[1]/apx-search-selection-criteria/div/form/div[2]/div/button[1]')))
    search_button.click()
    #sleep time intentionnaly long
    time.sleep(40)

    # Set and click the download button
    download_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="verra-application"]/div/apx-search-page/div/apx-search-container/div/div[2]/div/div[2]/apx-project-search-results/div/apx-search-results-header/div/button[1]/i')))
    download_button.click()
    #sleep time intentionally long
    time.sleep(60)

    #close browser
    driver.quit()


def move_file_from_downloads(filename):
    # Find the file in the Downloads folder
    downloads_folder = os.path.expanduser('~/Downloads')
    source_path = None
    
    if os.path.exists(downloads_folder):
        for file in os.listdir(downloads_folder):
            if filename in file:
                source_path = os.path.join(downloads_folder, file)
                break
    
    if source_path is None:
        print(f"File '{filename}' not found in Downloads folder.")
        return None
    
    # Get the current directory (where the .py file is located)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create the destination path
    destination_path = os.path.join(current_dir, os.path.basename(source_path))
    
    try:
        # Move the file
        shutil.move(source_path, destination_path)
        print(f"File moved successfully to: {destination_path}")
        return destination_path
    except Exception as e:
        print(f"Error moving file: {e}")
        return None


#---------------TRANSFORM--------------------
#Transform a csv input, return a dict #TODO remove if not used
def csv2Dict(inputFilePath):
    with open(inputFilePath, 'r', encoding='utf-8', newline = '') as inputFile: #encoding test
        csvInputReader = csv.DictReader(inputFile)
        #returns list of dictionaries 
        csvDict = [dict(row) for row in csvInputReader]
        return csvDict    

#transform Vcu data to dict, with additional columns and extracted/formatted data
def VcuCsvScrape(inputFilePath, selectedColumns):

    data = []
    addColumns = ['Registry', 'Credits Retired', 'SDGs', 'Project Website']
    prjURL = "https://registry.verra.org/app/projectDetail/VCS/"
    
    with open(inputFilePath, 'rb') as inputFile:
        # Reads existing CSV into a list of dictionaries using csv.reader
        # Read the file and replace NULL bytes with an empty byte
        cleaned_data = inputFile.read().replace(b'\x00', b'')

        # Convert the cleaned binary data back to a string
        cleaned_data_str = cleaned_data.decode('utf-8', errors='replace')

        # Use StringIO to treat the cleaned string data as a file
        inputFile = io.StringIO(cleaned_data_str)

        # Read the CSV data using csv.reader
        csv_reader = csv.reader(inputFile)

        # Read the header
        header = next(csv_reader)

        # Iterate through the rest of the lines (data rows)
        for row in csv_reader:
            # Check if the row has enough columns and process the data
            selectedData = {col: row[header.index(col)] for col in selectedColumns if col in header}
            for keys in addColumns:
                selectedData[keys] = ''
                selectedData['Registry'] = 'VERRA'
                selectedData['Project Website'] = prjURL + str(selectedData['ID'])
                selectedData['Quantity Issued'] = selectedData['Quantity Issued'].replace(',','').strip()
                if (selectedData['Retirement/Cancellation Date']):
                    selectedData['Credits Retired'] = selectedData['Quantity Issued']
                if (selectedData['Sustainable Development Goals']):
                    s = selectedData['Sustainable Development Goals']
                    sdgList = []
                    for index, char in enumerate(s):
                        if char == ":":
                            sdgList.append(s[(index - 2):index])
                    selectedData['SDGs'] = sdgList
                if (selectedData['Sustainable Development Goals'] == ''):
                    selectedData['SDGs'] = []
            data.append(selectedData)
    return data   

#download AllProjects CSV from Verra and pull relevant columns and data including 'Crediting Period Start Date', 
def VcsAllProjectsScrape(dictFromCsv, selectedColumns):
    data = []
    for row in dictFromCsv:
        selectedData = {col: row[col] for col in selectedColumns if col in row}
        data.append(selectedData)
    return data

#Summarize issued/retired data by project
def summaryDict(inputList, keys2Summarize):
    summaryList = []
    idList = []

    for dict in inputList:
        if dict['ID'] not in idList:
            idList.append(dict['ID'])
            summaryList.append(dict)
            # test = dict['Quantity Issued']
            # dict['Quantity Issued'] = test.replace(',', '')
        elif dict['ID'] in idList:
            for dict2 in summaryList:
                if dict['ID'] == dict2['ID']:
                    #summarize quantity issued
                    vI1 = dict2['Quantity Issued']
                    vI2 = dict['Quantity Issued']
                    vINew = int(vI1) + int(vI2)
                    dict2['Quantity Issued'] = str(vINew) #TODO come back and format this string with commas, or do it later in the process
                    #summarize credits retired
                    vR1 = dict2['Credits Retired']
                    vR2 = dict['Credits Retired']
                    if (vR1 == ''):
                        vR1 = '0'
                    if (vR2 == ''):
                        vRNew = vR1
                    if (vR2 != '' and vR1 == '0'):
                        vRNew = vR2
                    elif (vR2 != ''):
                        vRNew = int(vR1) + int(vR2)
                    dict2['Credits Retired'] = str(vRNew) #TODO come back and format this string with commas, or do it later in the process
                    
    return summaryList


#combine the two output
def combineData(vcuSummarized, allProjListStartDates):
    combinedList = []

    for dict in vcuSummarized:
        combinedList.append(dict)
        dict['Crediting Period Start Date'] = ''
    
    for dict in combinedList:
        targetValue = dict['ID']
        dictList = [d for d in allProjListStartDates if d.get('ID') == targetValue]
        if (dictList):
            dictStartDate = dictList[0]
            date = dictStartDate['Crediting Period Start Date']
            if (date != ''):
                date2 = date[5:7] + '/' + date[8:] + '/' + date[0:4]
            else:
                date2 = ''
        else: 
            date2 = ''
        dict['Crediting Period Start Date'] = date2

    return combinedList


def cleanFormat (combinedList):
    formattedList = []
    newOrder = ['Registry', 'ID', 'Name', 'Type', 'Location', 'SDGs', 'Project Start Date', 'Credits Issued', 'Credits Retired', 'Project Website']

    for dict in combinedList:
        dict['Type'] = dict.pop('Project Type')
        dict['Location'] = dict.pop('Country/Area')
        dict['Credits Issued'] = dict.pop('Quantity Issued')
        # dict['Credits Retired'] = dict.pop('Retirement/Cancellation Date')
        dict.pop('Retirement/Cancellation Date')
        dict['Project Start Date'] = dict.pop('Crediting Period Start Date')
        formattedDict = {key: dict[key] for key in newOrder if key in dict}
        formattedList.append(formattedDict)

    return formattedList   

#---------------LOAD/EXPORT--------------------
def dictList2DF(formattedDictList):
    df = pd.DataFrame(formattedDictList)
    return df


# def dicts2DF(formattedDictList):
#     df = pd.DataFrame(formattedDictList)
#     #df.to_csv(outputFilePath, index=False)
#     return df

#---------------SET MAIN PROCESSES TO RUN--------------------

#this function includes 
def runall(fresh_data=False):   #def runall(fresh_data=False):
    #preset filenames
    vcuInputFilePath = 'vcus.csv'
    allProjInputFilePath = 'allprojects.csv'

    if (fresh_data):
        #retreive data
        retreiveVcuCsv()
        retreiveAllProjCsv()

        #move Data to current folder
        move_file_from_downloads(vcuInputFilePath)
        move_file_from_downloads(allProjInputFilePath)

    #Scrape from vcus.csv
    vcuColumns2Include = ['Sustainable Development Goals','ID', 'Name', 'Project Type','Country/Area','Quantity Issued', 'Retirement/Cancellation Date']
    vcuDict = VcuCsvScrape(vcuInputFilePath, vcuColumns2Include)
    #Summarize vcu.csv Data
    keys2Summarize = ['Quantity Issued']
    vcuSummarized = summaryDict(vcuDict, keys2Summarize)

    #Scraop from allprojects.csv
    allProjInputFilePath = 'allprojects.csv'
    allProjColumns2Include = ['ID', 'Crediting Period Start Date']

    allProjList = csv2Dict(allProjInputFilePath)
    allProjListStartDates = VcsAllProjectsScrape(allProjList, allProjColumns2Include)

    #Combine Data
    combinedData = combineData(vcuSummarized, allProjListStartDates)
    formattedDictList = cleanFormat(combinedData)

    # return finsihed formatted DF
    verraDf = dictList2DF(formattedDictList)
    return verraDf
