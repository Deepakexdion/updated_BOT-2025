def main_code(Created_date):  
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import Select
    from selenium.common.exceptions import NoAlertPresentException, TimeoutException
    import time
    from selenium import webdriver
    from selenium.webdriver.common.alert import Alert
    from selenium.common.exceptions import NoAlertPresentException
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service as ChromeService
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import NoSuchElementException, TimeoutException
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait, Select
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from collections import defaultdict
    from selenium.webdriver.common.alert import Alert
    from selenium import webdriver
    import time
    import re
    import logging
    import psutil
    import requests
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.image import MIMEImage
    import smtplib
    import io
    from datetime import datetime, timedelta
    import pytz
    import requests
    import time
    import json

    # Path to the JSON configuration file
    CONFIG_FILE = r"C:\Users\Bot_1\Documents\BOT_Facilities.JSON"

    def load_facilities():
        try:
            with open(CONFIG_FILE, "r") as file:
                config = json.load(file)
                return config.get("faci", [])
        except FileNotFoundError:
            print(f"Configuration file '{CONFIG_FILE}' not found.")
            return []
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return []
    # Example usage
    facilities = load_facilities()
    print("Facilities:", facilities)

        
    # Function to convert UTC to IST
    def convert_utc_to_ist(utc_str):
        utc_time = datetime.strptime(utc_str, "%Y-%m-%dT%H:%M:%S")
        ist_time = utc_time + timedelta(hours=5, minutes=30)
        return ist_time.strftime("%Y-%m-%d")

    # Function to get current system date in IST
    def system_cst_to_ist():
        cst_time = datetime.now()
        ist_time = cst_time + timedelta(hours=11, minutes=30)
        return ist_time.strftime("%Y-%m-%d")

    def send_screenshot_email(subject, visnum, encounter, driver):
        # Email configuration
        sender_email = 'internalprojects@exdion.com'
        receiver_email = 'Deepak_tr@exdion.com'
        cc_email = 'Deepak_tr@exdion.com'
        password = 'yvJ94dKvV4"480'

        # Email body with placeholders for variables and image
        body = f"""
        Hi All,<br><br>

        Please review the attached screenshot. The visit ID has failed; kindly complete the visit manually..<br><br>
    
        <b>Visit Number:</b> {visnum}<br>
        <b>Encounter:</b> {encounter}<br><br>
        <img src="cid:uhc_screenshot" alt="Screenshot" width="500" style="border: none; display: block;">
        <br><br><br>
        Thanks,<br>
        Input_Bot
        <br><br>
        """
        # Create a multipart message and set headers
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Cc'] = cc_email
        msg['Subject'] = subject

        # Attach body to the message
        msg.attach(MIMEText(body, 'html'))

        # Capture screenshot from the existing Selenium driver
        screenshot_bytes = io.BytesIO(driver.get_screenshot_as_png())
        screenshot_bytes.seek(0)  # Move to the beginning of the BytesIO buffer

        # Attach the screenshot as an inline image
        img = MIMEImage(screenshot_bytes.read())
        img.add_header('Content-ID', '<uhc_screenshot>')
        img.add_header('Content-Disposition', 'inline', filename="screenshot.png")
        msg.attach(img)

        # Send the email
        try:
            with smtplib.SMTP('smtp.office365.com', 587) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(sender_email, password)
                server.sendmail(sender_email, [receiver_email] + cc_email.split(','), msg.as_string())
                print("Email sent successfully!")
        except Exception as e:
            print(f"An error occurred: {e}")

    payload = {'username': 'api_user@exdionace.ai', 'password': r'&D/]\R[n+A)}^#%'}
    headers = {"accept": "*/*", "Content-Type": "application/json"}

    try:
        # Login and get the access token
        response = requests.post("https://www.exdion-h.studio/api/Login/SignIn", headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        access_token = data['accessToken']
    except requests.exceptions.RequestException as e:
        print(f"Login request failed: {e}")

    def get_jobs(username, password):
        # Define the payload and headers
        payload = {'username': username, 'password': password}
        headers = {"accept": "*/*", "Content-Type": "application/json"}
        
        try:
            # Login and get the access token
            response = requests.post("https://www.exdion-h.studio/api/Login/SignIn", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            access_token = data['accessToken']
        except requests.exceptions.RequestException as e:
            print(f"Login request failed: {e}")
            return None

        try:
            # Get the jobs
            job_response = requests.get("https://exdion-h.studio/api/Query/GetJobs?status=job%20ready", 
                                        headers={"Authorization": f"Bearer {access_token}"})
            job_response.raise_for_status()
            ready_jobs = job_response.json()
            return ready_jobs
        except requests.exceptions.RequestException as e:
            print(f"Get jobs request failed: {e}")
            return None
        
    def update_job_status(client_id, job_id, access_token):
        try:
            response = requests.post(
                f"https://exdion-h.studio/api/Jobs/UpdateJobEhrPostStatus?clientID={client_id}&jobID={job_id}&IsSuccessful=false",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            response.raise_for_status()  # Raise an error for bad status codes
            print("API request successful.")
        except requests.RequestException as req_e:
            print(f"Failed to send API request: {req_e}")
            
    def process_contracts_and_log(ready_jobs, endate):
        # Initialize the list to store log messages
        log_messages = []

        # Open the log file for appending
        with open("invalid_contracts.log", "a") as log_file:
            for rdp in ready_jobs:  # Iterate over each job record
                # Extract relevant data from each record
                visnum = rdp.get("visitNumber", "")
                jobi = rdp.get("jobID", "")
                clientd = rdp.get("clientID", "")
                client_name = rdp.get("clientName", "")
                patient = rdp.get("patientName", "")
                Create_datelog = rdp.get("createdOn", "")
                enco = rdp.get("encounterDate", "")
                faci = rdp.get("appointmentFacility", "")
                visty = rdp.get("visitType", "")
                primary_ins = rdp.get('primaryInsurance', "")
                provider_name = rdp.get('provider', "")
                accnumber = rdp.get('accountNumber', "")
                yeprec = rdp.get("predictedCategory", "")
                Place_of_service = rdp.get("financialClass", "")
                POS_1 = rdp.get("pos", "")
                con_type = rdp.get("contractType", "")
                region = rdp.get("regionName", "")
                # Condition for filtering records based on date, facility, and contract type
                if Create_datelog[:10] == Created_date and faci in facilities:
                #    ['FCLONDONKY','CANTONMS', 'WESTPOINT', 'CROWLEY', 'DENHAMSPLA','FCMTSTERKY', 'FCPIKEVIKY', 'FCSOMERSKY', 'FCWINCHEKY', 'FRANKLIN', 'LAWRENCEKY', 'LEBANON', 'LEITCHFIEL', 'MADISONVIL', 'MAYFIELD', 'MAYSVILLE',
                #     'VMCLINICKY', 'WASHINGTON', 'PARISKY','FCMIDDLEKY']:
                    if con_type in ["NGC", "GC"]:
                        log_message = f"Valid contract type: {Created_date}, {faci}, {visnum}, {con_type}\n"
                    else:
                        log_message = f"Invalid contract type: {Created_date}, {faci}, {visnum}, {con_type}\n"
                    
                    # Append the tuple of endate and log message to the list
                    log_messages.append((Created_date, log_message))

            # Sort the log messages by endate
            log_messages.sort()

            # Write the sorted log messages to the file
            for _, message in log_messages:
                log_file.write(message)
                # print(message)
    def get_jobs(username, password):
        # Define the payload and headers
        payload = {'username': username, 'password': password}
        headers = {"accept": "*/*", "Content-Type": "application/json"}
        
        try:
            # Login and get the access token
            response = requests.post("https://www.exdion-h.studio/api/Login/SignIn", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            access_token = data['accessToken']
        except requests.exceptions.RequestException as e:
            print(f"Login request failed: {e}")
            return None
        try:
            # Get the jobs
            job_response = requests.get("https://exdion-h.studio/api/Query/GetJobs?status=job%20ready", 
                                        headers={"Authorization": f"Bearer {access_token}"})
            job_response.raise_for_status()
            ready_jobs = job_response.json()
            return ready_jobs
        except requests.exceptions.RequestException as e:
            print(f"Get jobs request failed: {e}")
            return None        
    def scroll_into_view(driver, element):
        from selenium.webdriver.common.by import By
        driver.execute_script("arguments[0].scrollIntoView(true);", element)

    def select_dropdown_value(driver, dropdown_id, value_to_select):
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import Select
        from selenium.common.exceptions import NoSuchElementException
        # Locate the dropdown element
        dropdown = Select(driver.find_element(By.ID, dropdown_id))

        # Get all options in the dropdown
        options = dropdown.options

        # Extract the text of each option
        dropdown_values = [option.text for option in options]

        # Print the complete list of values
        print(dropdown_values)

        try:
            # Select the option by visible text
            dropdown.select_by_visible_text(value_to_select)
            print(f'Successfully selected: {value_to_select}')
        except NoSuchElementException:
            print(f'Option "{value_to_select}" not found in the dropdown.')

    def insurance_not_found(driver, pri_ins,select_dropdown_value):
        import time
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import Select
        from selenium.common.exceptions import NoAlertPresentException, NoSuchElementException, TimeoutException
        from datetime import datetime  
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC  
        
        # Fetch all the table rows
        table_rows = driver.find_elements(By.XPATH, '//*[@id="ctl00_contentMain_ctlPatSummary_dgPatBilling"]/tbody/tr')
        pri_ins_found = False  # Flag to track if pri_ins is found in any row

        # Check all rows for the primary insurance
        for r in range(2, len(table_rows) + 1):
            try:
                # Locate the third cell in each row
                row_text_element = driver.find_element(By.XPATH, f'//*[@id="ctl00_contentMain_ctlPatSummary_dgPatBilling"]/tbody/tr[{r}]/td[3]')
                text_in_row = row_text_element.text.strip()
                print(f"Row {r}: {text_in_row}")

                # If pri_ins is found in any row, set the flag to True (exact match)
                if text_in_row == pri_ins:
                    print(f"Primary insurance '{text_in_row}' found in row {r}.")
                    pri_ins_found = True

            except Exception as e:
                print(f"Error occurred at row {r}: {e}")

        # After checking all rows, if pri_ins is found, break and exit
        if pri_ins_found:
            print("Primary insurance found in the table, exiting the process.")
            return

        # Continue with the rest of the process if pri_ins was not found
        print("Primary insurance not found in any row, continuing with the process.")

        # Example processing code if pri_ins was not found
        for r in range(2, len(table_rows) + 1):
            try:
                # Locate the third cell in each row
                row_text_element = driver.find_element(By.XPATH, f'//*[@id="ctl00_contentMain_ctlPatSummary_dgPatBilling"]/tbody/tr[{r}]/td[3]')
                text_in_row = row_text_element.text.strip()
                print(f"Processing Row {r}: {text_in_row}")

                # Skip processing if pri_ins is found (redundant check)
                if text_in_row == pri_ins:
                    print(f"Primary insurance '{text_in_row}' found in row {r}, skipping.")
                    continue

                # Scroll and select 'Insurance' from dropdown
                driver.find_element(By.XPATH, '//*[@id="ctl00_contentMain_ctlPatSummary_dgPatBilling_ctl02_radioList"]').click()
                New_payer = driver.find_element(By.ID, "ddlPayerType")
                driver.execute_script("arguments[0].scrollIntoView(true);", New_payer)
                dropdown = Select(New_payer)
                dropdown.select_by_visible_text('Insurance')

                # Clear and enter insurance name
                ins_name = driver.find_element(By.ID, "txtSearchName")
                ins_name.clear()
                ins_name.send_keys(pri_ins)
                time.sleep(1)
                search = driver.find_element(By.ID, "btnSearch")
                search.click()


                Ser=driver.find_element(By.ID,"btnSearch")
                Ser.click()
                time.sleep(2)

                primary_ins1 = pri_ins
                select_dropdown_value(driver, "ddlPayerList", primary_ins1)

                # Get and re-enter member ID
                member_ID1 = driver.find_element(By.ID, "txtMemberID")
                member_id = member_ID1.get_attribute("value")
                print(f"Member ID: {member_id}")

                # Get effective date
                effectivedate1 = driver.find_element(By.ID, "txtEffectDate")
                effectivedate = effectivedate1.get_attribute("value")
                print(f"Effective Date: {effectivedate}")

                time.sleep(1)
                # Click Add Payer button
                Add = driver.find_element(By.ID, "btnAddPayer")
                Add.click()
                time.sleep(1)

                # Handle alert if it appears
                try:
                    WebDriverWait(driver, 3).until(EC.alert_is_present())
                    alert = driver.switch_to.alert
                    alert.accept()
                except (NoAlertPresentException, TimeoutException):
                    pass
                # Re-enter the member ID
                mem = driver.find_element(By.ID, "txtMemberID")
                mem.clear()
                mem.send_keys(member_id)
                print(f"Copied Member ID: {member_id}")

                # Scroll and enter the effective date
                driver.execute_script("arguments[0].scrollIntoView(true);", mem)
                effective = driver.find_element(By.ID, "txtEffectDate")
                effective.clear()
                effective.send_keys(effectivedate)

                # Save and Exit
                save_and_Exit = driver.find_element(By.ID, "btnDoneCopy")
                driver.execute_script("arguments[0].scrollIntoView(true);", save_and_Exit)
                time.sleep(3)
                save_and_Exit.click() 
                try:
                    from selenium.webdriver.common.action_chains import ActionChains
                    from selenium.common.exceptions import NoSuchElementException
                    # Create an ActionChains object
                    action = ActionChains(driver)
                    for i in range(6, 16):
                        try:
                            xpath = f"//*[@id='pageBody']/div[{i}]/div[3]/div/button[2]/span"
                            element = driver.find_element(By.XPATH, xpath) 
                            # Perform double click
                            action.double_click(element).perform()
                            save_and_Exit.click() 
                            print(f"Element found and double-clicked at index {i}")
                            break  # Exit loop once the element is clicked
                        except NoSuchElementException:
                            print(f"Element not found at index {i}, continuing...")
                        except Exception as e:
                            print(f"An error occurred at index {i}: {e}") 
                except:
                    pass 
                print(f"Process completed successfully for row {r}")
                # Break the loop after saving and exiting
                break
            except Exception as e:
                print(f"Error occurred at row {r}: {e}")
    def scroll_into_view(driver, element):
        from selenium.webdriver.common.by import By
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
    def Sequence_process_table(driver, pri_ins,scroll_into_view):
        import time
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import Select
        from selenium.common.exceptions import NoAlertPresentException, NoSuchElementException, TimeoutException
        from datetime import datetime  
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        try:
            table_rows = driver.find_elements(By.XPATH, '//*[@id="ctl00_contentMain_ctlPatSummary_dgPatBilling"]/tbody/tr')
            r = 2
            try:
                # Get the text from the 3rd column of the second row
                row_text_element = driver.find_element(By.XPATH, f'//*[@id="ctl00_contentMain_ctlPatSummary_dgPatBilling"]/tbody/tr[{r}]/td[3]')
                text_in_row = row_text_element.text.strip()

                # Check if the text from the 3rd column exactly matches pri_ins
                if text_in_row == pri_ins:
                    print(f"Correct sequence for Row {r}, pattern '{text_in_row}' found.")
                    return True  # Exact match found, stop further execution

                else:
                    for r in range(2, len(table_rows) + 1):
                        try:
                            row_text_element = driver.find_element(By.XPATH, f'//*[@id="ctl00_contentMain_ctlPatSummary_dgPatBilling"]/tbody/tr[{r}]/td[3]')
                            text_in_row = row_text_element.text.strip()    
                            # Check if the text in the row exactly matches pri_ins
                            if text_in_row == pri_ins:
                                print(f"Found matching insurance pattern '{text_in_row}' in row {r}.")
                                time.sleep(2)
                                
                                # Click the radio button for the matching row
                                radio_button = driver.find_element(By.XPATH, f'//*[@id="ctl00_contentMain_ctlPatSummary_dgPatBilling_ctl0{r}_radioList"]')
                                radio_button.click()
                                print(f"Clicked radio button for Row {r}, pattern '{text_in_row}' found.")  
                                
                                # Locate all rows starting from index 2 in the table
                                table_second = driver.find_elements(By.XPATH, '//*[@id="dgPatBilling"]/tbody/tr')

                                # Initialize flag to check if a match has already been made and to track the priority for non-matched rows
                                match_found = False
                                priority_counter = 2

                                # Iterate over the rows starting from the second one
                                for r in range(2, len(table_second) + 1):
                                    # Get the text from the 5th column of the current row
                                    row_text_element_1 = driver.find_element(By.XPATH, f'//*[@id="dgPatBilling"]/tbody/tr[{r}]/td[5]')
                                    text_in_row_1 = row_text_element_1.text.strip()
                                    print(text_in_row_1)

                                    # Check if the text is in the pri_ins list (matched insurance)
                                    if text_in_row_1 == pri_ins and not match_found:
                                        print(f"Insurance match found for row {r}")
                                        match_found = True  # Ensure that only the first match gets priority 1

                                        # Set priority for the current row as "1"
                                        prio_1 = driver.find_element(By.XPATH, f'//*[@id="dgPatBilling"]/tbody/tr[{r}]/td[3]/input')
                                        prio_1.clear()
                                        prio_1.send_keys("1")  # Set priority to 1

                                    # For non-matched rows or if the first match has already been processed
                                    else:
                                        print(f"Setting priority {priority_counter} for row {r}")

                                        # Set priority for non-matched rows or remaining rows
                                        prio_other = driver.find_element(By.XPATH, f'//*[@id="dgPatBilling"]/tbody/tr[{r}]/td[3]/input')
                                        prio_other.clear()
                                        prio_other.send_keys(str(priority_counter))  # Set priority to 2, 3, and so on

                                        # Increment the priority counter for the remaining rows
                                        priority_counter += 1

                                time.sleep(2)
                                save_and_exit_button = driver.find_element(By.ID,"btnDone")
                                scroll_into_view(driver, save_and_exit_button)
                                save_and_exit_button.click() 
                                time.sleep(2)
                                try:
                                    from selenium.webdriver.common.action_chains import ActionChains
                                    from selenium.common.exceptions import NoSuchElementException
                                    # Create an ActionChains object
                                    action = ActionChains(driver)
                                    for i in range(6, 16):
                                        try:
                                            xpath = f"//*[@id='pageBody']/div[{i}]/div[3]/div/button[2]/span"
                                            element = driver.find_element(By.XPATH, xpath)
                                            
                                            # Perform double click
                                            action.double_click(element).perform()
                                            save_and_exit_button.click() 
                                            print(f"Element found and double-clicked at index {i}")
                                            break  # Exit loop once the element is clicked
                                        except NoSuchElementException:
                                            print(f"Element not found at index {i}, continuing...")
                                        except Exception as e:
                                            print(f"An error occurred at index {i}: {e}") 
                                except:
                                    pass 
                                return True  # Success after updating the priorities
                        except NoSuchElementException as e:
                            print(f"Error locating element in row {r}: {e}")
                            continue  # If the row has an issue, move to the next one
            except NoSuchElementException as e:
                print(f"Error locating element in row {r}: {e}")
                return False  # No element found or no match, return False
        except NoSuchElementException as e:
            print(f"Error locating the table rows: {e}")
    def previous_visitor1(driver, faci, ddate):  
        from selenium.webdriver.common.by import By
        from selenium.common.exceptions import NoSuchElementException
        tablereading = driver.find_elements(By.XPATH, '//*[@id="dgPrevVisits"]/tbody/tr')
        for r in range(1, len(tablereading) + 1):
            tablereadingrow1 = driver.find_element(By.XPATH, f"//*[@id='dgPrevVisits']/tbody/tr[{r}]/td[1]").text
            tablereadingrow2 = driver.find_element(By.XPATH, f"//*[@id='dgPrevVisits']/tbody/tr[{r}]/td[2]").text 
            if tablereadingrow2 == faci and tablereadingrow1 == ddate:
                print("Found matches")
                # Scroll to the elements
                tablereadingrow1_element = driver.find_element(By.XPATH, f"//*[@id='dgPrevVisits']/tbody/tr[{r}]/td[1]")
                tablereadingrow2_element = driver.find_element(By.XPATH, f"//*[@id='dgPrevVisits']/tbody/tr[{r}]/td[2]")
                driver.execute_script("arguments[0].scrollIntoView();", tablereadingrow1_element)
                driver.execute_script("arguments[0].scrollIntoView();", tablereadingrow2_element)
                try:
                    for i in range(4):
                        try:
                            driver.find_element(By.XPATH, f"//table[@id='dgPrevVisits']/tbody/tr[{r}]/td[3]/a[{i+1}]").click()
                            break  
                        except:
                            continue 
                except NoSuchElementException:
                    print("All attempts failed")
                break 
    def previous_visitor1(driver, faci, ddate):  
        from selenium.webdriver.common.by import By
        from selenium.common.exceptions import NoSuchElementException
        tablereading = driver.find_elements(By.XPATH, '//*[@id="dgPrevVisits"]/tbody/tr')
        for r in range(1, len(tablereading) + 1):
            tablereadingrow1 = driver.find_element(By.XPATH, f"//*[@id='dgPrevVisits']/tbody/tr[{r}]/td[1]").text
            tablereadingrow2 = driver.find_element(By.XPATH, f"//*[@id='dgPrevVisits']/tbody/tr[{r}]/td[2]").text 
            if tablereadingrow2 == faci and tablereadingrow1 == ddate:
                print("Found matches")
                # Scroll to the elements
                tablereadingrow1_element = driver.find_element(By.XPATH, f"//*[@id='dgPrevVisits']/tbody/tr[{r}]/td[1]")
                tablereadingrow2_element = driver.find_element(By.XPATH, f"//*[@id='dgPrevVisits']/tbody/tr[{r}]/td[2]")
                driver.execute_script("arguments[0].scrollIntoView();", tablereadingrow1_element)
                driver.execute_script("arguments[0].scrollIntoView();", tablereadingrow2_element)
                try:
                    for i in range(4):
                        try:
                            driver.find_element(By.XPATH, f"//table[@id='dgPrevVisits']/tbody/tr[{r}]/td[3]/a[{i+1}]").click()
                            break  
                        except:
                            continue 
                except NoSuchElementException:
                    print("All attempts failed")
                break 

    def process_data(driver, Created_date):
        import requests
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.support.ui import WebDriverWait, Select
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import NoSuchElementException, TimeoutException
        from datetime import datetime
        import time

        # Define the payload and headers
        payload = {'username': 'api_user@exdionace.ai', 'password': r'&D/]\R[n+A)}^#%'}
        headers = {"accept": "*/*", "Content-Type": "application/json"}

        try:
            # Login and get the access token
            response = requests.post("https://www.exdion-h.studio/api/Login/SignIn", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            access_token = data['accessToken']
        except requests.exceptions.RequestException as e:
            print(f"Login request failed: {e}")
            return

        try:
            # Get the jobs
            r4 = requests.get("https://exdion-h.studio/api/Query/GetJobs?status=job%20ready", headers={"Authorization": f"Bearer {access_token}"})
            r4.raise_for_status()
            ready = r4.json()
        except requests.exceptions.RequestException as e:
            print(f"Get jobs request failed: {e}")
            return

        for rdp in ready:
            try:
                visnum = rdp["visitNumber"]
                jobi_DC = rdp["jobID"]
                clientd_DC = rdp["clientID"]
                client_name = rdp["clientName"]
                patient = rdp["patientName"]
                created_DENHAMSPLA1 = convert_utc_to_ist(rdp["createdOn"][:19])
                created_DENHAMSPLA=created_DENHAMSPLA1[:10]
                enco = rdp["encounterDate"]
                endate_DENHAMSPLA = enco[:10]
                faci = rdp["appointmentFacility"]
                visty = rdp["visitType"]
                primary_ins = rdp['primaryInsurance']
                provider_name = rdp['provider']
                accnumber = rdp['accountNumber']
                yeprec = rdp["predictedCategory"]
                Place_of_service = rdp["financialClass"]
                POS_1 = rdp["pos"]
                con_type = rdp["contractType"]
                region = rdp["regionName"]
                stp_1 = rdp["stp"]
                # Check if the condition is met; if not, skip to the next job
                # if (created_DENHAMSPLA == Created_date 
                if (created_DENHAMSPLA in facilities 
                    and con_type in ["NGC", "GC", "RHC-MCO"] 
                    and primary_ins == "ACCESS HEALTH" 
                    and stp_1 == "STP"):  
                # The rest of your Selenium code goes here...
                    try:
                        driver.find_element(By.ID, "tdMenuBarItemPatient").click()
                        driver.find_element(By.ID, "menu_Patient_PatSummary").click()
                    except NoSuchElementException as e:
                        print(f"Error while navigating to patient summary: {e}")
                        raise e
                    
                    # Select practice
                    try:
                        target_value = faci
                        key1 = Region(target_value)
                        dropdown_element = WebDriverWait(driver, 3).until(
                            EC.presence_of_element_located((By.ID, 'ddlPractice'))
                        )
                        dropdown = Select(dropdown_element)
                        dropdown.select_by_value(key1)
                    except Exception as e:
                        print(f"Failed to update Region: {e}")
                        raise e

                    # Convert date format
                    date = datetime.strptime(endate_DENHAMSPLA,"%Y-%m-%d")    
                    ddate = datetime.strftime(date, "%m/%d/%Y")

                    # Navigate to patient summary
                    try:
                        menu_item = WebDriverWait(driver, 3).until(
                            EC.presence_of_element_located((By.ID, "tdMenuBarItemPatient"))
                        )
                        menu_item.click()

                        patient_summary = WebDriverWait(driver, 3).until(
                            EC.presence_of_element_located((By.ID, "menu_Patient_PatSummary"))
                        )
                        patient_summary.click()
                    except (NoSuchElementException, TimeoutException) as e:
                        print(f"Error while navigating to patient summary: {e}")
                        raise e

                    # Search by patient account number
                    try:
                        pataccnum = driver.find_element(By.ID, "textAdvPatNum")
                        pataccnum.clear()
                        pataccnum.send_keys(str(accnumber))
                        pataccnum.send_keys(Keys.ENTER)
                        Search = driver.find_element(By.ID, "BtnSearch")
                        Search.click()
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                        time.sleep(2)
                        driver.execute_script("window.scrollTo(300, 300)")
                        driver.find_element(By.ID, "lbtnPatNum").click()
                        time.sleep(2)
                    except NoSuchElementException as e:
                        update_job_status(clientd, jobi, access_token)
                        print("Error while searching patient account number:", e) 
                        raise e  
                    time.sleep(2)
                    try:
                        previous_visitor1(driver, faci, ddate)
                    except Exception as e:
                        print(f"Failed to match visitor: {e}")
                        raise e

                    # Charge entry
                    try:
                        driver.execute_script("window.scrollTo(300, 300)")
                        driver.find_element(By.ID, "btnCrgEnter").click()
                        print("Charge entry clicked")
                    except NoSuchElementException as e:
                        try:
                            driver.find_element(By.ID, "btnGoCrgEntry").click()
                            print("Charge entry (Go) clicked")
                        except NoSuchElementException as e:
                            print(f"Charge entry button not found: {e}")
                            raise e

                    driver.execute_script("window.scrollTo(300, 300)")
                    time.sleep(2)
                            
                    # Continue button
                    try:
                        driver.execute_script("window.scrollTo(0, 500)")
                        wait = WebDriverWait(driver, 4)  # Adjust timeout as needed
                        continue_button = wait.until(EC.element_to_be_clickable((By.NAME, "btnContAdd")))   
                        continue_button.click()
                    except:
                        pass
                        print("Continue button not found or not clickable:")   
                    try:
                        print("Updating withhold status...")
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")   
                        wait = WebDriverWait(driver, 5)  # Wait for up to 3 seconds
                        reasons = wait.until(EC.visibility_of_element_located((By.ID, "ddlWithholdRsn")))   
                        reasons.send_keys("Commercial Insurance Review")
                        print("Withhold status updated successfully")
                    except TimeoutException:
                        print("Timed out waiting for withhold reason dropdown to become visible")
                        raise e
                    except Exception as e:
                        print(f"Failed to update withhold status: {str(e)}")
                        raise e
                    
                    try:
                        driver.execute_script("window.scrollTo(0, 3000)")
                        save = driver.find_element(By.XPATH, '//*[@id="btnUpdateFooter"]')
                        time.sleep(2)
                        save.click()
                    except NoSuchElementException as e:
                        print(f"Error in save and exit: {e}")
                        raise e
                    
                    try:
                        print(f"Updating EHR UPDATING status successfully for Contains Access Health")
                        r7 = requests.post(
                            f"https://exdion-h.studio/api/Jobs/UpdateJobEhrPostStatus?clientID={clientd_DC}&jobID={jobi_DC}&IsSuccessful=true",
                            headers={"Authorization": f"Bearer {access_token}"}
                        )
                        r7.raise_for_status()
                        print("EHR UPDATING status updated successfully")
                        time.sleep(2)
                    except requests.exceptions.RequestException as e:
                        print(f"Failed to update EHR status: {e}")
                        raise e

            except Exception as e:
                # update_job_status(clientd_DC, jobi_DC, access_token)
                print(f"Error occurred: {e}. Moving to next iteration.")
                continue


    def kill_chromedriver():
        for process in psutil.process_iter():
            try:
                # Check if process name contains 'chromedriver'
                if 'chromedriver' in process.name().lower():
                    process.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

    def handle_pos_condition(driver,contract_type,MOD1,MOD2):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import Select
        if contract_type == "RHC-MCO":
            print("RHC-MCO")
            dropdown = Select(driver.find_element(By.ID, "txtCrgDtlMod1_0"))
            selected_option = dropdown.first_selected_option
            print(selected_option.get_attribute("value"))
            if selected_option.get_attribute("value") == "CG":
                print("FOUND CG MODIFIER")
                dropdown.select_by_index(0)
                try:
                    mod1 = driver.find_element(By.ID, 'txtCrgDtlMod1_0')
                    if mod1 is not None and MOD1 != "nan":
                        mod1.send_keys(MOD1)
                except:
                    pass
                try:
                    mod2 = driver.find_element(By.ID, 'txtCrgDtlMod2_0')
                    if mod2 is not None and MOD2 != "nan":
                        mod2.send_keys(MOD2)
                except:
                    pass
                print("Saving the file")
                driver.execute_script("window.scrollTo(0, 3000)")
                save_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="btnUpdateFooter"]'))
                )
                save_button.click()
                try:
                    WebDriverWait(driver,3).until(EC.alert_is_present())
                    alert = driver.switch_to.alert
                    alert.accept()
                except:
                    print("No alert found after saving")

    def navigate_to_patient_summary(driver):
        try:
            patient_menu = WebDriverWait(driver,5).until(
                EC.presence_of_element_located((By.ID, "tdMenuBarItemPatient"))
            )
            patient_menu.click()
            
            patient_summary = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "menu_Patient_PatSummary"))
            )
            patient_summary.click()
        except (TimeoutException, NoSuchElementException) as e:
            print("Error while navigating to patient summary:", e)



    def update_job_status(client_id, job_id, access_token):
        try:
            response = requests.post(
                f"https://exdion-h.studio/api/Jobs/UpdateJobEhrPostStatus?clientID={client_id}&jobID={job_id}&IsSuccessful=false",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            response.raise_for_status()  # Raise an error for bad status codes
            print("API request successful.")
        except requests.RequestException as req_e:
            print(f"Failed to send API request: {req_e}")

    logger = logging.getLogger(__name__)
    fileHandler = logging.FileHandler(r"C:\Users\Bot_1\Documents\bot_logs.log")
    formatter = logging.Formatter("%(asctime)s :%(levelname)s :%(name)s :%(message)s")
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    # setting the logger level
    logger.setLevel(logging.DEBUG)
    logger.debug("Debug log")

    def recalculate_length(driver):
        # Assuming this function returns the number of rows in the table
        clmtable = driver.find_elements(By.XPATH, "//*[@id='tblCrgItems']/tbody/tr")
        return len(clmtable)
    def find_delete():
        delete_icon = driver.find_element(By.CLASS_NAME, "mdi-delete")
        driver.execute_script("arguments[0].scrollIntoView(true);", delete_icon)

    def click_ok_button_if_present(driver):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.common.exceptions import NoSuchElementException
        import time
        try:
            ok_button = driver.find_element(By.CSS_SELECTOR, ".CGAlertOK.ui-button.ui-widget.ui-state-default.ui-corner-all.ui-button-text-only")
            actions = ActionChains(driver)
            actions.move_to_element(ok_button).click().perform()
            return True
        except NoSuchElementException:
            return False
        except Exception as e:
            return False

    def format_number(number):
        if number == "none" or number is None:
            return
        # Convert the number to string
        number_str = str(number)
        # Check if the number is already in the correct format (10 or 11 digits with hyphens)
        if re.match(r'^\d{5}-\d{3}-\d{2,3}$', number_str):
            return number_str
        
        # Remove any existing non-numeric characters (e.g., extra dashes)
        cleaned_number = re.sub(r'[^0-9]', '', number_str)
        
        # Ensure the number is either exactly 10 or 11 digits long
        if len(cleaned_number) not in {10, 11}:
            return number_str  # Return the original number if it doesn't meet the criteria
        
        # Extract parts based on the required format
        if len(cleaned_number) == 10:
            part1 = cleaned_number[:5]
            part2 = cleaned_number[5:8]
            part3 = cleaned_number[8:]
        else:  # len(cleaned_number) == 11
            part1 = cleaned_number[:5]
            part2 = cleaned_number[5:8]
            part3 = cleaned_number[8:]
        
        # Combine parts into the formatted string
        formatted_number = f"{part1}-{part2}-{part3}"   
        return formatted_number
    def PQRS_CODE_GC(contract_type):
        if contract_type == "GC":
            # Locate all rows in the claims table
            claim_table = driver.find_elements(By.XPATH, "//*[@id='tblCrgItems']/tbody/tr")
            total_rows = len(claim_table)

            # Determine how many rows to process
            rows_to_process = total_rows // 3 if total_rows % 3 == 0 else total_rows

            # Loop through the rows to extract the procedure code and update the value if a condition is met
            for index in range(rows_to_process):
                # Locate the procedure code element for the current row
                proc_code_element = driver.find_element(By.XPATH, f"//*[@id='txtCrgDtlProcID_{index}']")
                proc_code_value = proc_code_element.get_property("value")
                
                # Print the row and procedure code for debugging purposes
                print(f"Row {index} - Procedure code: {proc_code_value}")
                
                # Check if the procedure code ends with 'F'
                if proc_code_value.endswith('F'):
                    # If it ends with 'F', update the corresponding charge element to '0.00'
                    charge_element = driver.find_element(By.XPATH, f"//*[@id='txtCharge_{index}']")
                    charge_element.clear()  # Clear the existing value
                    charge_element.send_keys("0.00")  # Update the value to '0.00'
                    print(f"Updated charge in Row {index} to '0.00'") 
    def PQRS_CODE_NGC(contract_type, primary_ins):
    # List of primary insurance codes for processing
        primary_ins_codes = [
            "FC_BCBS FEDERAL PROGRAM", "FC_BCBS ANTHEM MEDICAID", "BCBS ANTHEM MEDICAID", 
            "FC_BCBS ANTHEM MEDICARE", "BCBS FEDERAL PROGRAM", "BCBS FED", "FC_BCBS ANTHEM MCR SUPP", 
            "BCBS MEDICARE ADVANTAGE /32406", "BCBS MEDICARE ADVANTAGE/7003", "BCBS ANTHEM MEDICARE", 
            "BCBS_URGENTCARE_TN", "BCBS MEDICARE ADVANTAGE/130", "BCBS MEDICAID", 
            "BCBS ANTHEM", "BCBS ANTHEM MCR SUPP"
        ]
        # Locate all rows in the claims table
        claim_table = driver.find_elements(By.XPATH, "//*[@id='tblCrgItems']/tbody/tr")
        total_rows = len(claim_table)

        # Determine how many rows to process
        rows_to_process = total_rows // 3 if total_rows % 3 == 0 else total_rows

        # Check for contract type and primary insurance conditions
        if contract_type == "NGC" and primary_ins in primary_ins_codes:
            print("Processing for NGC and specified primary insurance in list")
            
            # Loop through the rows
            for index in range(rows_to_process):
                # Locate the procedure code element for the current row
                proc_code_element = driver.find_element(By.XPATH, f"//*[@id='txtCrgDtlProcID_{index}']")
                proc_code_value = proc_code_element.get_property("value")
                
                # Print the row and procedure code for debugging purposes
                print(f"Row {index} - Procedure code: {proc_code_value}")
                
                # Check if the procedure code ends with 'F'
                if proc_code_value.endswith('F'):
                    # Update the charge element to '0.00'
                    charge_element = driver.find_element(By.XPATH, f"//*[@id='txtCharge_{index}']")
                    charge_element.clear()  # Clear the existing value
                    charge_element.send_keys("0.00")  # Update the value to '0.00'
                    print(f"Updated charge in Row {index} to '0.00'")
        
        elif contract_type == "NGC" and primary_ins not in primary_ins_codes:
            print("Processing for NGC and primary insurance not in specified list") 
            # Loop through the rows
            for index in range(rows_to_process):
                # Locate the procedure code element for the current row
                proc_code_element = driver.find_element(By.XPATH, f"//*[@id='txtCrgDtlProcID_{index}']")
                proc_code_value = proc_code_element.get_property("value")  
                # Print the row and procedure code for debugging purposes
                print(f"Row {index} - Procedure code: {proc_code_value}")
                # Check if the procedure code ends with 'F'
                if proc_code_value.endswith('F'):
                    # Update the charge element to '0.00'
                    charge_element = driver.find_element(By.XPATH, f"//*[@id='txtCharge_{index}']")
                    charge_element.clear()  # Clear the existing value
                    charge_element.send_keys("0.01")  # Update the value to '0.00'
                    print(f"Updated charge in Row {index} to '0.01'") 
    def PQRS_CODE_RHC_MCO(contract_type):
        if contract_type == "RHC-MCO":
            # Locate all rows in the claims table
            claim_table = driver.find_elements(By.XPATH, "//*[@id='tblCrgItems']/tbody/tr")
            total_rows = len(claim_table)

            # Determine how many rows to process
            rows_to_process = total_rows // 3 if total_rows % 3 == 0 else total_rows

            # Loop through the rows to extract the procedure code and update the value if a condition is met
            for index in range(rows_to_process):
                # Locate the procedure code element for the current row
                proc_code_element = driver.find_element(By.XPATH, f"//*[@id='txtCrgDtlProcID_{index}']")
                proc_code_value = proc_code_element.get_property("value")
                
                # Print the row and procedure code for debugging purposes
                print(f"Row {index} - Procedure code: {proc_code_value}")
                
                # Check if the procedure code ends with 'F'
                if proc_code_value.endswith('F'):
                    # If it ends with 'F', update the corresponding charge element to '0.00'
                    charge_element = driver.find_element(By.XPATH, f"//*[@id='txtCharge_{index}']")
                    charge_element.clear()  # Clear the existing value
                    charge_element.send_keys("0.01")  # Update the value to '0.00'
                    print(f"Updated charge in Row {index} to '0.01'")                                  
    def add_cpt_code(driver, cpt_list):
        if cpt_list:
            for CPT in cpt_list:
                try:
                    addcpt = driver.find_element(By.XPATH, '//*[@id="txtProc0"]')
                    addcpt.clear()
                    addcpt.send_keys(CPT)
                    print(f"Successfully added CPT code: {CPT}")
                except NoSuchElementException:
                    print(f"Failed to update CPT code: {CPT}")
                try:
                    keyfind(driver)
                    addit = driver.find_element(By.ID, "btnContAdd")
                    addit.click()
                    WebDriverWait(driver, 1).until(EC.alert_is_present())
                    alert = driver.switch_to.alert
                    alert.accept()
                    driver.execute_script("window.scrollTo(0,-1000)")
                except:
                    print("not added cpt")
        else:
            print("No CPT codes to add")
    def scroll_into_view(driver, element):
        driver.execute_script("arguments[0].scrollIntoView(true);", element)

    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import NoSuchElementException
    def previous_vis(driver):
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        try:
            previous_visit = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='pnlMain']/table[3]/tbody/tr[20]/td[1]")))
            driver.execute_script("arguments[0].scrollIntoView(true);", previous_visit)
        except Exception as e:
            print("Error:", e)
            
    def previous_visitor(driver):  
        from selenium.webdriver.common.by import By
        from selenium.common.exceptions import NoSuchElementException
        tablereading=driver.find_elements(By.XPATH,'//*[@id="dgPrevVisits"]/tbody/tr')
        for r in range(1, len(tablereading) + 1):
            tablereadingrow1 = driver.find_element(By.XPATH, f"//*[@id='dgPrevVisits']/tbody/tr[{r}]/td[1]").text
            tablereadingrow2 = driver.find_element(By.XPATH, f"//*[@id='dgPrevVisits']/tbody/tr[{r}]/td[2]").text 
            if tablereadingrow2 == faci and tablereadingrow1 == ddate:
                print("found matches")
                # Scroll to the elements
                tablereadingrow1_element = driver.find_element(By.XPATH, f"//*[@id='dgPrevVisits']/tbody/tr[{r}]/td[1]")
                tablereadingrow2_element = driver.find_element(By.XPATH, f"//*[@id='dgPrevVisits']/tbody/tr[{r}]/td[2]")
                driver.execute_script("arguments[0].scrollIntoView();", tablereadingrow1_element)
                driver.execute_script("arguments[0].scrollIntoView();", tablereadingrow2_element)
                try:
                    for i in range(4):
                        try:
                            driver.find_element(By.XPATH, f"//table[@id='dgPrevVisits']/tbody/tr[{r}]/td[3]/a[{i+1}]").click()
                            break  
                        except:
                            continue 
                except NoSuchElementException:
                    print("All attempts failed")
                break 
                
                
    def keyfind(driver):
        try:
            add_button = WebDriverWait(driver,3).until(EC.presence_of_element_located((By.ID, "btnContAdd")))
            driver.execute_script("arguments[0].scrollIntoView(true);", add_button)
        except TimeoutException as e:
            print("Error:", e)
            
    def self_charges(key):
        medication_dict = {
            "S9083": "$135"    
        }
        if key in medication_dict:
            # If yes, return the value associated with the key
            return medication_dict[key]
        else:
            # If not, return a default value or handle the case as needed
            return ""  # You can adjust this to return any default value you prefer


    def GC(cntract_type):
        if cntract_type =="GC":
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            clmtable = driver.find_elements(By.XPATH, "//*[@id='tblCrgItems']/tbody/tr")
            length = len(clmtable)
            if length % 3 == 0:
                subtraction_value = length // 3 * 2
            else:
                subtraction_value = 0  
            result = length - subtraction_value
            for j in range(0, result):
                zero_charge_element = driver.find_element(By.XPATH, "//*[@id='txtCharge_" + str(j) + "']")
                zero_charge_value = zero_charge_element.get_property("value")
                print(zero_charge_value)
                # Check if zero_charge_value is empty or between 0.00 and 0.99
                try:
                    zero_charge_float = float(zero_charge_value)
                    if zero_charge_float >= 0.00 and zero_charge_float <= 0.99:
                        condition_met = True
                    else:
                        condition_met = False
                except ValueError:
                    condition_met = (zero_charge_value == "")
                if condition_met:
                    x = driver.find_element(By.XPATH, "//*[@id='txtCrgDtlProcID_" + str(j) + "']").get_property("value")
                    checkbox = driver.find_element(By.XPATH, "//*[@id='chkBillTo_" + str(j) + "']")
                    WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='chkBillTo_" + str(j) + "']")))
                    checkbox.click()
    def find_delete():
        delete_icon = driver.find_element(By.CLASS_NAME, "mdi-delete")
        driver.execute_script("arguments[0].scrollIntoView(true);", delete_icon)
        
    def NGC_copay(contract_type):
        try:
            if contract_type == "NGC" or contract_type == "RHC-MCO":
                # Handle alert
                try:
                    WebDriverWait(driver, 3).until(EC.alert_is_present())
                    alert = driver.switch_to.alert
                    alert.accept()
                except:
                    print("No alert found")

                # Find the copay amount element
                disabled_element = driver.find_element(By.CSS_SELECTOR, "input#txtCopayAmt_1")
                value_attribute = disabled_element.get_attribute("value")
                disabled_element1 = driver.find_element(By.ID, "txtCurrPayAmt_1")
                value_attribute1 = disabled_element1.get_attribute("value")
                disabled_element2 = driver.find_element(By.ID, "txtCopayAmt_2")
                value_attribute2 = disabled_element2.get_attribute("value")
                copay_value = float(value_attribute1) + float(value_attribute)+float(value_attribute2)
                print(copay_value)
                # Procedure codes list
                procedure_codes = ["SPPHY","99211", "99212", "99213", "99214", "99215","99201", "99202", "99203", "99204", "99205","SPPHY"]
                # Get claim table rows
                claim_table_rows = driver.find_elements(By.XPATH, "//*[@id='tblCrgItems']/tbody/tr")
                row_count = len(claim_table_rows)

                # Calculate result
                if row_count % 3 == 0:
                    subtract_value = row_count // 3 * 2
                else:
                    subtract_value = 0
                result_count = row_count - subtract_value

                # Loop through each row and update copay
                for index in range(result_count):
                    try:
                        procedure_code_element = driver.find_element(By.XPATH, f"//*[@id='txtCrgDtlProcID_{index}']")
                        procedure_code = procedure_code_element.get_attribute("value")
                        if procedure_code in procedure_codes:
                            copay_paid_element = driver.find_element(By.XPATH, f"//*[@id='txtPaid_{index}']")
                            copay_paid_element.clear()
                            copay_paid_element.send_keys(copay_value)
                    except:
                        print(f"Error processing row {index}")
                        continue

                # Save the changes
                print("Saving the file")
                driver.execute_script("window.scrollTo(0, 3000)")
                save_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="btnUpdateFooter"]'))
                )
                save_button.click()
                try:
                    WebDriverWait(driver,3).until(EC.alert_is_present())
                    alert = driver.switch_to.alert
                    alert.accept()
                except:
                    print("No alert found after saving")
        except Exception as e:
            print(f"An error occurred: {e}")
    from selenium import webdriver
    import time
    def GC_Copay(cntract_type):
        if cntract_type == "GC":
            print("Found GC Visit value")
            disabled_element = driver.find_element(By.CSS_SELECTOR, "input#txtCopayAmt_1")
            value_attribute = disabled_element.get_attribute("value")
            disabled_element1 = driver.find_element(By.ID, "txtCurrPayAmt_1")
            value_attribute1 = disabled_element1.get_attribute("value")
            disabled_element2 = driver.find_element(By.ID, "txtCopayAmt_2")
            value_attribute2 = disabled_element2.get_attribute("value")
            value_attribute = float(value_attribute1) + float(value_attribute)+float(value_attribute2)
            print(value_attribute)
            claim_table = driver.find_elements(By.XPATH, "//*[@id='tblCrgItems']/tbody/tr")
            procedure_codes = ["S9083", "99211", "99212", "99213", "99214", "99215", "99201", "99202", "99203", "99204", "99205"]
            total_rows = len(claim_table)
            print(f"Number of rows in the claim table: {total_rows}")

            # Calculate the number of rows to process
            if total_rows % 3 == 0:
                rows_to_process = total_rows // 3
            else:
                rows_to_process = total_rows

            print(f"Processing the first {rows_to_process} rows")
            time.sleep(2)  # Allow the page to load
            # Flag to check if S9083 was found
            S9083_found = False

            for index in range(rows_to_process):
                try:
                    proc_code_element = driver.find_element(By.XPATH, f"//*[@id='txtCrgDtlProcID_{index}']")
                    proc_code_value = proc_code_element.get_property("value")
                    print(f"Row {index} - Procedure code: {proc_code_value}")
                    if proc_code_value == "S9083":
                        copaid_element = driver.find_element(By.XPATH, f"//*[@id='txtPaid_{index}']")
                        copaid_element.clear()
                        copaid_element.send_keys(value_attribute)
                        S9083_found = True
                        print(f"Entered value_attribute for S9083 in row {index}")
                        break  # Exit the loop since S9083 is found
                except Exception as e:
                    print(f"An error occurred for row {index}: {e}")
            if not S9083_found:
                print("S9083 not found, processing other procedure codes")
                for index in range(rows_to_process):
                    try:
                        proc_code_element = driver.find_element(By.XPATH, f"//*[@id='txtCrgDtlProcID_{index}']")
                        proc_code_value = proc_code_element.get_property("value")
                        print(f"Row {index} - Procedure code: {proc_code_value}")

                        if proc_code_value in procedure_codes:
                            copaid_element = driver.find_element(By.XPATH, f"//*[@id='txtPaid_{index}']")
                            copaid_element.clear()
                            copaid_element.send_keys(value_attribute)
                            print(f"Entered S9083 for procedure code {proc_code_value} in row {index}")
                    except Exception as e:
                        print(f"An error occurred for row {index}: {e}")
            print("Saving the file")
            time.sleep(2)  # Allow any final changes to be processed
            driver.execute_script("window.scrollTo(0, 3000)")     
    def Region(key):
        medication_dict = {
        "BARDSTOWN":"FPKY",
        "BENTON":"FPKY",
        "BHCLINICKY":"FPKY",
        "BARDSTOWN": "FPKY",
        "BENTON": "FPKY",
        "BHCLINICKY": "FPKY",
        "BRANDENBKY": "FPKY",
        "CAMPBELLSV": "FPKY",
        "CENTRALCTY": "FPKY",
        "CORBINKY": "FPKY",
        "FRANKLIN": "FPKY",
        "LAWRENCEKY": "FPKY",
        "LEBANON": "FPKY",
        "LEITCHFIEL": "FPKY",
        "MADISONVIL": "FPKY",
        "MAYFIELD": "FPKY",
        "MAYSVILLE": "FPKY",
        "MONTICELLO": "FPKY",
        "MURRAY": "FPKY",
        "PARISKY": "FPKY",
        "RUSSELLVIL": "FPKY",
        "SOMERSET": "FPKY",
        "VMCLINICKY": "FPKY",
        "WASHINGTON": "FPKY",
        "FCBARDSTKY": "FPKY",
        "FCCORBINKY": "FPKY",
        "FCDANVILKY": "FPKY",
        "FCGLASGOKY": "FPKY",
        "FCHAZARDKY": "FPKY",
        "FCHOPKINKY": "FPKY",
        "FCLONDONKY": "FPKY",
        "FCMADISOKY": "FPKY",
        "FCMIDDLEKY": "FPKY",
        "FCMTSTERKY": "FPKY",
        "FCPIKEVIKY": "FPKY",
        "FCSOMERSKY": "FPKY",
        "FCWINCHEKY": "FPKY",
        "ADMINAL": "FPAL",
        "ALABASTEAL": "FPAL",
        "BHCLINICAL": "FPAL",
        "HUEYTOWNAL": "FPAL",
        "JACKSONVAL": "FPAL",
        "LINCOLNAL": "FPAL",
        "PTALABASAL": "FPAL",
        "PTHUEYTOAL": "FPAL",
        "SPANISHFAL": "FPAL",
        "SYLACAUGAL": "FPAL",
        "ADMININ": "FPIN",
        "ATTICAIN": "FPIN",
        "BHCLINICIN": "FPIN",
        "BRAZILIN": "FPIN",
        "CLINTONIN": "FPIN",
        "FCBEDFORIN": "FPIN",
        "FCGREENFIN": "FPIN",
        "FCNEWCASIN": "FPIN",
        "FCRICHMOIN": "FPIN",
        "FCSEYMOUIN": "FPIN",
        "HANOVERIN": "FPIN",
        "KENDALVIIN": "FPIN",
        "MARTINSVIN": "FPIN",
        "NORTHVERIN": "FPIN",
        "PORTLANDIN": "FPIN",
        "ROCHESTEIN": "FPIN",
        "SHELBYVIIN": "FPIN",
        "TELLCITYIN": "FPIN",
        "WASHINTOIN": "FPIN",
        "ADMINKY": "FPKY",
        "ALBANYKY": "FPKY",
        "BARDSTOWN": "FPKY",
        "BEAVERDAM": "FPKY",
        "BENTON": "FPKY",
        "BHCLINICKY": "FPKY",
        "BRANDENBKY": "FPKY",
        "CAMPBELLSV": "FPKY",
        "CENTRALCTY": "FPKY",
        "CORBINKY": "FPKY",
        "FCBARDSTKY": "FPKY",
        "FCCORBINKY": "FPKY",
        "FCDANVILKY": "FPKY",
        "FCFRANKFKY": "FPKY",
        "FCGLASGOKY": "FPKY",
        "FCHAZARDKY": "FPKY",
        "FCHENDERKY": "FPKY",
        "FCHOPKINKY": "FPKY",
        "FCLONDONKY": "FPKY",
        "FCMADISOKY": "FPKY",
        "FCMIDDLEKY": "FPKY",
        "FCMTSTERKY": "FPKY",
        "FCPIKEVIKY": "FPKY",
        "FCSHEPHEKY": "FPKY",
        "FCSOMERSKY": "FPKY",
        "FCWINCHEKY": "FPKY",
        "FRANKLIN": "FPKY",
        "LAWRENCEKY": "FPKY",
        "LEBANON": "FPKY",
        "LEITCHFIEL": "FPKY",
        "MADISONVIL": "FPKY",
        "MAYFIELD": "FPKY",
        "MAYSVILLE": "FPKY",
        "MONTICELLO": "FPKY",
        "MURRAY": "FPKY",
        "PRINCETON": "FPKY",
        "RUSSELLVIL": "FPKY",
        "SOMERSET": "FPKY",
        "VMCLINICKY": "FPKY",
        "WASHINGTON": "FPKY",
        "ADMINLA": "FPLA",
        "BAKERLA": "FPLA",
        "BEGLIS": "FPLA",
        "BHCLINICLA": "FPLA",
        "BREAUXBRLA": "FPLA",
        "CHALMETTLA": "FPLA",
        "CO CLUB RD": "FPLA",
        "CROWLEY": "FPLA",
        "DENHAMSPLA": "FPLA",
        "DERIDDER": "FPLA",
        "DONALDSOLA": "FPLA",
        "EBATONROLA": "FPLA",
        "FRANKLINLA": "FPLA",
        "HOUMALA": "FPLA",
        "HWY14": "FPLA",
        "INDEPENDLA": "FPLA",
        "JENNINGS": "FPLA",
        "KAPLANLA": "FPLA",
        "KEYSER": "FPLA",
        "LEESVILLE": "FPLA",
        "MAINSFLDLA": "FPLA",
        "MARREROLA": "FPLA",
        "PEARLRIVLA": "FPLA",
        "PINEVILLLA": "FPLA",
        "PONCHATOLA": "FPLA",
        "PTMOSSBLUF": "FPLA",
        "SAM HSTN": "FPLA",
        "SULPHURLA": "FPLA",
        "VMCLINICLA": "FPLA",
        "WATSONLA": "FPLA",
        "WESTMONROE": "FPLA",
        "ADMINMS": "FPMS",
        "BHCLINICMS": "FPMS",
        "BILOXIMS": "FPMS",
        "BROOKHAVMS": "FPMS",
        "CANTONMS": "FPMS",
        "CARTHAGEMS": "FPMS",
        "CLARKSDALE": "FPMS",
        "COLUMBIAMS": "FPMS",
        "COLUMBUSMS": "FPMS",
        "CORINTHMS": "FPMS",
        "ELLISVILMS": "FPMS",
        "FORESTMS": "FPMS",
        "GAUTIERMS": "FPMS",
        "GREENVILMS": "FPMS",
        "GREENWOOD": "FPMS",
        "GRENADA": "FPMS",
        "HAZLEHURMS": "FPMS",
        "HOLLYSPRGS": "FPMS",
        "INDIANOLA": "FPMS",
        "IUKAMS": "FPMS",
        "KOSCIUSKO": "FPMS",
        "LONGBEACMS": "FPMS",
        "MAGEE": "FPMS",
        "MCCOMBMS": "FPMS",
        "NATCHEZMS": "FPMS",
        "NEWTONMS": "FPMS",
        "OLIVEBRAMS": "FPMS",
        "PHILADELPH": "FPMS",
        "RICHLANDMS": "FPMS",
        "RIDGELANMS": "FPMS",
        "RIPLEY": "FPMS",
        "SOUTHAVEMS": "FPMS",
        "VICKSBURMS": "FPMS",
        "VMCLINICMS": "FPMS",
        "WALLSMS": "FPMS",
        "WAVELANDMS": "FPMS",
        "WAYNESBOMS": "FPMS",
        "WESTPOINT": "FPMS",
        "WIGGINSMS": "FPMS",
        "YAZOOMS": "FPMS",
        "GREENBRIAR":"FPAR",
        "MTNHOMEAR":"FPAR",
        "HODGENVIKY":"FPKY"    
        }    
        # Check if the key exists in the dictionary
        if key in medication_dict:
            return medication_dict[key]
        else:
            return None 

    def process_financial_class(financial_class):
        try:
            # Define the updated list of Medicare classes with stripped spaces
            medicare_classes = [
                '3-Medicare', '26-Medicaid', '4-Medicaid', 'FC_Medicaid', 'FC_RHC Medicaid',
                'RHC Medicaid', '33-Medicare Part', '6-Other Medicare', 'FC_Medicare',
                'FC_RHC Medicare', 'Other Medicare A', '21-Magnolia', '23-LA Health Connections',
                '33-Medicare Part A', '34-RHC Medicaid', '19-BlueMedicaid', '13-tricare',
                'FC_Tricare', '41-rhc_medicare', '40-FC_Medicaid', '43-RHC_Medicaid',
                '42-FC_Medicare', '44-FC_Tricare'
            ]
            
            # Clean up spaces from financial_class
            financial_class = financial_class.strip() 
            if financial_class in medicare_classes:
                print("Processing Medicare claim")
                selected_option = driver.find_element(By.CSS_SELECTOR, 'option[selected="selected"]')
                selected_text = selected_option.text
                time.sleep(2)            
                input_field1 = driver.find_element(By.ID, "ddlHeaderRefPhy")
                input_field1.send_keys(selected_text)
                save = driver.find_element(By.ID, "btnUpdate")
                save.click()          
                try:
                    alert = driver.switch_to.alert
                    alert.accept()
                except:
                    print("No alert present")
            else:
                print("Not a Medicare claim")
        except Exception as e:
            print(f"Error in processing financial class: {e}")
    # try:        
        # Logging in
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        driver.maximize_window()
        driver.get("https://pvpm.practicevelocity.com/")
        # Explicit wait to ensure the elements are present before interacting
        wait = WebDriverWait(driver,5)  # 10 seconds timeout
        # Wait for the login input box to be present and send keys
        login_input = wait.until(EC.presence_of_element_located((By.ID, "txtLogin")))
        login_input.send_keys("KNAGES@FPUCS")
        time.sleep(1)
        try:
            next=driver.find_element(By.ID,"btnNext")
            next.click()
        except:
            pass    
        # Wait for the password input box to be present and send keys
        password_input = wait.until(EC.presence_of_element_located((By.ID, "txtPassword")))
        password_input.send_keys("Exdionnov@2024")   
        # Wait for the submit button to be clickable and click it
        submit_button = wait.until(EC.element_to_be_clickable((By.NAME, "btnSubmit")))
        submit_button.click()
    except:
        print("failed to login")

    # endate="2024-09-21"
    endate_log = Created_date
    username = 'api_user@exdionace.ai'
    password = r'&D/]\R[n+A)}^#%'
    ready_jobs = get_jobs(username, password)
    if ready_jobs:
        process_contracts_and_log(ready_jobs, endate_log)

    # try:
    #     process_data(driver,Created_date)
    #     print("updating access health")
    # except:
    #     print("failed in access health")

    username = 'api_user@exdionace.ai'
    password = r'&D/]\R[n+A)}^#%'
    ready = get_jobs(username, password)
    try:
        for rdp in ready:
            visnum = rdp["visitNumber"]    
            jobi = rdp["jobID"]
            clientd = rdp["clientID"]
            client_name = rdp["clientName"]
            patient = rdp["patientName"]
            created_date_111 = convert_utc_to_ist(rdp["createdOn"][:19])
            created = created_date_111[:10]
            enco = rdp["encounterDate"]
            endate = enco[:10]
            faci = rdp["appointmentFacility"]
            visty = rdp["visitType"]
            primary_ins = rdp['primaryInsurance']
            provider_name = rdp['provider']
            accnumber = rdp['accountNumber']
            yeprec = rdp["predictedCategory"]
            Place_of_service = rdp["financialClass"]
            POS_1 = rdp["pos"]
            con_type = rdp["contractType"]
            region=rdp["regionName"]
            STP1 = rdp["stp"]             
            if created in Created_date and faci in facilities:
            #    ['FCCORBINKY','FCHENDERKY','FCHOPKINKY','CORBINKY','CAMPBELLSV','CENTRALCTY',
            #     'FCMIDDLEKY','FCMTSTERKY','FCWINCHEKY','SOMERSET','FCPIKEVIKY','LEBANON',
            #     'FCLONDONKY','BENTON','FCSOMERSKY','FCFRANKFKY','FCDANVILKY','MAYFIELD','MAYSVILLE','MONTICELLO','PARISKY',
            #     'BRANDENBKY','FCGLASGOKY','CANTONMS','WESTPOINT','CROWLEY','DENHAMSPLA','BARDSTOWN','BEAVERDAM',
            #     'DRYRIDGEKY','FCBARDSTKY','FCHAZARDKY','FCMADISOKY','FRANKLIN',
            #     'FCSHEPHEKY','HODGENVIKY','LAWRENCEKY','LEITCHFIEL','MADISONVIL','RUSSELLVIL','PRINCETON','VMCLINICKY','WASHINGTON',
            #     'GREENBRIAR','MTNHOMEAR','MURRAY','FCGREENFIN','TELLCITYIN','SYLACAUGAL','HUEYTOWNAL']:
                if con_type in ["NGC", "GC", "RHC-MCO"] and STP1 == "STP" and "_test" not in visnum.lower():
                    logger.info(f"Matched record: {clientd}, {jobi}, {patient}, {enco}, {endate}, {faci}, {visty}, {visnum},{created}, {provider_name}, {yeprec}, {accnumber}, {POS_1}, {Place_of_service}")
                    print("valid contract type",clientd, jobi,client_name, patient,endate, faci, visty, visnum,provider_name,con_type,created)     
                    try:
                        driver.find_element(By.ID, "tdMenuBarItemPatient").click()
                        driver.find_element(By.ID, "menu_Patient_PatSummary").click()
                    except NoSuchElementException as e:
                        print("Error while navigating to patient summary:", e)  
                        
                    #select partice
                    try:
                        target_value = faci
                        key1 = Region(target_value)
                        dropdown_element = WebDriverWait(driver, 3).until(
                            EC.presence_of_element_located((By.ID, 'ddlPractice'))
                        )
                        dropdown = Select(dropdown_element)
                        dropdown.select_by_value(key1)
                    except:
                        print("failed to updated Region")
                    import requests
                    playload = {'username' : 'api_user@exdionace.ai', 'password' : r'&D/]\R[n+A)}^#%'}
                    headers = {"accept": "*/*", "Content-Type": "application/json"}
                    a =requests.post("https://www.exdion-h.studio/api/Login/SignIn", headers = headers, json = playload)
                    data = a.json()
                    access_token = data['accessToken']
                    # print(access_token)
                    r2=requests.get("https://exdion-h.studio/api/Jobs/GetJobCodes?clientID="+str(clientd)+"&jobID="+str(jobi)+"", headers={"Authorization": f"Bearer {access_token}"})
                    codes=r2.json()
                    JOBs=[]
                    clientpd=[]
                    cpts = []
                    mods = []
                    icdss = []
                    units = []
                    ndcs = []
                    FC=[]
                    POS=[]
                    cn_type=[]
                    region1=[]
                    for dd in codes["cptViewModels"]:
                        cpt = []
                        unit = []
                        dd3 = dd["cptHcpcs"]
                        dd4 = dd["units"]
                        dd5 = dd["ndc"]
                        cpt.append(dd3)
                        unit.append(dd4)
                        # print("cpt", cpt)
                        # print("unit", unit)
                        # print("ndc", dd5)
                        modd = []
                        for dd2 in dd["jobModifiers"]:
                            modi = dd2["modifier"]
                            modd.append(modi)
                        icdd = []
                        for dd1 in dd["jobICDs"]:
                            icd = dd1["icd"]
                            icdd.append(icd)
                        ndcs.append(dd5)
                        cpts.append(cpt)
                        mods.append(modd)
                        icdss.append(icdd)
                        units.append(unit)
                        fin_clss=[]
                        facility = rdp["financialClass"]
                        FC.append(facility)
                        pos=rdp["pos"]
                        POS.append(pos)
                        cn_typee=rdp["contractType"]
                        cn_type.append(cn_typee)
                        JOBs.append(jobi) 
                        clientpd.append(clientd) 
                        region1.append(region)  
                    import pandas as pd
                    df = pd.DataFrame({
                                    'Client_id': clientpd,
                                    'JOB_ID': JOBs,
                                    'cpt': [i[0] for i in cpts],
                                    'unit': [i[0] for i in units],
                                    'Modifier1': [i[0] if i else None for i in mods],
                                    'Modifier2': [i[1] if len(i)>1  else None for i in mods],
                                    'Modifier3': [i[2] if len(i)>2  else None for i in mods],
                                    'Modifier4': [i[3] if len(i)>3  else None for i in mods],
                                    'ICD1': [i[0] if i else None for i in icdss],
                                    'ICD2': [i[1] if len(i)>1 else None for i in icdss],
                                    'ICD3':[i[2] if len(i)>2 else None for i in icdss],
                                    'ICD4':[i[3] if len(i)>3 else None for i in icdss],
                                    'ICD5':[i[4] if len(i)>4 else None for i in icdss],
                                    'ICD6':[i[5] if len(i)>5 else None for i in icdss],
                                    'ICD7':[i[6] if len(i)>6 else None for i in icdss],
                                    'ICD8':[i[7] if len(i)>7 else None for i in icdss],
                                    'ICD9':[i[8] if len(i)>8 else None for i in icdss],
                                    'ICD10':[i[9] if len(i)>9 else None for i in icdss],
                                    'NDCM':[i[:15] if isinstance(i, str) else (None if isinstance(i, (float, int)) else str(i)[:15]) for i in ndcs],
                                    'POS': [str(i)[0:5] if i is not None else None for i in POS] if POS is not None else None,
                                    'finical_cls': [str(i)[0:50] for i in FC],
                                    'contract_type':[str(i)[0:50] for i in cn_type],
                                    'Region':[str(i)[0:50] for i in region1],
                                    })
                    # print(df)
                    logger.info(f"charge_enter: \n{df.to_string(index=False)}")
                    try:
                        #countig ICD 
                        from collections import OrderedDict
                        icdss_combined = [item for sublist in icdss for item in sublist]
                        icdss_unique = list(OrderedDict.fromkeys(icdss_combined))
                        # print(icdss_unique)
                    except:
                        icdss_unique = []
                        [icdss_unique.append(item) for sublist in icdss for item in sublist if item not in icdss_unique]

                    # Print the unique list
                    print(icdss_unique)
                    try:
                        j_series_failed = df[(df['cpt'].str.startswith('J')) & (df['NDCM'].isna())]
                        if not j_series_failed.empty:
                            print("Failed rows where CPT starts with 'J' and NDCM is empty:")
                            update_job_status(clientd, jobi, access_token)
                            print("Invalid  NDC codes")
                            continue
                        else:
                            print("No failed rows.")
                    except:
                        print("error in validating J series code ") 
                    ##########################################################################################
                    from datetime import datetime
                    from datetime import datetime
                    date = datetime.strptime(endate,"%Y-%m-%d")    
                    ddate=datetime.strftime(date, "%m/%d/%Y")
                    try:
                        # Wait explicitly for the menu item to be present and then click
                        menu_item = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.ID, "tdMenuBarItemPatient"))
                        )
                        menu_item.click()

                        # Wait explicitly for the patient summary item to be present and then click
                        patient_summary = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.ID, "menu_Patient_PatSummary"))
                        )
                        patient_summary.click()
                    except (NoSuchElementException, TimeoutException) as e:
                        print("Error while navigating to patient summary:", e)

                    # Search by patient account number
                    try:
                        pataccnum = driver.find_element(By.ID, "textAdvPatNum")
                        pataccnum.clear()
                        pataccnum.send_keys(str(accnumber))
                        time.sleep(2)
                        pataccnum.send_keys(Keys.ENTER)
                        Search = driver.find_element(By.ID, "BtnSearch")
                        Search.click()
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                        time.sleep(2)
                        driver.execute_script("window.scrollTo(300, 300)")
                        driver.find_element(By.ID, "lbtnPatNum").click()
                        time.sleep(2)
                    except NoSuchElementException as e:
                        # update_job_status(clientd, jobi, access_token)
                        print("Error while searching patient account number:", e) 
                        continue  

                    try:
                        print("found Payer summary")
                        payer_summary = driver.find_element(By.ID, "pnlMain")
                        driver.execute_script("arguments[0].scrollIntoView(true);", payer_summary)
                    except:
                        print("failed Payer summary")
                    try:
                        print("checking if primary is present")
                        pri_ins_list = primary_ins
                        insurance_not_found(driver, pri_ins_list,select_dropdown_value)
                    except:
                        print("Error in insurance_not_found function ")
                    try:
                        pri_ins_sequence=primary_ins
                        Sequence_process_table(driver, pri_ins_sequence,scroll_into_view)
                    except:
                        print("Error in Sequence_process_table function ")  
                    try:
                        previous_visitor(driver)
                    except:
                        print("failed to match visitor")
                    # Charge entry
                    try:
                        time.sleep(3)
                        driver.execute_script("window.scrollTo(300, 300)")
                        driver.find_element(By.ID, "btnCrgEnter").click()
                        print("Charge entry clicked")
                    except:
                        driver.find_element(By.ID, "btnGoCrgEntry").click()
                        print("Charge entry (Go) clicked")
                        pass
                    driver.execute_script("window.scrollTo(300, 300)")
                    time.sleep(2)                    
                    # Continue button
                    try:
                        # Scroll down to make the button visible
                        driver.execute_script("window.scrollTo(0, 500)")   
                        # Wait until the button is clickable
                        wait = WebDriverWait(driver,5)  # Adjust timeout as needed
                        continue_button = wait.until(EC.element_to_be_clickable((By.NAME, "btnContAdd")))   
                        # Click the button
                        continue_button.click()
                    except:
                        print("Continue button not found or not clickable")
                        pass
                    ####ndc format 
                    try:
                        # Wait for the NDC checkbox to be present in the DOM
                        ndc_checkbox = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.ID, "cbNdcFlag"))
                        )
                        driver.execute_script("arguments[0].scrollIntoView(true);", ndc_checkbox)
                        WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.ID, "cbNdcFlag"))
                        )
                        # Check if the checkbox is already selected
                        if not ndc_checkbox.is_selected():
                            # Click the checkbox to enable it
                            ndc_checkbox.click()
                    except Exception as e:
                        print(f"Failed to update NDC: {e}")
                        pass
                    # try:
                    #     # Scroll to the continue button
                    #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  
                    #     # Wait for the continue button to be clickable
                    #     continue_button = WebDriverWait(driver, 3).until(
                    #         EC.element_to_be_clickable((By.NAME, "btnContAdd"))
                    #     )   
                    #     # Attempt to click the button using JavaScript to bypass any overlays
                    #     driver.execute_script("arguments[0].click();", continue_button)
                    # except:
                    #     print("Failed to click continue button:")
                    #     pass

                    # try:
                    #     cpt_codes = remove_cpts(driver)
                    #     print(cpt_codes)
                    # except:
                    #     print("error while deleting CPT")

                    # def recalculate_length(driver):
                    #     clmtable = driver.find_elements(By.XPATH, "//*[@id='tblCrgItems']/tbody/tr")
                    #     return len(clmtable)

                    # # Initial calculation
                    # length = recalculate_length(driver)
                    # # Process each row in reverse order
                    # cpt_list = []
                    # for j in range(length - 1, -1, -1):
                    #     try:
                    #         # Get the value from the specific cell
                    #         x = driver.find_element(By.XPATH, f"//*[@id='txtCrgDtlProcID_{j}']").get_property("value")
                    #         print(f"Processing row {j} with value {x}")

                    #         if x == '99051' or x == '99000':
                    #             cpt_list.append(x)
                    #             print(f"Found CPT {x}, appending to list")

                    #         # Delete the row regardless of the CPT code
                    #         find_delete()  # Assuming this function is defined elsewhere
                    #         remove_button = driver.find_element(By.XPATH, f"//*[@id='btnDeleteItem_{j}']")
                    #         remove_button.click()
                    #         WebDriverWait(driver, 10).until(EC.alert_is_present())
                    #         alert = driver.switch_to.alert
                    #         alert.accept()           

                    #         # Recalculate the length after deletion
                    #         length = recalculate_length(driver)
                    #     except:
                    #         print(f"Failed to process CPT for row {j}")
                    # Initial calculation
                    length = recalculate_length(driver)
                    cpt_list = []
                    for j in range(length - 1, -1, -1):
                        try:
                            click_ok_button_if_present(driver)   
                        except:
                            print("NO GC CPT found")   
                        try:
                            from selenium.webdriver.common.by import By
                            from selenium.webdriver.common.action_chains import ActionChains
                            from selenium.common.exceptions import NoSuchElementException, UnexpectedAlertPresentException
                            # Get the value from the specific cell
                            x = driver.find_element(By.XPATH, f"//*[@id='txtCrgDtlProcID_{j}']").get_property("value")
                            print(f"Processing row {j} with value {x}")

                            if x == '99051' or x == '99000':
                                cpt_list.append(x)
                                print(f"Found CPT {x}, appending to list")

                            # Delete the row regardless of the CPT code
                            find_delete()  # Assuming this function is defined elsewhere
                            remove_button = driver.find_element(By.XPATH, f"//*[@id='btnDeleteItem_{j}']")
                            remove_button.click()           
                            try:
                                WebDriverWait(driver, 5).until(EC.alert_is_present())
                                alert = driver.switch_to.alert
                                alert.accept()  
                                print(f"Handled alert for row {j}")
                            except UnexpectedAlertPresentException:
                                print(f"Unexpected alert present while processing row {j}. Handling the alert.")
                                alert = driver.switch_to.alert
                                alert.accept()
                            # Recalculate the length after deletion
                            length = recalculate_length(driver)
                            try:
                                print("GC modifier found")
                                click_ok_button_if_present(driver)   
                            except:
                                print("NO GC CPT found")
                        except NoSuchElementException:
                            pass
                            # print(f"Element not found for row {j}. Skipping this row.")
                        except Exception as e:
                            pass
                            # print(f"Failed to process CPT for row {j}. Error: {e}")

                    import time
                    from selenium.webdriver.common.by import By
                    from selenium.webdriver.support.ui import WebDriverWait
                    from selenium.webdriver.support import expected_conditions as EC
                    # Removing ICD into PVM
                    icdd = driver.find_elements(By.XPATH, "//*[@id='frmCrgEntry']/table[7]/tbody/tr[1]/td")
                    w = len(icdss_unique)
                    leng = w + 3
                    for ic1 in range(1, leng):
                        print(ic1)
                        try:
                            button = driver.find_element(By.ID, 'btnDiagChk' + str(ic1))
                            driver.execute_script("arguments[0].scrollIntoView(true);", button)
                            clearicd = driver.find_element(By.XPATH, "//*[@id='btnHeaderDiagPick"+str(ic1)+"']")
                            clearicd.click()
                        except:
                            print("not there to add icd")
                    try: 
                        driver.find_element(By.XPATH, "//input[@type='submit']").click()
                        time.sleep(1)
                    except:
                        print("exception not there")
                    driver.execute_script("window.scrollTo(0,-400)")
                    time.sleep(2)

                    # ADD POS CODE
                    try:
                        Pos = WebDriverWait(driver,3).until(EC.presence_of_element_located((By.ID, "ddlHeaderPOS")))
                        driver.execute_script("arguments[0].scrollIntoView(true);", Pos)
                        POS_1 = rdp["pos"]
                        print(POS_1)
                        from selenium.webdriver.support.ui import Select
                        select_element = driver.find_element(By.ID, "ddlHeaderPOS")
                        select = Select(select_element)
                        select.select_by_value(POS_1)
                    except:
                        print("error in POS")
                    import time
                    from selenium.webdriver.common.by import By
                    from selenium.common.exceptions import NoSuchElementException
                    try:
                        m = 1
                        for icdd in icdss_unique:
                            print(icdd)
                            try:
                                button = driver.find_element(By.ID, "btnDiagChk1")
                                driver.execute_script("arguments[0].scrollIntoView(true);", button)
                                driver.find_element(By.XPATH, f"//*[@id='trDiagCode{m}']")
                                ICD = driver.find_element(By.XPATH, f"//*[@id='txtHeaderDiagCode{m}']")
                                ICD.clear()
                                ICD.send_keys(icdd)
                                check = driver.find_element(By.XPATH, f"//*[@id='btnDiagChk{m}']")
                                check.click()
                                try:
                                    time.sleep(2)
                                    alert = driver.switch_to.alert
                                    alert.accept()
                                except:
                                    print("Alert not found")
                                m += 1                                      
                                time.sleep(2)
                            except:
                                print("Element not found")
                    except:
                        print("Error:", e)

                    for j, cpt in df.iterrows():
                        print(j)
                        keyfind(driver)
                        CPT = cpt['cpt']
                        UNIT1 = cpt['unit']
                        UNIT=int(UNIT1)
                        MOD1 = cpt['Modifier1']
                        MOD2 = cpt['Modifier2']
                        MOD3 = cpt['Modifier3']
                        ICD1 = cpt['ICD1']
                        ICD2 = cpt['ICD2']
                        ICD3 = cpt['ICD3']
                        ICD4 = cpt['ICD4']
                        ICD5 = cpt['ICD5']
                        ICD6 = cpt['ICD6']
                        ICD7 = cpt['ICD7']
                        ICD8 = cpt['ICD8']
                        ICD9 = cpt['ICD9']
                        ICD10 = cpt['ICD10']
                        ndcy = cpt['NDCM']
                        Finiclass =cpt['finical_cls']
                        cntract_type=cpt['contract_type']
                        try:
                            addcpt = driver.find_element(By.XPATH, '//*[@id="txtProc0"]')
                            addcpt.clear()
                            addcpt.send_keys(CPT)
                        except:
                            pass
                            # print("failed to update CPT")
                        try:
                            mod1 = driver.find_element(By.XPATH, '//*[@id="ddlModifier1_0"]')
                            if mod1 is not None and MOD1 != "nan":
                                mod1.send_keys(MOD1)
                        except:
                            pass
                            # print("Failed to update Modifier 1")
                        try:
                            mod2 = driver.find_element(By.XPATH, f'//*[@id="ddlModifier2_0"]')
                            if mod2 is not None and MOD2 != "nan":
                                mod2.send_keys(MOD2)
                        except:
                            pass
                            # print("Failed to update Modifier 2")
                        try:
                            mod3 = driver.find_element(By.XPATH, '//*[@id="ddlModifier3_0"]')      
                            if mod3 is not None and MOD3 != "nan":
                                mod3.send_keys(MOD3)       
                        except:
                            pass
                            # print("Failed to update Modifier 3") 
                        try:
                            units = driver.find_element(By.XPATH,'//*[@id="txtQuantity0"]')
                            units.click()
                            units.clear()
                            units.send_keys(UNIT)
                        except:
                            print("Failed to update Units")
                        try:
                            for i in range(1, 5):
                                driver.find_element(By.XPATH, f'//*[@id="ddlDiag{i}_0"]/option[1]').click()
                        except:
                            print("Error while emptying the ICD Codes")

                        # Handling ICD codes
                        for cnum in range(1, len(CPT) + 8):
                            procednum = driver.find_element(By.XPATH, f'//*[@id="txtHeaderDiagCode{cnum}"]').get_property("value")
                            procedcheck = driver.find_element(By.XPATH, f'//*[@id="trDiagCode{cnum}"]/td[1]').text
                            x = driver.find_element(By.XPATH, '//*[@id="txtProc0"]').get_property("value")
                            try:
                                if x == str(CPT) and ICD1 == procednum:
                                    d2 = driver.find_element(By.XPATH, '//*[@id="ddlDiag1_0"]')
                                    d2.send_keys(procedcheck)
                                elif x == str(CPT) and ICD2 == procednum:
                                    d2 = driver.find_element(By.XPATH, '//*[@id="ddlDiag2_0"]')
                                    d2.send_keys(procedcheck)
                                elif x == str(CPT) and ICD3 == procednum:
                                    d2 = driver.find_element(By.XPATH, '//*[@id="ddlDiag3_0"]')
                                    d2.send_keys(procedcheck)
                                elif x == str(CPT) and ICD4 == procednum:
                                    d2 = driver.find_element(By.XPATH, '//*[@id="ddlDiag4_0"]')
                                    d2.send_keys(procedcheck)
                                elif x == str(CPT) and ICD5 == procednum:
                                    d2 = driver.find_element(By.XPATH, '//*[@id="ddlDiag5_0"]')
                                    d2.send_keys(procedcheck)
                                elif x == str(CPT) and ICD6 == procednum:
                                    d2 = driver.find_element(By.XPATH, '//*[@id="ddlDiag6_0"]')
                                    d2.send_keys(procedcheck)
                                elif x == str(CPT) and ICD7 == procednum:
                                    d2 = driver.find_element(By.XPATH, '//*[@id="ddlDiag7_0"]')
                                    d2.send_keys(procedcheck) 
                                elif x == str(CPT) and ICD8 == procednum:
                                    d2 = driver.find_element(By.XPATH, '//*[@id="ddlDiag8_0"]')
                                    d2.send_keys(procedcheck)  
                                elif x == str(CPT) and ICD9 == procednum:
                                    d2 = driver.find_element(By.XPATH, '//*[@id="ddlDiag9_0"]')
                                    d2.send_keys(procedcheck)     
                            except:
                                print("failed to update ICD codes")
                        ##################################################ADDING CPT##################################################      
                        try:
                            keyfind(driver)
                            addit = driver.find_element(By.ID, "btnContAdd")
                            addit.click()
                            try:
                                click_ok_button_if_present(driver)
                                WebDriverWait(driver, 4).until(EC.alert_is_present())
                                alert = driver.switch_to.alert
                                alert.accept()
                                time.sleep(2)
                                driver.execute_script("window.scrollTo(0,-1000)")
                            except:  
                                pass   
                        except:
                            print("not added cpt")
                            update_job_status(clientd, jobi, access_token)
                            navigate_to_patient_summary(driver)
                            continue
                        ##################################################ADDING NDC##################################################       
                        try:
                            clmtable = driver.find_elements(By.XPATH, "//*[@id='tblCrgItems']/tbody/tr")
                            print(len(clmtable))  
                            length = len(clmtable)
                            if length % 3 == 0:
                                subtraction_value = length // 3 * 2
                            else:
                                subtraction_value = 0
                            result = length - subtraction_value
                            for j in range(result):
                                print(j)
                                try:                                                     
                                    if df.loc[j, 'NDCM'] != "None":  # Check if the value from DataFrame is not None
                                        checkbox = driver.find_element(By.XPATH, f'//*[@id="chkSendDescriptionInEDI{j}"]')
                                        checkbox.click()
                                        ndc1 = driver.find_element(By.XPATH, f'//*[@id="txtCrgDtlNdcNum_{j}"]')
                                        print(ndc1.text)
                                        ndc1.clear()    
                                        number =str(df.loc[j, 'NDCM'])
                                        formatted_number = format_number(number)
                                        print(formatted_number)    
                                        ndc1.send_keys(formatted_number)
                                        qty = driver.find_element(By.XPATH, f'//*[@id="txtCrgDtlNdcQnty_{j}"]')
                                        qty.clear()
                                        qty.send_keys("1")
                                        driver.find_element(By.XPATH, f'//*[@id="ddlCrgDtlNdcUOM_{j}"]/option[5]').click()
                                    # else:
                                    #     print("NDCM value is None. Check why it's not assigned a valid value.")
                                except:
                                    pass
                                    # print("Error in NDC:")
                        except:
                            pass   
                            # print("saving the file")
                    try:
                        POS_MOD1=df.loc[0, 'Modifier1']
                        POS_MOD2=df.loc[0, 'Modifier2']
                        contype = df.loc[0,'contract_type']
                        handle_pos_condition(driver,contype,POS_MOD1,POS_MOD2) 
                       
                    except:
                        print("Error in POS 72 ")         
                    try:
                        add_cpt_code(driver, cpt_list)
                    except:
                        print("failed to add provider code")
                    try:
                        print("PQRS For GC visits")
                        contype = df.loc[0,'contract_type']
                        PQRS_CODE_GC(contype)
                    except:
                        update_job_status(clientd, jobi, access_token)
                        print("failed to pqrs COPAY  GC Visit")
                        continue
                    try:
                        print("PQRS For GC visits")
                        primary_insu1=primary_ins
                        contype = df.loc[0,'contract_type']
                        PQRS_CODE_NGC(contype, primary_insu1)
                    except:
                        update_job_status(clientd, jobi, access_token)
                        print("failed to PQRS NGC Visit")
                        continue
                    try:
                        print("PQRS For RHC-MCO  visits")
                        contype = df.loc[0,'contract_type']
                        PQRS_CODE_RHC_MCO(contype)
                    except:
                        print("failed to PQRS RHC-MCO Visit")
                        continue
                    try:
                        driver.execute_script("window.scrollTo(0,700)")
                        GC(cntract_type)
                        print("updated GC ")
                    except:
                        print("Failed to updated GC")              
                        time.sleep(1)
                    try:
                        print("copay for GC visit")
                        Copay = df.loc[0,'contract_type']
                        GC_Copay(Copay)
                    except:
                        update_job_status(clientd, jobi, access_token)
                        print("failed to Copay GC Visit")
                        continue
                    try:
                        print("copay for NGC visit")
                        Copay = df.loc[0,'contract_type']
                        NGC_copay(Copay)
                    except:
                        update_job_status(clientd, jobi, access_token)
                        print("failed to Copay  NGC Visit")
                        continue
                    try:
                        financial_class = cpt['finical_cls']
                        process_financial_class(financial_class)
                    except:
                        print("not found medicaid")
                    # try:
                    #     driver.execute_script("window.scrollTo(0,3000)")
                    #     save=driver.find_element_by_xpath('//*[@id="btnUpdateFooter"]')
                    #     time.sleep(2)
                    #     save.click()
                    #     time.sleep(2)
                    # except:
                    #     print("failed in save button")     
                    # try:
                    #     try:
                    #         alert = Alert(driver)
                    #         alert.accept()
                    #     except:
                    #         print("No alert found")
                    #     disabled_element = driver.find_element(By.CSS_SELECTOR, "input#txtCopayAmt_1")
                    #     text_content = disabled_element.text
                    #     value_attribute = disabled_element.get_attribute("value")
                    #     value_attribute
                    #     list = ["99211","99212","99213","99214","99215","99201","99202","99203","99204","99205","SPPHY"]
                    #     clmtable= driver.find_elements(By.XPATH,"//*[@id='tblCrgItems']/tbody/tr")
                    #     length = len(clmtable)
                    #     if length % 3 == 0:
                    #         subtraction_value = length // 3 * 2
                    #     else:
                    #         subtraction_value = 0  
                    #     result = length - subtraction_value
                    #     result
                    #     time.sleep(2)
                    #     for j in range(0,result):
                    #         print(j)
                    #         try:
                    #             driver.find_element(By.XPATH,"//*[@id='rowProcCode"+str(j)+"']/td[1]")
                    #             x= driver.find_element(By.XPATH,"//*[@id='txtCrgDtlProcID_"+str(j)+"']").get_property("value")
                    #             print(x)
                    #             if x in list:
                    #                 copaid= driver.find_element(By.XPATH, "//*[@id='txtPaid_"+str(j)+"']")
                    #                 copaid.clear()
                    #                 copaid.send_keys(value_attribute) 
                    #         except:
                    #             print("not found") 
                    # except:
                    #     print("failed to updated copay")                
                    # try:
                    #     alert=driver.switch_to_alert() 
                    #     alert.accept()
                    # except:
                    #     print("not present")
                    try:
                        if df.loc[0,'contract_type']=="GC":
                            print("GC visits Updating withhold status...")
                            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")   
                            # Use explicit wait for the element to be present and visible
                            wait = WebDriverWait(driver,3)  # Wait for up to 10 seconds
                            reasons = wait.until(EC.visibility_of_element_located((By.ID, "ddlWithholdRsn")))   
                            reasons.send_keys("----------------------------------")
                            print("Withhold status updated successfully")
                        else:
                            print("visits Updating withhold status...")
                            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")   
                            # Use explicit wait for the element to be present and visible
                            wait = WebDriverWait(driver,3)  # Wait for up to 10 seconds
                            reasons = wait.until(EC.visibility_of_element_located((By.ID, "ddlWithholdRsn")))   
                            reasons.send_keys("----------------------------------")    
                    except TimeoutException:
                        print("Timed out waiting for withhold reason dropdown to become visible")
                    except Exception as e:
                        print(f"Failed to update withhold status: {str(e)}")
                    
                    try:
                        driver.execute_script("window.scrollTo(0, 3000)")
                        save = driver.find_element(By.XPATH, '//*[@id="btnUpdateFooter"]')
                        time.sleep(2)
                        save.click()      
                        # save_and_exit_button = driver.find_element(By.ID, "btnDone")
                        # scroll_into_view(driver, save_and_exit_button)
                        # time.sleep(5)
                        # save_and_exit_button.click()
                    except:
                        print("error found in save and exit")
                    try:
                        alert = Alert(driver)
                        alert.accept()
                        # update_job_status(clientd, jobi, access_token)
                        # print("Failed due paid amount is not matching")
                        # continue           
                    except NoAlertPresentException:
                        # If NoAlertPresentException is raised, it means there was no alert, so do nothing or handle as needed
                        print("No alert found") 
                    try:
                        print("updating ehr UPDATING status as successfully")
                        import requests
                        jobid = df['JOB_ID'].iloc[0]
                        clientd = df['Client_id'].iloc[0]
                        r7 = requests.post(
                        f"https://exdion-h.studio/api/Jobs/UpdateJobEhrPostStatus?clientID={clientd}&jobID={jobid}&IsSuccessful=true",
                        headers={"Authorization": f"Bearer {access_token}"})
                        print(r7)
                        logger.info(f"successfully updated: {clientd}, {jobid}, {patient},{endate}, {faci}, {visty}, {visnum}, {provider_name}, {yeprec}, {accnumber}, {POS_1}, {Place_of_service},{con_type}")
                        # jobi = clientd = client_name = patient = enco = endate = faci = visty = visnum = ins = provider_name = accnumber = yeprec = Place_of_service = POS_1 = con_type = None    
                        time.sleep(2)   
                    except:
                        print("Bot Failed to updated API")
                    time.sleep(2) 
                else:
                    print("Invalid contract type",clientd, jobi,client_name, patient,endate, faci, visty, visnum,provider_name,con_type)    
                    update_job_status(clientd, jobi, access_token)
                    # r8 = requests.post(
                    #             f"https://exdion-h.studio/api/Jobs/UpdateJobEhrPostStatus?clientID={clientd}&jobID={jobi}&IsSuccessful=false",
                    #             headers={"Authorization": f"Bearer {access_token}"})
                    #             # print(f"Invalid contract type: {con_type}")
                    logger.info(f"Invalid contract type:{clientd}, {jobi}, {patient},{endate}, {faci}, {visty}, {visnum}, {provider_name}, {yeprec}, {accnumber}, {POS_1}, {Place_of_service},{con_type}")          
                    continue
            continue
        driver.close()
        kill_chromedriver()
        print("BOT Action completed ")             
    except:
        print("bot failed") 
        update_job_status(clientd, jobi, access_token)
        from datetime import datetime
        send_screenshot_email(f"Update bot-1 failed Visit_ID : {visnum}",visnum,datetime.strptime(endate, "%d/%m/%Y").strftime("%d/%m/%Y"),driver)
        logger.info(f"Failed to update: {clientd}, {jobi}, {patient},{endate}, {faci}, {visty}, {visnum}, {provider_name}, {yeprec}, {accnumber}, {POS_1}, {Place_of_service},{con_type}")
        # continue
        #     # time.sleep(3)




























