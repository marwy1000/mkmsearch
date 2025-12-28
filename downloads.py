import os
from time import sleep
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from utils import request_delay

# Define the directory for CSV files
CSV_DIR = "csv_files"

def download_reports(year=None, month=None):
    if (year and not month) or (month and not year):
        print('Both year and month needs to be defined at the same time, or left out')
        exit(1)

    if year is not None and month is not None and is_future_date(year, month):
        print(f"Skipping future date. Year: {year}. Month: {month}")
        exit(1)

    if not os.path.exists(CSV_DIR):
        os.makedirs(CSV_DIR)

    # Load the Downloads page
    from login import login
    try:
        scraper = login()
    except Exception as e:
        print(f"Login failed: {e}")
        exit(1)

    downloads_url = "https://www.cardmarket.com/en/Magic/Account/Downloads"
    downloads_page = scraper.get(downloads_url)
    
    # Check if the page loaded correctly
    if downloads_page.status_code != 200:
        print("Failed to load the Downloads page.")
        return
    
    # Parse the HTML to extract download details
    soup = BeautifulSoup(downloads_page.text, "html.parser")
    
    # Find all rows with download links
    rows = soup.find_all("form", action="/en/Magic/PostGetAction/User_Reporting_DownloadReportFileFromAws")
    # Remove duplicates
    rows = list({str(row): row for row in rows}.values())
    for row in rows:
        
        # Get __cmtkn and idRequest values
        token_value = row.find("input", {"name": "__cmtkn"})["value"]
        id_request = row.find("input", {"name": "idRequest"})["value"]
        
        # Get the filename from the button text
        filename = row.find("button").text.strip()
        file_path = os.path.join(CSV_DIR, filename)
        
        # Extract year and month from the filename
        file_year, file_month = None, None
        try:
            # Extract year and month assuming filename contains "YYYY-MM"
            file_year, file_month = map(int, filename.split("-byPurchaseDate-")[1].split("-")[:2])
        except (IndexError, ValueError):
            print(f"Could not extract year/month from filename: {filename}")
            continue

        # Determine whether to download based on input
        if year is not None and month is not None:
            if file_year != year or file_month != month:
                continue  # Skip files that don't match the specified year/month

            # Force download even if file exists
            print(f"Forcing download for {filename}...")
        elif os.path.exists(file_path):
            print(f"{filename} already downloaded.")
            continue

        # Prepare payload for download
        download_url = "https://www.cardmarket.com/en/Magic/PostGetAction/User_Reporting_DownloadReportFileFromAws"
        payload = {
            "__cmtkn": token_value,
            "idRequest": id_request,
        }
        
        # Send the POST request to download the file
        response = scraper.post(download_url, data=payload)
        
        # Check for successful download
        if response.status_code == 200:
            with open(file_path, "wb") as file:
                file.write(response.content)
            print(f"Downloaded {filename}")
        else:
            print(f"Failed to download {filename}")
        
        # Add a 10-second delay after each download
        sleep(request_delay())
  

def generate_reports(all, year, month, current_month, previous_month):
    """
    Generate reports for specified time
    """
    try:
        from login import login
        # Establish a logged-in session
        try:
            scraper = login()
        except Exception as e:
            print(f"Login failed: {e}")
            exit(1)
            
        # Access the statistics page to retrieve the hidden token and user information
        stats_url = "https://www.cardmarket.com/en/Magic/Account/Statistics"
        response = scraper.get(stats_url)
        
        if response.status_code != 200:
            raise Exception("Failed to load the statistics page")

        # Parse HTML to find hidden fields
        soup = BeautifulSoup(response.text, 'html.parser')
        hidden_token = soup.find("input", {"name": "__cmtkn"})["value"]
        id_user = soup.find("input", {"name": "idUser"})["value"]
        price_for_buyer = soup.find("input", {"name": "priceForBuyer"})["value"]

        # Extract available months and years
        mkm_months = {option['value']: option.text for option in soup.select('select[name="month"] option')}
        mkm_years = {option['value']: option.text for option in soup.select('select[name="year"] option')}
        default_report_type = 'datePurchased'  # Set to "Purchase Date"

        # Corrected URL for report generation
        report_url = "https://www.cardmarket.com/en/Magic/PostGetAction/Reports_Asynchronous_GetMonthlyPurchaseSummary"


        # Handle current month and previous month logic
        if all:
            years_to_generate = mkm_years.keys()
            months_to_generate = mkm_months.keys()
        # Handle current month and previous month logic
        elif current_month:
            today = datetime.today()
            years_to_generate = [str(today.year)]
            months_to_generate = [str(today.month)]
        elif previous_month:
            today = datetime.today()
            first_day_current_month = today.replace(day=1)
            last_month = first_day_current_month - timedelta(days=1)
            years_to_generate = [str(last_month.year)]
            months_to_generate = [str(last_month.month)]
        elif year:
            years_to_generate = [year]
            if month:
                months_to_generate = [month]
            else:
                months_to_generate = [1,2,3,4,5,6,7,8,9,10,11,12]
        else:
            years_to_generate = []
            months_to_generate = []

        # Loop over the specified years and months
        for year_value in years_to_generate:
            for month_value in months_to_generate:
                if not is_future_date(year_value, month_value):
                    payload = {
                        '__cmtkn': hidden_token,
                        'idUser': id_user,
                        'priceForBuyer': price_for_buyer,
                        'month': month_value,
                        'year': year_value,
                        'dateUsed': default_report_type,
                        'format': 'csv',  # or 'xls' based on preference
                    }
                    
                    # Send a single POST request to initiate the report generation
                    report_response = scraper.post(report_url, data=payload)
                    
                    if report_response.status_code == 200:
                        print(f"Report generation initiated for {year_value}-{month_value} (Purchase Date)")
                    else:
                        print(f"Failed to initiate report for {year_value}-{month_value} (Purchase Date)")
                        continue  # Skip to the next combination if report generation fails
                    
                    sleep(request_delay())  # Sleep for the specified delay
    except Exception as e:
        print(e)          

def is_future_date(year, month):
    """
    Check if the given year and month are in the future.
    """
    today = datetime.today()
    if int(year) > today.year or (int(year) == today.year and int(month) > today.month):
        return True
    return False