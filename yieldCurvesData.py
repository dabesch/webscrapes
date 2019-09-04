"""
Web scrape for collecting the yield curve data from the US Treasury page.
I do not collect the original data, and the data belongs to www.treasury.gov

Methodology used described here:
https://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/yieldmethod.aspx
"""
from bs4 import BeautifulSoup
import requests
import pandas as pd


def getXML():
    fileURL = 'http://data.treasury.gov/feed.svc/DailyTreasuryYieldCurveRateData'
    response = requests.get(fileURL)
    soup = BeautifulSoup(response.text, 'xml')
    updated = soup.find('updated')
    print(updated)
    entries = soup.find_all('entry')
    return entries


def getSeries(entry):
    res = []
    fields = ['NEW_DATE', 'BC_1MONTH', 'BC_2MONTH', 'BC_3MONTH', 'BC_6MONTH', 'BC_1YEAR', 'BC_2YEAR', 'BC_3YEAR',
              'BC_5YEAR', 'BC_7YEAR', 'BC_10YEAR', 'BC_20YEAR', 'BC_30YEAR']
    for f in fields:
        e = entry.properties.find(f)
        if 'm:null' in e.attrs:
            res.append(None)
        else:
            res.append(e.contents[0])
    return pd.DataFrame(res, index=fields).T


def produceDF():
    entries = getXML()
    df = pd.concat([getSeries(e) for e in entries])

    df.columns = ['date', '1', '2', '3', '6', '12', '24', '36', '60', '84', '120', '240', '360']
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    for c in df.columns:
        df[c] = pd.to_numeric(df[c])

    return df
