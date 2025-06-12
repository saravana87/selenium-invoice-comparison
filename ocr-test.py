from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import requests
import pdfplumber
from urllib.parse import urljoin

def download_extracttext(pdf_url):
    
    pdf_path = "downloaded_invoice.pdf"
    response = requests.get(pdf_url)
    with open(pdf_path, 'wb') as f:
        f.write(response.content)

    # Step 2: Extract text using pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        text = pdf.pages[0].extract_text()
        print("Extracted PDF Text:\n", text)
    

# Use local ChromeDriver (must be in PATH or specify full path)
driver = webdriver.Chrome()

driver.get("https://digitalgrub.ws/selenium_ocr_test.html")
driver.maximize_window()
driver.implicitly_wait(10)
page_url = driver.current_url

# Switch to PDF iframe
iframe = driver.find_element(By.TAG_NAME, "iframe")
#driver.switch_to.frame(iframe)
pdf_src_url = iframe.get_attribute("src")
print("PDF URL:", pdf_src_url)
pdf_url = urljoin(page_url, pdf_src_url)
print("Full PDF URL:", pdf_url)

# Try extracting text from PDF (if it's selectable)
try:
    pdf_text = driver.find_element(By.TAG_NAME, "body").text
    download_extracttext(pdf_url)
    #print("Extracted text:\n", pdf_text)
except:
    print("Unable to extract text. PDF might be rendered on canvas.")

driver.switch_to.default_content()

# Example: Fill the invoice number (hardcoded for now)
#driver.find_element(By.ID, "invoice-number").send_keys("661935")

time.sleep(5)
driver.quit()

