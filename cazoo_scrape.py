# Just something I put together while shopping for a new car, just scraper and potentially unstable with any changes
# made by the developers

import random
from time import sleep

import pandas as pd
import requests
from bs4 import BeautifulSoup


def get_details(details):
    """
    Processed a BeautifulSoup contents list and extracts out the details from that list
    :param details: list object of BeautifulSoup objects which feature the details of each car
    :return: Dict object with attributes from each vehicle
    """
    model = details[0].text
    model_sub = details[1].text
    mileage, reg, engine, fuel = [c.text for c in details[2].contents]
    # format mileage and reg to numeric
    mileage = int(mileage.split(' ')[0].replace(',', ''))
    year = int(reg[:4])

    return {'model': model, 'sub_type': model_sub, 'mileage': mileage, 'year': year, 'engine': engine, 'fuel': fuel}


def price_process(price_string):
    """
    Standardised process for handling any prices stored as strings
    :param price_string: string object with the price in it
    :return: returns an int value for the price
    """
    price_val = price_string.split('£')[-1]
    price_val = price_val.replace(',', '')
    return int(price_val)


def get_price(entry, old_price=None):
    """
    Collects the price value for the vehicle from the BeautifulSoup object. Can currently handle if there is reduced 
    price handle and returns both values if present (3-4% of vehicles were reduced at time of dev).
    :param entry: The BeautifulSoup object which contains the price information
    :param old_price: Which value to use as a fill for the old price value if it is not present in the dataset
    :return: two int values which contain the price and the old price, if no old price present it is replaced with None 
            as default
    """
    if entry.find(class_='full-pricestyles__OldPrice-sc-12l0fhp-2 druKTD'):
        old_price, price = [i.text for i in entry.find(class_='full-pricestyles__PriceGB-sc-12l0fhp-0 fQMXJE').contents]
        old_price = price_process(old_price)
    else:
        price = entry.find(class_='full-pricestyles__PriceGB-sc-12l0fhp-0 lcuIyU').text
    # Convert/clean strings
    price = price_process(price)
    return price, old_price


def scrape_entry(entry):
    """
    Takes a BeautifulSoup object and extracts out the vehicle details and price. 
    :param entry: A BeautifulSoup object with the entry details from Cazoo. This is the form of extracting data from a 
    "grid" entry on the current site.
    :return: A dict object containing all the details and price for a vehicle
    """
    details = entry.find(class_='vehicle-cardstyles__DetailWrap-sc-1bxv5iu-5 kXMHHU').contents
    price, old_price = get_price(entry)

    # Process results into dict
    results = get_details(details)
    results['price'] = price
    results['old_price'] = old_price
    return results


def get_page_count(soup_obj):
    """
    Takes a BeautifulSoup object and extracts the max page number from the bottom of the page.
    This can be used to calculate the number of loops required to process the full dataset
    :param soup_obj: This is the BeautifulSoup object for the whole page
    :return: an int which is the number of total pages with the results from 
    """
    pages = soup_obj.find_all(
        class_='paginationstyles__StyledPaginationItem-sc-1pjwu78-1 paginationstyles__StyledPageItem-sc-1pjwu78-3 hbGThF')
    num = pages[-1].text.split()[-1]
    return int(num)


def code_stability_check(resp):
    """
    Function acts as a breaker if essential html classes are missing from the script. Can be used to check whether the 
    web page design has been changed.The script could still fail if there has been formatting changes in the vehicle 
    details section
    :param resp: a requests response object which would contain an example of a page
    """
    soup = BeautifulSoup(resp.text, 'lxml')
    used_classes = {'Vehicles': 'vehicle-cardstyles__Card-sc-1bxv5iu-0 giiAxy',
                    'Page numbers': 'paginationstyles__StyledPaginationItem-sc-1pjwu78-1 paginationstyles__StyledPageItem-sc-1pjwu78-3 hbGThF',
                    'Pricing': 'full-pricestyles__PriceGB-sc-12l0fhp-0 fQMXJE',
                    'Old Pricing': 'full-pricestyles__OldPrice-sc-12l0fhp-2 druKTD'}
    missing = []
    for k, v in used_classes.items():
        if not soup.find(class_=v):
            missing.append(k)
    if missing:
        message = '\n\t'.join([f'{m}: {used_classes[m]}' for m in missing])
        raise Exception(f"Error the following classes are missing/outdated:\n\t{message}")


def scrape_page_of_results(response, return_pages=False):
    """
    Takes the data from a requests response and processes each vehicle found on a page
    :param response: a requests response object from the url of page
    :param return_pages: Bool. Used to return the total number of pages per request.
    :return: a Pandas DataFrame with the results of the scrape present.
    """
    soup = BeautifulSoup(response.text, 'lxml')
    page_results = []
    for e in soup.find_all(class_='vehicle-cardstyles__Card-sc-1bxv5iu-0 giiAxy'):
        page_results.append(scrape_entry(e))

    if return_pages:
        return pd.DataFrame(page_results), get_page_count(soup)
    else:
        return pd.DataFrame(page_results)


if __name__ == '__main__':
    # Config stage.
    # Using params to handle the parameters used in selection. In this example only 4-5 door cars and purchase only
    base_url = 'https://www.cazoo.co.uk/cars/'
    output_csv = 'cazoo_data.csv'
    r_params = {'chosenPriceType': 'total',
                'ownershipType': 'purchase',
                'numDoors': '4%2C5'}

    # Read base page, collect total page count for use in loop later
    response = requests.get(base_url, params=r_params)
    code_stability_check(response)  # Breaks the script if tags have been changed

    df, page_count = scrape_page_of_results(response, True)
    df.to_csv(output_csv, index=False)

    # Run for all pages
    for i in range(2, page_count + 1):
        # Forced sleep to prevent hammering server, randomness to represent more human-like behaviour
        # 3 to 6 calls a minute
        sleep_val = random.choice(range(10, 20))
        sleep(sleep_val)
        r_params['page'] = i
        response = requests.get(base_url, params=r_params)
        df = scrape_page_of_results(response)

        # append data
        df.to_csv(output_csv, mode='a', header=False, index=False)
        print(f'Page {i}/{page_count} complete', end='\r')
