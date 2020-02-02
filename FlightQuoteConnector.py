import requests
#
# url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browsequotes/v1.0/US/USD/en-US/SFO-sky/JFK-sky/2019-12-05"
#
# querystring = {"inboundpartialdate":"2019-12-05"}
#
# headers = {
#     'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
#     'x-rapidapi-key': "ab2bb01f37msha32356797613784p1c4e2ejsn75d5549b2f53"
#     }
#
# response = requests.request("GET", url, headers=headers, params=querystring)
#
# print(response.text)

# atom script에서 utf-8을 해결하기 위한 코드 - 시작

import sys
import io
import time
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding = 'utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding = 'utf-8')
# atom script에서 utf-8을 해결하기 위한 코드 -끝
import DatabaseQuery

from datetime import datetime
from datetime import timedelta
import dateutil.parser
import pandas as pd
#databaseQuery 모듈을 위한 내용들
from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.mysql import INTEGER, LONGTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import sqlalchemy as db

import logging
import os, inspect

class FlightQuoteConnector():

    flightLogger = ""
    alchemyLogger = ""

    sessionUrl = ""
    sessionQueryString = {}
    sessionHeaders = {}
    sessionKey = ""
    rawFlightItineraries = []
    rawFlightSegments = []
    rawFlightLegs = []
    rawFlightCarriers = []
    rawFlightAgents = []
    gridSearchDatesList = []
    originPlace = ""
    destinationPlace = ""
    payLoadOriginPlace = ""
    payLoadDestinationPlace = ""
    cabinClass = ""
    children = ""
    infants = ""
    adults = ""

    def __init__(self,url,key,enginePath):
        # self.outboundDate = outboundDate
        # self.inboundDate = inboundDate
        # self.pageIndex = pageIndex
        # self.pageSize = pageSize
        self.flightLogger = logging.getLogger("flight")
        self.flightLogger.setLevel(logging.INFO)
        streamHandler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        streamHandler.setFormatter(formatter)
        self.flightLogger.addHandler(streamHandler)
        path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        fileHandler = logging.FileHandler(path+"/main.log")
        fileHandler.setFormatter(formatter)
        self.flightLogger.addHandler(fileHandler)
        self.alchemyLogger = logging.getLogger('sqlalchemy.engine')
        self.alchemyLogger.setLevel(logging.ERROR)
        self.alchemyLogger.addHandler(fileHandler)

        self.url = url
        self.key = key
        self.enginePath = enginePath
        # 실제 한 번의 APICall은 아니지만, 한 회의 Cron이 도는 것을 같은 ID로 표기하자
        self.apiCallId = self.makeApiCallId()

    def getAndUpdateData(self,startMonth, endMonth, originPlace, destinationPlace):
        assert type(startMonth) is datetime, "start Month는 DateTime만 받아요."
        assert type(endMonth) is datetime, "end Month는 DateTime만 받아요."
        #Range 만들기
        dateRange = pd.date_range(startMonth.strftime("%Y-%m-%d"), endMonth.strftime("%Y-%m-%d"),freq = 'MS').strftime("%Y-%m").tolist()
        # dateRange = pd.date_range("2019-01-02", "2019-08-03", freq='MS').strftime(
        #     "%Y-%m").tolist()
        self.flightLogger.info(dateRange)
        for i in dateRange:
            try:
                self.getOneData(originPlace = originPlace, destinationPlace = destinationPlace, outboundDate = i)
            except KeyError:
                #이건 무조건 초과 이슈
                time.sleep(30)
            if self.rawFlightQuotes == None:
                continue
            self.updateDB()
            self.clearVar()
            time.sleep(3)
        #속도향상을 위해 조금만 모아서 하ㅏㅈ


        for j in dateRange:
            # 돌아오는 비행기도 알아보자
            self.getOneData(originPlace=destinationPlace, destinationPlace=originPlace, outboundDate=j)
            if self.rawFlightQuotes == None:
                continue
            self.updateDB()
            self.clearVar()
            time.sleep(3)



    def getOneData(self,originPlace, destinationPlace, outboundDate, inboundDate = 0):
        print( "get OneData Start")
        skyOriginPlace = originPlace + "-sky"
        skyDestinationPlace = destinationPlace + "-sky"
        url = f"https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browsequotes/v1.0/US/KRW/en-US/{skyOriginPlace}/{skyDestinationPlace}/{outboundDate}"
        print(url)
        # InboundDate를 쓰려면 주석 해제
        # querystring = {"inboundpartialdate": inboundDate}
        headers = {
        'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
        'x-rapidapi-key': self.key
        }

        response = requests.request("GET", url, headers=headers
                                   #, params=querystring #Inbound Date를 쓰려면 주석 해제
                                    )

        # self.flightLogger.info("(5) getOneData This should Show After getAndUpdateData")
        self.flightLogger.info("Get New data from" + str(url))
        try:
            resultQuotes = response.json()["Quotes"]
            resultCarriers = response.json()["Carriers"]
            resultPlaces = response.json()["Places"]

        except KeyError:
            self.flightLogger.warn("Key Error While Parsing Response. This is Response :" + str(response.text))
            raise KeyError
        self.rawFlightQuotes = self.makeRawFlightQuotes(resultQuotes,originPlace, destinationPlace, outboundDate, inboundDate, self.apiCallId)
        # self.rawFlightCarriers = self.makeRawFlightCarriers(resultCarriers, self.apiCallId)
        # self.rawFlightPlaces = self.makeRawFlightPlaces(resultPlaces, self.apiCallId)

    #TODO : *awg 형식으로 변경, apicallID 생성함수 추가

    def makeIntToString(self,num):
        # 목적은 오직 항상 4자리 string을 주기 위한 것이다.
        # classCounter와 하나의 함수를 만들 수도 있고, 단순한 로직으로 바꿀 수도 있다. 나중에 리팩토링
        # print("일단 들어온 숫자는 ", num)
        if num < 10000:
            return str(num).zfill(4)
        elif num < 100000000:
            return str(num % 10000 + 1).zfill(4)
        else:
            return str(num % 100000000 + 1).zfill(4)


    classCounter = 1
    def makeApiCallId(self):
        prefix = "flightApiCall"
        id = prefix + "_" + self.makeIntToString(FlightQuoteConnector.classCounter) + "_" + str(datetime.now().strftime("%Y%m%d%H%M%S"))
        FlightQuoteConnector.classCounter += 1
        # print(id)
        return id

    def makeRawFlightQuotes(self, quotes, originPlace, destinationPlace, outboundDate, inboundDate ,apiCallId):
        results = []
        pricingOptions = []
        # print(apiCallId)
        # print("iti의 길이")
        # print(len(iti))
        #날짜 데이터 몰아서 정리
        outboundDate = datetime.strptime(outboundDate, "%Y-%m")
        if inboundDate == 0:
            inboundDate == None
        else :
            datetime.strptime(inboundDate, "%Y-%m")
        # 일단 INBOUNd는 무시

        for i in quotes:
            result = DatabaseQuery.RawFlightQuote(
                QuoteId = i["QuoteId"],
                MinPrice = i["MinPrice"],
                Direct = i["Direct"],
                OutboundLeg = i["OutboundLeg"],
                QuoteDateTime = i["QuoteDateTime"],
                originPlace = originPlace,
                destinationPlace = destinationPlace,
                outboundDate = outboundDate,
                apiCallId = apiCallId,
                inboundDate = inboundDate
            )
            results.append(result)
        return results


    def makeRawFlightCarriers(self, carriers, apiCallId):
        results = []
        for i in carriers:
            result = DatabaseQuery.RawFlightCarrier(**i, apiCallId = apiCallId)
            results.append(result)
        return results
    def makeRawFlightPlaces(self, places, apiCallId):
        results = []
        for i in places:
            result = DatabaseQuery.RawFlightPlace(**i, apiCallId =  apiCallId)
            results.append(result)
        return results
    def updateDB(self):
        engine = create_engine(self.enginePath, echo=False)
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add_all(self.rawFlightQuotes)
        # session.add_all(self.rawFlightCarriers)
        # session.add_all(self.rawFlightPlaces)
        session.commit()

        self.flightLogger.info(f"(5) Commit Done - [quotes : {len(self.rawFlightQuotes)}]")
        del session


    def clearVar(self):
        self.rawFlightQuotes = None
        # self.rawFlightCarriers = None
        # self.rawFlightPlaces = None

if __name__ == "__main__":
  print("Yeah")