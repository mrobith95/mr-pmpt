import numpy as np
import pandas as pd
# from datetime import datetime, timedelta
import riskfolio as rp
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mtick
from download_data_bulk import download_data_check

def do_analysis(tick_list, risk_float, isit_rp):
    to_download =  ['AAPL', 'AMGN', 'AMZN', 'AXP', 'BA',
                    'CAT', 'CRM', 'CSCO', 'CVX', 'DIS',
                    'GS', 'HD', 'HON', 'IBM', 'JNJ',
                    'JPM', 'KO', 'MCD', 'MMM', 'MRK',
                    'MSFT', 'NKE', 'NVDA', 'PG', 'SHW',
                    'TRV', 'UNH', 'V', 'VZ', 'WMT',
                    'GC=F', 'SI=F', 'PL=F', 'PA=F', 'HG=F',
                    'CL=F', 'BZ=F', 'NG=F', 'HO=F', 'RB=F', 
                    'BTC-USD', 'ETH-USD', 'XRP-USD', 'BNB-USD', 'SOL-USD', 
                    'DOGE-USD', 'ADA-USD', 'TRX-USD', 'SUI20947-USD', 'LINK-USD']
    download_data_check(to_download)
    risk_float = float(risk_float)
    # isit_rp = False

    ## look for what symbols used
    symbol_used = [False]*len(to_download)
    symbol_name = [None]*len(to_download)
    for i in range(len(to_download)):
        if to_download[i] in tick_list: ## check if a symbol used
            symbol_used[i] = True
            symbol_name[i] = to_download[i]
    # print(symbol_used)
    n_symbol = sum(symbol_used)

    # ## prepare data of return
    # all_return = [None]*n_symbol

    count = -1 # counter

    ## read multiple symbols
    first_time = True
    for i in range(len(to_download)):
        if symbol_used[i]:
            count = count + 1 ## modify counter
            stock = to_download[i]
            raw_data = pd.read_csv('data/'+stock+'.csv')
            data = raw_data.copy() # copy

            ## remove latest rows that is NaN
            kk = max(data.index)
            while pd.isna(data.loc[kk,'Close']):
                data = data.drop(kk)
                kk = kk-1

            data = data.drop(max(data.index)) # remove latest candle. We assume this candle still forming

            if first_time:
                rekam_close = data[['Date', 'Close']].copy() ## save rekam_close first
                rekam_close.rename({'Close': stock+'_close'}, axis=1, inplace=True)
                first_time = False
            else:
                rekam_close_new = data[['Date', 'Close']].copy() ## save rekam_close first
                rekam_close_new.rename({'Close': stock+'_close'}, axis=1, inplace=True)
                rekam_close = rekam_close.merge(rekam_close_new, on='Date', how='outer')
            

    rekam_close = rekam_close.dropna() ## drop naNs ANYWHERE

    ## now compute return
    rekam_return = rekam_close.copy()

    for i in range(len(to_download)):
        if symbol_used[i]:
            count = count + 1 ## modify counter
            stock = to_download[i]

            rekam_return[stock] = rekam_close[stock+'_close'].pct_change()
            rekam_return.drop(stock+'_close', axis=1, inplace=True)

    # rekam_return_ori = rekam_return.copy() # note that this still has NaNs at first-appear index
    rekam_return = rekam_return.dropna() ## drop naNs ANYWHERE
    rekam_return_date = rekam_return['Date'].astype('datetime64[ns]') ## save date data
    # all_return_np = np.array(rekam_return.drop('Date', axis=1)).T
    rekam_return = rekam_return.drop('Date', axis=1) # menyesuaikan input untuk riskfolio-lib
    # print('====')

    ## do optimization

    # make portofolio object
    port = rp.Portfolio(returns=rekam_return)

    # choose mean and covariance estimation
    method_mu = 'hist'
    method_cov = 'hist'
    port.assets_stats(method_mu = method_mu, method_cov=method_cov)

    # Estimate portofolio
    model = 'Classic' #classic opt.
    rm = 'MV' #risk measure
    obj = 'Sharpe' # can be 'MinRisk', 'MaxRet', 'Utility', 'Sharpe' for risk-adjusted return
    hist = True 
    rf = 0 #risk-free return
    raf = 0 #risk aversion factor for 'Utility' objective

    if isit_rp:
        rp_w = port.rp_optimization(model=model, rm=rm, hist=hist, rf=rf, b=None)

        disprpw = rp_w.copy()
        disprpw = 100*disprpw
        disprpw = (disprpw.round(2))

        out_w = rp_w.copy()
        disp_out_w = disprpw.copy()

    else:

        w = port.optimization(model=model, rm=rm, obj=obj, hist=hist, rf=rf, l=raf)
        dispw = w.copy()

        # dispw untuk keperlu display only
        dispw = 100*dispw
        dispw = (dispw.round(2))

        # print(w)
        # print('-====')

        if risk_float == 0:
            # print(dispw)
            out_w = w.copy()
            disp_out_w = dispw.copy()
            # print('return w dan dispw')

        else:

            ## get info on expected return, covariance, and returns
            mu = port.mu
            cov = port.cov
            return_port = port.returns

            ## get info on w's return and risk
            best_return = ((mu @ w).loc[0,'weights'])*252 # this is annual return, considering daily data
            best_risk   = rp.Sharpe_Risk(w=w, cov=cov, returns=return_port, rm=rm, rf=rf, alpha=0.05)*(252**0.5) # daily factor included

            # efficient frontier limit for cons and aggresive models
            limits = port.frontier_limits(model=model, rm=rm, rf=rf, hist=hist)

            # get info on limits' return and risk
            min_ret = ((mu @ limits['w_min']).loc[0])*252
            min_risk = rp.Sharpe_Risk(w=limits['w_min'], cov=cov, returns=return_port, rm=rm, rf=rf, alpha=0.05)*(252**0.5)
            max_ret = ((mu @ limits['w_max']).loc[0])*252
            max_risk = rp.Sharpe_Risk(w=limits['w_max'], cov=cov, returns=return_port, rm=rm, rf=rf, alpha=0.05)*(252**0.5)

            ## quick pick
            if risk_float == 1:
                agg_w = limits['w_max'].to_frame().copy().rename({'w_max':'weights'}, axis=1)
            elif risk_float == -1:
                agg_w = limits['w_min'].to_frame().copy().rename({'w_min':'weights'}, axis=1)
            else:
                ## set reference for constraint
                if risk_float > 0:
                    agg_ret = (best_return + (risk_float)*(max_ret - best_return))/252
                    agg_risk = (best_risk + (risk_float)*(max_risk - best_risk))/(252**0.5)
                elif risk_float < 0:
                    agg_ret = (best_return + (risk_float)*(best_return - min_ret))/252
                    agg_risk = (best_risk + (risk_float)*(best_risk - min_risk))/(252**0.5)

                ## redo optimization
                port.lowerret = agg_ret
                port.upperdev = agg_risk

                agg_w = port.optimization(model=model, rm=rm, obj=obj, hist=hist, rf=rf, l=raf)

            dispaggw = agg_w.copy()
            dispaggw = 100*dispaggw
            dispaggw = (dispaggw.round(2))

            # print('====')
            # print(dispaggw)
            out_w = agg_w.copy()
            disp_out_w = dispaggw.copy()

    # print(disp_out_w)

    ## display data of expected return, standard deviation, risk-adjusted return, max drawdown

    ## get info on expected return, covariance, and returns
    mu = port.mu
    cov = port.cov
    return_port = port.returns

    ## compute data
    best_return = ((mu @ out_w).loc[0,'weights'])*252 # this is annual return, considering daily data
    best_stdev  = rp.Sharpe_Risk(w=out_w, cov=cov, returns=return_port, rm=rm, rf=rf, alpha=0.05)*(252**0.5) # daily factor included
    best_adjret = best_return/best_stdev
    best_mdd    = rp.Sharpe_Risk(w=out_w, cov=cov, returns=return_port, rm='MDD', rf=rf, alpha=0.05)

    ## compute additional info
    best_var =  rp.Sharpe_Risk(w=out_w, cov=cov, returns=return_port, rm='VaR', rf=rf, alpha=0.05)
    best_cvar =  rp.Sharpe_Risk(w=out_w, cov=cov, returns=return_port, rm='CVaR', rf=rf, alpha=0.05)
    best_worst = rp.Sharpe_Risk(w=out_w, cov=cov, returns=return_port, rm='WR', rf=rf, alpha=0.05)
    best_add = rp.Sharpe_Risk(w=out_w, cov=cov, returns=return_port, rm='ADD', rf=rf, alpha=0.05)
    best_dar = rp.Sharpe_Risk(w=out_w, cov=cov, returns=return_port, rm='DaR', rf=rf, alpha=0.05)
    best_cdar = rp.Sharpe_Risk(w=out_w, cov=cov, returns=return_port, rm='CDaR', rf=rf, alpha=0.05)

    # print(best_return)
    # print(best_stdev)
    # print(best_adjret)
    # print(best_mdd)

    ## consider equal weighting
    eq_w = out_w.copy()
    eq_w['weights'] = 1/len(eq_w)

    ## compute data from this equal weighting
    eq_return = ((mu @ eq_w).loc[0,'weights'])*252 # this is annual return, considering daily data
    eq_stdev  = rp.Sharpe_Risk(w=eq_w, cov=cov, returns=return_port, rm=rm, rf=rf, alpha=0.05)*(252**0.5) # daily factor included
    eq_adjret = eq_return/eq_stdev
    eq_mdd    = rp.Sharpe_Risk(w=eq_w, cov=cov, returns=return_port, rm='MDD', rf=rf, alpha=0.05)

    # print('-----')
    # print(eq_return)
    # print(eq_stdev)
    # print(eq_adjret)
    # print(eq_mdd)

    ## make comparison table
    ini_comp = {}
    ini_comp['Metrics'] = ['Annual Expected Return (%)', 'Annual Standard Deviation (%)', 'Risk-Adjusted Return (ER/SD, %)', 'Annual Max. Drawdown* (%)']
    ini_comp['Optimized'] = [best_return, best_stdev, best_adjret, best_mdd]
    ini_comp['Equal Weight'] = [eq_return, eq_stdev, eq_adjret, eq_mdd]

    pd_comp = pd.DataFrame(ini_comp)
    pd_comp_disp = pd_comp.copy()
    pd_comp_disp['Optimized'] = (100*pd_comp_disp['Optimized']).round(2)
    pd_comp_disp['Equal Weight'] = (100*pd_comp_disp['Equal Weight']).round(2)
    # print(pd_comp_disp)

    ## plotting important stuff
    out_w = out_w.rename({'weights':'Optimized*'}, axis=1)
    eq_w = eq_w.rename({'weights':'Equal Weight*'}, axis=1)
    all_w = pd.concat([out_w, eq_w],axis=1)
    return_daily = rekam_return @ all_w

    # ## plotting cumulative compounded of portfolios
    # all_w = all_w.rename()
    # # print(all_w)
    # # print(rekam_return.shape)
    # # print(out_w.shape)
    # ax_ser = rp.plot_series(returns = rekam_return, w = out_w) ## probably will use our own
    # plt.show()
    # ## custom
    # compute return via matmul


    # compute cumulative product
    return_daily['Optimized'] = (1+return_daily['Optimized*']).cumprod()
    return_daily['Equal Weight'] = (1+return_daily['Equal Weight*']).cumprod()

    ## define fig and ax for these
    fig_ser_cust, ax_ser_cust = plt.subplots(figsize=(9,6))

    ## pick data to plot and its label
    ax_ser_cust.plot(rekam_return_date, return_daily[['Equal Weight','Optimized']], label=['Equal Weight','Optimized'])

    ## legend, datetime modifier, grid, title, and layout
    ax_ser_cust.legend()
    ax_ser_cust.grid(True)
    ax_ser_cust.set_title('Historical Compounded Cumulative Returns')
    ax_ser_cust = plt.tight_layout()
    ax_ser_cust = plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    ax_ser_cust = plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

    plt.close(fig_ser_cust) ## close plots

    # plt.show()

    # # plot portfolio composition
    fig_pie, ax_pie = plt.subplots(figsize=(9,6))
    ax_pie = rp.plot_pie(w=out_w, title='Asset Composition', others=0.05) # plot kepotong
    ax_pie.set_aspect('auto')

    plt.close(fig_pie) ## close plots

    # plot hist return
    # ax_hist = rp.plot_hist(returns = rekam_return, w = out_w) # work, but probably need our own
    ## special: binning
    bin_spec = np.arange(np.floor(min(100*return_daily['Optimized*'])),
                        np.ceil(max(100*return_daily['Optimized*']))+0.25,
                        0.25)

    fig_hist, ax_hist = plt.subplots(figsize=(9,6))
    ax_hist.hist(100*return_daily['Optimized*'], bins=bin_spec,
                weights=np.ones_like(return_daily['Optimized*'])/len(return_daily['Optimized*']),
                edgecolor='black', alpha=0.7)
    ax_hist.axvline(100*best_return/252, label=f'Mean: {round(100*best_return/252,2)}%', color='#ff7f0e', lw=2)
    ax_hist.axvline(-100*best_var, label=f'95% VaR: {round(-100*best_var,2)}%', color='#2ca02c', lw=2)
    ax_hist.axvline(-100*best_cvar, label=f'95% CVaR: {round(-100*best_cvar,2)}%', color='#d62728', lw=2)
    ax_hist.axvline(-100*best_worst, label=f'Worst: {round(-100*best_worst,2)}%', color='#9467bd', lw=2)
    ax_hist.legend()
    ax_hist.grid(True)
    ax_hist.set_title('Portfolio Returns Histogram')
    ax_hist.set_ylabel('Probability Density')
    ax_hist = plt.tight_layout()
    ax_hist = plt.gca().xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'{x:.2f}%'))
    ax_hist = plt.gca().xaxis.set_major_locator(mtick.MultipleLocator(1))
    ax_hist = plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))
    #plt.show()

    plt.close(fig_hist) ## close plots

    # # plot drawdown
    # ax_dd = rp.plot_drawdown(returns = rekam_return, w = out_w) # work, but probably need our own
    # plt.show()

    ## buat drawdown dlu
    # print(return_daily)
    running_sum = return_daily['Optimized*'].cumsum()
    running_max = running_sum.cummax()
    return_daily['drawdown'] = (running_sum - running_max)
    # print(return_daily)


    fig_dd, ax_dd = plt.subplots(figsize=(9,6))
    ax_dd.plot(rekam_return_date, return_daily['drawdown'])
    ax_dd.fill_between(rekam_return_date, return_daily['drawdown'], 0, alpha=0.3)
    ax_dd.set_ylim(return_daily['drawdown'].min()*1.1, 0)
    ax_dd.axhline(-1*best_add, label=f'Mean DD: {round(-100*best_add,2)}%', color='#ff7f0e', lw=2)
    ax_dd.axhline(-1*best_dar, label=f'95% DaR: {round(-100*best_dar,2)}%', color='#2ca02c', lw=2)
    ax_dd.axhline(-1*best_cdar, label=f'95% CDaR: {round(-100*best_cdar,2)}%', color='#d62728', lw=2)
    ax_dd.axhline(-1*best_mdd, label=f'Max DD: {round(-100*best_mdd,2)}%', color='#9467bd', lw=2)
    ax_dd.legend()
    ax_dd.grid(True)
    ax_dd.set_title('Historical Uncompounded Drawdown')
    ax_dd = plt.tight_layout()
    ax_dd = plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))
    # plt.show()
    plt.close(fig_dd) ## close plots

    ## modify output
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

    map_ticker = {isi_tick[i]: isi_dropdown[i] for i in range(len(isi_dropdown))}
    disp_out_w = disp_out_w.rename(map_ticker)
    disp_out_w_2 = disp_out_w.reset_index(names='Tickers')
    disp_out_w_2 = disp_out_w_2.rename({'weights':'Weights (%)'}, axis=1)

    return disp_out_w, fig_pie, disp_out_w_2, pd_comp_disp, fig_ser_cust, fig_hist, fig_dd