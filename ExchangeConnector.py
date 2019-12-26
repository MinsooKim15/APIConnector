# 일단 아래에 필요한 모든 코드를 한 번에 적는다.
# 동작이 모두 완벽히 잘 되는지 확인한다.
# 객체지향으로 변경한다.
# 모듈화해 문서를 쪼갠다.
# 완성!!

# atom script에서 utf-8을 해결하기 위한 코드 - 시작

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding = 'utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding = 'utf-8')
# atom script에서 utf-8을 해결하기 위한 코드 -끝

#databaseQuery 모듈을 위한 내용들
from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.mysql import INTEGER, LONGTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import sqlalchemy as db

import dateutil.parser

Base = declarative_base()
metadata = Base.metadata
#databaseQuery 모듈을 위한 내용들 - 끝

import DatabaseQuery
from datetime import datetime
from datetime import timedelta

from typing import List, Any
import requests
import logging
import os, inspect

class ExchangeConnector():
    rawExchanges: List[Any] = []
    dateList : List[DateTime] = []

    def __init__(self,authKey,enginePath):
        path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        self.authKey = authKey # TODO: config 문서로 빼기
        self.enginePath = enginePath # 그냥 숫자여도 잘 들어가네
        self.dataType = "AP01" #AP01 빼고는 쓸 일이 없다.

        #이 밑은 로깅을 위한 코드임.
        self.exchangeLogger = logging.getLogger("exchange")
        self.exchangeLogger.setLevel(logging.INFO)
        streamHandler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        streamHandler.setFormatter(formatter)
        self.exchangeLogger.addHandler(streamHandler)
        fileHandler = logging.FileHandler(path+"/main.log")
        fileHandler.setFormatter(formatter)
        self.exchangeLogger.addHandler(fileHandler)
        self.exchangeLogger.info("Exchange Connector Init")
        self.alchemyLogger = logging.getLogger('sqlalchemy.engine')
        self.alchemyLogger.setLevel(logging.ERROR)
        self.alchemyLogger.addHandler(fileHandler)


    def getOneData(self,searchDate):
        # self.searchdate = searchdate
        self.url = f"https://www.koreaexim.go.kr/site/program/financial/exchangeJSON?authkey={self.authKey}&searchdate={searchDate}&data={self.dataType}"
        response = requests.get(self.url)
        exchange = response.json()
        for i in exchange:
            rawExchange = DatabaseQuery.RawExchange(rateDate = searchDate, **i)
            self.rawExchanges.append(rawExchange)
    def setDateTime(self,startDate,endDate=0):
        if endDate ==0:
            #endDate 설정 안 했다면,
            sdate = dateutil.parser.parse(startDate)
            self.dateList.append(sdate)
        else:
            sdate = dateutil.parser.parse(startDate)  # start date
            edate = dateutil.parser.parse(endDate) # end date
            delta = edate - sdate  # as timedelta
            for i in range(delta.days + 1):
                day = sdate + timedelta(days=i)
                self.dateList.append(day)


    def getData(self):
        for i in self.dateList:
            paramDate = i.strftime("%Y%m%d")
            self.getOneData(searchDate = paramDate)
        self.exchangeLogger.info("{url:%s, , sizeOfRawWeatherRecords : %d}" %(str(self.url), len(self.rawExchanges)))

    def updateDB(self):
        engine = create_engine(self.enginePath, echo=True)
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add_all(self.rawExchanges)
        session.commit()

    def clearVar(self):
        self.rawExchanges = None

if __name__ == "__main__":
    import json, os, inspect
    with open('config.json', 'r') as f:
        config = json.load(f)

    weatherUrl = config["weather"]["url"]
    exchangeAuthKey = config["exchange"]["authKey"]
    flightUrl = config["flight"]["url"]
    flightKey = config["flight"]["x-rapidapi-key"]
    dbEnginePath = config["db"]["enginePath"]
    exchangeConnector = ExchangeConnector(authKey = exchangeAuthKey, enginePath= dbEnginePath)
    exchangeConnector.setDateTime(startDate="20190101", endDate = "20191219")
    exchangeConnector.getData()
    exchangeConnector.updateDB()
    exchangeConnector.clearVar()
