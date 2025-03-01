from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException, NoSuchFrameException
import pandas as pd
import time
import re

# This is the webscraping script that is run to collect all the events at Univeristy of South Carolina and Columbia. Written by Anne. 

driver  = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.maximize_window()

locations_list = []
titles_list = []
start_dates_list = []
end_dates_list = []
filter_list = []
url_list= []
df = pd.DataFrame(columns=['Title','Location','Start_Date','End_Date','Filter']) 
 # EDIT THIS when need to update what timeframe we are scraping 
months_to_track = ["April 2023","May 2023","June 2023","July 2023","August 2023"]

# Boolean variable for testing. Change to true when we want to pull from all websites. 
uofsc_events =  True
columbia_events = True
athletic_events = True

# METHODS FOR DATE FORMATTING/DATA CLEANING

# Return numerical representation of month based on text
def identify_month(str):
        if str.find('jan') != -1 or str.find('january') != -1:
                return "01"
        elif str.find('feb') != -1 or str.find('february') != -1:
                return "02"
        elif str.find('mar') != -1 or str.find('march') != -1:
                return "03"
        elif str.find('apr') != -1 or str.find('april') != -1:
                return "04"
        elif str.find('may') != -1:
                return "05"
        elif str.find('jun') != -1 or str.find('june') != -1:
                return "06"
        elif str.find('jul') != -1 or str.find('july') != -1:
                return "07"
        elif str.find('aug') != -1 or str.find('august') != -1:
                return "08"
        elif str.find('sep') != -1 or str.find('september') != -1:
                return "09"
        elif str.find('oct') != -1 or str.find('october') != -1:
                return "10"
        elif str.find('nov') != -1 or str.find('november') != -1:
                return "11"
        elif str.find('dec') != -1 or str.find('december') != -1:
                return "12"
        else: 
                return "0"

# Format the times of UofSC Events
# Starting Format Example: Tuesday, Feb. 21, 8:30 a.m. – 4:30 p.m.
def format_time_uofsc(list_nums,res):
        length = len(list_nums)
        # Accounts For Format: Wednesday, Feb. 22, 11 a.m. – 2 p.m. (3 numbers in the string)
        if length == 3:
                hour = str(list_nums[1])
                hour = am_or_pm(res,hour)
                start_time = hour + ":00:00"
                hour = str(list_nums[2])
                hour = am_or_pm(res,hour)
                end_time = hour + ":00:00"
                return start_time, end_time
        # Accounts For Format: Tuesday, Feb. 21, 8:30 a.m. – 4:30 p.m. (5 numbers in the string)
        elif length == 5:
                hour = str(list_nums[1])
                hour = am_or_pm(res,hour)
                min = str(list_nums[2])
                start_time = hour + ":" + min + ":00"
                hour = str(list_nums[3])
                hour = am_or_pm(res,hour)
                min = str(list_nums[4])
                end_time = hour + ":" + min + ":00"
                return start_time, end_time
        # Accounts For Format: Tuesday, Feb. 21, 8 a.m. – 4:30 p.m. (4 numbers in the string)
        elif length == 4:
                temp = str(list_nums[2])
                # Checks which time has non-zero minutes
                if temp == '15' or temp == '30' or temp == '45':
                        hour = str(list_nums[1])
                        hour = am_or_pm(res,hour)
                        min = str(list_nums[2])
                        start_time = hour + ":" + min + ":00"
                        hour = str(list_nums[3])
                        hour = am_or_pm(res,hour)
                        end_time = hour + ":00:00"
                        return start_time, end_time
                else:
                        hour = str(list_nums[1])
                        hour = am_or_pm(res,hour)
                        start_time = hour + ":00:00"
                        hour = str(list_nums[2])
                        hour = am_or_pm(res,hour)
                        min = str(list_nums[3])
                        end_time = hour + ":" + min + ":00"
                        return start_time, end_time
        else:  
                return ""

