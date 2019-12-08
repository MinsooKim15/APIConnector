# 여기서 모든 실행 코드를 관리한다.
# 나머지 코드는 모두 여기서 import해 실행하며, package의 의존성도 여기서 모두 관리한다.

# atom script에서 utf-8을 해결하기 위한 코드 - 시작
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding = 'utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding = 'utf-8')
# atom script에서 utf-8을 해결하기 위한 코드 -끝

# coding: utf-8
from sqlalchemy import Column, DateTime, String,Float, Text, FLOAT
from sqlalchemy.dialects.mysql import INTEGER, LONGTEXT,TINYINT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import sqlalchemy as db
from datetime import datetime
from datetime import date


# 개별 모듈 import
import DatabaseQuery
from ExchangeConnector import ExchangeConnector
from FlightConnector import *
from WeatherConnector import WeatherConnector



#Config Import
# main_with_json.py

def makeDateRange(startDate,range = 365):
    startDateInString = startDate.strftime("%Y-%m-%d")
    endDate = startDate + timedelta(days= range)
    endDateInString = endDate.strftime("%Y-%m-%d")
    return [startDateInString, endDateInString]


import time
import logging
import datetime as dt

class MyFormatter(logging.Formatter):

    def __init__(self,fmt=None,datefmt=None):
        super(MyFormatter,self).__init__(fmt,datefmt)
        self.reftime = dt.datetime.fromtimestamp(time.mktime(time.localtime()))

    def formatTime(self, record, datefmt=None):
        ctime = dt.datetime.fromtimestamp(time.mktime(self.converter(record.created)))
        ct = (ctime - self.reftime).timetuple()
        if datefmt:
            s = time.strftime(datefmt, ct)
        else:
            t = time.strftime("%Y-%m-%d %H:%M:%S", ct)
            s = "%s,%03d" % (t, record.msecs)
        return s

if __name__ == "__main__":
    import json

    with open('config.json', 'r') as f:
        config = json.load(f)

    weatherUrl = config["weather"]["url"]
    exchangeAuthKey = config["exchange"]["authKey"]
    flightUrl = config["flight"]["url"]
    flightKey = config["flight"]["x-rapidapi-key"]
    dbEnginePath = config["db"]["enginePath"]

    with open('airportList.json',  'r') as j:
        airportList = json.load(j)

    nearAsiaList = list(airportList["northEastAsia"].keys()) + list(airportList["southAsia"].keys())
    farList = list(airportList["southWestAsia"].keys()) + list(airportList["europe"].keys()) + list(airportList["northAmerica"].keys()) + list(airportList["oceania"].keys())
    veryFarList = list(airportList["africa"].keys()) + list(airportList["latinAmerica"].keys())
    print(nearAsiaList)
    print(farList)
    print(veryFarList)
    # # 시간 소모 적은 거 -> 많은 거 순임.
    # weatherConnector = WeatherConnector(url = weatherUrl, enginePath = dbEnginePath)
    # weatherConnector.getData()
    # weatherConnector.updateDB()
    # weatherConnector.clearVar()
    # # execute only if run as a script
    # exchangeConnector = ExchangeConnector(authKey = exchangeAuthKey, enginePath= dbEnginePath)
    # exchangeConnector.setDateTime(startDate="20190101")
    # exchangeConnector.getData()
    # exchangeConnector.updateDB()
    # exchangeConnector.clearVar()
    # 1개 호출시 -> setOption,setDateOption,CreateSession, getAndIUpdate순
    # 여러개 호출시 -> 아래 코드 형식으로 가자

    # 오늘부터 1년
    today = datetime.now()
    dateRange = makeDateRange(today, range=10)
    flightConnector = FlightConnector(url = flightUrl, key=flightKey, enginePath=dbEnginePath)
    print("일단 여기 까진 동작")
    #
    #
    for i in nearAsiaList:
    #일본 동남아는 3~6일 사이가 주로 가는 시간대로 가정한다.
        print("시작")
        flightConnector.setOption(destinationPlace=i)
        flightConnector.setGridSearchDatesByConstant(dateRange = dateRange, minimumTerm = 3, maximumTerm = 6)
        flightConnector.gridSearchGetDateAndUpdateDB()
    for j in farList:
    #멀다면 1주 ~ 2주를 주로 가는 시간대로 가정한다.
        flightConnector.setOption(destinationPlace=j)
        flightConnector.setGridSearchDatesByConstant(dateRange=dateRange, minimumTerm= 6, maximumTerm= 15)
        flightConnector.gridSearchGetDateAndUpdateDB()
    for k in veryFarList:
        flightConnector.setOption(destinationPlace=k)
        flightConnector.setGridSearchDatesByConstant(dateRange=dateRange, minimumTerm = 12, maximumTerm = 30)
        flightConnector.gridSearchGetDateAndUpdateDB()
    # handler = logging.StreamHandler(MyFormatter())
    # logger = logging.getLogger()
    # logger.addHandler(handler)
    # # flightConnector.setGridSearchDates(outboundDateRange= dateRange , inboundDateRange= dateRange)
    # flightConnector.gridSearchGetDateAndUpdateDB()
