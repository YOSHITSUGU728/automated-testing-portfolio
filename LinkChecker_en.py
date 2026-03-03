import time
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
import requests
import csv

class LinkChecker:
    def __init__(self, base_url, output_dir=None):
        # Output to LinkChecker folder on Desktop
        if output_dir is None:
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            output_dir = os.path.join(desktop_path, "LinkChecker")
        self.base_url = base_url
        self.output_dir = output_dir
        self.setup_output_directory()
        self.setup_driver()
        self.error_links = []
        
    def setup_output_directory(self):
        """Create directory for saving results"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # Subdirectory for screenshots
        self.screenshot_dir = os.path.join(self.output_dir, "screenshots")
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)
    
    def setup_driver(self):
        """Configure Selenium WebDriver"""
        import sys
        import os
        import logging
        
        # Suppress Chrome logs via environment variables
        os.environ['WDM_LOG_LEVEL'] = '0'
        os.environ['WDM_PRINT_FIRST_LINE'] = 'False'
        
        # Suppress all warnings to Python stdout
        if not sys.warnoptions:
            import warnings
            warnings.simplefilter("ignore")
        
        # Completely suppress Chrome/Selenium related logs
        logging.getLogger('selenium').setLevel(logging.CRITICAL)
        logging.getLogger('urllib3').setLevel(logging.CRITICAL)
        logging.getLogger('webdriver_manager').setLevel(logging.CRITICAL)
        
        options = Options()
        
        # Additional options to suppress WebGL errors
        options.add_argument('--disable-webgl')
        options.add_argument('--disable-webgl2')
        options.add_argument('--disable-3d-apis')
        options.add_argument('--disable-accelerated-2d-canvas')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--disable-gpu-sandbox')
        options.add_argument('--disable-swiftshader')
        options.add_argument('--disable-vulkan')
        options.add_argument('--disable-canvas-aa')
        options.add_argument('--disable-2d-canvas-image-chromium')
        
        # Settings to avoid bot detection
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Avoid HTTP/2 related issues
        options.add_argument('--disable-http2')
        options.add_argument('--disable-features=VizDisplayCompositor')
        
        # Basic performance optimization options
        options.add_argument('--disable-background-networking')
        options.add_argument('--disable-sync')
        options.add_argument('--disable-translate')
        options.add_argument('--disable-default-apps')
        options.add_argument('--no-first-run')
        options.add_argument('--disable-ipc-flooding-protection')
        
        # Set log level to suppress error output (maximum suppression)
        options.add_argument('--log-level=3')
        options.add_argument('--silent')
        options.add_argument('--disable-logging')
        options.add_argument('--quiet')
        options.add_argument('--disable-dev-tools')
        options.add_argument('--disable-infobars')
        
        # Completely suppress Chrome stdout
        if os.name == 'nt':  # Windows
            options.add_argument('--disable-logging')
            options.add_argument('--log-level=3')
            # Redirect error output to nul on Windows
            options.add_argument('--enable-logging=stderr')
            os.environ['CHROME_LOG_FILE'] = 'nul'
        
        # Completely disable logging
        import logging
        logging.getLogger('selenium').setLevel(logging.CRITICAL)
        logging.getLogger('urllib3').setLevel(logging.CRITICAL)
        
        # Chrome service configuration (force headless)
        from selenium.webdriver.chrome.service import Service
        
        # Find ChromeDriver depending on environment
        try:
            service = Service()
        except:
            service = None
            
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.set_page_load_timeout(15)
        
        # Script to avoid WebDriver detection
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
    
    def get_all_links(self):
        """Get all links on the page"""
        try:
            print("  🌐 Accessing page...")
            self.driver.get(self.base_url)
            
            # Minimize wait time for performance
            print("  ⏳ Waiting for page to load...")
            time.sleep(2)  # Reduced from 5 seconds to 2 seconds
            
            # Handle cookie popup first
            print("  🍪 Processing initial cookies...")
            self.handle_cookie_popup()
            
            # Wait for JavaScript execution to complete (simplified)
            try:
                self.driver.execute_script("return document.readyState") == "complete"
                print("  ✅ Page load complete")
            except:
                print("  ⚠️ Failed to check page state (continuing)")
            
            # Reduce wait before getting link elements
            time.sleep(1)  # Reduced from 2 seconds to 1 second
            
            # Get all anchor tags
            print("  🔍 Searching for link elements...")
            link_elements = self.driver.find_elements(By.TAG_NAME, "a")
            print(f"  📊 Number of anchor tags found: {len(link_elements)}")
            
            # Debug: Check page state in more detail
            page_title = self.driver.title
            current_url = self.driver.current_url
            print(f"  📄 Page title: {page_title}")
            print(f"  🌐 Current URL: {current_url}")
            print(f"  📄 Page source size: {len(self.driver.page_source)} characters")
            
            # Debug: Check first few elements
            if len(link_elements) == 0:
                print("  🚨 No anchor tags found - checking other elements...")
                all_elements = self.driver.find_elements(By.XPATH, "//*")
                print(f"  📊 Total elements: {len(all_elements)}")
                
                # Check body content briefly
                try:
                    body = self.driver.find_element(By.TAG_NAME, "body")
                    body_text = body.text[:200] if body.text else "No text"
                    print(f"  📝 Body content sample: {body_text}")
                except:
                    print("  ⚠️ Failed to get body element")
            
            links_info = []
            valid_links = 0
            
            for i, element in enumerate(link_elements):
                try:
                    href = element.get_attribute("href")
                    if not href:
                        continue
                        
                    # Only target links starting with http
                    if not href.startswith('http'):
                        continue
                        
                    valid_links += 1
                    text = element.text.strip()
                    
                    # Save element info in advance (to handle Stale Element)
                    element_data = {}
                    try:
                        element_data = {
                            'location': element.location,
                            'size': element.size,
                            'rect': element.rect,
                            'tag_name': element.tag_name,
                            'classes': element.get_attribute("class") or "",
                            'id': element.get_attribute("id") or "",
                            'xpath': self.get_element_xpath(element)  # Add XPath
                        }
                    except:
                        element_data = {'location': {'x': 0, 'y': 0}, 'size': {'width': 0, 'height': 0}}
                    
                    # Check other attributes if no link text
                    if not text:
                        text = element.get_attribute("title") or \
                               element.get_attribute("alt") or \
                               element.get_attribute("aria-label")
                    
                    # Get additional details
                    additional_info = self.get_link_details(element)
                    
                    # Use detail info if text cannot be retrieved
                    if not text or text.strip() == "":
                        text = f"No text({additional_info})"
                    
                    links_info.append({
                        'url': href,
                        'text': text,
                        'element': element,
                        'details': additional_info,
                        'element_data': element_data
                    })
                    
                except Exception as e:
                    print(f"  ⚠️ Error processing link {i+1}: {str(e)[:50]}...")
                    continue
            
            print(f"  ✅ Valid links: {valid_links}")
            return links_info
            
        except Exception as e:
            print(f"Error getting links: {e}")
            print("  💡 There may be a problem accessing the site")
            return []
    
    def get_element_xpath(self, element):
        """Get XPath of element"""
        try:
            # Generate XPath using JavaScript
            xpath = self.driver.execute_script("""
                function getXPath(element) {
                    if (element.id !== '') {
                        return '//*[@id="' + element.id + '"]';
                    }
                    if (element === document.body) {
                        return '/html/body';
                    }
                    
                    var ix = 0;
                    var siblings = element.parentNode.childNodes;
                    for (var i = 0; i < siblings.length; i++) {
                        var sibling = siblings[i];
                        if (sibling === element) {
                            var tagName = element.tagName.toLowerCase();
                            return getXPath(element.parentNode) + '/' + tagName + '[' + (ix + 1) + ']';
                        }
                        if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                            ix++;
                        }
                    }
                }
                return getXPath(arguments[0]);
            """, element)
            return xpath
        except:
            return ""
    
    def get_link_details(self, element):
        """Get detailed information about a link element"""
        details = []
        
        try:
            # ID attribute
            element_id = element.get_attribute("id")
            if element_id:
                details.append(f"ID:{element_id}")
            
            # Class attribute
            class_name = element.get_attribute("class")
            if class_name:
                classes = class_name.split()[:2]  # Only first 2 classes
                details.append(f"Class:{' '.join(classes)}")
            
            # Parent element info
            try:
                parent = element.find_element(By.XPATH, "..")
                parent_tag = parent.tag_name
                parent_class = parent.get_attribute("class")
                if parent_class:
                    parent_classes = parent_class.split()[:1]  # Only first class
                    details.append(f"Parent:{parent_tag}.{parent_classes[0]}" if parent_classes else f"Parent:{parent_tag}")
                else:
                    details.append(f"Parent:{parent_tag}")
            except:
                pass
            
            # Check child elements (images, etc.)
            try:
                child_imgs = element.find_elements(By.TAG_NAME, "img")
                if child_imgs:
                    img_alt = child_imgs[0].get_attribute("alt") or "image"
                    details.append(f"Image:{img_alt}")
                
                child_spans = element.find_elements(By.TAG_NAME, "span")
                if child_spans and not child_imgs:  # Only if no images
                    span_text = child_spans[0].text.strip()
                    if span_text:
                        details.append(f"Span:{span_text[:10]}")
                    
                child_icons = element.find_elements(By.XPATH, ".//*[contains(@class, 'icon') or contains(@class, 'fa-')]")
                if child_icons:
                    details.append("Icon")
                    
            except:
                pass
                
            # Position info (rough location)
            try:
                location = element.location
                if location['y'] < 100:
                    details.append("Top")
                elif location['y'] > 500:
                    details.append("Bottom")
                else:
                    details.append("Middle")
            except:
                pass
                
            return " | ".join(details) if details else "Details unknown"
            
        except Exception as e:
            return "Retrieval error"
    
    def check_link_status(self, url):
        """Check HTTP status of a link"""
        try:
            # Set browser-like User-Agent and headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Try HEAD request first
            response = requests.head(url, timeout=8, allow_redirects=True, headers=headers)  # Reduced from 15s to 8s
            status_code = response.status_code
            
            # If HEAD returns 4xx error, also verify with GET (except 403)
            if 400 <= status_code < 500 and status_code not in [403, 404]:
                try:
                    response = requests.get(url, timeout=8, allow_redirects=True, headers=headers)  # Reduced from 15s to 8s
                    get_status = response.status_code
                    return get_status
                except:
                    return status_code
            
            return status_code
            
        except requests.exceptions.RequestException as e:
            print(f"    ⚠️ requests failed: {str(e)[:50]}...")
            try:
                # Verify directly with Selenium (more accurate)
                return self.check_with_selenium(url)
            except:
                return 0  # Inaccessible
    
    def check_with_selenium(self, url):
        """More accurate status check using Selenium"""
        try:
            print(f"    🔍 Verifying directly with Selenium...")
            
            # Save current URL
            original_url = self.driver.current_url
            
            # Access target URL
            self.driver.get(url)
            time.sleep(2)  # Reduced from 3s to 2s
            
            # Handle cookies
            self.handle_cookie_popup()
            
            # Final URL after redirects
            final_url = self.driver.current_url
            
            # Get page title and check if it's an error page
            page_title = self.driver.title.lower() if self.driver.title else ""
            
            # Get main page content (first 1000 chars only)
            try:
                # Get text from body element (more reliable)
                body_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()[:2000]
            except:
                body_text = self.driver.page_source.lower()[:2000]
            
            # Detect clear 404 error pages (stricter criteria)
            clear_error_indicators = [
                'page not found',
                'not found on this server',
                '404 error',
                'the requested url',
                'file not found',
            ]
            
            # Determine if it's a clear error page
            is_clear_error = any(indicator in page_title for indicator in clear_error_indicators) or \
                           any(indicator in body_text for indicator in clear_error_indicators)
            
            # Check for signs of a normal page
            normal_page_indicators = [
                'trading',
                'forex',
                'fx',
                'broker',
                'spread'
            ]
            
            has_normal_content = any(indicator in body_text for indicator in normal_page_indicators)
            
            # Judgment logic
            if is_clear_error:
                print(f"    ❌ Selenium: Clear error page detected")
                return 404
            elif has_normal_content and len(body_text) > 500:  # Sufficient content exists
                print(f"    ✅ Selenium: Normal page confirmed (rich content)")
                return 200
            elif len(body_text) < 100:  # Extremely little content
                print(f"    ⚠️ Selenium: Page with very little content")
                return 404
            else:
                print(f"    ✅ Selenium: Determined as normal page (default)")
                return 200
                
        except Exception as e:
            print(f"    ⚠️ Selenium check failed: {str(e)[:50]}...")
            return 200  # Treat as normal on error (safe side)
        finally:
            # Return to original page
            try:
                if original_url and original_url != url:
                    self.driver.get(original_url)
                    time.sleep(2)
            except:
                pass
    
    def take_screenshot(self, url, link_text, status_code, original_element=None):
        """Take screenshot of 404 page"""
        try:
            # Capture page before error (highlight link element)
            before_screenshot = None
            if original_element and status_code in [404, 500, 502, 503] or status_code == 0:
                before_screenshot = self.take_before_screenshot(original_element, link_text, status_code)
            
            self.driver.get(url)
            time.sleep(3)  # Wait for page load
            
            # Handle cookie consent popup
            self.handle_cookie_popup()
            
            # Generate filename (remove special characters)
            safe_text = "".join(c for c in link_text if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_text = safe_text[:50]  # Limit character count
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            filename = f"{status_code}_{safe_text}_{timestamp}.png"
            filepath = os.path.join(self.screenshot_dir, filename)
            
            self.driver.save_screenshot(filepath)
            
            # Return paths including pre-error capture
            result_paths = [filepath]
            if before_screenshot:
                result_paths.append(before_screenshot)
            
            return result_paths if len(result_paths) > 1 else filepath
            
        except Exception as e:
            print(f"Screenshot error ({url}): {e}")
            return None
    
    def take_before_screenshot(self, element, link_text, status_code):
        """Capture page before error (highlight link element)"""
        try:
            # Return to original page
            current_url = self.driver.current_url
            if current_url != self.base_url:
                try:
                    self.driver.get(self.base_url)
                    time.sleep(3)  # Extended wait time
                    # Re-run cookie handling
                    self.handle_cookie_popup()
                except:
                    print("  ⚠️ Could not return to original page")
                    return None
            
            # Re-search for error link (more precise search)
            found_element = self.find_target_link(link_text, element)
            
            if found_element:
                # Highlight the element
                self.highlight_element_advanced(found_element, link_text)
                time.sleep(3)  # Highlight display time
            else:
                print("  ⚠️ Could not re-find error element")
                # Fallback display
                self.create_fallback_highlight(link_text)
            
            # Generate filename
            safe_text = "".join(c for c in link_text if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_text = safe_text[:50]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            filename = f"BEFORE_{status_code}_{safe_text}_{timestamp}.png"
            filepath = os.path.join(self.screenshot_dir, filename)
            
            self.driver.save_screenshot(filepath)
            print(f"  📸 Pre-error screenshot saved: {os.path.basename(filepath)}")
            
            # Remove highlights
            self.remove_all_highlights()
            
            return filepath
            
        except Exception as e:
            print(f"  ⚠️ Pre-error screenshot error (continuing): {str(e)[:50]}...")
            return None
    
    def find_target_link(self, link_text, original_element):
        """Precisely search for target link"""
        try:
            # Get original element data
            element_data = original_element.get('element_data', {}) if isinstance(original_element, dict) else {}
            
            # Try multiple search strategies
            search_strategies = []
            
            # 1. Exact match search
            if link_text and link_text != "No text":
                clean_text = link_text.replace("No text(", "").replace(")", "").strip()
                if clean_text:
                    search_strategies.extend([
                        f"//a[normalize-space(text())='{clean_text}']",
                        f"//a[contains(normalize-space(text()), '{clean_text[:15]}')]"
                    ])
            
            # 2. Class-based search (from saved info)
            if 'classes' in element_data and element_data['classes']:
                classes = element_data['classes'].split()
                for cls in classes[:3]:  # Search with first 3 classes
                    search_strategies.append(f"//a[contains(@class, '{cls}')]")
            
            # 3. XPath search (if saved)
            if 'xpath' in element_data and element_data['xpath']:
                search_strategies.append(element_data['xpath'])
            
            # 4. Position-based search
            if 'location' in element_data:
                loc = element_data['location']
                search_strategies.extend([
                    f"//a[position() <= 10]",  # From first 10 links
                    "//nav//a",  # Links in navigation
                    "//header//a"  # Links in header
                ])
            
            print(f"  🔍 Trying {len(search_strategies)} search strategies...")
            
            # Try each strategy in order
            for i, strategy in enumerate(search_strategies):
                try:
                    elements = self.driver.find_elements(By.XPATH, strategy)
                    
                    for element in elements:
                        # Check element visibility
                        if element.is_displayed() and element.is_enabled():
                            element_text = element.text.strip()
                            element_href = element.get_attribute("href") or ""
                            
                            print(f"  🎯 Candidate found [{i+1}]: '{element_text}' -> {element_href[:50]}...")
                            
                            # Improved text matching
                            if self.is_matching_link(link_text, element_text, element_href):
                                print(f"  ✅ Match successful: '{element_text}'")
                                return element
                                
                except Exception as e:
                    continue
            
            print("  ❌ All search strategies failed")
            return None
            
        except Exception as e:
            print(f"  ⚠️ Target search error: {str(e)[:50]}")
            return None
    
    def is_matching_link(self, original_text, element_text, element_href):
        """Determine if a link matches"""
        try:
            # Exact text match
            if original_text == element_text:
                return True
            
            # Partial match (10 or more characters)
            if len(original_text) > 10:
                clean_original = original_text.replace("No text(", "").replace(")", "")
                if clean_original in element_text or element_text in clean_original:
                    return True
            
            # Keyword matching
            original_keywords = original_text.split()
            element_keywords = element_text.split()
            
            matches = 0
            for orig_word in original_keywords:
                if len(orig_word) > 2:  # Only words with 2+ characters
                    for elem_word in element_keywords:
                        if orig_word in elem_word or elem_word in orig_word:
                            matches += 1
                            break
            
            # 50% or more keywords match
            if len(original_keywords) > 0 and matches / len(original_keywords) >= 0.5:
                return True
                
            return False
            
        except:
            return False
    
    def highlight_element_advanced(self, element, link_text):
        """Advanced highlight display for element"""
        try:
            # Scroll element to center of screen first
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", element)
            time.sleep(1)
            
            # Apply advanced highlight style
            highlight_script = """
            var element = arguments[0];
            var linkText = arguments[1];
            
            // Remove existing highlights
            var existing = document.querySelectorAll('.link-error-highlight, #highlight-label');
            existing.forEach(function(el) { el.remove(); });
            
            // Apply red border and animation to element
            element.style.cssText += `
                border: 3px solid #ff0000 !important;
                background-color: rgba(255, 0, 0, 0.1) !important;
                outline: 2px solid #ff6666 !important;
                outline-offset: 2px !important;
                box-shadow: 0 0 15px rgba(255, 0, 0, 0.8) !important;
                animation: blink-red 1s infinite alternate !important;
                position: relative !important;
                z-index: 999999 !important;
            `;
            
            // Add CSS animation
            var style = document.createElement('style');
            style.textContent = `
                @keyframes blink-red {
                    0% { box-shadow: 0 0 15px rgba(255, 0, 0, 0.8); }
                    100% { box-shadow: 0 0 25px rgba(255, 0, 0, 1); }
                }
            `;
            document.head.appendChild(style);
            
            // Create error label
            var label = document.createElement('div');
            label.id = 'highlight-label';
            label.innerHTML = 'ERROR LINK: ' + linkText.substring(0, 30) + (linkText.length > 30 ? '...' : '');
            label.style.cssText = `
                position: fixed;
                top: 20px;
                left: 50%;
                transform: translateX(-50%);
                background: linear-gradient(45deg, #ff0000, #ff6666);
                color: white;
                padding: 10px 20px;
                font-family: Arial, sans-serif;
                font-size: 14px;
                font-weight: bold;
                border-radius: 25px;
                box-shadow: 0 4px 15px rgba(255, 0, 0, 0.3);
                z-index: 1000000;
                animation: slideDown 0.5s ease-out;
                text-align: center;
                max-width: 400px;
                word-wrap: break-word;
            `;
            
            // Animation for label
            var labelStyle = document.createElement('style');
            labelStyle.textContent = `
                @keyframes slideDown {
                    0% { transform: translateX(-50%) translateY(-100%); opacity: 0; }
                    100% { transform: translateX(-50%) translateY(0); opacity: 1; }
                }
            `;
            document.head.appendChild(labelStyle);
            
            document.body.appendChild(label);
            
            return true;
            """
            
            success = self.driver.execute_script(highlight_script, element, link_text)
            print(f"  🔴 Advanced highlight applied: '{element.text[:30]}'")
            return True
            
        except Exception as e:
            print(f"  ⚠️ Advanced highlight failed: {str(e)[:50]}")
            return self.highlight_element_fallback(element)
    
    def highlight_element_fallback(self, element):
        """Fallback highlight"""
        try:
            self.driver.execute_script("""
                var el = arguments[0];
                el.style.border = '3px solid red';
                el.style.backgroundColor = 'rgba(255, 0, 0, 0.1)';
            """, element)
            print("  🟡 Fallback highlight applied")
            return True
        except:
            return False
    
    def create_fallback_highlight(self, link_text):
        """Fallback display when element cannot be found"""
        try:
            fallback_script = f"""
            // Remove existing display
            var existing = document.getElementById('fallback-highlight');
            if (existing) existing.remove();
            
            // Create fallback display
            var container = document.createElement('div');
            container.id = 'fallback-highlight';
            container.style.cssText = `
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 80%;
                max-width: 600px;
                background: rgba(255, 0, 0, 0.95);
                color: white;
                padding: 30px;
                border-radius: 15px;
                text-align: center;
                font-family: Arial, sans-serif;
                font-size: 16px;
                z-index: 1000000;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
                border: 3px solid white;
            `;
            
            container.innerHTML = `
                <h3 style="margin: 0 0 15px 0; font-size: 20px;">⚠️ Error link detected</h3>
                <p style="margin: 0 0 15px 0; font-size: 14px;">Link text:</p>
                <div style="background: rgba(255,255,255,0.2); padding: 10px; border-radius: 5px; font-family: monospace;">
                    {link_text[:100]}
                </div>
                <p style="margin: 15px 0 0 0; font-size: 12px; opacity: 0.8;">
                    * Could not identify exact location
                </p>
            `;
            
            document.body.appendChild(container);
            """
            
            self.driver.execute_script(fallback_script)
            print(f"  🟡 Fallback display created: {link_text[:30]}...")
            
        except Exception as e:
            print(f"  ⚠️ Fallback display failed: {str(e)[:50]}")
    
    def remove_all_highlights(self):
        """Remove all highlights"""
        try:
            cleanup_script = """
            // Remove all highlight elements
            var highlights = document.querySelectorAll('.link-error-highlight, #highlight-label, #fallback-highlight');
            highlights.forEach(function(el) { el.remove(); });
            
            // Clean up styles on all anchor tags
            var links = document.querySelectorAll('a');
            links.forEach(function(link) {
                // Only remove highlight-related styles
                link.style.border = link.style.border.replace(/.*solid.*red.*/gi, '');
                link.style.backgroundColor = link.style.backgroundColor.replace(/rgba\\(255,\\s*0,\\s*0.*\\)/gi, '');
                link.style.outline = link.style.outline.replace(/.*solid.*red.*/gi, '');
                link.style.boxShadow = link.style.boxShadow.replace(/.*rgba\\(255,\\s*0,\\s*0.*\\)/gi, '');
                link.style.animation = link.style.animation.replace(/blink-red.*/gi, '');
            });
            
            // Also remove added style elements
            var addedStyles = document.querySelectorAll('style');
            addedStyles.forEach(function(style) {
                if (style.textContent.includes('blink-red') || style.textContent.includes('slideDown')) {
                    style.remove();
                }
            });
            """
            
            self.driver.execute_script(cleanup_script)
            print("  🧹 All highlights cleaned up")
            
        except Exception as e:
            print(f"  ⚠️ Cleanup error: {str(e)[:50]}")
    
    def handle_cookie_popup(self):
        """Handle cookie consent popup"""
        try:
            cookie_selectors = [
                "//button[contains(text(), 'Accetta tutti i cookie')]",
                "//button[contains(text(), 'Accetta solo i cookie tecnici')]",
                "//button[contains(text(), 'Accetta')]",
                "button:contains('Accetta tutti')",
                ".cookie-accept-all",
                "[data-cookie-accept]",
                "//button[contains(text(), 'Accept')]",
                "//button[contains(text(), 'OK')]",
                "//button[contains(text(), 'Agree')]",
                "//button[contains(@class, 'cookie')]",
                "//button[contains(@class, 'accept')]",
            ]
            
            time.sleep(3)
            
            print("    🍪 Checking for cookie popup...")
            
            for i, selector in enumerate(cookie_selectors):
                try:
                    if selector.startswith("//") or selector.startswith("/"):
                        # XPath
                        buttons = self.driver.find_elements(By.XPATH, selector)
                    else:
                        # CSS selector
                        buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            # Scroll to button before clicking
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                            time.sleep(0.5)
                            
                            # Check button text
                            button_text = button.text or button.get_attribute("textContent") or ""
                            print(f"    🎯 Cookie button found: '{button_text}'")
                            
                            # Use JavaScript click
                            self.driver.execute_script("arguments[0].click();", button)
                            time.sleep(2)
                            print(f"    ✅ Cookie button clicked successfully")
                            
                            # Wait for popup to disappear after cookie handling
                            time.sleep(3)
                            return True
                except Exception as e:
                    continue
            
            # Last resort: force hide all cookie popups
            try:
                print("    🔧 Force hiding cookie popup...")
                remove_script = """
                // Hide by common cookie popup class names
                var selectors = [
                    '[class*="cookie"]', '[id*="cookie"]', '[class*="gdpr"]', 
                    '[class*="consent"]', '[id*="consent"]', '[class*="privacy"]',
                    '.modal', '[class*="overlay"]', '[class*="popup"]'
                ];
                
                var removed = 0;
                selectors.forEach(function(selector) {
                    var elements = document.querySelectorAll(selector);
                    elements.forEach(function(el) {
                        var rect = el.getBoundingClientRect();
                        if (rect.height > 100 && (rect.width > 300 || rect.height > 200)) {
                            el.style.display = 'none';
                            removed++;
                        }
                    });
                });
                
                return removed;
                """
                
                removed_count = self.driver.execute_script(remove_script)
                if removed_count > 0:
                    print(f"    ✅ Hidden {removed_count} cookie elements")
                    time.sleep(2)
                    return True
                    
            except Exception as e:
                pass
            
            print("    ⚠️ Could not handle cookie popup")
            return False
                
        except Exception as e:
            print(f"    ⚠️ Cookie handling error: {str(e)[:50]}")
            return False
    
    def run_check(self):
        """Main processing"""
        print(f"Starting site check: {self.base_url}")
        
        # Get all links
        all_links = self.get_all_links()
        print(f"Number of links retrieved: {len(all_links)}")
        
        # Remove duplicate URLs (keep text from first occurrence)
        unique_links = {}
        for link_info in all_links:
            url = link_info['url']
            if url not in unique_links:
                unique_links[url] = link_info
            else:
                # Update if existing text is "No text" but new one has text
                if unique_links[url]['text'] == "No text" and link_info['text'] != "No text":
                    unique_links[url]['text'] = link_info['text']
        
        links = list(unique_links.values())
        print(f"Links after deduplication: {len(links)} (duplicates removed: {len(all_links) - len(links)})")
        
        results = []
        error_count = 0
        
        for i, link_info in enumerate(links, 1):
            url = link_info['url']
            text = link_info['text']
            
            print(f"[{i}/{len(links)}] Checking: {text[:30]}...")
            
            # HTTP status check
            status_code = self.check_link_status(url)
            
            result = {
                'Link Text': text,
                'URL': url,
                'Status Code': status_code,
                'Screenshot Path': '',
                'Pre-Error Screenshot Path': '',
                'Check Time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Only target true errors (exclude 403)
            if status_code == 404 or status_code in [500, 502, 503, 504] or status_code == 0:
                error_count += 1
                print(f"  ❌ Error detected: {status_code}")
                
                # Take screenshot (including pre-error)
                screenshot_result = self.take_screenshot(url, text, status_code, link_info)
                if screenshot_result:
                    if isinstance(screenshot_result, list):
                        result['Screenshot Path'] = screenshot_result[0]  # Post-error
                        result['Pre-Error Screenshot Path'] = screenshot_result[1]  # Pre-error
                        print(f"  📸 Post-error screenshot: {os.path.basename(screenshot_result[0])}")
                    else:
                        result['Screenshot Path'] = screenshot_result
                        print(f"  📸 Screenshot saved: {os.path.basename(screenshot_result)}")
                
                self.error_links.append(result)
            else:
                print(f"  ✅ OK: {status_code}")
            
            results.append(result)
            time.sleep(1)  # Reduce server load
        
        # Save results to CSV
        self.save_results(results)
        
        print(f"\n=== Check Complete ===")
        print(f"Total links: {len(links)}")
        print(f"Error links: {error_count}")
        print(f"Results saved to: {self.output_dir}")
        
        return results
    
    def save_results(self, results):
        """Save results to CSV file"""
        csv_path = os.path.join(self.output_dir, f"link_check_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            if results:
                fieldnames = results[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
        
        print(f"Results CSV saved: {csv_path}")
        
        # Also create CSV for errors only
        if self.error_links:
            error_csv_path = os.path.join(self.output_dir, f"error_links_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            with open(error_csv_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = self.error_links[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.error_links)
            print(f"Error links CSV saved: {error_csv_path}")
    
    def close(self):
        """Clean up resources"""
        if hasattr(self, 'driver'):
            self.driver.quit()

# Usage example
if __name__ == "__main__":
    # ★ Change this to the actual target URL ★
    target_url = "https://example.com"  # Replace with your target URL
    
    checker = LinkChecker(target_url)
    
    try:
        results = checker.run_check()
    finally:
        checker.close()
