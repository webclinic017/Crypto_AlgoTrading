import time
import backtrader as bt
import datetime as dt
import pandas as pd
from config import BINANCE, ENV, PRODUCTION, COIN_TARGET, COIN_REFER, DEBUG
from strategies.basic_rsi import BasicRSI
from utils import print_trade_analysis, print_sqn

class CustomDataset(bt.feeds.GenericCSVData):
    params = (
        ('datetime', 1),sdfsdf
        ('open', 2),
        ('high', 3),
        ('low', 4),
        ('close', 5),
        ('volume', 6),
    )

def main():    
    data = CustomDataset(
            name=COIN_TARGET,
            dataname="data/binance_btc_df.csv",
            timeframe=bt.TimeFrame.Minutes,
            fromdate=dt.datetime(2020, 1, 1),
            todate=dt.datetime(2021, 12, 31),
            nullvalue=0.0
        )

    class FullMoney(bt.sizers.PercentSizer):
        params = (
            ('percents', 99),
        )

    # cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=1)
    cerebro = bt.Cerebro(quicknotify=True)
    cerebro.adddata(data)
    broker = cerebro.getbroker()
    broker.setcommission(commission=0.001, name=COIN_TARGET)  # Simulating exchange fee
    broker.setcash(1000000.0)
    cerebro.addsizer(FullMoney)

    # Analyzers to evaluate trades and strategies
    # SQN = Average( profit / risk ) / StdDev( profit / risk ) * SquareRoot( number of trades )
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
    cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")
    #cerebro.addanalyzer(bt.analyzers.SharpeRatio_A, _name='mysharpe')

    # Include Strategy
    cerebro.addstrategy(BasicRSI)
    # cerebro.addstrategy(RsiSignalStrategy)

    # Starting backtrader bot
    initial_value = cerebro.broker.getvalue()
    print('Starting Portfolio Value: %.2f' % initial_value)
    result = cerebro.run()
    
    # Print analyzers - results
    final_value = cerebro.broker.getvalue()
    print('Final Portfolio Value: %.2f' % final_value)
    print('Profit %.3f%%' % ((final_value - initial_value) / initial_value * 100))
    print_sqn(result[0].analyzers.sqn.get_analysis())
    #print('Sharpe Ratio:', result[0].analyzers.mysharpe.get_analysis())
    print_trade_analysis(result[0].analyzers.ta.get_analysis())
    

    # plot result
    if DEBUG:
        cerebro.plot()
    

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("finished.")
        time = dt.datetime.now().strftime("%d-%m-%y %H:%M")
        print("Finished finished at time: ", time)
    except Exception as err:
        print("Finished with error: ", err)
        raise