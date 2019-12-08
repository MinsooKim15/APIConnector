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
class ExchangeConnector():
    rawExchanges: List[Any] = []
    dateList : List[DateTime] = []

    def __init__(self,authKey,enginePath):
        self.authKey = authKey # TODO: config 문서로 빼기
        self.enginePath = enginePath
        # self.searchdate = searchdate # 그냥 숫자여도 잘 들어가네
        self.dataType = "AP01" #AP01 빼고는 쓸 일이 없다.

    def getOneData(self,searchDate):
        # self.searchdate = searchdate
        self.url = f"https://www.koreaexim.go.kr/site/program/financial/exchangeJSON?authkey={self.authKey}&searchdate={searchDate}&data={self.dataType}"
        print(self.url)
        response = requests.get(self.url)
        exchange = response.json()
        for i in exchange:
            rawExchange = databaseQuery.RawExchange(rateDate = self.searchdate, **i)
            self.rawExchanges.append(rawExchange)
        print(self.rawExchanges)
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

    def updateDB(self):
        engine = create_engine(self.enginePath, echo=True)
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add_all(self.rawExchanges)
        session.commit()

    def clearVar(self):
        self.rawExchanges = None
    #TODO : Null 값처리?

if __name__ == "__main__":
    # 직접 옛날 데이터를 축적해야 할 수 있다.
    # 여기는 그런 것을 위한 코드만 추가
    print("Yeah")
    # # execute only if run as a script
    # exchangeConnector = ExchangeConnector(20191105)
    # exchangeConnector.getData()
    # exchangeConnector.updateDB()