# Format the times of Columbia and Athletic Events
# Starting Format Example: Thu Feb 23 1:00 pm or Fri Feb 24 - Sat Feb 25 or May 9 @ 1:00 pm
# Need to account for multiple day activities 
def format_time(list_nums,multiday_event,all_day,tba,res):
        # If multiday event, assign arbitrary start time of noon
        if multiday_event:
                time = "12:00:00"
                return time
        if all_day != -1:
                time = "9:00:00"
                return time
        if tba != -1:
                time = "00:00:00"
                return time
        else:
                # Check for hours and minutes
                hour = str(list_nums[1])
                hour = am_or_pm(res,hour)
                if list_nums[2] == 0:
                        minute = "00"
                else:
                        minute = str(list_nums[2])
                time = hour + ":" + minute + ":00"
                return time

# Format the complete datetime usign original string and boolean for uofsc event
def format_date(og_date,usc_event):
        # Will this be a multiday event? Like this format: Fri Feb 24 - Sat Feb 25
        if og_date.find('-') != -1:
                multiday_event = True
        else:
                multiday_event = False
        # Delete all punctuation from the string
        res = re.sub(r'[^\w\s]', ' ', og_date)
        # Make the string lowercase
        res = res.lower()
        month = identify_month(res)
        all_day = res.find('all day')
        tba = res.find('tba')
        # Pull all the numbers from string
        temp = re.findall(r'\d+', og_date)
        result = list(map(int, temp)) 
        # First number is the day for all formats
        day = str(result[0])
        # THIS IS HARDCODED CHANGE IF EXPANDING PROJECT
        year = "2023"
        date = year +"-"+ month +"-"+ day
        if usc_event:
               start_time, end_time = format_time_uofsc(result,res) 
        else: 
                start_time = format_time(result,multiday_event,all_day,tba,res)
                end_time = "00:00:00"
        formatted_start_date = date + " " + start_time
        formatted_end_date = date + " " + end_time
        return formatted_start_date, formatted_end_date

# Checks if the hour is in the am or pm
def am_or_pm(res,hour):
        pm_check = False
        am_check = False

        if res.find('pm') != -1 or res.find('p m') != -1:
                pm_check = True
        if res.find('am') != -1 or res.find('a m') != -1:
                am_check = True
  
        if pm_check and am_check:
                return hour
        elif am_check:
                return hour
        elif pm_check:
                if hour == '12':
                        return hour
                else: 
                        temp =  int(hour) + 12
                        return str(temp)
        else:
                return hour

# Data cleaning of event location
def location_clean(ex_str):
        new_str = ex_str
        if ex_str == "See event description for more details.":
                new_str = "Location TBD"
        
        return new_str

