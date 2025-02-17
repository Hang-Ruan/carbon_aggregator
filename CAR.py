#this script is used to scrape the data from the CAR website
#if refresh_data is set to True, the script will scrape the data from the website
#otherwise, it will read the data from the csv file: CAR_issued_projects_data.csv, CAR_retired_projects_data.csv
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
    TimeoutException,
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd

def setup_driver(headless=True):
    """
    Sets up the Selenium WebDriver.
    
    Parameters:
    - headless (bool): Whether to run the browser in headless mode.
    
    Returns:
    - webdriver.Chrome: Configured Selenium WebDriver.
    """
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options

    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--log-level=3")

    # Initialize WebDriver using WebDriver Manager
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def find_issued_target_table(soup):
    """
    Identifies the target table containing project data by matching required headers.

    Parameters:
    - soup (BeautifulSoup): Parsed HTML content.

    Returns:
    - Tag: The BeautifulSoup Tag object for the target table, or None if not found.
    """
    # Define the required headers based on desired keys
    required_headers = [
        'Project ID',
        'Project Name',
        'Project Type',
        'Date Issued',
        'Project Site Country',
        'Total Offset Credits Issued',
        'Project Website'
    ]

    tables = soup.find_all('table', width="100%", cellspacing="2", cellpadding="5", bgcolor="#F3F3ED")
    for table in tables:
        header_row = table.find('tr')
        if not header_row:
            continue
        headers = [th.get_text(strip=True) for th in header_row.find_all(['td', 'th'])]
        if all(header in headers for header in required_headers):
            return table
    return None


def find_retired_target_table(soup):
    """
    Identifies the target table containing project data by matching required headers.

    Parameters:
    - soup (BeautifulSoup): Parsed HTML content.

    Returns:
    - Tag: The BeautifulSoup Tag object for the target table, or None if not found.
    """
    # Define the required headers based on desired keys
    required_headers = [
        'Project ID',
        'Project Name',
        'Project Type',
        'Status Effective',       # Maps to 'Date Issued'
        'Project Site Country',
        'Quantity of Offset Credits'
        # 'Project Website' is not present in this table
    ]

    # Find all tables with specific attributes (adjust as necessary)
    tables = soup.find_all('table', width="100%", cellspacing="2", cellpadding="5", bgcolor="#F3F3ED")
    
    for table in tables:
        header_row = table.find('tr')
        if not header_row:
            continue  # Skip if no header row found
        
        # Extract full header names without splitting
        headers = [th.get_text(separator=' ', strip=True) for th in header_row.find_all(['td', 'th'])]
        
        # Check if all required headers are present in the current table (case-insensitive)
        if all(any(required_header.lower() in header.lower() for header in headers) for required_header in required_headers):
            return table  # Target table found
    return None  # Target table not found

def extract_issued_project_data(table):
    projects = []
    
    # Iterate over all data rows
    for row in table.find_all('tr')[1:]:  # Skip header row
        cells = row.find_all('td')
        if not cells or len(cells) < 26:
            continue  # Skip if not enough cells
        
        try:
            project = {
                'Registry':'CAR',
                'ID': cells[1].get_text(strip=True) or None,
                'Name': cells[3].get_text(strip=True) or None,
                'Type': cells[6].get_text(strip=True) or None,
                'Location': cells[22].get_text(strip=True) or None,
                'SDGs': [],
                'Project Start Date': cells[0].get_text(strip=True) or None,
                'Credits Issued': 0,
                'Credits Retired': 0, 
                'Project Website': None
            }
            
            # Num of credit issued (Column 14)
            num_credit_text = cells[14].get_text(strip=True)
            if num_credit_text:
                num_credit_text = num_credit_text.replace(',', '')
                try:
                    project['Credits Issued'] = int(num_credit_text)
                except ValueError:
                    project['Credits Issued'] = None
            
            # Project Website (Column 25)
            website_cell = cells[25]
            website_link = website_cell.find('a')
            if website_link and 'href' in website_link.attrs:
                project['Project Website'] = website_link['href']
            else:
                project['Project Website'] = None
            
            projects.append(project)
        except Exception as e:
            print(f"Error parsing row: {e}")
            continue  # Skip rows with parsing errors
    
    return projects

def extract_retired_project_data(table):
    """
    Extracts project data from the provided table based on specific column indices.

    Parameters:
    - table (Tag): BeautifulSoup Tag object representing the table.

    Returns:
    - List[Dict]: A list of dictionaries containing project data.
    """
    projects = []
    # Iterate over all data rows, skipping the header row
    for row in table.find_all('tr')[1:]:
        cells = row.find_all('td')
        if not cells or len(cells) < 19:
            continue  # Ensure the row has enough cells
    
        try:
            project = {
                'Registry':'CAR',
                'ID': cells[4].get_text(strip=True) or None,
                'Name': cells[5].get_text(strip=True) or None,
                'Type': cells[6].get_text(strip=True) or None,
                'Location': cells[11].get_text(strip=True) or None,
                'SDGs':[],
                'Project Start Date': cells[3].get_text(strip=True) or None,
                'Credits Issued': 0,
                'Credits Retired': 0,
                'Project Website': None
            }
             # Num of credit issued (Column 14)
            num_credit_text = cells[2].get_text(strip=True)
            if num_credit_text:
                num_credit_text = num_credit_text.replace(',', '')
                try:
                    project['Credits Retired'] = int(num_credit_text)
                except ValueError:
                    project['Credits Retired'] = None
                
            projects.append(project)
        except Exception as e:
            print(f"Error parsing row: {e}")
            continue  # Skip rows with parsing errors

    return projects

