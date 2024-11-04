import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time

# Function to initialize WebDriver
def init_driver():
    service = Service('Main\chromedriver.exe')
    driver = webdriver.Chrome(service=service)
    return driver

# Function to find the search box using various strategies
def find_search_box(driver):
    search_box = None
    try:
        search_box = driver.find_element(By.NAME, "search")
    except:
        try:
            search_box = driver.find_element(By.ID, "search")
        except:
            try:
                search_box = driver.find_element(By.XPATH, '//input[contains(@placeholder, "Search")]')
            except:
                try:
                    search_box = driver.find_element(By.XPATH, '//input[contains(@class, "search")]')
                except:
                    raise Exception("Search box not found.")
    
    return search_box

# Function to search the query in the documentation and return result URLs
def search_documentation(doc_link, query):
    driver = init_driver()
    driver.get(doc_link)
    time.sleep(3)

    try:
        search_box = find_search_box(driver)
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        result_links = []

        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('http') or href.startswith('/'):
                full_link = href if href.startswith('http') else doc_link + href
                result_links.append(full_link)

        driver.quit()
        return result_links
    
    except Exception as e:
        driver.quit()
        print(f"Error occurred: {e}")
        return []

# Streamlit interface
st.title("Salesforce Apex Documentation Search")

# User input for query
query = st.text_input("Enter your search query:")

if st.button("Search"):
    if query:
        doc_link = "https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_dev_guide.htm"
        result_urls = search_documentation(doc_link, query)
        
        # Display results
        if result_urls:
            st.subheader("Search Results:")
            
            for url in result_urls:
                st.markdown(f"[{url}]({url})")
        else:
            st.warning("No results found.")
    else:
        st.warning("Please enter a query.")
