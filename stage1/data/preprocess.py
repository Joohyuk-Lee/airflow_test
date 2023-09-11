

from os.path import join as opj
import pandas as pd
import numpy as np
from tqdm.auto import tqdm


import ta

from stage1.utils import get_week_of_month

from sklearn.model_selection import train_test_split
# yahoo financial, unofficial way, rate limit
from pandas_datareader import data as pdr
import yfinance as yf
yf.pdr_override()


class DataPreprocess:
    """
    각 자산별로 데이터를 수집해 오는 class
    user_name별, model_name별 정리 필요
    """

    def __init__(self, cfg):
        self.cfg = cfg
        # self.logger = logger
    def load_data(self, logger=None):
        
        if self.cfg.base.user_name == "jw":
            """JW_KS_LSTM_model.ipynb

            Automatically generated by Colaboratory.

            Original file is located at
                https://colab.research.google.com/drive/1SH5BSpLNYOY3gV4sOSo6eLCm6wXRz6oy

            Standard Scale -> test 제외 후 각각
            """
            ### 현재 주어진 stock_dat.csv가 이 코드들로 생성되었다는 가정하에 주석처리 (-> 했었지만.. 학습|검증 데이터 만드는 데 raw_train, dates들을 활용하여 다시 주석 해제...)
            # # stock data .csv가 없을 경우만 실행하는 코드 -> 추론할 때 이 과정이 필요하다면 넣어주어야 한다.
            # # if os.path.exists(opj(base.data_dir, "stock_data.csv")):
            raw_train = pd.read_csv(opj(self.cfg.base.data_dir, "adj_raw_train.csv"))

            #date열 str에서 datetime형으로 변환
            raw_train['date'] = pd.to_datetime(raw_train['date'])

            target_year=2021
            train = raw_train[raw_train['date'].dt.year<target_year]
            # len(train)

            target_year=2021
            validation = raw_train[raw_train['date'].dt.year==target_year]
            # len(validation)

            target_year=2022
            test = raw_train[raw_train['date'].dt.year==target_year]
            # len(test)

            raw_train

            raw_train['target'] = raw_train.d_ret

            raw_train = raw_train.drop('d_ret',axis=1)
            # 아래 코드들과 호환을 위해 아래 한 줄을 추가..
            dates = pd.to_datetime(raw_train['date'])
            
            raw_train.set_index("date",inplace=True)


            # save original 'returns' prices for later
            original_returns = raw_train['target'].values

            # # separate dates for future plotting
            # dates = pd.to_datetime(raw_train['date'])

            # raw_train.set_index("date",inplace=True)

            # variables for training
            cols = list(raw_train)[0:9]

            # new dataframe with only training data
            stock_data = raw_train[cols].astype(float)

            # stock_data.to_csv("stock_data.csv")

            # if os.path.exists(opj(base.data_dir, "stock_data.csv")): 이 부분에 대한 else
            # else:
            stock_data = pd.read_csv(opj(self.cfg.base.data_dir, "stock_data.csv"))

            # normalize the dataset
            from sklearn.preprocessing import StandardScaler, MinMaxScaler
            scaler = StandardScaler()
            scaler = scaler.fit(stock_data[:1229])
            stock_data_scaled = scaler.transform(stock_data[:1229])

            # normalize the dataset
            from sklearn.preprocessing import StandardScaler, MinMaxScaler

            stock_data_scaled_test = scaler.transform(stock_data[1229:])

            stock_data_target = raw_train[["target"]]

            stock_data_target[1229:]

            stock_data_scaled_test.shape

            # split to train data and test data
            n_train = 981
            train_data_scaled = stock_data_scaled[0: n_train]
            train_dates = dates[0: n_train]

            n_validation = n_train + 248
            val_data_scaled = stock_data_scaled[n_train: n_validation]
            val_dates = dates[n_train: n_validation]

            n_test = n_validation

            test_data_scaled = stock_data_scaled_test
            test_dates = dates[n_test:]

            # split to train data and test data
            n_train = 981
            train_data_test_scaled = stock_data_target[0: n_train]
            train_dates = dates[0: n_train]

            n_validation = n_train + 248
            val_data_test_scaled = stock_data_target[n_train: n_validation]
            val_dates = dates[n_train: n_validation]

            n_test = n_validation

            test_data_test_scaled = stock_data_target[n_test:]
            test_dates = dates[n_test:]

            import numpy as np
            # data reformatting for LSTM
            pred_days = 1  # prediction period - 3months
            seq_len = 10   # sequence length = past days for future prediction.
            input_dim = 10  # input_dimension = ['close', 'open', 'high', 'low', 'rsi', 'MACD_12_26', 'mavg', 'CSI', 'kalman','target]

            trainX = []
            trainY = []
            valX = []
            valY = []
            testX = []
            testY = []

            for i in range(seq_len, n_train-pred_days +1):
                trainX.append(train_data_scaled[i - seq_len:i, 0:train_data_scaled.shape[1]])
                trainY.append(train_data_test_scaled[i + pred_days - 1:i + pred_days].values)

            for i in range(seq_len, len(val_data_scaled)-pred_days +1):
                valX.append(val_data_scaled[i - seq_len:i, 0:val_data_scaled.shape[1]])
                valY.append(val_data_test_scaled[i + pred_days - 1:i + pred_days].values)

            for i in range(seq_len, len(test_data_scaled)-pred_days +1):
                testX.append(test_data_scaled[i - seq_len:i, 0:test_data_scaled.shape[1]])
                testY.append(test_data_test_scaled[i + pred_days - 1:i + pred_days].values)

            trainX, trainY = np.array(trainX), np.array(trainY)
            valX, valY = np.array(valX), np.array(valY)
            testX, testY = np.array(testX), np.array(testY)

            print(trainX.shape, trainY.shape)
            print(testX.shape, testY.shape)
            print(valX.shape, valY.shape)

            '''
            (971, 10, 9) (971, 1, 1)
            (236, 10, 9) (236, 1, 1)
            (238, 10, 9) (238, 1, 1)
            '''
            return trainX, trainY, valX, valY, testX, testY 

        # if self.cfg.base.model_name:
        # return 

        elif self.cfg.base.user_name == "jh":

            

            if self.cfg.base.mode == 'infer':
                from stage1.utils import scaler
                test = pdr.get_data_yahoo(self.cfg.base.index_name, self.cfg.test.start_date, self.cfg.test.end_date).reset_index()
                x_data, y_data, date_list = jh_make_data(test, self.cfg.data)
                
                logger.info(f"!!Valid data infoi!! \n  x_data.shape : {x_data.shape} \t y_data.shape : {y_data.shape}")
                # 학습 때 활용했던 mn, sd 그대로 사용
                ### STANDARIZE
                x_data,y_data = scaler(x_data,y_data, self.cfg.base,is_train=False, logger=logger)



                return x_data, y_data, date_list
            else:
                from stage1.utils import scaler
                train = pdr.get_data_yahoo(self.cfg.base.index_name, self.cfg.train.start_date, self.cfg.train.end_date).reset_index()
                # valid 활용을 사실 안함...
                # valid = pdr.get_data_yahoo(self.cfg.base.index_name, self.cfg.valid.start_date, self.cfg.valid.end_date).reset_index()

                logger.info(f"train data start date : {train.Date.min()} end date : {train.Date.max()}")
                ### 학습 데이터 생성
                x_data, y_data, _ = jh_make_data(train, self.cfg.data)
                logger.info(f"!!Train data infoi!! \n  x_data.shape : {x_data.shape} \t y_data.shape : {y_data.shape}")
                ### STANDARIZE
                x_data,y_data = scaler(x_data,y_data, self.cfg.base, is_train=True, logger=logger)

                X_train, X_valid, y_train, y_valid = train_test_split(x_data, y_data, shuffle=True,random_state=self.cfg.base.seed, test_size=0.2)

                return X_train, X_valid, y_train, y_valid



