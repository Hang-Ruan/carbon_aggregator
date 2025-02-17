# TEAM: CARBON AGGREGATOR

## Members
- **Ian Hash (ihash)**
- **Hang Ruan (hruan)**
- **Yuxin Zheng (yuxinz3)**
- **Ida Mattsson (imattsso)**

---

## Welcome to Team Carbon Aggregator's Final Project!

### How to Run the Carbon Aggregator App

1. **Internet Connection:**  
   Ensure you have a stable internet connection.

2. **Install Anaconda and Python:**  
   If you haven’t already, download and install [Anaconda](https://www.anaconda.com/products/individual) (which includes Python). Allow Anaconda to install all the default packages.

3. **Chrome Browser:**  
   Make sure you have the latest version of the Chrome web browser installed.

4. **Install Required Packages:**  
   In addition to the default packages, install the following packages in your `base` environment (either via Anaconda’s Environments > Packages or using pip from the command line):

   - **Selenium:**  
     ```bash
     pip install selenium
     ```
   - **Chrome WebDriver Manager:**  
     ```bash
     pip install webdriver-manager
     ```
   - **Pandas:**  
     ```bash
     pip install pandas
     ```
   - **Requests:**  
     ```bash
     pip install requests
     ```

5. **Download and Unzip Files:**  
   Download and unzip `carbon_aggregator.zip` to your downloads folder, then unzip the folder.

6. **Run the Application:**  
   Open your preferred IDE, terminal, or IDLE and navigate to the folder containing `MAIN.py`. Then, execute the file.  
   *Note: The app has been successfully run using VSCode, PyCharm, Spyder on a Mac, and IDLE on a Windows machine.*

7. **Data Aggregation Options:**  
   When running `MAIN.py`, you will be prompted whether you want to clean local data or scrape fresh data before cleaning.
   
   - **OPTION 1:**  
     For the first run, it is recommended to choose this option. Enter any number key that is not 0 when prompted. This option aggregates and formats the data already present in the same folder as `MAIN.py`.
   
   - **OPTION 2:**  
     To download fresh data, move the following files out of the `carbon_aggregator` folder *before* running `MAIN.py` and selecting option `0`:
     - `ACR_Projects.txt`
     - `ACR_RetiredCredits.txt`
     - `allprojects.csv`
     - `vcus.csv`
     - `CAR_issued_projects_data.csv`
     - `CAR_retired_projects_data.csv`
     - `Mrk_projects.csv`
     - `Country_codes.csv`

     Once moved, select option `0` to scrape fresh data. The application will then output `all_Markets.csv` as described in step 9.

8. **Output:**  
   After the run completes, you should see the file `all_Markets.csv` in the `carbon_aggregator` folder. This file contains the aggregated data for all carbon credit markets and is used as the input for the data visualization tool.

9. **Data Visualization:**  
   For an enhanced viewing experience, check out our data visualization tool at:
   [https://carbonoffsetregistries.streamlit.app/](https://carbonoffsetregistries.streamlit.app/)

   The visualization includes:
   - A table of data from all four registries.
   - A bar graph showing the distribution of SDG for each registry.
   - A table of SDGs and their descriptions.
   - Filters and search bar interactions.

10. **Interactive Use:**  
    - **Start:** Select the desired location(s) on the sidebar to view the associated projects.
    - **Filter:**  
      - Filter the project table and SDG distribution chart by registries.
      - Filter the project table by location.
      - Use the search bar (numbers 1 to 17) to view projects for each SDG.

### How to Update the Visualization with New Data

1. **Download the Repository:**  
   Clone or download the repository from GitHub:  
   [https://github.com/yxinzh/carbonoffset-dataset](https://github.com/yxinzh/carbonoffset-dataset)

2. **Run Data Aggregation Script:**  
   Execute `count_sdg.py` from the `carbon_aggregator.zip` folder.  
   *Note: Ensure that `all_Markets.csv` (generated from `MAIN.py`) is present in the local folder.*  
   This will create a new CSV file named `sdg_counts.csv`.

3. **Update Files in the Repository:**  
   In the downloaded repository, navigate to the `data` folder and replace the old `all_Markets.csv` and `sdg_counts.csv` with the new ones.

4. **Run the Visualization App:**  
   Open your command interface, navigate to the repository folder, and run:
   ```bash
   streamlit run streamlit_app.py

Enjoy using the Carbon Aggregator App!
