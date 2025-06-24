import gradio as gr
import pandas as pd
from do_analysis import *

# globals
isi_dropdown = ['Apple (AAPL)',
                'Amgen (AMGN)',
                'Amazon (AMZN)',
                'American Express (AXP)',
                'Boeing (BA)',
                'Caterpillar (CAT)',
                'Salesforce (CRM)',
                'Cisco (CSCO)',
                'Chevron (CVX)',
                'Disney (DIS)',
                'Goldman Sachs (GS)',
                'Home Depot (HD)',
                'Honeywell (HON)',
                'IBM (IBM)',
                'Johnson & Johnson (JNJ)',
                'JPMorgan Chase (JPM)',
                'Coca-Cola (KO)',
                "McDonald's (MCD)",
                '3M (MMM)',
                'Merck (MRK)',
                'Microsoft (MSFT)',
                'Nike (NKE)',
                'Nvidia (NVDA)',
                'Procter & Gamble (PG)',
                'Sherwin-Williams (SHW)',
                'Travelers (TRV)',
                'UnitedHealth Group (UNH)',
                'Visa (V)',
                'Verizon (VZ)',
                'Walmart (WMT)',
                'Gold', 'Silver', 'Platinum', 'Palladium', 'Copper',
                'WTI Crude Oil', 'Brent Crude Oil', 'Natural Gas', 'Heating Oil', 'RBOB Gasoline',
                'Bitcoin', 'Ethereum', 'XRP (Ripple)', 'Binance Coin', 'Solana',
                'Dogecoin', 'Cardano', 'Tron (Tronix)', 'Sui', 'Chainlink']
isi_tick = ['AAPL', 'AMGN', 'AMZN', 'AXP', 'BA',
            'CAT', 'CRM', 'CSCO', 'CVX', 'DIS',
            'GS', 'HD', 'HON', 'IBM', 'JNJ',
            'JPM', 'KO', 'MCD', 'MMM', 'MRK',
            'MSFT', 'NKE', 'NVDA', 'PG', 'SHW',
            'TRV', 'UNH', 'V', 'VZ', 'WMT',
            'GC=F', 'SI=F', 'PL=F', 'PA=F', 'HG=F', # Gold, Silver, Platinum, Palladium, Copper
            'CL=F', 'BZ=F', 'NG=F', 'HO=F', 'RB=F', # Crude Oil, Brent Crude Oil, Natural Gas, Heating Oil, RBOB Gasoline
            'BTC-USD', 'ETH-USD', 'XRP-USD', 'BNB-USD', 'SOL-USD', # Bitcoin, Ethereum, XRP, BNB, Solana
            'DOGE-USD', 'ADA-USD', 'TRX-USD', 'SUI20947-USD', 'LINK-USD'] # Dogecoin, Cardano, TRON, Sui, Chainlink

ini_dict = {isi_dropdown[i]: isi_tick[i] for i in range(len(isi_dropdown))}
ini_df = pd.Series(ini_dict)

def_ac = {'Tickers': [' '], 'Weights (%)': [' ']}
def_ac = pd.DataFrame(def_ac)

ini_comp = {}
ini_comp['Metrics'] = ['Annual Expected Return (%)', 'Annual Standard Deviation (%)', 'Risk-Adjusted Return (ER/SD, %)', 'Annual Max. Drawdown* (%)']
ini_comp['Optimized'] = [0, 0, 0, 0]
ini_comp['Equal Weight'] = [0, 0, 0, 0]
pd_comp = pd.DataFrame(ini_comp)

def grafik_lilin(ticker_choice, risk_type, is_rp):

    ## check input: ticker must be larger than 1
    if ticker_choice is None or len(ticker_choice) < 2:
        raise gr.Error('Choose at least 2 tickers.', duration=5)

    if is_rp == 'Maximize Risk-adjusted Return':
        logik_rp = False
    else:
        logik_rp = True

    ## warning: move moderate / risk parity to conservative / risk parity
    if risk_type == 'Moderate' and logik_rp:
        risk_type = 'Conservative'
        gr.Warning('Risk Parity with Moderate Risk seems to be not working. Risk replaced to Conservative instead.', duration=5)

    abbrev = ini_df[ticker_choice]
    luaran, fig_comp, out_w, performance, fig_ser, fig_hist, fig_dd = do_analysis(abbrev.tolist(), risk_type, logik_rp)
    # print(luaran)
    return fig_comp, out_w, performance, fig_ser, fig_hist, fig_dd

## preset for ticker selection
def stock_only(exist): #choose stock only
    ini_val = set(isi_dropdown[0:30])

    if exist is None:
        exist = []

    new_val = list(set(exist) | ini_val)
    new_val.sort()

    ## loop
    luaran = []
    for isi in isi_dropdown:
        if isi in new_val:
            luaran.append(isi)

    return gr.update(value=luaran)

def metal_only(exist): #choose metals only
    ini_val = set(isi_dropdown[30:35])

    if exist is None:
        exist = []

    new_val = list(set(exist) | ini_val)
    new_val.sort()

    ## loop
    luaran = []
    for isi in isi_dropdown:
        if isi in new_val:
            luaran.append(isi)

    return gr.update(value=luaran)

