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

#databaseQuery 모듈을 위한 내용들
from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.mysql import INTEGER, LONGTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import sqlalchemy as db

import logging
import os, inspect

class FlightConnector():

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

    def setDateOption(self, outboundDate,inboundDate):
        self.outboundDate = outboundDate #inbound/OutboundDate는 항상 "%Y-%m-%d" String이어야 한다.
        self.inboundDate = inboundDate

    def setGridSearchDatesByConstant(self,dateRange, minimumTerm,maximumTerm):
        if type(dateRange) != list or len(dateRange) != 2:
            raise ValueError
        startDate, endDate = dateRange
        startDateFormatted = dateutil.parser.parse(startDate)
        endDateFormatted = dateutil.parser.parse(endDate)
        dateList = []
        timeDelta = endDateFormatted - startDateFormatted
        self.gridSearchDatesList = []
        for i in range(timeDelta.days + 1):
            day = startDateFormatted + timedelta(days=i)
            dateList.append(day)
        for oDate in dateList:
            for iDate in dateList:
                if ((iDate - oDate) >= timedelta(days=minimumTerm)) and ((iDate - oDate) <= timedelta(days = maximumTerm)):
                    dateTuple = (oDate.strftime("%Y-%m-%d"), iDate.strftime("%Y-%m-%d"))
                    self.gridSearchDatesList.append(dateTuple)

    def setGridSearchDates(self, outboundDateRange,inboundDateRange):
        # 각각의 Range는 시작, 끝으로 구성된 두 개의 값을 가진 List여야 한다.
        if type(outboundDateRange) != list or len(outboundDateRange) != 2:
            raise ValueError
        outboundStart, outboundEnd = outboundDateRange
        outboundStartDate = dateutil.parser.parse(outboundStart)  # start date
        outboundEndDate = dateutil.parser.parse(outboundEnd)
        inboundStart, inboundEnd = inboundDateRange
        inboundStartDate = dateutil.parser.parse(inboundStart)  # start date
        inboundEndDate = dateutil.parser.parse(inboundEnd)

        outboundDelta = outboundEndDate - outboundStartDate
        inboundDelta = inboundEndDate - inboundStartDate

        outboundDateList = []
        inboundDateList = []
        for i in range(outboundDelta.days + 1):
            day = outboundStartDate + timedelta(days=i)
            outboundDateList.append(day)
        for k in range(inboundDelta.days + 1):
            day = inboundStartDate + timedelta(days=k)
            inboundDateList.append(day)


        for oDate in outboundDateList:
            for iDate in inboundDateList:
                if oDate < iDate:
                    dateTuple = (oDate.strftime("%Y-%m-%d"),iDate.strftime("%Y-%m-%d"))
                    self.gridSearchDatesList.append(dateTuple)

    def gridSearchGetDateAndUpdateDB(self):
        #Tuple의 앞이 항상 outbound입니다.
        #아니라면 API 에러 뽑겠지
        for dateTuple in self.gridSearchDatesList:
            outDate, inDate = dateTuple
            self.setDateOption(outboundDate=outDate, inboundDate=inDate)
            try:
                self.createSession()
            except KeyError as error:
                #이번 날짜 Tuple은 날린다.
                time.sleep(30)
                continue
            self.getAndUpdateData()
            self.clearVar()
            # 무료 API여서 약 분당 40회(호출당 두번 * 20회) 하기 위해 쉰다.
            time.sleep(3)



    # TODO : Create Grid Search Function
    # TODO : Grid Search -> Execute
    def setOption(self,destinationPlace, originPlace = "ICN" , cabinClass = "economy", children = 0, infants= 0, adults = 1):
        # 공항 코드를 받아서, skyscanner parameter로 바꿈.
        self.originPlace = originPlace
        self.destinationPlace = destinationPlace
        self.payLoadOriginPlace = originPlace + "-sky"
        self.payLoadDestinationPlace = destinationPlace + "-sky"
        self.cabinClass = cabinClass
        self.children = children
        self.infants = infants
        self.adults = adults
        self.flightLogger.info("setOption self.originPlace : " + str(self.originPlace) + ", self.destinationPlace : " + str(self.destinationPlace))

    def createSession(self):
        url = self.url
        payload = f"inboundDate={self.inboundDate}&cabinClass={self.cabinClass}&children={self.children}&infants={self.infants}&country=KO&currency=KRW&locale=en-US&originPlace={self.payLoadOriginPlace}&destinationPlace={self.payLoadDestinationPlace}&outboundDate={self.outboundDate}&adults={self.adults}"
        # payload = "inboundDate=2020-01-06&cabinClass=economy&children=0&infants=0&country=US&currency=KRW&locale=en-US&originPlace=ICN-sky&destinationPlace=JFK-sky&outboundDate=2020-01-02&adults=1"
        headers = {
        'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
        'x-rapidapi-key': self.key,
        'content-type': "application/x-www-form-urlencoded"
        }
        response = requests.request("POST", url, data=payload, headers=headers)
        # self.flightLogger.info("(2) create Session should show first of all other methods except Init")
        self.flightLogger.info("created Session with:" +str(payload))
        # print(response.headers)
        # print(response.json())
        try:
            self.sessionKey = response.headers["Location"].split('/')[-1]
        except KeyError:
            self.flightLogger.warn("No SessionKey Returned. Response Body :" + str(response.text))
            raise KeyError("No Session Key")
        # print("Session Key:", self.sessionKey)

    def getAndUpdateData(self):
        # 해당 inboundDate, outboundDate의 모든 index, page의 데이터를 순차적으로 commit한다.
        # self.flightLogger.info("(4) getAndUpdateData : This should Show after getAndUpdateData")
        for i in range(1, 1000):
            # print(i, "번째")
            try :
                hasResult = self.getOneData(pageIndex = i, pageSize=500)
            except KeyError:
                time.sleep(30)
                continue

            # print("결과가 있나요?",hasResult)
            if hasResult:
                self.updateDB()
            else:
                break

    def getOneData(self,pageIndex = 1, pageSize = 1000):
        url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/pricing/uk2/v1.0/"
        queryUrl = url + self.sessionKey
        querystring = {"originAirports":self.originPlace,"destinationAirports":self.destinationPlace,"pageIndex":pageIndex,"pageSize":pageSize}
        headers = {
        'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
        'x-rapidapi-key': self.key
        }

        response = requests.request("GET", queryUrl, headers=headers, params=querystring)
        # print(response.status_code)
        # print(response.text)
        # print(response.json())
        # self.flightLogger.info("(5) getOneData This should Show After getAndUpdateData")
        self.flightLogger.info("Get New data from" + str(querystring))
        try:
            resultQuery = response.json()["Query"]
            resultItineraries = response.json()["Itineraries"]
            resultLegs = response.json()["Legs"]
            resultSegments = response.json()["Segments"]
            resultCarriers = response.json()["Carriers"]
            resultAgents = response.json()["Agents"]
            resultPlaces = response.json()["Places"]
            self.apiCallId = self.makeApiCallId()
        except KeyError:
            self.flightLogger.warn("Key Error While Parsing Response. This is Response :" + str(response.text))
            raise KeyError
        # print("ApiCallId는:", self.apiCallId)

        self.rawFlightItineraries, self.rawPricingOptions = self.makeRawFlightItineraries(iti = resultItineraries, query = resultQuery, apiCallId = self.apiCallId)
        self.rawFlightLegs = self.makeRawFlightLegs(resultLegs, self.apiCallId)
        self.rawFlightSegments = self.makeRawFlightSegments(resultSegments, self.apiCallId)
        self.rawFlightCarriers = self.makeRawFlightCarriers(resultCarriers, self.apiCallId)
        self.rawFlightPlaces = self.makeRawFlightPlaces(resultPlaces, self.apiCallId)
        self.rawFlightAgents = self.makeRawFlightAgents(resultAgents, self.apiCallId)
        # print("**************")
        # print(self.rawFlightItineraries)
        if len(self.rawFlightItineraries) > 0:
            return True
        else :
            return False

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
        id = prefix + "_" + self.makeIntToString(FlightConnector.classCounter) + "_" + str(datetime.now().strftime("%Y%m%d%H%M%S"))
        FlightConnector.classCounter += 1
        # print(id)
        return id

    def makeRawFlightItineraries(self, iti, query,apiCallId):
        results = []
        pricingOptions = []
        # print(apiCallId)
        # print("iti의 길이")
        # print(len(iti))
        for i in iti:
            result = DatabaseQuery.RawFlightItinerary(
                OutboundLegId = i["OutboundLegId"],
                InboundLegId = i["InboundLegId"],
                #임시 삭제
                PricingOptions  = i["PricingOptions"],
                BookingDetailsLink = i["BookingDetailsLink"],
                Adults = query["Adults"],
                Children = query["Children"],
                OriginPlace  = query["OriginPlace"],
                DestinationPlace = query["DestinationPlace"],
                OutboundDate = query["OutboundDate"],
                InboundDate = query["InboundDate"],
                CabinClass = query["CabinClass"],
                GroupPricing = query["GroupPricing"],
                apiCallId = apiCallId)
            results.append(result)
            for k in i["PricingOptions"]:
                pricingOptionResult = DatabaseQuery.RawFlightPricingOption(
                    rawFlightItinerariesId = result.rawFlightItinerariesId,
                    agents = k["Agents"],
                    price = k["Price"],
                    deepLinkUrl = k["DeeplinkUrl"]
                )
                pricingOptions.append(pricingOptionResult)
        return (results, pricingOptions)
    def makeRawFlightLegs(self, legs, apiCallId):
        results = []
        for i in legs:
            result = DatabaseQuery.RawFlightLeg(**i, apiCallId = apiCallId)
            results.append(result)
        return results

    def makeRawFlightSegments(self, segs, apiCallId):
        results = []
        for i in segs:
            result = DatabaseQuery.RawFlightSegment(**i, apiCallId = apiCallId)
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
    def makeRawFlightAgents(self, agents, apiCallId):
        results = []
        for i in agents:
            result = DatabaseQuery.RawFlightAgent(**i, apiCallId = apiCallId)
            results.append(result)
        return results
    def updateDB(self):
        engine = create_engine(self.enginePath, echo=False)
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add_all(self.rawFlightItineraries)
        session.add_all(self.rawPricingOptions)
        session.add_all(self.rawFlightLegs)
        session.add_all(self.rawFlightSegments)
        session.add_all(self.rawFlightCarriers)
        session.add_all(self.rawFlightPlaces)
        session.add_all(self.rawFlightAgents)
        session.commit()

        self.flightLogger.info(f"(5) Commit Done - [itineraries : {len(self.rawFlightItineraries)}, pricingOptions : {len(self.rawPricingOptions)}, legs : {len(self.rawFlightLegs)}, segments : {len(self.rawFlightSegments)},  carriers : {len(self.rawFlightCarriers)}, places : {len(self.rawFlightPlaces)}, agents : {len(self.rawFlightAgents)}]")

        del session

    def clearVar(self):
        self.rawFlightItineraries = None
        self.rawFlightLegs = None
        self.rawFlightCarriers = None
        self.rawFlightSegments = None
        self.rawFlightAgents = None
        self.rawPricingOptions = None