def jh_make_features(df_):
    """
        특징을 추가해주는 함수. -> 거시경제 등 API로 받아올 수 있다면 이 곳에 추가!
    """
    df = df_.copy()
    df['OCmean'] = (df['Open']+df['Close']).div(2)
    df['HLmean'] = (df['High']+df['Low']).div(2)


    H, L, C, V = df['High'], df['Low'], df['Close'], df['Volume']
    df['ATR'] = ta.volatility.average_true_range(high=H, low=L, close=C, fillna=True)
    df['Parabolic SAR'] = ta.trend.psar_down(high=H, low=L, close=C, fillna=True)
    df['MACD'] = ta.trend.macd(close=C, fillna=True)
    df['SMA'] = ta.trend.sma_indicator(close=C, fillna=True)
    df['EMA'] = ta.trend.ema_indicator(close=C, fillna=True)
    df['RSI'] = ta.momentum.rsi(close=C, fillna=True)


    df['day'] = df.Date.dt.day
    df['month'] = df.Date.dt.month
    df['week'] = df.Date.dt.isocalendar().week
    df['year'] = df.Date.dt.year
    df['dayofweek'] = df.Date.dt.dayofweek
    # 고려사항 : 예를 들어, 우리나라 증권시장의 선물·옵션 동시 만기일은 매년 3, 6, 9, 12월 두 번째 목요일이에요.
    df['weekofmonth'] = df.apply(lambda row: get_week_of_month(row['year'], row['month'], row['day']), axis=1)

    return df

