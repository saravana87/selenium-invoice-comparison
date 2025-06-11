from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()

driver.get("https://www.selenium.dev/selenium/web/web-form.html")

# Wait until the title is loaded
title = driver.title
print(f"Page title: {title}")

# Find the text box and submit button
text_box = driver.find_element(by=By.NAME, value="my-text")
submit_button = driver.find_element(by=By.CSS_SELECTOR, value="button")

# Send input and click the submit button
text_box.send_keys("Selenium")
submit_button.click()

# Wait explicitly for the message element to be visible
message = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.ID, "message"))
)

# Retrieve and print the message text
text = message.text
print(f"Message: {text}")

driver.quit()