# WEBSCRAPING UOFSC EVENTS
if(uofsc_events): 
        driver.get('https://www.sc.edu/calendar/uofsc/')
        driver.switch_to.frame("trumba.spud.0.iframe")
        curr_month = driver.find_element(By.XPATH,"//*[@id='rootDiv']/div[2]/div[1]").text
        
        # Check that the currmonth on the webpage is one of the months we want to track
        while(curr_month in months_to_track):
                eventsNotFound = 0
                j = 2
                # 15 is an arbitrary number for the number of days on a given page
                while(eventsNotFound < 15):
                        # There is only 25 events per page on the calendar 
                        for i in range(2,26):
                                try:
                                        title = driver.find_element(By.XPATH, "//*[@id='rootDiv']/div[2]/div["+str(j)+"]/div["+str(i)+"]/div/table/tbody/tr/td[2]/div[1]/a").text
                                        titles_list.append(title)
                                        try: 
                                                location = driver.find_element(By.XPATH, "//*[@id='rootDiv']/div[2]/div["+str(j)+"]/div["+str(i)+"]/div/table/tbody/tr/td[2]/table/tbody/tr/td[2]/span").text
                                                location = location.strip('\"')
                                                location = location_clean(location)
                                                locations_list.append(location)
                                        except NoSuchElementException:
                                                location = "Location TBD"
                                                locations_list.append(location)
                                        date = driver.find_element(By.XPATH, "//*[@id='rootDiv']/div[2]/div["+str(j)+"]/div["+str(i)+"]/div/table/tbody/tr/td[2]/div[2]/span").text
                                        date = date.strip('\"')
                                        try: 
                                                start_date,end_date = format_date(date,True)
                                                start_dates_list.append(start_date)
                                                end_dates_list.append(end_date)
                                        except:
                                                empty_date = "0000-00-00 00:00:00"
                                                start_dates_list.append(empty_date)
                                                end_dates_list.append(empty_date)
                                        filter_list.append("UofSC Event")
                                        try: 
                                                navigate = driver.find_element(By.XPATH, "//*[@id='rootDiv']/div[2]/div["+str(j)+"]/div["+str(i)+"]/div/table/tbody/tr/td[2]/div[1]/a")
                                                try:
                                                        navigate.click()
                                                except ElementClickInterceptedException:
                                                        driver.execute_script("arguments[0].scrollIntoView();", navigate)
                                                        try: 
                                                                navigate.click()
                                                        except ElementClickInterceptedException:
                                                                url = driver.current_url
                                                                url_list.append(url)
                                                                continue
                                                time.sleep(1)
                                                url = driver.current_url
                                                url_list.append(url)
                                                driver.back()
                                                time.sleep(0.500)
                                                driver.switch_to.frame("trumba.spud.0.iframe")
                                        except NoSuchElementException:
                                                print("An element while looking for url could not be found")
                                except NoSuchElementException:
                                        eventsNotFound = eventsNotFound + 1
                                        j = j + 1
                                        break
                                except StaleElementReferenceException:
                                        continue
                try: 
                        element=WebDriverWait(driver,20).until(EC.visibility_of_element_located((By.XPATH ,"//*[@id='ctl04_ctl06_ctl00_lnk2NextPg']")))
                        driver.execute_script("arguments[0].scrollIntoView();", element)
                        driver.execute_script("arguments[0].click();", element)
                        iframe = WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.CSS_SELECTOR ,"iframe[title*='List Calendar View']")))
                        driver.switch_to.frame(iframe)
                        curr_month = driver.find_element(By.XPATH,"//*[@id='rootDiv']/div[2]/div[1]").text
                except TimeoutException:
                        break

