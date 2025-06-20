# user_data/strategies/HighAccuracyStrategy.py

from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class HighAccuracyStrategy(IStrategy):
    INTERFACE_VERSION = 3

    timeframe = '15m'
    stake_amount = 500  # ₹500 per trade (set this in config.json too)
    minimal_roi = {"0": 0.04}  # 4% target profit
    stoploss = -0.015  # 1.5% stop loss
    trailing_stop = True
    trailing_stop_positive = 0.015
    trailing_stop_positive_offset = 0.025
    trailing_only_offset_is_reached = True

    use_custom_stoploss = False
    process_only_new_candles = True

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Indicators
        dataframe['rsi'] = ta.RSI(dataframe)
        dataframe['ema_fast'] = ta.EMA(dataframe, timeperiod=9)
        dataframe['ema_slow'] = ta.EMA(dataframe, timeperiod=21)
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['adx'] = ta.ADX(dataframe)
        dataframe['supertrend'] = ta.MINUS_DI(dataframe, timeperiod=14) < ta.PLUS_DI(dataframe, timeperiod=14)
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['rsi'] < 30) &
                (dataframe['macd'] > dataframe['macdsignal']) &
                (dataframe['ema_fast'] > dataframe['ema_slow']) &
                (dataframe['adx'] > 20) &
                (dataframe['supertrend'])
            ),
            'buy'] = 1
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['rsi'] > 70) |
                (dataframe['macd'] < dataframe['macdsignal']) |
                (dataframe['ema_fast'] < dataframe['ema_slow'])
            ),
            'sell'] = 1
        return dataframe