def jh_make_data(df, cfg_data, return_to_df=False):
    """
        cfg data feature_list에 있는 feature을 활용해 시계열 데이터를 만드는 함수
    """
    df_ = jh_make_features(df)
    df = df_[cfg_data.feature_list].copy()
    # change into uncommented code (delete "+1" in -1 axis of df.iloc). caused by  IndexError: index 1230 is out of bounds for axis 0 with size 1230
    # total_sample_num = df.iloc[cfg_data.lookback_window-1:-cfg_data.lookahead_window+1].shape[0]
    total_sample_num = df.iloc[cfg_data.lookback_window-1:-cfg_data.lookahead_window].shape[0]


    # 수익 계산 위해 사용
    fea_num = df.columns.get_loc("Close")
    # 날짜 계산할 때는 df_ 사용
    fea_num_Date = df_.columns.get_loc("Date")
    # 특징 하나일 떄는 아래와 같이 사용
    # x_data = np.zeros((total_sample_num, cfg_data.lookback_window, 1))
    x_data = np.zeros((total_sample_num, cfg_data.lookback_window, df.shape[1]))
    y_data = np.zeros((total_sample_num, 1))
    date_list = []
    end_date = cfg_data.lookback_window-1

    for idx in tqdm(range(total_sample_num)):

        # 특징 하나일 떄는 아래와 같이 사용
        # x_data[idx,] = df.iloc[idx:idx+cfg_data.lookback_window, fea_num].values
        x_data[idx,] = df.iloc[idx:idx+cfg_data.lookback_window, :].values

        # 반복 효율을 위해 a로 변환 가능 [a는 for문 밖으로]
        # a = end_date+cfg_data.lookahead_window
        # y_data[idx,] = df.iloc[idx+a, fea_num]/df.iloc[idx+end_date, fea_num]
        # y_data[idx,] = df.iloc[idx+end_date+cfg_data.lookahead_window, fea_num]/df.iloc[idx+end_date, fea_num]-1
        y_data[idx,] = df.iloc[idx+end_date+cfg_data.lookahead_window, fea_num]/df.iloc[idx+end_date, fea_num]-1
        # 날짜 계산할 때는 df_ 사용
        date_list.append(df_.iloc[idx+end_date, fea_num_Date])
    # pd.DataFrame(y_data).describe()

    if return_to_df:
        pass
        # FEATURES = [f'f{x}' for x in range(WIDTH-COPIES-4-1)]
        # TARGETS = [f'y{x}' for x in range(5)]
        # train_data = pd.DataFrame(x_data3,columns=FEATURES)
        # train_data[TARGETS] = y_data3
        # train_data['cfips'] = np.repeat(KEEP,COPIES)
        # print('Our GRU training data has shape:', train_data.shape )
        # train_data.head()
    else:
        return x_data, y_data, date_list
