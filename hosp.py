
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
import pyodbc

# ========================
# Browser Setup
# ========================
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-notifications")

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 10)

driver.get("https://www.google.com/maps/search/new+cairo+hospitals/")
wait.until(EC.presence_of_element_located((By.CLASS_NAME, "Nv2PK")))

# ========================

# ========================
# Smart Scroll (Correct Container)
# ========================

scrollable_div = wait.until(
    EC.presence_of_element_located(
        (By.XPATH, "//div[@role='feed']")
    )
)

last_count = 0

while True:
    driver.execute_script(
        "arguments[0].scrollBy(0, 1000);",
        scrollable_div
    )

    time.sleep(2)

    results = driver.find_elements(By.CLASS_NAME, "Nv2PK")
    current_count = len(results)

    print("Loaded:", current_count)

    if current_count == last_count:
        print("End of list reached.")
        break

    last_count = current_count


results = driver.find_elements(By.CLASS_NAME, "Nv2PK")

data_list = []

# ========================
# Open Each Result
# ========================
for i in range(len(results)):

    results = driver.find_elements(By.CLASS_NAME, "Nv2PK")
    results[i].click()

    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "DUwDvf")))

    # Name
    try:
        name = driver.find_element(By.CLASS_NAME, "DUwDvf").text
    except:
        name = None

    # Address
    try:
        address = driver.find_element(By.XPATH, "//button[@data-item-id='address']").text
    except:
        address = None

    # Phone
    try:
        phone = driver.find_element(By.XPATH, "//button[contains(@data-item-id,'phone')]").text
    except:
        phone = None

    # Website
    try:
        website = driver.find_element(By.XPATH, "//a[@data-item-id='authority']").get_attribute("href")
    except:
        website = None

    # Rating
    try:
        rating = float(driver.find_element(By.CLASS_NAME, "MW4etd").text)
    except:
        rating = None

    # Coordinates from URL
    try:
        current_url = driver.current_url
        if "@" in current_url:
            coords = current_url.split("@")[1].split(",")
            coordinates = coords[0] + "," + coords[1]
        else:
            coordinates = None
    except:
        coordinates = None

    data_list.append((
        name,
        address,
        phone,
        website,
        coordinates,
        rating,
        "New Cairo",
        datetime.today().date()
    ))

    time.sleep(30)

driver.quit()


# ========================
# Database Connection
# ========================
def get_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=.;"
        "DATABASE=hospitals2;"
        "TrustServerCertificate=yes;"
        "Trusted_Connection=yes;"
    )


# ========================
# Create Table
# ========================
def create_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='hospitals2')
        CREATE TABLE hospitals2 (
            id INT IDENTITY(1,1) PRIMARY KEY,
            name NVARCHAR(MAX),
            address NVARCHAR(MAX),
            phone NVARCHAR(255),
            website NVARCHAR(MAX),
            coordinates NVARCHAR(MAX),
            rating FLOAT,
            city NVARCHAR(255),
            scrape_date DATE
        )
    """)

    conn.commit()
    conn.close()


# ========================
# Insert Data
# ========================
def insert_data(data):
    conn = get_connection()
    cursor = conn.cursor()

    for row in data:
        cursor.execute("""
            INSERT INTO hospitals2
            (name, address, phone, website, coordinates, rating, city, scrape_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, row)

    conn.commit()
    conn.close()


# ========================
# Execute
# ========================
create_table()
insert_data(data_list)

print("Data inserted successfully!")
