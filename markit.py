import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException #reference: ChatGPT
import time
import pandas as pd

#Reference: "Python Selenium Tutorial #1 - Web Scraping, Bots & Testing" by Tech With Tim on YouTube https://www.youtube.com/watch?v=Xjv1sY630Uc&t=576s
driver = webdriver.Chrome()

#iterables for storage

issuances_dict = {}
data_list = []

#functiions
def extract_data(url):
    driver.get(url)
    while True:
        time.sleep(5)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        table_list = soup.find('table')
        if table_list: #make sure it's not null
            for row in table_list.find_all('tr'):
                data = {}
                cells = row.find_all('td')
                values = [cell.text.strip() for cell in cells]

                base = 'https://mer.markit.com/br-reg/public/'
                a_tags = row.find_all('a') #find hyperlink to extract id
                detail_url = [base + a.get('href') for a in a_tags]  # extracts url to details
                proj_id = [a.get('href')[a.get('href').find('=')+1:] for a in a_tags] #extracts id of projects

                project_details = values + proj_id #list of details for each project

                if project_details: #only take valid projects with id
                    project = 'MRK' + project_details[-1]
                    if project in issuances_dict:
                        issuances_dict[project]['Credits Issued'] += int(project_details[6].replace(',',''))
                    else:
                        data['Registry'] = 'MRK'
                        data['ID'] = project
                        data['Name'] = project_details[1]
                        data['Type'] = project_details[4]
                        data['Location'] = ''
                        data['SDGs'] = []
                        data['Project Start Date'] = ''
                        data['Credits Issued'] = int(project_details[6].replace(',',''))
                        data['Credits Retired'] = 0
                        if detail_url:
                            data['Project Website'] = detail_url[0]
                        else:
                            data['Project Website'] = ''
                        issuances_dict[project] = data
        try:
            next_link = driver.find_element(By.LINK_TEXT, 'Next →') #while true, try click next, except break, reference: ChatGPT
            next_link.click()
        except NoSuchElementException:
            break

def extract_retired_credits(url):
    driver.get(url)
    while True:
        time.sleep(5)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        table_list = soup.find('table')
        if table_list:
            for row in table_list.find_all('tr')[1::2]: #skipping every other row, reference: ChatGPT
                cells = row.find_all('td')
                values = [cell.text.strip() for cell in cells]
                a_tags = row.find_all('a')  # find hyperlink to extract id
                if a_tags:
                    proj_id = [a.get('href')[a.get('href').find('=') + 1:] for a in a_tags]  # extracts id of projects
                    project = 'MRK' + proj_id[0]
                    if project in issuances_dict:
                        issuances_dict[project]['Credits Retired'] += int(values[7].replace(',',''))
        try:
            next_link = driver.find_element(By.LINK_TEXT, 'Next →') #while true, try click next, except break, reference: ChatGPT
            next_link.click()
        except NoSuchElementException:
            break

def fill_location(dict):
    l1 = []
    if dict['Project Website']:
        driver.get(dict['Project Website']) #go to website
        time.sleep(5)  # Wait for the page to load, reference: ChatGPT
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        table_list = soup.find('table', class_='table table-condensed table-hover table-shadow')
        if table_list:
            for row in table_list.find_all('tr'):
                cells = row.find_all('td')
                values = [cell.text.strip() for cell in cells] # text.strip() reference: ChatGPT
                l1.append(values)
        # return str of country
        last_comma = l1[2][0].rfind(',')
        dict['Location'] = l1[2][0][last_comma + 1:]

def runall(refresh_data=False):
    if refresh_data:
        url = 'https://mer.markit.com/br-reg/public/index.jsp?entity=issuance&srd=false&sort=account_name&dir=ASC&start=0&entity_domain=Markit&additionalCertificationId=&acronym=&standardId=&categoryId=&unitClass='
        retired_url = 'https://mer.markit.com/br-reg/public/index.jsp?entity=retirement&srd=false&sort=account_name&dir=ASC&start=0&entity_domain=Markit&additionalCertificationId=&acronym=&standardId=&categoryId=&unitClass='
        if refresh_data:
            extract_data(url)
            extract_retired_credits(retired_url)

            for value in issuances_dict.values():
                fill_location(value)

            #close browser
            driver.quit()
            #fill in list for dataframe
            for key, value in issuances_dict.items():
                data_list.append(value)
            #create dataframe
            df = pd.DataFrame(data_list)
            return df

            #convert df to csv
            # df.to_csv('markit_projects.csv', index=False)
    else:
        df = pd.read_csv('mrk_projects.csv')
        return df



