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
                'Gold (GC=F)', 'Silver (SI=F)', 'Platinum (PL=F)', 'Palladium (PA=F)', 'Copper (HG=F)',
                'WTI Crude Oil (CL=F)', 'Brent Crude Oil (BZ=F)', 'Natural Gas (NG=F)', 'Heating Oil (HO=F)', 'RBOB Gasoline (RB=F)',
                'Bitcoin (BTC-USD)', 'Ethereum (ETH-USD)', 'XRP (Ripple) (XRP-USD)', 'Binance Coin (BNB-USD)', 'Solana (SOL-USD)',
                'Dogecoin (DOGE-USD)', 'Cardano (ADA-USD)', 'Tron (Tronix) (TRX-USD)', 'Sui (SUI20947-USD)', 'Chainlink (LINK-USD)']
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
        risk_float = gr.Slider(minimum=-1, maximum=1, value=0, step=0.01, label='Risk Tolerance',
                               info="""Use the slider to determine risk tolerance, ot type between -1 to 1. Default is 0.
                                The more left/right the slider, more conservative/aggresive portfolio is.
                                Beware: Too aggresive porftfolios might use only 1 asset! """)
        is_rp     = gr.Dropdown(['Maximize Risk-adjusted Return','Spread Risk Across Assets (Risk Parity)'], 
                                label='Allocation Strategy',
                                info="""Choose Allocation Strategy.
                                For now, Risk parity ignores risk tolerance""",
                                value='Maximize Risk-adjusted Return')

    submit_button = gr.Button("Submit", variant='primary')

    gr.Markdown("""## Assets Composition """)
    asset_fig = gr.Plot(label='asset-composition-plot', format='png')
    asset_comp = gr.Dataframe(label='asset-composition', value=def_ac)
    gr.Markdown("""Plot and table above showing the percentage allocation of each asset in a portfolio. For example: If ABC's weight is 10% and your balance is 1000 USD, then you should allocate 100 USD to buy ABC.""")

    gr.Markdown("""## Performance Comparison """)
    perf_comp = gr.Dataframe(label='performance-comparison', value=pd_comp)
    gr.Markdown("""* Annual Expected Return is the average return a portfolio is expected to generate in one year, based on historical data.
                * Annualized Standard Deviation is a measure of the volatility or risk of a portfolio's returns over a year, indicating how much the returns typically deviate from the average.
                * Annualized Risk-adjusted Return is Annualized Expected Return / Annualized Standard Deviation, displayed as percentage. 
                * Max Drawdown is the largest peak-to-trough decline in portfolio value over 2 years, showing the worst historical loss before a recovery. On more techincal detail, Drawdowns are computed from uncompounded cumulative returns.""")

    gr.Markdown("""## Historical Compounded Cumulative Returns """)
    ret_comp = gr.Plot(label='historical-compounded-cumulative-returns', format='png')
    gr.Markdown("""This plot describes total return of a portfolio over 2 years assuming reinvestment of profits, compounded at each time step.""")

    gr.Markdown("""## Portfolio Returns Histogram """)
    ret_hist = gr.Plot(label='return-histogram', format='png')
    gr.Markdown("""This bar plot showing the distribution of portfolio returns over 2 years, visualizing frequency and range of returns. 
                
                * Value at Risk (VaR) estimates the maximum expected loss at a 95% confidence level, while Conditional Value at Risk (CVaR) is the average loss beyond the VaR threshold.""")

    gr.Markdown("""## Historical Uncompounded Drawdown """)
    dd_hist = gr.Plot(label='historical-drawdown', format='png')
    gr.Markdown("""This plot showing the percentage losses from the most recent peak without compounding the effects over 2 years.
                
                * Drawdown at Risk (DaR) measures the potential drawdown at a 95% confidence level, and Conditional Drawdown at Risk (CDaR) averages the worst drawdowns beyond that level.""")

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
                        inputs=[ticker_choice, risk_float, is_rp],
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
