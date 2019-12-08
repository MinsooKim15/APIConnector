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
import json

with open('config.json', 'r') as f:
    config = json.load(f)

weatherUrl = config["weather"]["url"]
exchangeAuthKey = config["exchange"]["authKey"]
flightUrl = config["flight"]["url"]
flightKey = config["flight"]["x-rapidapi-key"]
dbEnginePath = config["db"]["enginePath"]


if __name__ == "__main__":

    # 시간 소모 적은 거 -> 많은 거 순임.
    # weatherConnector = WeatherConnector(url = weatherUrl, enginePath = dbEnginePath)
    # weatherConnector.getData()
    # weatherConnector.updateDB()
    # weatherConnector.clearVar()
    # execute only if run as a script
    # exchangeConnector = ExchangeConnector(authKey = exchangeAuthKey, enginePath= dbEnginePath)
    # exchangeConnector.setDateTime(startDate="20190101")
    # exchangeConnector.getData()
    # exchangeConnector.updateDB()
    # exchangeConnector.clearVar()
    flightConnector = FlightConnector(url = flightUrl, key=flightKey, enginePath=dbEnginePath)
    flightConnector.setOption(destinationPlace="JFK")
    flightConnector.setGridSearchDates(outboundDateRange=["2020-01-01", "2020-03-01"], inboundDateRange=["2020-01-01", "2020-03-06"])
    print(flightConnector.gridSearchDatesList)
    flightConnector.gridSearchGetDateAndUpdateDB()
    # flightConnector.setDateOption(outboundDate= "2020-01-01", inboundDate= "2020-01-06")

    #
    # flightConnector.getAndUpdateData()