main function
from datetime import datetime, timedelta, timezone
import pytz
import requests
import os
import shutil
import tempfile
import json
import time

# Clear temporary folder function
def clear_temp_folder():
    temp_dir = tempfile.gettempdir()
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
            except PermissionError:
                print(f"Skipped (in use): {file_path}")
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")

        for dir in dirs:
            dir_path = os.path.join(root, dir)
            try:
                shutil.rmtree(dir_path)
            except PermissionError:
                print(f"Skipped (in use): {dir_path}")
            except Exception as e:
                print(f"Error deleting folder {dir_path}: {e}")

clear_temp_folder()

# Load facilities from JSON file
CONFIG_FILE = r"C:\Users\Bot_1\Documents\BOT_Facilities.JSON"

def load_facilities():
    try:
        with open(CONFIG_FILE, "r") as file:
            config = json.load(file)
            return config.get("faci", [])
    except FileNotFoundError:
        print(f"Configuration file '{CONFIG_FILE}' not found.")
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return []

facilities = load_facilities()
print("Facilities:", facilities)




from datetime import datetime, timedelta, timezone

def cst_to_ist_with_yesterday_and_today():
    # Get the current UTC time and convert to CST
    utc_now = datetime.now(timezone.utc)
    cst_time = utc_now - timedelta(hours=6)  # CST is UTC-6

    # Calculate yesterday and today in CST
    yesterday_cst = cst_time - timedelta(days=1)
    today_cst = cst_time

    # Convert CST dates to IST
    yesterday_ist = yesterday_cst + timedelta(hours=11, minutes=30)
    today_ist = today_cst + timedelta(hours=11, minutes=30)

    # Return the dates as a list
    return [yesterday_ist.strftime('%Y-%m-%d'), today_ist.strftime('%Y-%m-%d')]


