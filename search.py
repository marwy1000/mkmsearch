import os
import re
from datetime import datetime
import glob
import pandas as pd
from rich import print

# Specify the directory containing the CSV files
CSV_DIRECTORY = 'csv_files'
product_field = "Description" #"Localized Product Name"

product_name_column = "Product Name"
set_name_column = "Set Name"
user_name_column = "Username"
date_of_purchase_column = "Purchased"
total_price_column = "Sum"
quantity_column = "Qty"
order_id_column = "OrderID"
shipment_cost_column = "Shipment Costs"
quality_column = "Quality"
language_column = "Lang"
foiliness_column = "Foil"

original_header = [
    order_id_column, user_name_column, 'Name', 'Street', 'City', 'Country', 'Is Professional', 'VAT Number', 
    date_of_purchase_column, 'Article Count', 'Merchandise Value', shipment_cost_column, 'Trustee service fee', 
    'Total Value', 'Currency', 'Description', 'Product ID', 'Localized Product Name'
]

def get_dataframe():
    # Initialize an empty list to hold dataframes
    dataframes = []
    # Use glob to find all .csv files in the directory
    for filename in glob.glob(os.path.join(CSV_DIRECTORY, '*.csv')):
        file_path = os.path.join(filename)

        # Read the file and rename columns
        df = pd.read_csv(file_path, sep=';', header=0)  # You should already have the correct header from original_header
        df.columns = original_header  # Rename columns to the standardized header
        dataframes.append(df)

    # Concatenate all dataframes into one
    combined_df = pd.concat(dataframes, ignore_index=True)

    # Rename columns
    combined_df.rename(columns={
        'Date of Purchase': date_of_purchase_column
    }, inplace=True)

    # Convert "Date of Purchase" to datetime and strip the time (only keep the date)
    combined_df[date_of_purchase_column] = pd.to_datetime(combined_df[date_of_purchase_column]).dt.date


    # Parse the product field and create a MultiIndex DataFrame
    parsed_products = []
    order_ids = []
    for _, row in combined_df.iterrows():
        product_df = parse_products(row[product_field], row["Currency"])

        parsed_products.append(product_df)

        # Track the order ID for MultiIndex purposes
        order_id = row[order_id_column]
        order_ids.extend([order_id] * len(product_df))

    # Concatenate all parsed product dataframes
    products_df = pd.concat(parsed_products, ignore_index=True)
    products_df[order_id_column] = order_ids

    # Set MultiIndex with OrderID and a sequential integer for each product entry
    products_df = products_df.set_index([order_id_column, products_df.groupby(order_id_column).cumcount()])

    # Merge parsed products back with the original DataFrame to retain other columns
    merged_df = combined_df[original_header].drop_duplicates()
    final_df = pd.merge(products_df, merged_df, on=order_id_column, how='left')

    return final_df

def split_products(s: str):
    return [
        p.strip()
        for p in re.split(r'\s\|\s(?![^()]*\))', s)
        if p.strip()
    ]

def parse_products(product_str, currency):
    # Split by " | " to separate individual products
    products = split_products(product_str)

    # Lists to store parsed data
    quantities, product_names, set_names, qualities, languages, foils, prices, total_prices = [], [], [], [], [], [], [], []

    # E.g. 1x Myth Realized (Dragons of Tarkir) - 26 - Rare - MT - English - Foil - 4,99 EUR;
    # 1x Cabal Therapy (Premium Deck Series: Graveborn) - Uncommon - NM - English - Foil - 6,00 EUR 
    # 5x Beast Token (G 3/3) / Elemental Token (G 5/3) (Commander 2014) - T 19/21 - Token - MT - English - 0,10 EUR
    # 3x 80 KMC Hyper mat Sleeves (Black) - English - 5,99 EUR 

    quantity_pattern = r"(\d+)x"  # Matches quantity
    product_pattern = r" (.+?) \("  # Matches product name (up to the first '(')
    set_pattern = r'\(([^()]+)\)(?=[^()]*$)' #r"\((.*?)\)"  # Matches set name within parentheses
    quality_pattern = quality_regex = r'\b( - MT - | - NM - | - EX - | - GD - | - LP - | - PL - | - PO -)\b' # r"\) - \d+ - \w+ - (\w+) - "
    alternative_quality_pattern = r"\) - \w+ - (\w+) - "
    language_pattern = r'\b(English|German|French|Italian|Spanish|Japanese|Simplified Chinese|Traditional Chinese|Korean|Portuguese|Russian)\b'
    price_pattern = fr"- ([\d,.]+) {currency}"  # Matches price with dynamic currency

    for product in products:
        # Extract quantity
        quantity = re.search(quantity_pattern, product)
        quantity_val = int(quantity.group(1)) if quantity else None

        quantities.append(quantity_val)

        # Extract product name
        product_name = re.search(product_pattern, product)
        product_names.append(product_name.group(1).strip() if product_name else None)

        # Extract set name
        set_name = re.search(set_pattern, product)
        set_names.append(set_name.group(1).replace("Magic: The Gathering | ", "").strip() if set_name else None)

        # Extract quality
        quality = re.search(quality_pattern, product)
        qualities.append(quality.group(1).replace(" - ", "").strip() if quality else "N/A")
        
        # Extract language
        language = re.search(language_pattern, product)
        languages.append(language.group(0).strip() if language else None)
        
        foils.append("⭐" if " - Foil - " in product else "❌") #✅✖️foil.group(1).strip()
        
        # Extract price
        price = re.search(price_pattern, product)
        price_val = float(price.group(1).replace(',', '.')) if price else None
        prices.append(price_val)

        # Calculate total price (quantity * unit price)
        total_price = quantity_val * price_val if quantity_val and price_val else None
        total_prices.append(total_price)
    # Create DataFrame from parsed data with a "Total Price" column
    parsed_df = pd.DataFrame({
        quantity_column: quantities,
        product_name_column: product_names,
        set_name_column: set_names,
        "Price": prices,
        quality_column: qualities,
        foiliness_column: foils,
        language_column: languages,
        total_price_column: total_prices
    })
    
    return parsed_df


