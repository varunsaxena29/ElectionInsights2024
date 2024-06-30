from asyncio import wait
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timedelta
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.chrome.service import Service as ChromeService

file_path = "insights.txt"
chrome_options = webdriver.ChromeOptions()
#chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--verbose')
chrome_options.add_argument("--safebrowsing-disable-download-protection")
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-software-rasterizer')
driver = webdriver.Chrome(options=chrome_options, service=ChromeService(ChromeDriverManager().install()))
driver.maximize_window()

driver.get('https://results.eci.gov.in/')
original_window = driver.current_window_handle
wait = WebDriverWait(driver, 10)
def extract_party_wise_winners():
    top_winners = []
    for i in range(1, 4):
        try:
            constituency = driver.find_element(by=By.XPATH,value=f"/html/body/main/div/div[3]/div/table/tbody/tr[{i}]/td[2]/a").text
            winning_candidate = driver.find_element(by=By.XPATH,value=f"/html/body/main/div/div[3]/div/table/tbody/tr[{i}]/td[3]").text
            total_votes = driver.find_element(by=By.XPATH,value=f"/html/body/main/div/div[3]/div/table/tbody/tr[{i}]/td[4]").text
            margin = driver.find_element(by=By.XPATH,value=f"/html/body/main/div/div[3]/div/table/tbody/tr[{i}]/td[5]").text
            status = driver.find_element(by=By.XPATH,value=f"/html/body/main/div/div[3]/div/table/tbody/tr[{i}]/td[6]").text
            d = {
                "constituency": constituency,
                "winning_candidate": winning_candidate,
                "total_votes": total_votes,
                "margin": margin,
                "status": status
            }
            top_winners.append(d)
        except Exception as e:
            print("extract_party_wise_winners error")
    driver.back()
    return top_winners
def extract_party_wise_results(state_name):
    i = 1
    txt_data = []
    state_wise_party_arr = []
    txt_data.append(f"**Overall Results for {state_name}: **")
    total_assembly_constituencies = driver.find_element(by=By.XPATH,value=f"/html/body/main/div[2]/section/div/div/div[1]/div/div[2]/div/div/table/tfoot/tr/th[4]").text
    txt_data.append(f"- Total Assembly Constituencies: {total_assembly_constituencies}")
    txt_data.append(f"*Party wise Results: *")
    while True:
        try:
            state_wise_party_name = driver.find_element(by=By.XPATH,value=f"/html/body/main/div[2]/section/div/div/div[1]/div/div[2]/div/div/table/tbody/tr[{i}]/td[1]").text
            # element = WebDriverWait(driver, timeout=10).until(EC.presence_of_element_located(state_wise_party_name))
            try:
                driver.execute_script(f"window.scrollBy(0, {50});")
            except Exception as e:
                print("Scroll error")
            state_wise_party_won_number = driver.find_element(by=By.XPATH,value=f"/html/body/main/div[2]/section/div/div/div[1]/div/div[2]/div/div/table/tbody/tr[{i}]/td[2]/a").text 
            state_wise_party_seat_leading = driver.find_element(by=By.XPATH,value=f"/html/body/main/div[2]/section/div/div/div[1]/div/div[2]/div/div/table/tbody/tr[{i}]/td[3]").text
            state_wise_party_total_number = driver.find_element(by=By.XPATH,value=f"/html/body/main/div[2]/section/div/div/div[1]/div/div[2]/div/div/table/tbody/tr[{i}]/td[4]").text
            top_winners = driver.find_element(by=By.XPATH,value=f"/html/body/main/div[2]/section/div/div/div[1]/div/div[2]/div/div/table/tbody/tr[{i}]/td[2]/a").click()
            winners = extract_party_wise_winners()
            data = {
                "state_wise_party_name": state_wise_party_name,
                "state_wise_party_won_number": state_wise_party_won_number,
                "state_wise_party_total_number": state_wise_party_total_number
            }
            txt_data.append(f"-- {state_wise_party_name}")
            txt_data.append(f"  - Seats Won: {state_wise_party_won_number}, Seat leading: {state_wise_party_seat_leading}, Total Seats: {state_wise_party_total_number} ")
            txt_data.append(f"  -- Constituency Breakdown: --")
            for winner in winners:
                txt_data.append(f"   - Constituency : {winner['constituency']}")
                txt_data.append(f"     - Winning Candidate : {winner['winning_candidate']}, Total Votes: {winner['total_votes']}, Margin: {winner['margin']}, Status: {winner['status']}")
                
            state_wise_party_arr.append(data)
            
            i = i+1
        except Exception as e:
            print("extract_party_wise_results error")
            break
    driver.back()
    driver.close()
    
    driver.switch_to.window(original_window) 
    return { "state_name": state_name, "party_wise_results": state_wise_party_arr, "txt_data": txt_data }

def append_data_in_txt(data):
    with open(file_path, "a") as f:
        for d in data:
            f.write(f'{d}\n')
    print(f"Data has been written to {file_path}")
def switch_to_new_window(original_window):

# Loop through until we find a new window handle
    try:
        wait.until(EC.number_of_windows_to_be(2))
        for window_handle in driver.window_handles:
            if window_handle != original_window:
                driver.switch_to.window(window_handle)
                break
    except Exception as e:
        print("window err", e)
    try:
        driver.execute_script(f"window.scrollBy(0, {50});")
    except Exception as e:
        print(e)
    time.sleep(3)

