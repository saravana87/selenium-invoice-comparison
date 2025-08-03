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
    """
    Downloads a PDF from the given URL, saves it locally, and extracts invoice data and text using pdfplumber.
    Args:
        pdf_url (str): The URL of the PDF to download and process.
    Returns:
        None. Prints extracted invoice data and regex results.
    """
    pdf_path = "downloaded_invoice.pdf"
    # Download the PDF from the URL
    try:
        response = requests.get(pdf_url)
        response.raise_for_status()
        with open(pdf_path, "wb") as f:
            f.write(response.content)
    except Exception as e:
        print(f"Failed to download PDF: {e}")
        return

    # Step 2: Extract text using pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        text = pdf.pages[0].extract_text()
        page0 = pdf.pages[0]
        # Extract tables
        tables = page0.extract_tables()
        invoice_data = {}
        line_items = []
        totals = {}
        for table in tables:
            for i, row in enumerate(table):
                print(row)
                if row == ['Invoice No', 'Customer No', 'Invoice Period', 'Date']:
                    data_row = table[i + 1]
                    invoice_data['invoice_no'] = data_row[0]
                    invoice_data['customer_no'] = data_row[1]
                    invoice_data['invoice_period'] = data_row[2]
                    invoice_data['date'] = data_row[3]
                elif row == ['Service Description', 'Amount\n-without VAT-', 'quantity', 'Total Amount']:
                    j = i + 1
                    while j < len(table) and table[j][0] and 'Total' not in table[j][1]:
                        line_items.append({
                            'description': table[j][0],
                            'unit_price': table[j][1],
                            'quantity': table[j][2],
                            'total': table[j][3]
                        })
                        j += 1
                if row[1] == 'Total':
                    totals['net_total'] = row[3]
                if row[1] and 'VAT' in row[1]:
                    totals['vat'] = row[3]
                if row[1] and 'Gross' in row[1]:
                    totals['gross_total'] = row[3]

        invoice_data['line_items'] = line_items
        invoice_data['totals'] = totals
        print(invoice_data)

        # Basic regex from text
        invoice_no = re.search(r"Invoice\s*Number\s*[:\-]?\s*(\S+)", text, re.IGNORECASE)
        customer_no = re.search(r"Customer\s*Number\s*[:\-]?\s*(\S+)", text, re.IGNORECASE)
        total_amount = re.search(r"Total\s*Amount\s*[:\-]?\s*\$?([\d,.]+)", text, re.IGNORECASE)
        invoice_period = re.search(r"Period\s*[:\-]?\s*([\w\s\-]+)", text, re.IGNORECASE)

        #print("Invoice No:", invoice_no.group(1) if invoice_no else "Not found")
        #print("Customer No:", customer_no.group(1) if customer_no else "Not found")
        #print("Total Amount:", total_amount.group(1) if total_amount else "Not found")
        #print("Period:", invoice_period.group(1) if invoice_period else "Not found")

# Use local ChromeDriver (must be in PATH or specify full path)
driver = webdriver.Chrome()

driver.get("https://digitalgrub.ws/selenium_ocr_test.html")
#driver.maximize_window()
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

