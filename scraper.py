"""
README

Generates Excel file with technical indicators for tickers derived from yahoo finance. Made by Hayden Herstrom with help from internet

Dependencies:
    pandas
    beautifulsoup4
    openpyxl
    urllib3
    maybe others... py -m pip install {packagename}

"""


from bs4 import BeautifulSoup
import urllib.request
import pandas as pd
import time
from datetime import datetime

def scrape_yahoo(stock):
    technicals = {}
    try:
        url = f'https://finance.yahoo.com/quote/' + stock.upper() + '/key-statistics'
        print(f"Fetching URL: {url}")
        
        # Set headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        request = urllib.request.Request(url, headers=headers)
        
        # Use urlopen correctly
        with urllib.request.urlopen(request) as response:
            page = response.read()
        
        soup = BeautifulSoup(page, 'html.parser')
       
        # Parse tables
        tables = soup.findAll('table', class_='table yf-vaowmx')
        
        if not tables:
            print("No tables found with table yf-vaowmx")
            return technicals

        technicals["Ticker"] = stock
        for table in tables:
            table_body = table.find('tbody')
            rows = table_body.find_all('tr') if table_body else []

            for row in rows:
                # Get label and value from the row
                cols = row.find_all('td')
                if len(cols) == 2:  # Ensure there are exactly 2 columns (label and value)
                    label = cols[0].text.strip()
                    value = cols[1].text.strip()
                    value = standardize_value(value) # makes everything into a float except dates, those stay strings
                    label = remove_dates_from_keys(label) #removes dates from short interest columns
                    technicals[label] = value
                    #print(f"{label}: {value}")

        return technicals

    except Exception as e:
        print('Failed, exception:', str(e))
        return technicals




""" def scrape(stock_list, interested, technicals):
	for each_stock in stock_list:
		technicals = scrape_yahoo(each_stock)
		print(each_stock)
		for ind in interested:
			print(ind + ": "+ technicals[ind])
		print("------")
		time.sleep(1)													# Use delay to avoid getting flagged as bot
	return technicals """

def standardize_value(value):
    """
    Standardizes a string value to a numeric type.
    Handles percentages (%), millions (M), and billions (B).
    
    Args:
        value (str): The input value as a string.
        
    Returns:
        float: The standardized numeric value, or None if conversion fails.
    """
    if isinstance(value, str):  # Ensure it's a string
        value = value.strip()  # Remove any leading/trailing spaces
        value = value.replace(',', '')

        if value.endswith('%'):
            return float(value.rstrip('%')) / 100  # Convert percentage to fraction
        elif value.endswith('M'):
            return float(value.rstrip('M')) * 1_000_000  # Convert millions
        elif value.endswith('B'):
            return float(value.rstrip('B')) * 1_000_000_000  # Convert billions
    return value  # Return the value as-is if not a string

def remove_dates_from_keys(column_name):
    # Find the first occurrence of '(' and ')', which could be the date
    start = column_name.find('(')
    end = column_name.find(')')
    
    # If both are found and a valid date pattern is detected
    if start != -1 and end != -1:
        date_part = column_name[start:end+1]
        # Check if the part between parentheses looks like a date (MM/DD/YYYY)
        date_string = column_name[start+1:end]
        if len(date_string.split('/')) == 3:
            column_name = column_name[:start] + column_name[end+1:]
    return column_name

sample_column = "Short % of Shares Outstanding (12/13/2024) "
sample_column = remove_dates_from_keys(sample_column)
print(sample_column)

def main():
	#stock_list = ['aapl', 'tsla', 'ge']
	#interested = ['Market Cap (intraday)', 'Return on Equity', 'Revenue', 'Quarterly Revenue Growth']
	#technicals = {}
	#tech = scrape(stock_list, interested, technicals)
	#print(tech)
    stocks = input("Enter tickers, seperated by commas: ")
    print(stocks)
    stocks = stocks.split(",")
    data_list = []
    for stock in stocks:
        data = scrape_yahoo(stock)
        if data:
            data_list.append(data)
            """ for key, value in data.items():
                #print(f"{key}: {value}")
                with open(stock+".txt", 'w', encoding='utf-8') as file:
                    file.write(str(data)) """
            #if you want to write to file
            time.sleep(.5)
        else: print("data is empty")
    df = pd.DataFrame(data_list)
    file_name = time.strftime("%Y-%m-%d-%H-%M-%S")+'stock_data.xlsx'
    df.to_excel(file_name, index=False)

	
if __name__ == "__main__":
	main()