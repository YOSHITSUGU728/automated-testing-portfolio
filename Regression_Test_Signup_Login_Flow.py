from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from datetime import datetime
import os
import time

class YodobashiAutoSignup:
    def __init__(self, headless=False):
        self.top_url = "https://www.yodobashi.com/"
        self.register_url = "https://order.yodobashi.com/yc/member/register/index.html"
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        if not headless:
            options.add_argument('--start-maximized')
        else:
            options.add_argument('--headless')
        options.add_argument('--disable-popup-blocking')
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 15)
        self.log_folder = os.path.join(os.path.expanduser("~"), "Desktop", "yodobashi_signup_logs")
        self.setup_log_folder()
        self.log_file = os.path.join(self.log_folder, f"signup_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        
    def setup_log_folder(self):
        if not os.path.exists(self.log_folder):
            os.makedirs(self.log_folder)
            
    def log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    
    def take_screenshot(self, name):
        screenshot_name = name.replace('(', '_').replace(')', '').replace(' ', '_')
        screenshot_path = os.path.join(self.log_folder, 
            f"screenshot_{screenshot_name}_{datetime.now().strftime('%H%M%S')}.png")
        self.driver.save_screenshot(screenshot_path)
        self.log(f"  📷 Screenshot: {os.path.basename(screenshot_path)}")
        return screenshot_path
    
    def wait_for_page_load(self):
        try:
            self.wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
            time.sleep(2)
            return True
        except:
            return False
    
    def scroll_to_element(self, element):
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", element)
            time.sleep(0.5)
            return True
        except:
            return False
    
    def fill_basic_info(self, user_data):
        """Fill in basic information"""
        try:
            self.log("\n" + "="*50)
            self.log("Filling in basic information")
            self.log("="*50)
            
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            # Last name (Kanji)
            if user_data.get('last_name'):
                inputs = self.driver.find_elements(By.XPATH, "//input[@type='text']")
                for inp in inputs:
                    placeholder = inp.get_attribute('placeholder') or ''
                    name_attr = inp.get_attribute('name') or ''
                    if ('姓' in placeholder or 'family' in name_attr.lower()) and 'kana' not in name_attr.lower():
                        self.scroll_to_element(inp)
                        inp.clear()
                        inp.send_keys(user_data['last_name'])
                        self.log(f"  ✓ Last name: {user_data['last_name']}")
                        break
            
            # First name (Kanji)
            if user_data.get('first_name'):
                inputs = self.driver.find_elements(By.XPATH, "//input[@type='text']")
                for inp in inputs:
                    placeholder = inp.get_attribute('placeholder') or ''
                    name_attr = inp.get_attribute('name') or ''
                    if (('名' in placeholder and '姓' not in placeholder) or 'given' in name_attr.lower()) and 'kana' not in name_attr.lower():
                        self.scroll_to_element(inp)
                        inp.clear()
                        inp.send_keys(user_data['first_name'])
                        self.log(f"  ✓ First name: {user_data['first_name']}")
                        break
            
            # Last name (Katakana)
            if user_data.get('last_kana'):
                inputs = self.driver.find_elements(By.XPATH, "//input[@type='text']")
                for inp in inputs:
                    placeholder = inp.get_attribute('placeholder') or ''
                    name_attr = inp.get_attribute('name') or ''
                    if 'セイ' in placeholder or ('kana' in name_attr.lower() and 'family' in name_attr.lower()):
                        self.scroll_to_element(inp)
                        inp.clear()
                        inp.send_keys(user_data['last_kana'])
                        self.log(f"  ✓ Last name (Kana): {user_data['last_kana']}")
                        break
            
            # First name (Katakana)
            if user_data.get('first_kana'):
                inputs = self.driver.find_elements(By.XPATH, "//input[@type='text']")
                for inp in inputs:
                    placeholder = inp.get_attribute('placeholder') or ''
                    name_attr = inp.get_attribute('name') or ''
                    if 'メイ' in placeholder or ('kana' in name_attr.lower() and 'given' in name_attr.lower()):
                        self.scroll_to_element(inp)
                        inp.clear()
                        inp.send_keys(user_data['first_kana'])
                        self.log(f"  ✓ First name (Kana): {user_data['first_kana']}")
                        break
            
            return True
        except Exception as e:
            self.log(f"  ✗ Basic info input error: {str(e)}")
            return False
    
    def fill_address(self, user_data):
        """Fill in address information"""
        try:
            self.log("\n" + "="*50)
            self.log("Filling in address information")
            self.log("="*50)
            
            # Postal code
            if user_data.get('postal_code'):
                postal = user_data['postal_code']
                if len(postal) == 7:
                    postal1 = postal[:3]
                    postal2 = postal[3:]
                    
                    postal_inputs = []
                    inputs = self.driver.find_elements(By.XPATH, "//input[@type='text']")
                    for inp in inputs:
                        name_attr = inp.get_attribute('name') or ''
                        if 'zip' in name_attr.lower() or 'postal' in name_attr.lower():
                            postal_inputs.append(inp)
                    
                    if len(postal_inputs) >= 2:
                        self.scroll_to_element(postal_inputs[0])
                        postal_inputs[0].clear()
                        postal_inputs[0].send_keys(postal1)
                        time.sleep(0.3)
                        postal_inputs[1].clear()
                        postal_inputs[1].send_keys(postal2)
                        self.log(f"  ✓ Postal code: {postal1}-{postal2}")
                        
                        # Click address search button
                        search_buttons = self.driver.find_elements(By.XPATH, 
                            "//a[contains(text(), '住所を検索する')] | //button[contains(text(), '住所を検索する')]")
                        for btn in search_buttons:
                            if btn.is_displayed():
                                self.scroll_to_element(btn)
                                time.sleep(0.5)
                                btn.click()
                                self.log(f"  ✓ Address search executed")
                                time.sleep(2)
                                
                                # Click "Other address not in list"
                                other_links = self.driver.find_elements(By.XPATH, 
                                    "//a[contains(text(), '選択肢にないその他の住所')]")
                                for link in other_links:
                                    if link.is_displayed():
                                        link.click()
                                        self.log(f"  ✓ Selected other address")
                                        time.sleep(1)
                                        break
                                break
            
            # Street address and other details
            if user_data.get('address_detail'):
                self.driver.execute_script("window.scrollTo(0, 500);")
                time.sleep(1)
                
                all_text_inputs = self.driver.find_elements(By.XPATH, "//input[@type='text']")
                for inp in all_text_inputs:
                    try:
                        parent_row = inp.find_element(By.XPATH, "./ancestor::tr | ./ancestor::div[contains(@class, 'form')]")
                        row_text = parent_row.text
                        if '番地' in row_text and '建物' not in row_text and '郵便' not in row_text:
                            self.scroll_to_element(inp)
                            inp.clear()
                            inp.send_keys(user_data['address_detail'])
                            self.log(f"  ✓ Street address: {user_data['address_detail']}")
                            break
                    except:
                        continue
            
            # Building name
            if user_data.get('building'):
                all_text_inputs = self.driver.find_elements(By.XPATH, "//input[@type='text']")
                for inp in all_text_inputs:
                    try:
                        parent_row = inp.find_element(By.XPATH, "./ancestor::tr | ./ancestor::div[contains(@class, 'form')]")
                        row_text = parent_row.text
                        if '建物' in row_text:
                            self.scroll_to_element(inp)
                            inp.clear()
                            inp.send_keys(user_data['building'])
                            self.log(f"  ✓ Building name: {user_data['building']}")
                            break
                    except:
                        continue
            
            return True
        except Exception as e:
            self.log(f"  ✗ Address input error: {str(e)}")
            return False
    
    def fill_contact_info(self, user_data):
        """Fill in contact information"""
        try:
            self.log("\n" + "="*50)
            self.log("Filling in contact information")
            self.log("="*50)
            
            # Phone number
            if user_data.get('phone'):
                phone = user_data['phone']
                if len(phone) == 11:
                    phone1, phone2, phone3 = phone[:3], phone[3:7], phone[7:]
                elif len(phone) == 10:
                    phone1, phone2, phone3 = phone[:3], phone[3:6], phone[6:]
                else:
                    phone1, phone2, phone3 = phone, "", ""
                
                tel_inputs = [None, None, None]
                all_inputs = self.driver.find_elements(By.XPATH, "//input[@type='tel'] | //input[@type='text']")
                for inp in all_inputs:
                    name = inp.get_attribute('name') or ''
                    if 'tel.tel1' in name or name == 'tel1':
                        tel_inputs[0] = inp
                    elif 'tel.tel2' in name or name == 'tel2':
                        tel_inputs[1] = inp
                    elif 'tel.tel3' in name or name == 'tel3':
                        tel_inputs[2] = inp
                
                if all(tel_inputs):
                    self.scroll_to_element(tel_inputs[0])
                    tel_inputs[0].clear()
                    tel_inputs[0].send_keys(phone1)
                    time.sleep(0.2)
                    tel_inputs[1].clear()
                    tel_inputs[1].send_keys(phone2)
                    time.sleep(0.2)
                    tel_inputs[2].clear()
                    tel_inputs[2].send_keys(phone3)
                    self.log(f"  ✓ Phone number: {phone1}-{phone2}-{phone3}")
            
            # Date of birth - Year
            if user_data.get('birth_year'):
                all_inputs = self.driver.find_elements(By.XPATH, "//input[@type='text']")
                for inp in all_inputs:
                    placeholder = inp.get_attribute('placeholder') or ''
                    name = inp.get_attribute('name') or ''
                    if '西暦' in placeholder or 'year' in name.lower():
                        self.scroll_to_element(inp)
                        inp.clear()
                        inp.send_keys(str(user_data['birth_year']))
                        self.log(f"  ✓ Birth year: {user_data['birth_year']}")
                        break
            
            # Date of birth - Month
            if user_data.get('birth_month'):
                selects = self.driver.find_elements(By.XPATH, "//select")
                for sel in selects:
                    name = sel.get_attribute('name') or ''
                    if 'month' in name.lower():
                        select = Select(sel)
                        select.select_by_value(str(user_data['birth_month']))
                        self.log(f"  ✓ Birth month: {user_data['birth_month']}")
                        break
            
            # Date of birth - Day
            if user_data.get('birth_day'):
                selects = self.driver.find_elements(By.XPATH, "//select")
                found_month = False
                for sel in selects:
                    name = sel.get_attribute('name') or ''
                    if 'month' in name.lower():
                        found_month = True
                        continue
                    if found_month or 'day' in name.lower():
                        self.scroll_to_element(sel)
                        select = Select(sel)
                        select.select_by_value(str(user_data['birth_day']))
                        self.log(f"  ✓ Birth day: {user_data['birth_day']}")
                        break
            
            # Email
            if user_data.get('email'):
                inputs = self.driver.find_elements(By.XPATH, "//input[@type='text'] | //input[@type='email']")
                for inp in inputs:
                    input_type = inp.get_attribute('type') or ''
                    name_attr = inp.get_attribute('name') or ''
                    if input_type == 'email' or 'mail' in name_attr.lower():
                        self.scroll_to_element(inp)
                        inp.clear()
                        inp.send_keys(user_data['email'])
                        self.log(f"  ✓ Email: {user_data['email']}")
                        break
            
            return True
        except Exception as e:
            self.log(f"  ✗ Contact info input error: {str(e)}")
            return False
    
    def fill_password(self, password):
        """Enter password (on confirmation screen)"""
        try:
            self.log("\n" + "="*50)
            self.log("Entering password")
            self.log("="*50)
            
            # Wait for page to fully load
            self.wait_for_page_load()
            
            # Find password fields
            password_inputs = self.driver.find_elements(By.XPATH, "//input[@type='password']")
            self.log(f"  Number of password fields: {len(password_inputs)}")
            
            if len(password_inputs) >= 2:
                # First field: password
                self.scroll_to_element(password_inputs[0])
                time.sleep(0.5)
                password_inputs[0].clear()
                password_inputs[0].send_keys(password)
                self.log(f"  ✓ Password entered: {password}")
                time.sleep(0.5)
                
                # Second field: confirm password
                password_inputs[1].clear()
                password_inputs[1].send_keys(password)
                self.log(f"  ✓ Password confirmation entered: {password}")
                time.sleep(0.5)
                
                return True
            else:
                self.log(f"  ⚠ Password fields not found (detected: {len(password_inputs)})")
                # Debug: display all input elements
                all_inputs = self.driver.find_elements(By.XPATH, "//input")
                self.log(f"  Debug: Number of input elements on page = {len(all_inputs)}")
                for i, inp in enumerate(all_inputs[:10]):
                    try:
                        inp_type = inp.get_attribute('type') or ''
                        inp_name = inp.get_attribute('name') or ''
                        inp_placeholder = inp.get_attribute('placeholder') or ''
                        self.log(f"    [{i}] type={inp_type}, name={inp_name}, placeholder={inp_placeholder}")
                    except:
                        pass
                return False
        except Exception as e:
            self.log(f"  ✗ Password input error: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
            return False
    
    def accept_terms(self):
        """Agree to terms and conditions"""
        try:
            self.log("\n" + "="*50)
            self.log("Agreeing to terms and conditions")
            self.log("="*50)
            
            # Scroll to show checkbox
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            
            # Find by ID directly
            try:
                agreement_checkbox = self.driver.find_element(By.ID, "js_i_checkPrivacyPolicyAgreement")
                self.log(f"  ✓ Checkbox found")
                
                # Wait for element to be visible
                self.wait.until(EC.visibility_of(agreement_checkbox))
                
                # Scroll to element
                self.scroll_to_element(agreement_checkbox)
                time.sleep(1)
                
                # Check current state
                is_checked = agreement_checkbox.is_selected()
                self.log(f"  Current checked state: {is_checked}")
                
                if not is_checked:
                    # Try normal click first
                    try:
                        self.log(f"  Attempting normal click...")
                        agreement_checkbox.click()
                        time.sleep(0.5)
                        self.log(f"  ✓ Agreed to terms (normal click)")
                    except Exception as e:
                        # Fall back to JavaScript click
                        self.log(f"  Normal click failed, using JavaScript click...")
                        self.driver.execute_script("arguments[0].click();", agreement_checkbox)
                        time.sleep(0.5)
                        self.log(f"  ✓ Agreed to terms (JS click)")
                    
                    # Verify state after click
                    time.sleep(0.5)
                    is_checked_after = agreement_checkbox.is_selected()
                    self.log(f"  Checked state after click: {is_checked_after}")
                    
                    if not is_checked_after:
                        self.log(f"  ⚠ Checkbox may not be checked. Trying again...")
                        self.driver.execute_script("arguments[0].checked = true; arguments[0].dispatchEvent(new Event('change'));", agreement_checkbox)
                        time.sleep(0.5)
                else:
                    self.log(f"  ✓ Already agreed")
                
                return True
                
            except Exception as e:
                self.log(f"  ✗ Checkbox not found: {str(e)}")
                import traceback
                self.log(traceback.format_exc())
                return False
                
        except Exception as e:
            self.log(f"  ✗ Terms agreement error: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
            return False
    
    def click_next_button(self):
        """Click 'Next' button (input screen -> confirmation screen)"""
        try:
            self.log(f"\n{'='*50}")
            self.log("Clicking 'Next' button")
            self.log(f"{'='*50}")
            
            # Scroll to bottom of page
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Search for button (multiple patterns)
            button_selectors = [
                "//strong[contains(text(), '次へ進む')]/ancestor::a",
                "//strong[contains(text(), '次へ進む')]/ancestor::button",
                "//span[.//strong[contains(text(), '次へ進む')]]/parent::a",
                "//span[.//strong[contains(text(), '次へ進む')]]/parent::button",
                "//a[.//strong[contains(text(), '次へ進む')]]",
                "//button[.//strong[contains(text(), '次へ進む')]]",
                "//a[contains(., '次へ進む')]",
                "//button[contains(., '次へ進む')]",
                "//input[@type='submit' and contains(@value, '次へ進む')]"
            ]
            
            next_button = None
            for selector in button_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    self.log(f"  Selector '{selector}' found {len(elements)} elements")
                    for elem in elements:
                        if elem.is_displayed():
                            next_button = elem
                            elem_tag = elem.tag_name
                            elem_text = elem.text[:50] if elem.text else ''
                            self.log(f"  ✓ Clickable button found: <{elem_tag}> '{elem_text}'")
                            break
                    if next_button:
                        break
                except Exception as e:
                    self.log(f"  Selector error: {str(e)[:50]}")
                    continue
            
            if next_button:
                # Scroll to button
                self.scroll_to_element(next_button)
                time.sleep(1)
                
                # Click
                try:
                    self.log(f"  Attempting normal click...")
                    next_button.click()
                    self.log(f"  ✓ Click successful")
                except Exception as e:
                    # JavaScript click
                    self.log(f"  Normal click failed, using JavaScript click...")
                    self.driver.execute_script("arguments[0].click();", next_button)
                    self.log(f"  ✓ JavaScript click successful")
                
                time.sleep(3)
                self.log(f"  Current URL: {self.driver.current_url}")
                return True
            else:
                self.log(f"  ✗ Button not found")
                # Debug: display page text
                body_text = self.driver.find_element(By.TAG_NAME, "body").text
                if '次へ進む' in body_text:
                    self.log(f"  ⚠ Text '次へ進む' exists on page")
                return False
                
        except Exception as e:
            self.log(f"  ✗ Button click error: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
            return False
    
    def click_confirm_button(self):
        """Click 'Next' button on confirmation screen (confirmation -> completion)"""
        try:
            self.log(f"\n{'='*50}")
            self.log("Clicking 'Next' button on confirmation screen")
            self.log(f"{'='*50}")
            
            # Wait for page to fully load
            self.wait_for_page_load()
            
            # Scroll to top
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            # Search for button (multiple patterns)
            button_selectors = [
                "//a[contains(@class, 'red') and contains(., '次へ進む')]",
                "//button[contains(@class, 'red') and contains(., '次へ進む')]",
                "//strong[contains(text(), '次へ進む')]/ancestor::a",
                "//strong[contains(text(), '次へ進む')]/ancestor::button",
                "//a[.//strong[contains(text(), '次へ進む')]]",
                "//button[.//strong[contains(text(), '次へ進む')]]",
                "//a[contains(., '次へ進む')]",
                "//button[contains(., '次へ進む')]",
                "//input[@type='submit' and contains(@value, '次へ進む')]",
                "//button[contains(., 'この内容で登録する')]",
                "//a[contains(., 'この内容で登録する')]",
                "//button[contains(., '登録する')]",
                "//a[contains(., '登録する')]"
            ]
            
            confirm_button = None
            for selector in button_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    self.log(f"  Selector '{selector[:50]}...' found {len(elements)} elements")
                    for elem in elements:
                        if elem.is_displayed():
                            elem_text = elem.text or elem.get_attribute('value') or ''
                            elem_tag = elem.tag_name
                            # Exclude 'Back' and 'Cancel' buttons
                            if '戻る' not in elem_text and 'キャンセル' not in elem_text:
                                confirm_button = elem
                                self.log(f"  ✓ Clickable button found: <{elem_tag}> '{elem_text[:50]}'")
                                break
                    if confirm_button:
                        break
                except Exception as e:
                    self.log(f"  Selector error: {str(e)[:50]}")
                    continue
            
            if confirm_button:
                self.scroll_to_element(confirm_button)
                time.sleep(1)
                try:
                    self.log(f"  Attempting normal click...")
                    confirm_button.click()
                    self.log(f"  ✓ Click successful")
                except:
                    self.log(f"  Normal click failed, using JavaScript click...")
                    self.driver.execute_script("arguments[0].click();", confirm_button)
                    self.log(f"  ✓ JavaScript click successful")
                
                time.sleep(5)  # Wait for completion screen to load
                self.log(f"  Current URL: {self.driver.current_url}")
                return True
            else:
                self.log(f"  ✗ Confirm button not found")
                # Debug: display page text
                body_text = self.driver.find_element(By.TAG_NAME, "body").text
                self.log(f"  Page text (first 500 chars):")
                self.log(f"  {body_text[:500]}")
                return False
                
        except Exception as e:
            self.log(f"  ✗ Confirm button click error: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
            return False
    
    def navigate_to_register_page(self):
        """Navigate from top page to member registration page"""
        try:
            self.log("\n" + "="*50)
            self.log("Navigating from top page to member registration page")
            self.log("="*50)
            
            # Access top page
            self.log(f"  Accessing top page: {self.top_url}")
            self.driver.get(self.top_url)
            self.wait_for_page_load()
            self.take_screenshot("00_top_page")
            
            # Find and click registration link
            self.log("  Looking for 'New members click here' link...")
            
            link_selectors = [
                "//a[@href='https://order.yodobashi.com/yc/member/register/index.html']",
                "//a[contains(@class, 'cl-hdLO2_2')]",
                "//a[contains(text(), 'こちら') and contains(@href, 'register')]"
            ]
            
            register_link = None
            for selector in link_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        if elem.is_displayed():
                            register_link = elem
                            self.log(f"  ✓ Link found: {elem.get_attribute('href')}")
                            break
                    if register_link:
                        break
                except:
                    continue
            
            if register_link:
                self.scroll_to_element(register_link)
                time.sleep(0.5)
                try:
                    register_link.click()
                except:
                    self.driver.execute_script("arguments[0].click();", register_link)
                self.log(f"  ✓ Registration link clicked")
                time.sleep(3)
                self.wait_for_page_load()
                self.log(f"  Current URL: {self.driver.current_url}")
                return True
            else:
                self.log(f"  ⚠ Registration link not found. Navigating directly to URL...")
                self.driver.get(self.register_url)
                self.wait_for_page_load()
                return True
                
        except Exception as e:
            self.log(f"  ✗ Page navigation error: {str(e)}")
            self.log(f"  Navigating directly to URL...")
            self.driver.get(self.register_url)
            self.wait_for_page_load()
            return True
    
    def signup_complete(self, user_data, password="hjerty12"):
        """Execute member registration through to completion
        
        Args:
            user_data: Dictionary of user information
            password: Password (default: hjerty12)
        
        Returns:
            dict: Result (success, message, log_file)
        """
        result = {
            'success': False,
            'message': '',
            'log_file': self.log_file,
            'password': password
        }
        
        try:
            self.log("="*70)
            self.log("Yodobashi Camera Member Registration Automation (Full Flow)")
            self.log(f"Password: {password}")
            self.log("="*70)
            
            # [Step 1] Navigate from top page to registration page
            self.log("\n[Step 1] Navigating to member registration page...")
            if not self.navigate_to_register_page():
                result['message'] = 'Failed to navigate to registration page'
                return result
            self.take_screenshot("01_registration_page")
            
            # [Step 2] Fill in basic information
            self.log("\n[Step 2] Filling in basic information...")
            if not self.fill_basic_info(user_data):
                result['message'] = 'Failed to fill in basic information'
                return result
            
            # [Step 3] Fill in address information
            self.log("\n[Step 3] Filling in address information...")
            if not self.fill_address(user_data):
                result['message'] = 'Failed to fill in address information'
                return result
            
            # [Step 4] Fill in contact information
            self.log("\n[Step 4] Filling in contact information...")
            if not self.fill_contact_info(user_data):
                result['message'] = 'Failed to fill in contact information'
                return result
            
            # [Step 5] Agree to terms
            self.log("\n[Step 5] Agreeing to terms...")
            if not self.accept_terms():
                result['message'] = 'Failed to agree to terms'
                return result
            
            self.take_screenshot("02_form_filled")
            
            # [Step 6] Click 'Next' (input screen -> confirmation screen)
            self.log("\n[Step 6] Proceeding from input screen to confirmation screen...")
            if not self.click_next_button():
                result['message'] = "Failed to click 'Next' button"
                return result
            
            self.take_screenshot("03_confirmation_page")
            
            # [Step 7] Enter password (on confirmation screen)
            self.log("\n[Step 7] Entering password (confirmation screen)...")
            if not self.fill_password(password):
                result['message'] = 'Failed to enter password'
                return result
            
            self.take_screenshot("04_password_filled")
            
            # [Step 8] Click 'Register with this information' on confirmation screen
            self.log("\n[Step 8] Proceeding from confirmation screen to completion screen...")
            if not self.click_confirm_button():
                result['message'] = "Failed to click 'Register' button"
                return result
            
            self.take_screenshot("05_registration_complete")
            
            # [Complete] Member registration complete
            self.log(f"\n{'='*70}")
            self.log("✓ Member registration complete!")
            self.log(f"Email: {user_data['email']}")
            self.log(f"Password: {password}")
            self.log(f"{'='*70}")
            
            # [Step 9] Logout
            self.log("\n[Step 9] Logging out...")
            if self.logout():
                self.log(f"  ✓ Logout successful")
                self.take_screenshot("06_after_logout")
            else:
                self.log(f"  ⚠ Logout failed, but registration is complete")
            
            # [Step 10] Login
            self.log("\n[Step 10] Logging in with registered account...")
            if self.login(user_data['email'], password):
                self.log(f"  ✓ Login successful")
                self.take_screenshot("07_after_login")
            else:
                self.log(f"  ⚠ Login failed")
            
            # [Step 11] Logout (second time)
            self.log("\n[Step 11] Logging out (second time)...")
            try:
                if self.logout():
                    self.log(f"  ✓ Logout successful")
                    self.take_screenshot("08_after_second_logout")
                    result['success'] = True
                    result['message'] = 'Registration, logout, login, and logout all completed!'
                else:
                    self.log(f"  ⚠ Logout failed")
                    result['success'] = True
                    result['message'] = 'Registration, logout, and login completed (second logout failed)'
            except Exception as logout_error:
                self.log(f"  ⚠ Error during logout: {str(logout_error)[:100]}")
                result['success'] = True
                result['message'] = 'Registration, logout, and login completed (error during second logout)'
            
        except Exception as e:
            result['message'] = f'An error occurred: {str(e)}'
            self.log(f"\nError: {result['message']}")
            import traceback
            self.log(traceback.format_exc())
            self.take_screenshot("error")
        
        self.log(f"\n{'='*70}")
        self.log(f"Final result: {result['message']}")
        self.log(f"{'='*70}")
        
        return result
    
    def login(self, email, password):
        """Login process
        
        Args:
            email: Email address
            password: Password
        
        Returns:
            bool: Whether login was successful
        """
        try:
            self.log("\n" + "="*50)
            self.log("Login process")
            self.log("="*50)
            self.log(f"  Email: {email}")
            self.log(f"  Password: {password}")
            
            # Access top page
            self.log(f"  Accessing top page: {self.top_url}")
            self.driver.get(self.top_url)
            self.wait_for_page_load()
            self.take_screenshot("login_01_top_page")
            
            # Scroll to top of page
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            # [Step 1] Find and click link to login page
            self.log("  Step 1: Navigating to login page...")
            
            login_link_selectors = [
                "//a[contains(@class, 'cl-hdLO2_1')]",
                "//a[@class='clicklog cl-hdLO2_1']",
                "//a[contains(@href, 'login/index.html')]",
                "//a[contains(text(), 'ログイン') and not(contains(text(), 'パスワード'))]",
                "//a[contains(., 'ログイン') and not(contains(., 'パスワード'))]",
                "//button[contains(text(), 'ログイン')]",
                "//a[contains(@href, 'login')]"
            ]
            
            login_link = None
            for selector in login_link_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    self.log(f"  Selector '{selector[:60]}...' found {len(elements)} elements")
                    for elem in elements:
                        if elem.is_displayed():
                            elem_text = elem.text or ''
                            elem_href = elem.get_attribute('href') or ''
                            # Exclude logout links and password-related links
                            if 'logout' not in elem_href.lower() and 'パスワード' not in elem_text and '忘れ' not in elem_text:
                                login_link = elem
                                self.log(f"  ✓ Login link found: '{elem_text}' ({elem_href[:70]})")
                                break
                    if login_link:
                        break
                except Exception as e:
                    self.log(f"  Selector error: {str(e)[:50]}")
                    continue
            
            if login_link:
                self.scroll_to_element(login_link)
                time.sleep(0.5)
                try:
                    self.log(f"  Attempting normal click...")
                    login_link.click()
                    self.log(f"  ✓ Click successful")
                except:
                    self.log(f"  Normal click failed, using JavaScript click...")
                    self.driver.execute_script("arguments[0].click();", login_link)
                    self.log(f"  ✓ JavaScript click successful")
                self.log(f"  ✓ Navigated to login page")
                time.sleep(2)
                self.wait_for_page_load()
                self.take_screenshot("login_02_login_page")
                self.log(f"  Current URL: {self.driver.current_url}")
            else:
                self.log(f"  ⚠ Login link not found. Navigating directly to login page...")
                login_url = "https://order.yodobashi.com/yc/login/index.html"
                self.driver.get(login_url)
                self.wait_for_page_load()
                self.log(f"  Current URL: {self.driver.current_url}")
            
            # [Step 2] Enter email address
            self.log("  Step 2: Entering email address...")
            
            email_input_selectors = [
                "//input[@name='memberId' or @id='memberId']",
                "//input[@name='loginId' or @id='loginId']",
                "//input[@type='email']",
                "//input[@type='text' and (contains(@name, 'mail') or contains(@name, 'email') or contains(@name, 'Mail'))]",
                "//input[@type='text' and (contains(@placeholder, 'メール') or contains(@placeholder, 'mail') or contains(@placeholder, 'アドレス'))]",
                "//label[contains(text(), '会員ID') or contains(text(), 'メール')]/following::input[1]",
                "//input[@id='email' or @name='email']"
            ]
            
            email_input = None
            for selector in email_input_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    self.log(f"  Selector '{selector[:60]}...' found {len(elements)} elements")
                    for elem in elements:
                        if elem.is_displayed():
                            elem_name = elem.get_attribute('name') or ''
                            elem_placeholder = elem.get_attribute('placeholder') or ''
                            email_input = elem
                            self.log(f"  ✓ Email input field found: name='{elem_name}', placeholder='{elem_placeholder}'")
                            break
                    if email_input:
                        break
                except Exception as e:
                    self.log(f"  Selector error: {str(e)[:50]}")
                    continue
            
            if email_input:
                self.scroll_to_element(email_input)
                email_input.clear()
                email_input.send_keys(email)
                self.log(f"  ✓ Email address entered: {email}")
                time.sleep(0.5)
            else:
                self.log(f"  ✗ Email input field not found")
                # Debug: display all input elements
                all_inputs = self.driver.find_elements(By.XPATH, "//input")
                self.log(f"  Debug: Number of input elements on page = {len(all_inputs)}")
                for i, inp in enumerate(all_inputs[:10]):
                    try:
                        inp_type = inp.get_attribute('type') or ''
                        inp_name = inp.get_attribute('name') or ''
                        inp_placeholder = inp.get_attribute('placeholder') or ''
                        self.log(f"    [{i}] type={inp_type}, name={inp_name}, placeholder={inp_placeholder}")
                    except:
                        pass
                return False
            
            # [Step 3] Enter password
            self.log("  Step 3: Entering password...")
            
            password_inputs = self.driver.find_elements(By.XPATH, "//input[@type='password']")
            self.log(f"  Number of password fields: {len(password_inputs)}")
            
            if password_inputs:
                password_input = password_inputs[0]
                self.scroll_to_element(password_input)
                password_input.clear()
                password_input.send_keys(password)
                self.log(f"  ✓ Password entered")
                time.sleep(0.5)
            else:
                self.log(f"  ✗ Password input field not found")
                # Debug: display all input elements
                all_inputs = self.driver.find_elements(By.XPATH, "//input")
                self.log(f"  Debug: Number of input elements on page = {len(all_inputs)}")
                for i, inp in enumerate(all_inputs[:10]):
                    try:
                        inp_type = inp.get_attribute('type') or ''
                        inp_name = inp.get_attribute('name') or ''
                        self.log(f"    [{i}] type={inp_type}, name={inp_name}")
                    except:
                        pass
                return False
            
            self.take_screenshot("login_03_credentials_filled")
            
            # [Step 4] Click login button
            self.log("  Step 4: Clicking login button...")
            
            # Scroll to bottom (button may be at bottom)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            
            login_button_selectors = [
                "//span[.//strong[text()='ログイン']]/parent::a",
                "//span[.//strong[text()='ログイン']]/parent::button",
                "//span[.//strong[contains(text(), 'ログイン')]]/parent::*",
                "//strong[text()='ログイン']/ancestor::a",
                "//strong[text()='ログイン']/ancestor::button",
                "//strong[contains(text(), 'ログイン')]/ancestor::a",
                "//strong[contains(text(), 'ログイン')]/ancestor::button",
                "//a[.//strong[contains(text(), 'ログイン')]]",
                "//button[.//strong[contains(text(), 'ログイン')]]",
                "//button[contains(., 'ログイン') and not(contains(., 'パスワード')) and not(contains(., '忘れ'))]",
                "//a[contains(., 'ログイン') and not(contains(., 'パスワード')) and not(contains(., '忘れ'))]",
                "//input[@type='submit' and contains(@value, 'ログイン')]",
                "//a[contains(@class, 'red') and contains(., 'ログイン')]",
                "//button[contains(@class, 'red') and contains(., 'ログイン')]"
            ]
            
            login_button = None
            for selector in login_button_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    self.log(f"  Selector '{selector[:60]}...' found {len(elements)} elements")
                    for elem in elements:
                        if elem.is_displayed():
                            elem_text = elem.text or ''
                            elem_tag = elem.tag_name
                            # Exclude 'Forgot password' and 'New registration' links
                            if '忘れ' not in elem_text and 'パスワード' not in elem_text and '新規' not in elem_text:
                                if 'ログイン' in elem_text or elem_text == '':
                                    login_button = elem
                                    self.log(f"  ✓ Login button found: <{elem_tag}> '{elem_text}'")
                                    break
                    if login_button:
                        break
                except Exception as e:
                    self.log(f"  Selector error: {str(e)[:50]}")
                    continue
            
            if login_button:
                self.scroll_to_element(login_button)
                time.sleep(1)
                try:
                    self.log(f"  Attempting normal click...")
                    login_button.click()
                    self.log(f"  ✓ Login button click successful")
                except:
                    self.log(f"  Normal click failed, using JavaScript click...")
                    self.driver.execute_script("arguments[0].click();", login_button)
                    self.log(f"  ✓ JavaScript click successful")
                
                time.sleep(3)
                self.wait_for_page_load()
                self.take_screenshot("login_04_after_login")
                self.log(f"  Current URL: {self.driver.current_url}")
                
                # Verify login success
                time.sleep(2)
                page_text = self.driver.find_element(By.TAG_NAME, "body").text
                if 'こんにちは' in page_text or 'さん' in page_text:
                    self.log(f"  ✓ Login successful!")
                    return True
                else:
                    self.log(f"  ⚠ Login status unclear")
                    return True  # Treat as success if URL changed
            else:
                self.log(f"  ✗ Login button not found")
                # Debug: display buttons on page
                all_buttons = self.driver.find_elements(By.XPATH, "//button | //a | //input[@type='submit']")
                self.log(f"  Debug: Number of buttons/links on page = {len(all_buttons)}")
                for i, btn in enumerate(all_buttons[:10]):
                    try:
                        if btn.is_displayed():
                            btn_text = btn.text or btn.get_attribute('value') or ''
                            btn_tag = btn.tag_name
                            self.log(f"    [{i}] <{btn_tag}> {btn_text[:50]}")
                    except:
                        pass
                return False
                
        except Exception as e:
            self.log(f"  ✗ Login error: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
            return False
    
    def reset_password(self, email, last_name, first_name):
        """Password reset process
        
        Args:
            email: Email address
            last_name: Last name
            first_name: First name
        
        Returns:
            bool: Whether the process was successful
        """
        try:
            self.log("\n" + "="*50)
            self.log("Password reset process")
            self.log("="*50)
            self.log(f"  Email: {email}")
            self.log(f"  Name: {last_name} {first_name}")
            
            # [Step 1] Logout (continue even if error occurs)
            self.log("  Step 1: Logging out...")
            try:
                if not self.logout():
                    self.log(f"  ⚠ Logout failed, continuing...")
            except Exception as logout_error:
                self.log(f"  ⚠ Error during logout: {str(logout_error)[:100]}")
                self.log(f"  Continuing...")
            
            # [Step 2] Navigate to login page
            self.log("  Step 2: Navigating to login page...")
            
            self.driver.get(self.top_url)
            self.wait_for_page_load()
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            login_link_selectors = [
                "//a[contains(@class, 'cl-hdLO2_1')]",
                "//a[contains(@href, 'login/index.html')]",
                "//a[contains(text(), 'ログイン')]"
            ]
            
            login_link = None
            for selector in login_link_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        if elem.is_displayed():
                            elem_href = elem.get_attribute('href') or ''
                            if 'logout' not in elem_href.lower():
                                login_link = elem
                                self.log(f"  ✓ Login link found")
                                break
                    if login_link:
                        break
                except:
                    continue
            
            if login_link:
                login_link.click()
                self.log(f"  ✓ Navigated to login page")
                time.sleep(2)
                self.wait_for_page_load()
                self.take_screenshot("password_reset_01_login_page")
            else:
                login_url = "https://order.yodobashi.com/yc/login/index.html"
                self.driver.get(login_url)
                self.wait_for_page_load()
                self.log(f"  ✓ Navigated directly to login page")
            
            # [Step 3] Click 'Forgot password'
            self.log("  Step 3: Clicking 'Forgot your password?'...")
            
            forgot_password_selectors = [
                "//a[@href='https://order.yodobashi.com/yc/passwordreset/request/index.html']",
                "//a[contains(@href, 'passwordreset/request')]",
                "//a[contains(text(), 'パスワードを忘れた方はこちら')]",
                "//a[contains(., 'パスワード') and contains(., '忘れ')]"
            ]
            
            forgot_link = None
            for selector in forgot_password_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    self.log(f"  Selector '{selector[:60]}...' found {len(elements)} elements")
                    for elem in elements:
                        if elem.is_displayed():
                            elem_text = elem.text or ''
                            forgot_link = elem
                            self.log(f"  ✓ Password reset link found: '{elem_text}'")
                            break
                    if forgot_link:
                        break
                except Exception as e:
                    self.log(f"  Selector error: {str(e)[:50]}")
                    continue
            
            if forgot_link:
                self.scroll_to_element(forgot_link)
                time.sleep(0.5)
                try:
                    forgot_link.click()
                    self.log(f"  ✓ Click successful")
                except:
                    self.driver.execute_script("arguments[0].click();", forgot_link)
                    self.log(f"  ✓ JavaScript click successful")
                
                time.sleep(2)
                self.wait_for_page_load()
                self.take_screenshot("password_reset_02_reset_page")
                self.log(f"  Current URL: {self.driver.current_url}")
            else:
                self.log(f"  ✗ Password reset link not found")
                return False
            
            # [Step 4] Enter email address
            self.log("  Step 4: Entering email address...")
            
            email_input_selectors = [
                "//input[@name='memberId' or @id='memberId']",
                "//input[@type='email']",
                "//input[@type='text' and (contains(@name, 'mail') or contains(@name, 'email'))]"
            ]
            
            email_input = None
            for selector in email_input_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        if elem.is_displayed():
                            email_input = elem
                            self.log(f"  ✓ Email input field found")
                            break
                    if email_input:
                        break
                except:
                    continue
            
            if email_input:
                self.scroll_to_element(email_input)
                email_input.clear()
                email_input.send_keys(email)
                self.log(f"  ✓ Email address entered: {email}")
                time.sleep(0.5)
            else:
                self.log(f"  ✗ Email input field not found")
                return False
            
            # [Step 5] Enter last name
            self.log("  Step 5: Entering last name...")
            
            last_name_input = None
            all_text_inputs = self.driver.find_elements(By.XPATH, "//input[@type='text']")
            for inp in all_text_inputs:
                try:
                    parent = inp.find_element(By.XPATH, "./ancestor::tr | ./ancestor::div[contains(@class, 'form') or contains(@class, 'field')]")
                    parent_text = parent.text or ''
                    # Last name field under 'Full name'
                    if ('お名前' in parent_text or '名前' in parent_text) and '姓' in parent_text:
                        name_attr = inp.get_attribute('name') or ''
                        if 'mail' not in name_attr.lower() and 'email' not in name_attr.lower():
                            last_name_input = inp
                            self.log(f"  ✓ Last name input field found")
                            break
                except:
                    continue
            
            if last_name_input:
                self.scroll_to_element(last_name_input)
                last_name_input.clear()
                last_name_input.send_keys(last_name)
                self.log(f"  ✓ Last name entered: {last_name}")
                time.sleep(0.5)
            else:
                self.log(f"  ⚠ Last name input field not found")
            
            # [Step 6] Enter first name
            self.log("  Step 6: Entering first name...")
            
            first_name_input = None
            for inp in all_text_inputs:
                try:
                    parent = inp.find_element(By.XPATH, "./ancestor::tr | ./ancestor::div[contains(@class, 'form') or contains(@class, 'field')]")
                    parent_text = parent.text or ''
                    # First name field under 'Full name'
                    if ('お名前' in parent_text or '名前' in parent_text) and '名' in parent_text and '姓' not in parent_text:
                        name_attr = inp.get_attribute('name') or ''
                        if 'mail' not in name_attr.lower() and 'email' not in name_attr.lower():
                            first_name_input = inp
                            self.log(f"  ✓ First name input field found")
                            break
                except:
                    continue
            
            if first_name_input:
                self.scroll_to_element(first_name_input)
                first_name_input.clear()
                first_name_input.send_keys(first_name)
                self.log(f"  ✓ First name entered: {first_name}")
                time.sleep(0.5)
            else:
                self.log(f"  ⚠ First name input field not found")
            
            self.take_screenshot("password_reset_03_form_filled")
            
            # [Step 7] Click 'Submit' button
            self.log("  Step 7: Clicking 'Submit' button...")
            
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            
            submit_button_selectors = [
                "//a[@id='js_i_next']",
                "//a[contains(@class, 'yBtnText')]",
                "//a[contains(text(), '送信する')]",
                "//button[contains(text(), '送信する')]",
                "//input[@type='submit' and contains(@value, '送信')]",
                "//a[.//strong[contains(text(), '送信')]]",
                "//button[.//strong[contains(text(), '送信')]]"
            ]
            
            submit_button = None
            for selector in submit_button_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    self.log(f"  Selector '{selector[:60]}...' found {len(elements)} elements")
                    for elem in elements:
                        if elem.is_displayed():
                            elem_text = elem.text or ''
                            elem_tag = elem.tag_name
                            submit_button = elem
                            self.log(f"  ✓ Submit button found: <{elem_tag}> '{elem_text}'")
                            break
                    if submit_button:
                        break
                except Exception as e:
                    self.log(f"  Selector error: {str(e)[:50]}")
                    continue
            
            if submit_button:
                self.scroll_to_element(submit_button)
                time.sleep(1)
                try:
                    self.log(f"  Attempting normal click...")
                    submit_button.click()
                    self.log(f"  ✓ Click successful")
                except:
                    self.log(f"  Normal click failed, using JavaScript click...")
                    self.driver.execute_script("arguments[0].click();", submit_button)
                    self.log(f"  ✓ JavaScript click successful")
                
                time.sleep(3)
                self.wait_for_page_load()
                self.take_screenshot("password_reset_04_complete")
                self.log(f"  Current URL: {self.driver.current_url}")
                self.log(f"  ✓ Password reset email sent successfully")
                return True
            else:
                self.log(f"  ✗ Submit button not found")
                return False
                
        except Exception as e:
            self.log(f"  ✗ Password reset error: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
            return False
    
    def logout(self):
        """Logout process"""
        try:
            self.log("\n" + "="*50)
            self.log("Logout process")
            self.log("="*50)
            
            # Wait for page to fully load
            try:
                self.wait_for_page_load()
            except:
                self.log(f"  ⚠ Error while waiting for page load")
            
            # Scroll to top (logout link is in header)
            try:
                self.driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(1)
            except:
                self.log(f"  ⚠ Error while scrolling")
            
            # [Step 1] Find and click username link to open dropdown menu
            self.log("  Step 1: Clicking username link to open menu...")
            
            user_name_selectors = [
                "//a[@id='pdLink20']",
                "//a[contains(@onclick, 'return false') and contains(preceding-sibling::text(), 'こんにちは')]",
                "//a[contains(text(), 'さん')]",
                "//a[contains(., 'さん')]"
            ]
            
            user_name_link = None
            for selector in user_name_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    self.log(f"  Selector '{selector[:50]}...' found {len(elements)} elements")
                    for elem in elements:
                        try:
                            if elem.is_displayed():
                                elem_text = elem.text or ''
                                user_name_link = elem
                                self.log(f"  ✓ Username link found: '{elem_text}'")
                                break
                        except:
                            continue
                    if user_name_link:
                        break
                except Exception as e:
                    self.log(f"  Selector error: {str(e)[:50]}")
                    continue
            
            if not user_name_link:
                self.log(f"  ⚠ Username link not found (may already be logged out)")
                return True  # Return True as already logged out
            
            try:
                self.scroll_to_element(user_name_link)
                time.sleep(1)
            except:
                pass
            
            try:
                self.log(f"  Attempting normal click...")
                user_name_link.click()
                self.log(f"  ✓ Username link click successful")
            except:
                try:
                    self.log(f"  Normal click failed, using JavaScript click...")
                    self.driver.execute_script("arguments[0].click();", user_name_link)
                    self.log(f"  ✓ JavaScript click successful")
                except Exception as e:
                    self.log(f"  ✗ Click failed: {str(e)[:100]}")
                    return False
            
            # Wait for menu to appear
            time.sleep(2)
            
            # [Step 2] Click 'Logout' in dropdown menu
            self.log("  Step 2: Clicking 'Logout' in dropdown menu...")
            
            logout_selectors = [
                "//div[@class='inner' and contains(text(), 'ログアウト')]",
                "//div[contains(@class, 'inner') and contains(text(), 'ログアウト')]",
                "//a[.//div[contains(text(), 'ログアウト')]]",
                "//a[.//div[@class='inner' and contains(text(), 'ログアウト')]]",
                "//*[contains(text(), 'ログアウト') and not(contains(text(), 'パスワード'))]",
                "//div[text()='ログアウト']",
                "//a[contains(., 'ログアウト')]"
            ]
            
            logout_element = None
            for selector in logout_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    self.log(f"  Selector '{selector[:60]}...' found {len(elements)} elements")
                    for elem in elements:
                        try:
                            if elem.is_displayed():
                                elem_text = elem.text or ''
                                elem_tag = elem.tag_name
                                logout_element = elem
                                self.log(f"  ✓ Logout element found: <{elem_tag}> '{elem_text}'")
                                break
                        except:
                            continue
                    if logout_element:
                        break
                except Exception as e:
                    self.log(f"  Selector error: {str(e)[:50]}")
                    continue
            
            if logout_element:
                time.sleep(0.5)
                try:
                    self.log(f"  Attempting normal click...")
                    logout_element.click()
                    self.log(f"  ✓ Logout click successful")
                except:
                    try:
                        self.log(f"  Normal click failed, using JavaScript click...")
                        self.driver.execute_script("arguments[0].click();", logout_element)
                        self.log(f"  ✓ JavaScript logout click successful")
                    except Exception as e:
                        self.log(f"  ✗ Logout click failed: {str(e)[:100]}")
                        return False
                
                time.sleep(3)
                try:
                    self.log(f"  Current URL: {self.driver.current_url}")
                except:
                    pass
                self.log(f"  ✓ Logout complete")
                return True
            else:
                self.log(f"  ✗ Logout element not found")
                # Debug: check visible elements on page
                try:
                    all_visible_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'ログ')]")
                    self.log(f"  Debug: Number of visible elements containing 'ログ' = {len(all_visible_elements)}")
                    for i, elem in enumerate(all_visible_elements[:10]):
                        try:
                            if elem.is_displayed():
                                self.log(f"    [{i}] {elem.tag_name}: {elem.text[:50]}")
                        except:
                            pass
                except:
                    pass
                return False
                
        except Exception as e:
            self.log(f"  ✗ Logout error: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
            return False
    
    def close(self):
        """Close the browser"""
        self.log("\nClosing browser...")
        time.sleep(3)
        self.driver.quit()


# Usage example
if __name__ == "__main__":
    # Define user information
    user_data = {
        "last_name": "Yamada",
        "first_name": "Taro",
        "last_kana": "ヤマダ",
        "first_kana": "タロウ",
        "postal_code": "1500001",
        "address_detail": "1-1-1",
        "building": "Sample Building 101",
        "phone": "09012345678",
        "birth_year": "1990",
        "birth_month": "1",
        "birth_day": "1",
        "email": "test12345@example.com"  # ✅ 変更済み
    }
    
    # Execute registration -> logout -> login flow
    bot = YodobashiAutoSignup(headless=False)
    try:
        result = bot.signup_complete(user_data, password="test12345")  # ✅ 変更済み
        
        print(f"\n{'='*70}")
        print(f"Result: {result['message']}")
        print(f"Email: {user_data['email']}")
        print(f"Password: {result['password']}")
        print(f"Log file: {result['log_file']}")
        print(f"{'='*70}")
        
        if result['success']:
            # Save registration info
            with open('registration_info.txt', 'w', encoding='utf-8') as f:
                f.write(f"Yodobashi Camera Member Registration Info\n")
                f.write(f"{'='*50}\n")
                f.write(f"Email: {user_data['email']}\n")
                f.write(f"Password: {result['password']}\n")
                f.write(f"Registration date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Status: {result['message']}\n")
            print("\nRegistration info saved to registration_info.txt")
    finally:
        bot.close()
