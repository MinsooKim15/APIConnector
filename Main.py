# 여기서 모든 실행 코드를 관리한다.
# 나머지 코드는 모두 여기서 import해 실행하며, package의 의존성도 여기서 모두 관리한다.

# atom script에서 utf-8을 해결하기 위한 코드 - 시작
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding = 'utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding = 'utf-8')
from apscheduler.schedulers.blocking import BlockingScheduler
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
from FlightQuoteConnector import *


#Config Import
# main_with_json.py

def makeDateRange(startDate,range = 365):
    startDateInString = startDate.strftime("%Y-%m-%d")
    endDate = startDate + timedelta(days= range)
    endDateInString = endDate.strftime("%Y-%m-%d")
    return [startDateInString, endDateInString]

def makeDateString(date):
    # Datetime Object여야 함. 아직 타입 체킹은 넣지 않음
    return str(date.year) + str(date.month).zfill(2) + str(date.day).zfill(2)


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
    import json, os, inspect

    # 파일 경로 이슈
    path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

    mainLogger = logging.getLogger("main")
    mainLogger.setLevel(logging.INFO)
    streamHandler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    streamHandler.setFormatter(formatter)
    mainLogger.addHandler(streamHandler)
    fileHandler = logging.FileHandler(path + "/main.log")
    fileHandler.setFormatter(formatter)
    mainLogger.addHandler(fileHandler)




    with open(path + '/config.json', 'r') as f:
        config = json.load(f)

    weatherUrl = config["weather"]["url"]
    exchangeAuthKey = config["exchange"]["authKey"]
    flightUrl = config["flight"]["url"]
    flightKey = config["flight"]["x-rapidapi-key"]
    dbEnginePath = config["db"]["enginePath"]

    with open(path + '/airportList.json', 'r') as j:
        airportList = json.load(j)

    nearAsiaList = list(airportList["northEastAsia"].keys()) + list(airportList["southAsia"].keys())
    farList = list(airportList["southWestAsia"].keys()) + list(airportList["europe"].keys()) + list(airportList["northAmerica"].keys()) + list(airportList["oceania"].keys())
    veryFarList = list(airportList["africa"].keys()) + list(airportList["latinAmerica"].keys())
    # # print(nearAsiaList)
    # # print(farList)
    # # print(veryFarList)
    # # 오늘부터 1년
    today = datetime.now()
    # # 시간 소모 적은 거 -> 많은 거 순임.
    weatherConnector = WeatherConnector(url = weatherUrl, enginePath = dbEnginePath)
    weatherConnector.getData()
    weatherConnector.updateDB()
    weatherConnector.clearVar()
    # # # execute only if run as a script
    exchangeConnector = ExchangeConnector(authKey = exchangeAuthKey, enginePath= dbEnginePath)
    exchangeConnector.setDateTime(startDate=makeDateString(today))
    exchangeConnector.getData()
    exchangeConnector.updateDB()
    exchangeConnector.clearVar()
    # # 1개 호출시 -> setOption,setDateOption,CreateSession, getAndIUpdate순
    # # 여러개 호출시 -> 아래 코드 형식으로 가자
    #
    #
    # flightConnector = FlightConnector(url=flightUrl, key=flightKey, enginePath=dbEnginePath)
    # mainLogger.info("Init 성공")
    #
    # try:
    #     # targetDay = today + timedelta(days=90)
    #     # dateRange = makeDateRange(targetDay, range=10)
    #     # for i in nearAsiaList:
    #     #     # 일본 동남아는 3~6일 사이가 주로 가는 시간대로 가정한다.
    #     #     print("시작")
    #     #     print(i)
    #     #     flightConnector.setOption(destinationPlace=i)
    #     #     flightConnector.setGridSearchDatesByConstant(dateRange=dateRange, minimumTerm=3, maximumTerm=3)
    #     #     flightConnector.gridSearchGetDateAndUpdateDB()
    #     targetDay = today + timedelta(days=180)
    #     dateRange = makeDateRange(targetDay, range=10)
    #     for j in farList:
    #         # 멀다면 1주 ~ 2주를 주로 가는 시간대로 가정한다.
    #         flightConnector.setOption(destinationPlace=j)
    #         flightConnector.setGridSearchDatesByConstant(dateRange=dateRange, minimumTerm=7, maximumTerm=7)
    #         flightConnector.gridSearchGetDateAndUpdateDB()
    #     targetDay = today + timedelta(days=180)
    #     dateRange = makeDateRange(targetDay, range=10)
    #     for k in veryFarList:
    #         flightConnector.setOption(destinationPlace=k)
    #         flightConnector.setGridSearchDatesByConstant(dateRange=dateRange, minimumTerm=12, maximumTerm=12)
    #         flightConnector.gridSearchGetDateAndUpdateDB()
    # except MemoryError as error:
    #     # Output expected MemoryErrors.
    #     mainLogger.warn(error)
    #
    flightQuoteConnector = FlightQuoteConnector(url= flightUrl, key = flightKey, enginePath = dbEnginePath)
    try :
        startMonth = datetime.now()
        endMonth = datetime(year = 2020, month = 12, day = 31)
        for i in nearAsiaList:
            flightQuoteConnector.getAndUpdateData(startMonth=startMonth, endMonth= endMonth, originPlace="ICN", destinationPlace= i)
        for j in farList:
            flightQuoteConnector.getAndUpdateData(startMonth=startMonth, endMonth = endMonth, originPlace= "ICN", destinationPlace= j)
        for k in veryFarList:
            flightQuoteConnector.getAndUpdateData(startMonth=startMonth, endMonth=endMonth, originPlace="ICN",
                                                  destinationPlace=k)
    except MemoryError as error:
        # Output expected MemoryErrors.
        mainLogger.warn(error)

        # 여기는 Quote만