# Convert CST to IST and include Sunday and Monday
# def cst_to_ist_with_sunday():
#     utc_now = datetime.now(timezone.utc)
#     cst_time = utc_now - timedelta(hours=6)

#     if cst_time.weekday() == 0:  # Monday
#         sunday_cst = cst_time - timedelta(days=1)
#         sunday_ist = sunday_cst + timedelta(hours=11, minutes=30)
#         monday_ist = cst_time + timedelta(hours=11, minutes=30)
#         return sunday_ist.strftime('%Y-%m-%d'), monday_ist.strftime('%Y-%m-%d')
#     else:
#         ist_time = cst_time + timedelta(hours=11, minutes=30)
#         return ist_time.strftime("%Y-%m-%d"), None

# Convert UTC timestamp to IST
def convert_utc_to_ist(utc_str):
    utc_time = datetime.strptime(utc_str, "%Y-%m-%dT%H:%M:%S")
    ist_time = utc_time + timedelta(hours=5, minutes=30)
    return ist_time.strftime("%Y-%m-%d")

# Fetch jobs from API
def fetch_jobs(username, password):
    headers = {"accept": "*/*", "Content-Type": "application/json"}
    try:
        response = requests.post("https://www.exdion-h.studio/api/Login/SignIn", headers=headers, json={'username': username, 'password': password})
        response.raise_for_status()
        data = response.json()
        access_token = data['accessToken']
    except requests.exceptions.RequestException as e:
        print(f"Login request failed: {e}")
        return None

    try:
        r4 = requests.get("https://exdion-h.studio/api/Query/GetJobs?status=job%20ready", headers={"Authorization": f"Bearer {access_token}"})
        r4.raise_for_status()
        return r4.json()
    except requests.exceptions.RequestException as e:
        print(f"Get jobs request failed: {e}")
        return None