def handle_bye_election():
    txt_data = []
    txt_data.append(f"** Overall Results for Bye Election: **")
    i = 1
    while True:
        try:
            region_winner = driver.find_element(by=By.XPATH,value=f"/html/body/main/div/div[2]/div/div[{i}]/div/a/div/h3").text # Parliamentary Constituencies
                                                                    # /html/body/main/div/div[2]/div/div[1]/div/a/div/h3
            state_name_winner = driver.find_element(by=By.XPATH,value=f"/html/body/main/div/div[2]/div/div[{i}]/div/a/div/h4").text # Parliamentary Constituencies
            winner_name = driver.find_element(by=By.XPATH,value=f"/html/body/main/div/div[2]/div/div[{i}]/div/a/div/h5").text # Parliamentary Constituencies
            winning_party = driver.find_element(by=By.XPATH,value=f"/html/body/main/div/div[2]/div/div[{i}]/div/a/div/h6").text # Parliamentary Constituencies
            txt_data.append(f" - {region_winner}({state_name_winner})")
            txt_data.append(f"  - Winner: {winner_name}({winning_party})")
            i = i + 1
        except Exception as e:
            print("handle_bye_election Error")
            break
    return {"txt_data": txt_data}

def empty_file(file_path):
    with open(file_path, 'w') as file:
        pass
def extract_details():
    insights_data_arr = []
    try:
        insights_data_arr.append("1. Parliamentary Constituencies:")
        parliamentary_constituencies_count = driver.find_element(by=By.XPATH,value="/html/body/main/div[2]/section/div/div/div[1]/div/a/h1").text # Parliamentary Constituencies
        insights_data_arr.append(f"- There are a total of {parliamentary_constituencies_count} parliamentary constituencies.")
        insights_data_arr.append("2. Assembly Constituencies by State:")
        andhra_pradesh_constituencies_count = driver.find_element(by=By.XPATH,value="/html/body/main/div[2]/section/div/div/div[2]/div/a/h1").text # Andhra pradesh
        insights_data_arr.append(f"- Andhra Pradesh: Has {andhra_pradesh_constituencies_count} assembly constituencies.")
        odisha_constituencies_count = driver.find_element(by=By.XPATH,value="/html/body/main/div[2]/section/div/div/div[3]/div/a/h1").text # Odisha
        insights_data_arr.append(f"- Odisha: Has {odisha_constituencies_count} assembly constituencies.")
        bye_elections_constituencies_count = driver.find_element(by=By.XPATH,value="/html/body/main/div[2]/section/div/div/div[4]/div/a/h1").text # Bye elections
        insights_data_arr.append(f"- Bye Elections: {bye_elections_constituencies_count} assembly constituencies are listed under bye elections.")
        arunachal_pradesh_button = driver.find_element(by=By.XPATH,value="/html/body/main/div[2]/section/div/div/div[5]/a").click() # Arunachal Pradesh Button
        driver.implicitly_wait(3)
        time.sleep(3)
        
        # Extract Arunachal pradesh data
        switch_to_new_window(original_window=original_window)
        arunachal_pradesh_details_button = driver.find_element(by=By.XPATH,value="/html/body/main/div[2]/div/div[1]/div/div/div/div/a[2]").click() # Arunachal Pradesh Details Button
        arunachal_pradesh_data = extract_party_wise_results("Arunachal Pradesh")
        insights_data_arr.extend(arunachal_pradesh_data["txt_data"])
        
        # Extract Sikkim data
        sikkim_button = driver.find_element(by=By.XPATH,value="/html/body/main/div[2]/section/div/div/div[5]/a").click() # Sikkim Button
        switch_to_new_window(original_window=original_window)
        driver.implicitly_wait(3)
        sikkim_details_button = driver.find_element(by=By.XPATH,value="/html/body/main/div[2]/div/div[2]/div/div/div/div/a[2]").click() # Sikkim Details Button
        sikkim_data = extract_party_wise_results("Sikkim")
        insights_data_arr.extend(sikkim_data["txt_data"])
        
        # Andhra Pradesh data
        andhra_pradesh_button = driver.find_element(by=By.XPATH,value="/html/body/main/div[2]/section/div/div/div[2]/div/a").click() # Arunachal Pradesh Details Button
        switch_to_new_window(original_window=original_window)
        driver.implicitly_wait(3)
        andhra_pradesh_details_button = driver.find_element(by=By.XPATH,value="/html/body/main/div[2]/div/div[1]/div/div/div/div/a[2]").click() # Arunachal Pradesh Details Button
        andhra_pradesh_data = extract_party_wise_results("Andhra Pradesh")
        insights_data_arr.extend(andhra_pradesh_data["txt_data"])
        
        # Extract Odisha data
        odisha_button = driver.find_element(by=By.XPATH,value="/html/body/main/div[2]/section/div/div/div[3]/div/a").click() # Arunachal Pradesh Button
        switch_to_new_window(original_window=original_window)
        driver.implicitly_wait(3)
        odisha_details_button = driver.find_element(by=By.XPATH,value="/html/body/main/div[2]/div/div[2]/div/div/div/div/a[2]").click() # Arunachal Pradesh Details Button
        odisha_data = extract_party_wise_results("Odisha")
        insights_data_arr.extend(odisha_data["txt_data"])
        
        # Extract Odisha data
        bye_election_button = driver.find_element(by=By.XPATH,value="/html/body/main/div[2]/section/div/div/div[4]/div/a").click() # Arunachal Pradesh Button
        switch_to_new_window(original_window=original_window)
        bye_election_data = handle_bye_election()
        insights_data_arr.extend(bye_election_data["txt_data"])
    except Exception as e:
        print("outerr error")
    finally:
        append_data_in_txt(insights_data_arr)

empty_file(file_path)
extract_details()