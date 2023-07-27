# -*- coding:utf-8 -*-
# 君子爱财 取之有道

import sys
import logging

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split

sys.path.append("../lib/log")
from log import *
sys.path.append("../lib/database")
from database import *

# 拉取训练交易数据条目
GET_TRANSACTION_NUM = 1000

# 单条训练样本拥有的交易数据条目
TRAIN_DATA_TRANSACTION_NUM = 30

# 股票预测
class Predicter():
    def __init__(self):
        # 连接数据库
        self.database = Database()
        pass

    def price_rate(self, open_price, close_price):
        ''' 计算价格上浮率 '''
        return (close_price - open_price) / open_price * 100

    def gen_train_data(self, date):
        ''' 生成训练数据 '''
        fp = open(str(date)+".dat", "w")

        # 获取股票列表
        stock_list = self.database.get_all_stock()
        for stock in stock_list:
            stock_key = stock["key"]

            # 拉取交易数据
            transaction_list = self.database.get_transaction(stock_key, date, GET_TRANSACTION_NUM)

            # 生成训练样本
            self.gen_train_data_by_transaction_list(stock_key, transaction_list, fp)

        fp.close()

        return None

    def gen_train_data_by_transaction_list(self, stock_key, transaction_list, fp):
        ''' 通过交易列表生成训练数据
            @Param stock_key: 股票KEY
            @Param transaction_list: 交易数据
            @Param fname: 训练数据输出文件
        '''
        train_data_list = list()

        # 判断参数合法性
        if len(transaction_list) < TRAIN_DATA_TRANSACTION_NUM:
            logging.error("Transaction data not enough! stock_key:%s", stock_key)
            return None

        offset = len(transaction_list) - TRAIN_DATA_TRANSACTION_NUM
        while (offset > 0):
            train_data = ""
            # 生成训练数据
            index = offset + TRAIN_DATA_TRANSACTION_NUM - 1
            while (index >= offset):
                if (index - TRAIN_DATA_TRANSACTION_NUM + 1) != offset:
                    train_data += ","
                train_data += "%f,%f,%f,%f,%d,%d,%f" % (
                        transaction_list[index]["open_price"],
                        transaction_list[index]["close_price"],
                        transaction_list[index]["top_price"],
                        transaction_list[index]["bottom_price"],
                        transaction_list[index]["volume"],
                        transaction_list[index]["turnover"],
                        self.price_rate(transaction_list[index]["open_price"],
                                        transaction_list[index]["close_price"]))
                index -= 1
            # 设置预测结果(往前一天的收盘价 与 往后一天的收盘价做对比)
            price_rate = self.price_rate(
                    transaction_list[offset]["close_price"],
                    transaction_list[offset-1]["close_price"])
            train_data += ",%f\n" % (price_rate)

            train_data_list.append(train_data)
            offset -= 1

        # 将结果输出至文件
        fp.writelines(train_data_list)

        return None

    def load_train_data(self, date):
        ''' 加载训练数据, 并返回特征数据和目标数据 '''
        # 加载训练数据
        fp = open(str(date) + ".dat")
        lines = fp.readlines()
        fp.close()

        # 处理训练数据
        target_list = list()
        feature_list = list()

        index = 0
        for line in lines:
            index += 1
            logging.debug("Load train data. line:%d", index)
            line = line.strip()
            data = line.split(",")

            feature = list()
            target = float(data[-1])

            idx = 0
            while (idx < len(data)-1):
                feature.append(float(data[idx]))
                idx += 1
            feature_list.append(feature)
            target_list.append(target)

        return feature_list, target_list

    def train(self, date):
        ''' 模型训练 '''
        # 加载训练数据
        feature, target = self.load_train_data(date)

        # 划分训练集和测试集
        feature_train, feature_test, target_train, target_test = train_test_split(feature, target, test_size=0.05, random_state=1)

        # 创建线性回归对象
        #predict_model = LinearRegression()
        #predict_model.fit(feature_train, target_train) # 训练

        predict_model = MLPRegressor(hidden_layer_sizes=(100,), activation='relu', solver='adam', alpha=0.0001, batch_size='auto', learning_rate='constant', learning_rate_init=0.001, power_t=0.5, max_iter=200, shuffle=True, random_state=None, tol=0.0001, verbose=False, warm_start=False, momentum=0.9, nesterovs_momentum=True, early_stopping=False, validation_fraction=0.1, beta_1=0.9, beta_2=0.999, epsilon=1e-08, n_iter_no_change=10, max_fun=15000)
        predict_model.fit(feature_train, target_train) # 训练

        # 模型评估
        predict_test = predict_model.predict(feature_test)

        score = r2_score(target_test, predict_test)
        print('R-Squared:', score)

        predict_sum = 0
        target_sum = 0
        index = 0
        while (index < len(target_test)):
            predict_sum += predict_test[index]
            target_sum += target_test[index]
            logging.debug("feature[%d] %s", index, feature_test[index])
            logging.debug("compare[%d] %s:%s", index, predict_test[index], target_test[index])
            index += 1

        logging.debug("predict_sum: %s", predict_sum)
        logging.debug("target_sum: %s", target_sum)

        return None

if __name__ == "__main__":

    log_init("../../log/predicter.log")

    predict = Predicter()

    date = sys.argv[1]

    # 生成训练数据
    # predict.gen_train_data(date)

    # 进行模型训练
    predict.train(date)

    # 进行结果预测
    # predict.predit()
