import yfinance as yf
import pandas as pd
import os
import pytz
from datetime import datetime, timedelta

def download_data_bulk(to_download):

    alldata = yf.download(to_download, period='2y', ## klo tanpa period downloadnya sepanjang masa
                        rounding = True)
    alldata = alldata.reset_index() ## buat tanggal jadi data, bukan index
    ##print(alldata)
    ##print(alldata[('Close', 'AAPL')]) ## akses kolom
    ##print(alldata['Date']) ## akses tanggal

    ## making 'long string' format for Tickers
    ini_str = ''
    for stock in to_download:
        ini_str = ini_str+' '+stock
    ini_str = ini_str[1:]
    ##print(ini_str)

    ## saving long name to a csv
    allinfo = yf.Tickers(ini_str)
    for stock in to_download:
        pass

    #now saving data in pandas.
    for stock in to_download:
        ini_dict = {}
        ini_dict['Date'] = list(alldata['Date'])
        ini_dict['Open'] = list(alldata[('Open', stock)])
        ini_dict['High'] = list(alldata[('High', stock)])
        ini_dict['Low'] = list(alldata[('Low', stock)])
        ini_dict['Close'] = list(alldata[('Close', stock)])
        ini_dict['Volume'] = list(alldata[('Volume', stock)])
        ##print(ini_dict)

        ini_df = pd.DataFrame.from_dict(ini_dict)
        ##print(ini_df)

        ini_df.to_csv('data/'+stock+'.csv')
        ## NOTE: downloaded data still has index in it

def download_data_check(to_download):

    ## check if data folder exist. If not, add the folder
    if not os.path.exists('data'):
        os.makedirs('data')

    ## look for metadata.csv inside that folder. If it is not exist, download data
    ## if it is exist, read the data
    file_exists = os.path.isfile('data/metadata.csv')
    if file_exists:

        ## get today data
        timezone = pytz.timezone('Asia/Singapore')  # GMT+8
        local_time = datetime.now(timezone)
        local_str = local_time.strftime("%Y-%m-%d %H:%M:%S.%f%z")

        # read when the data was last updated
        ini_meta = pd.read_csv('data/metadata.csv', parse_dates=['Last Updated'])
        latest_update = ini_meta.loc[0,'Last Updated']

        ## add 1 day for update time threshold
        date_thres = latest_update + timedelta(days=1)

        if local_time > date_thres:
            download_data_bulk(to_download) ## download data

            ini_dict = {}
            ini_dict['Key'] = ['Value']
            ini_dict['Last Updated'] = [local_time]
            ini_df = pd.DataFrame(ini_dict)
            ini_df.to_csv('data/metadata.csv')

    ##otherwise, download and make metadata.csv 
    else:
        download_data_bulk(to_download) ## download data
        
        ## get today data, then save it on dataframe
        timezone = pytz.timezone('Asia/Singapore')  # GMT+8
        local_time = datetime.now(timezone)
        # local_str = local_time.strftime("%Y-%m-%d %H:%M:%S.%f%z")

        ini_dict = {}
        ini_dict['Key'] = ['Value']
        ini_dict['Last Updated'] = [local_time]
        ini_df = pd.DataFrame(ini_dict)
        ini_df.to_csv('data/metadata.csv')