# WEBSCRAPING COLUMBIA EVENTS
if(columbia_events): 
        driver.get('https://columbiasc.gov/calendar/list/')
        curr_month = driver.find_element(By.XPATH,"//*[@id='ajax-content-wrap']/div[1]/div[1]/div/div/div/div/div[2]/h2[1]/time").text
        while(curr_month in months_to_track):
                eventsNotFound = 0
                for i in range(1,12):
                        try:
                                title = driver.find_element(By.XPATH, "//*[@id='ajax-content-wrap']/div[1]/div[1]/div/div/div/div/div[2]/div["+str(i)+"]/div[2]/article/div/header/h3/a").text
                                titles_list.append(title)
                                try: 
                                        location = driver.find_element(By.XPATH, "//*[@id='ajax-content-wrap']/div[1]/div[1]/div/div/div/div/div[2]/div["+str(i)+"]/div[2]/article/div/header/address/span[2]").text
                                        location = location.strip('\"')
                                        locations_list.append(location)
                                except NoSuchElementException:
                                        location = "Location TBD"
                                        locations_list.append(location)
                                try:
                                        date = driver.find_element(By.XPATH, "//*[@id='ajax-content-wrap']/div[1]/div[1]/div/div/div/div/div[2]/div["+str(i)+"]/div[2]/article/div/header/div/time/span").text
                                        date = date.strip('\"')
                                        try: 
                                                start_date,end_date = format_date(date,False)
                                                start_dates_list.append(start_date)
                                                end_dates_list.append(end_date)
                                        except:
                                                start_dates_list.append(date)
                                                end_dates_list.append(date)
                                except NoSuchElementException:
                                        date = driver.find_element(By.XPATH, "//*[@id='ajax-content-wrap']/div[1]/div[1]/div/div/div/div/div[2]/div["+str(i)+"]/div[2]/article/div/header/div/time/span[1]").text
                                        try: 
                                                start_date,end_date = format_date(date,False)
                                                start_dates_list.append(start_date)
                                                end_dates_list.append(end_date)
                                        except:
                                                start_dates_list.append(date)
                                                end_dates_list.append(date)
                                filter_list.append("Columbia Event")
                                try: 
                                        navigate = driver.find_element(By.XPATH, "//*[@id='ajax-content-wrap']/div[1]/div[1]/div/div/div/div/div[2]/div["+str(i)+"]/div[2]/article/div/header/h3/a")
                                        try:
                                                navigate.click()
                                        except ElementClickInterceptedException:
                                                driver.execute_script("arguments[0].scrollIntoView();", navigate)
                                                navigate.click()
                                        time.sleep(1)
                                        url = driver.current_url
                                        url_list.append(url)
                                        driver.back()
                                        time.sleep(1)
                                except NoSuchElementException:
                                                print("An element while looking for url could not be found")
                        except NoSuchElementException:
                                break
                        except StaleElementReferenceException:
                                continue
                try: 
                        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='ajax-content-wrap']/div[1]/div[1]/div/div/div/div/nav/ul/li[3]/a")))
                        navigate = driver.find_element(By.XPATH, "//*[@id='ajax-content-wrap']/div[1]/div[1]/div/div/div/div/nav/ul/li[3]/a").click()
                        time.sleep(1)
                        curr_month = driver.find_element(By.XPATH,"//*[@id='ajax-content-wrap']/div[1]/div[1]/div/div/div/div/div[2]/h2[1]/time").text
                except TimeoutException:
                        break

# WEBSCRAPING ATHLETIC EVENTS
if(athletic_events):
        driver.get('https://gamecocksonline.com/all-sports-schedule/')
        j = 0
        while j < 20:
                for i in range(1,11):
                        try: 
                                sport = driver.find_element(By.XPATH, '//*[@id="event_list"]/div['+str(i)+']/div[2]/a').get_attribute('textContent')
                                opponent = driver.find_element(By.XPATH, '//*[@id="event_list"]/div['+str(i)+']/div[1]/div/div[1]/div[3]/strong').get_attribute('textContent')
                                versus = " UofSC vs. "
                                title = sport + versus + opponent
                                title = " ".join(title.split())
                                titles_list.append(title)
                                date = driver.find_element(By.XPATH, '//*[@id="event_list"]/div['+str(i)+']/div[1]/time').get_attribute('textContent')
                                date = " ".join(date.split())
                                try: 
                                        start_date,end_date = format_date(date,False)
                                        start_dates_list.append(start_date)
                                        end_dates_list.append(end_date)
                                except:
                                        start_dates_list.append(date)
                                        end_dates_list.append(date)
                                location = driver.find_element(By.XPATH, '//*[@id="event_list"]/div['+str(i)+']/div[1]/div/div[2]/strong').get_attribute('textContent')
                                location = location.strip('\"')
                                locations_list.append(location)
                                filter_list.append("Athletic Event")
                                url = driver.current_url
                                url_list.append(url)
                        except NoSuchElementException:
                                break
                try: 
                        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="loadMore"]')))
                        try: 
                                navigate = driver.find_element(By.XPATH, '//*[@id="loadMore"]').click()
                        except ElementClickInterceptedException:
                                continue
                        time.sleep(1)
                        j = j + 1
                except TimeoutException:
                        break


# Create dataframe
df['Location'] = pd.Series(locations_list)
df['Title'] = pd.Series(titles_list)
df['Start_Date'] = pd.Series(start_dates_list)
df['End_Date'] = pd.Series(end_dates_list)
df['Filter'] = filter_list
df['URL'] = pd.Series(url_list)
# Save CSV
df.to_csv(r'~/events.csv')