def find_next_button(driver):
    """
    Finds the "Next" button element on the current page.

    Parameters:
    - driver (webdriver.Chrome): The Selenium WebDriver instance.

    Returns:
    - WebElement or None: The Selenium WebElement for the "Next" button, or None if not found.
    """
    try:
        # Locate the "Next" button using the image's alt attribute
        next_button = driver.find_element(By.XPATH, "//a[img[@alt='move next']]")
        return next_button
    except NoSuchElementException:
        return None


def scrape_all_projects(start_url, total_page, delay_between_requests=2, headless=False,retired=False):
    """
    Scrapes all project data starting from the start_url by clicking the "Next" button using Selenium.

    Parameters:
    - start_url (str): The URL of the first page to start scraping.
    - delay_between_requests (int, optional): Delay in seconds between interactions to respect server load.
    - headless (bool): Whether to run the browser in headless mode.

    Returns:
    - List[Dict]: A list of dictionaries containing all scraped project data.
    """
    driver = setup_driver(headless=headless)
    projects = []
    seen_ids = set()
    page=1
    try:
        driver.get(start_url)
        time.sleep(delay_between_requests)  # Wait for the page to load
        
        while page<total_page:
            print(f"\nScraping Page {page}...")
            # Wait until the target table is present
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'table'))
                )
            except TimeoutException:
                print("Timeout waiting for the table to load.")
                break

            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'lxml')

            # Find the target table
            if retired:
                table = find_retired_target_table(soup)
            else:
                table = find_issued_target_table(soup)

            if not table:
                print("Target table not found on this page.")
                break

            # Extract project data
            if retired:
                page_projects = extract_retired_project_data(table)
            else:
                page_projects = extract_issued_project_data(table)
                
            if not page_projects:
                print("No project data found on this page.")
                break

            # Filter out duplicates based on 'ID'
            new_projects = []
            for project in page_projects:
                project_id = project.get('ID')
                if project_id and project_id not in seen_ids:
                    new_projects.append(project)
                    seen_ids.add(project_id)
                else:
                    print(f"Duplicate or missing Project ID: {project_id}")

            projects.extend(new_projects)
            print(f"Extracted {len(new_projects)} new projects from this page.")

            # Find and click the "Next" button
            next_button = find_next_button(driver)
            
            if next_button:
                try:
                    # Scroll to the "Next" button to ensure it's in view
                    driver.execute_script("arguments[0].scrollIntoView();", next_button)
                    time.sleep(1)  # Short pause to ensure the button is in view

                    next_button.click()
                    print("Clicked the Next button.")
                    page+=1
                except ElementClickInterceptedException:
                    print("Could not click the Next button. It might be hidden or overlapped by another element.")
                    break
                except Exception as e:
                    print(f"An unexpected error occurred while clicking Next: {e}")
                    break
            else:
                print("No Next button found. Scraping complete.")
                break

            # Wait for the next page to load
            time.sleep(delay_between_requests)

    finally:
        driver.quit()

    return projects

def runall(refresh_data=False):
    if refresh_data:
        # Define the URL of the first page
        start_url = 'https://thereserve2.apx.com/myModule/rpt/myrpt.asp?r=112'  

        # Scrape all projects
        all_issued_projects = scrape_all_projects(start_url, delay_between_requests=2, headless=False,total_page=79,retired=False)

        # Define the URL of the first page
        start_url = 'https://thereserve2.apx.com/myModule/rpt/myrpt.asp?r=206'  

        # Scrape all projects
        all_retired_projects = scrape_all_projects(start_url, delay_between_requests=2, headless=False,total_page=162,retired=True)
    
    else:
        all_issued_projects=pd.read_csv('CAR_issued_projects_data.csv').to_dict('records')
        all_retired_projects=pd.read_csv('CAR_retired_projects_data.csv').to_dict('records')

    all_projects=[]
    for i in all_issued_projects:
        for j in all_retired_projects:
            if i['ID']==j['ID']:
                i['Credits Retired']=j['Credits Retired']
        all_projects.append(i)

    map_dict={'MX':"Mexico",'US':"United States"}
    for i in all_projects:
        if i['Location'] in map_dict:
            i['Location']=map_dict[i['Location']]

    project_df = pd.DataFrame(all_projects)
    return project_df
