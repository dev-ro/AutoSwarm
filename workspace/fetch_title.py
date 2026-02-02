import requests
from bs4 import BeautifulSoup
import os

def verify_file():
    file_path = 'scraped_data.txt'
    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path)
        if file_size > 0:
            print(f"Verification Success: '{file_path}' exists and size is {file_size} bytes.")
        else:
            print(f"Verification Failed: '{file_path}' exists but is empty.")
    else:
        print(f"Verification Failed: '{file_path}' does not exist.")

def scrape_title():
    url = 'http://example.com'
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        if soup.title:
            title_text = soup.title.string
            with open('scraped_data.txt', 'w') as file:
                file.write(title_text)
            print(f"Title '{title_text}' extracted and saved to 'scraped_data.txt'.")
        else:
            print("No title tag found on the page.")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    scrape_title()
    verify_file()