def energy_only(exist): #choose energy only
    ini_val = set(isi_dropdown[35:40])

    if exist is None:
        exist = []

    new_val = list(set(exist) | ini_val)
    new_val.sort()

    ## loop
    luaran = []
    for isi in isi_dropdown:
        if isi in new_val:
            luaran.append(isi)

    return gr.update(value=luaran)

def crypto_only(exist): #choose crypto only
    ini_val = set(isi_dropdown[40:50])

    if exist is None:
        exist = []

    new_val = list(set(exist) | ini_val)
    new_val.sort()

    ## loop
    luaran = []
    for isi in isi_dropdown:
        if isi in new_val:
            luaran.append(isi)

    return gr.update(value=luaran)

# ## define function to map keys to values
# def key2val_dropdown(chosen):


#     return ini_dict.get(chosen, '---')

with gr.Blocks() as demo:

    gr.Markdown(
        """
        # mr-pmpt
        Portfolio optimization web-app

        Scroll to How it works section to read on how to use this web-app.

        __DISCLAIMER:__ Past performance doesn't always translate into the future. Weightings and/or asset composition given in this web-app should not be taken as financial advice.
        """
    )
    gr.Markdown("""## Ticker Input """)

    ticker_choice = gr.Dropdown(isi_dropdown, multiselect=True, label='Choose Tickers', info='Choose at least 2 from this list')
    ## note: multiselect return a list, so it is ordered

    with gr.Row():
        gr.Markdown("""__Add Preset :__ """)
        stock_button = gr.Button('Stocks')
        metal_button = gr.Button('Metals')
        energy_button = gr.Button('Energies')
        crypto_button = gr.Button('Cryptos')

    with gr.Row():
        risk_type = gr.Dropdown(['Conservative','Moderate','Aggresive'], 
                                label='Risk Tolerance',
                                info='Choose Risk Type',
                                value='Moderate')
        is_rp     = gr.Dropdown(['Maximize Risk-adjusted Return','Spread Risk Across Selected Assets'], 
                                label='Allocation Strategy',
                                info='Choose Allocation Strategy',
                                value='Maximize Risk-adjusted Return')

    submit_button = gr.Button("Submit", variant='primary')

    gr.Markdown("""## Assets Composition """)
    asset_fig = gr.Plot(label='asset-composition-plot', format='png')
    asset_comp = gr.Dataframe(label='asset-composition', value=def_ac)

    gr.Markdown("""## Performance Comparison """)
    perf_comp = gr.Dataframe(label='performance-comparison', value=pd_comp)
    gr.Markdown("""(*) Max Drawdown computed from _realized_ loss based on uncompounded cumulated returns.""")

    gr.Markdown("""## Historical Compounded Cumulative Returns """)
    ret_comp = gr.Plot(label='historical-compounded-cumulative-returns', format='png')

    gr.Markdown("""## Portfolio Returns Histogram """)
    ret_hist = gr.Plot(label='return-histogram', format='png')

    gr.Markdown("""## Historical Uncompounded Drawdown """)
    dd_hist = gr.Plot(label='historical-drawdown', format='png')

    # with gr.Row():
    #     symbol_choice = gr.Dropdown(isi_dropdown, label='Available Tickers', info="Choose 1 from the following list.")
    #     pi_1 = gr.Number(label="Prediction Interval (in %)", info="Enter value between 1 and 99 for Prediction Interval.",
    #                           value=95)
    #     pi_2 = gr.Number(label="more Prediction Interval (in %, optional)", info="Enter value between 1 and 99 for more Prediction Interval. 0 is treated as not using more PI.",
    #                      value = 0)

    # submit_button = gr.Button("Submit", variant='primary')
    # plot_result = gr.Plot(label='candlestick-chart', format='png')
    # pred_dict = gr.Dataframe(label='prediction-table')
    gr.Markdown(
        """
        ## How it works
        1. Choose 2 or more available tickers on Ticker Input section, or choose asset classes you prefer there.
        2. Choose Allocation Strategy. (Maximize risk-adjusted return / Spread risk across selected assets)
        3. Select Risk Tolerance. (Conservative, Moderate, Aggresive)
        4. Click Submit.
        5. Wait for the result to appear (especially when it is the first time you click submit). 
        
        Data is taken from yahoo finance, analysis is conducted by riskfolio-lib. Note that the historical data used for analysis might be delayed.
        """
    )

    # # # display chart only after submit button is clicked
    submit_button.click(fn=grafik_lilin,
                        inputs=[ticker_choice, risk_type, is_rp],
                        outputs=[asset_fig, asset_comp, perf_comp,
                                 ret_comp, ret_hist, dd_hist])
    
    # # # preset buttons
    stock_button.click(fn=stock_only,
                       inputs=ticker_choice,
                       outputs=ticker_choice)
    
    metal_button.click(fn=metal_only,
                       inputs=ticker_choice,
                       outputs=ticker_choice)
    
    energy_button.click(fn=energy_only,
                       inputs=ticker_choice,
                       outputs=ticker_choice)
    
    crypto_button.click(fn=crypto_only,
                       inputs=ticker_choice,
                       outputs=ticker_choice)

demo.launch()