def search(product_name, set_name, user_name, date_of_purchase, foiliness, sort_by, sort_order, display_columns, limit):
    try:
        dataframe = get_dataframe()
        columns = []
        match display_columns:
            case "1":
                display_columns =  f"{product_name_column},{quantity_column},{quality_column},{foiliness_column}"
            case "2":
                display_columns =  f"{product_name_column},{set_name_column},{quantity_column},{quality_column},{language_column},{foiliness_column},Price,{date_of_purchase_column}"
            case "3":
                display_columns =  f"{product_name_column},{set_name_column},{quantity_column},{total_price_column},Price,{date_of_purchase_column},{user_name_column},{order_id_column}"
            case "4":
                display_columns =  f"{set_name_column},{product_name_column},{user_name_column},{order_id_column},{quantity_column},{total_price_column},Price,{date_of_purchase_column}"
            case "5":
               display_columns =  f"{user_name_column},{order_id_column},{shipment_cost_column},{total_price_column},Price,{date_of_purchase_column}"
            case _:
                pass

        if date_of_purchase:
            columns.append({date_of_purchase_column: date_of_purchase})
            if date_of_purchase_column not in display_columns:
                display_columns = date_of_purchase_column + "," + display_columns
        if foiliness:
            columns.append({foiliness_column: "⭐"})
            if foiliness_column not in display_columns:
                display_columns = foiliness_column + "," + display_columns
        if user_name:
            columns.append({user_name_column: user_name})
            if user_name_column not in display_columns:
                display_columns = user_name_column + "," + display_columns 
        if set_name:
            columns.append({set_name_column: set_name})
            if set_name_column not in display_columns:
                display_columns = set_name_column+ "," + display_columns 
        if product_name:
            columns.append({product_name_column: product_name})
            if product_name_column not in display_columns:
                display_columns = product_name_column + "," + display_columns             
        
        # Apply optional filtering based on product name and set name
        filtered_df = filter_data(dataframe, columns)

        # Apply sorting
        if sort_by:
            filtered_df = filtered_df.sort_values(by=sort_by, ascending=sort_order)

        # Apply column selection
        if display_columns:
            columns_to_display = [col.strip() for col in display_columns.split(',')]
            filtered_df = filtered_df[columns_to_display]

        # Display limited results
        limit_message = False
        if len(filtered_df) > limit:
            limit_message = True
        filtered_df = filtered_df.head(limit)


        # Format and print results
        formatted_output(filtered_df, limit_message, limit, display_columns)
    except Exception as e:
        print(e)

def filter_data(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    for column in columns:
        for key, value in column.items():
            if key == date_of_purchase_column:
                # Handle the date comparisons
                if value.startswith(">"):
                    # Greater than
                    value = (value[1:].strip())  # Extract date from "> yyyy-mm-dd"
                    value = datetime.strptime(value, "%Y-%m-%d").date()
                    # df = combined_df[combined_df[key] > date_value]
                    # df[key] = pd.to_datetime(df[key], errors='coerce').dt.date
                    df = df[df[key] > value]
                elif value.startswith("<"):
                    # Less than
                    value = (value[1:].strip())  # Extract date from "> yyyy-mm-dd"
                    value = datetime.strptime(value, "%Y-%m-%d").date()
                    df = df[df[key] < value]
                elif "to" in value:
                    # Between dates
                    start_date, end_date = value.split("to")
                    start_date = datetime.strptime((start_date.strip()), "%Y-%m-%d").date()
                    end_date = datetime.strptime((end_date.strip()), "%Y-%m-%d").date()

                    df = df[(df[key] >= start_date) & (df[key] <= end_date)]
            elif df[key].dtype == 'object':  # String column
                # Apply .str.contains for string columns
                df = df[df[key].str.contains(value, case=False, na=False)]
            else:
                # For non-string columns, do a direct equality comparison
                df = df[df[key] == value]
    return df

def formatted_output(df: pd.DataFrame, limit_message: bool, limit: int, display_columns: str):
    """Formats and prints the DataFrame with headers and clear formatting."""
    pd.set_option('display.max_columns', None)


    TRUNCATE_COLUMNS = {  # Define columns to truncate and their max lengths
        "Product Name": 35,
        "Set Name": 35,
    }

    def truncate_value(value, max_length):
        """Helper function to truncate values to max_length."""
        if isinstance(value, str) and len(value) > max_length:
            return value[:max_length - 1] + "-"  # Truncate and append '...'
        return value

    # Apply truncation to the specified columns
    for column, max_length in TRUNCATE_COLUMNS.items():
        if column in df.columns:
            df[column] = df[column].apply(lambda x: truncate_value(x, max_length))



    if df.empty:
        print("No results found.")
    else:
        print(df.to_string(index=False))
        if limit_message:
            print(f"[yellow]Showing the first {limit} results.[/yellow]")
