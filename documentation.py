import requests
from bs4 import BeautifulSoup
import streamlit as st

# Function to scrape Salesforce Developer documentation
def scrape_salesforce_docs(query):
    # Construct a URL for the Salesforce Developer docs
    url = f"https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_classes.htm?q={query}"
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Search for documentation content
        sections = soup.find_all('section', class_='docs-section')
        
        results = []
        for section in sections:
            title = section.find('h1')
            description = section.find('p')
            if title and description:
                results.append({
                    'title': title.text.strip(),
                    'description': description.text.strip()
                })
        return results
    else:
        return []

# Streamlit app to search and display documentation results
def search_documentation():
    st.title("🔍 Salesforce Apex & LWC Documentation Search")
    st.write("""
    Use this tool to find methods, components, or guides for Apex and Lightning Web Components (LWC).
    Simply enter a search term below, and we'll help you find the relevant documentation.
    """)

    # Input field for search query
    search_query = st.text_input("Enter a method or topic (e.g., 'Apex Map', 'LWC connectedCallback')", "")

    # Search button
    if st.button("Search"):
        if search_query:
            # Fetch the search results using the scraping function
            results = scrape_salesforce_docs(search_query)

            if results:
                st.subheader("🔎 Search Results:")
                # Display the results
                for result in results:
                    with st.expander(result['title']):
                        st.write(f"**Description:** {result['description']}")
                        st.markdown("---")
            else:
                st.warning("No results found for your query. Please try another search term.")
        else:
            st.error("Please enter a search term to proceed.")

if __name__ == "__main__":
    search_documentation()