# Process jobs function
def process_jobs(ready, created_dates, facilities):
    jobs_found = False

    if ready is None:
        print("No jobs available or an error occurred.")
        return jobs_found
    
    for rdp in ready:
        created_date_ist = convert_utc_to_ist(rdp["createdOn"][:19])

        if created_date_ist in created_dates and rdp["appointmentFacility"] in facilities:
            jobs_found = True
            con_type = rdp["contractType"]
            stp1 = rdp["stp"]
            if con_type in ["NGC", "GC", "RHC-MCO"] and stp1 == "STP":
                print("Valid contract type:", created_date_ist, rdp["appointmentFacility"], rdp["visitNumber"], con_type)
            else:
                print("Invalid contract type:", created_date_ist, rdp["appointmentFacility"], rdp["visitNumber"], con_type, stp1)
    
    return jobs_found

# Main execution loop
username = 'api_user@exdionace.ai'
password = r'&D/]\R[n+A)}^#%' 

while True:
    try:
        Created_date_1 = cst_to_ist_with_yesterday_and_today()
        print("Created Dates:", Created_date_1)

        ready_jobs = fetch_jobs(username, password)
        if ready_jobs is not None:
            jobs_found = process_jobs(ready_jobs, Created_date_1, facilities)

            if jobs_found:
                print("Jobs found. Executing main code.")
                main_code(Created_date_1)  # Pass tuple with Sunday and Monday IST
            else:
                print("No valid jobs found.")
        else:
            print("No jobs retrieved. Retrying...")
    except Exception as e:
        print(f"Error occurred: {e}. Retrying...")
    time.sleep(30)

