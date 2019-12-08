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
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding = 'utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding = 'utf-8')
# atom script에서 utf-8을 해결하기 위한 코드 -끝
import DatabaseQuery

from datetime import datetime
from datetime import date

#databaseQuery 모듈을 위한 내용들
from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.mysql import INTEGER, LONGTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import sqlalchemy as db


class FlightConnector():
    sessionUrl = ""
    sessionQueryString = {}
    sessionHeaders = {}
    sessionKey = ""
    rawFlightItineraries = []
    rawFlightSegments = []
    rawFlightLegs = []
    rawFlightCarriers = []
    rawFlightAgents = []
    def __init__(self,outboundDate, inboundDate, pageIndex, pageSize,url,key,enginePath):
        self.outboundDate = outboundDate
        self.inboundDate = inboundDate
        self.pageIndex = pageIndex
        self.pageSize = pageSize
        self.url = url
        self.key = key
        self.enginePath = enginePath

    def createSession(self):
        url = self.url
        payload = "inboundDate=2020-01-06&cabinClass=economy&children=0&infants=0&country=US&currency=KRW&locale=en-US&originPlace=ICN-sky&destinationPlace=JFK-sky&outboundDate=2020-01-02&adults=1"
        headers = {
        'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
        'x-rapidapi-key': self.key,
        'content-type': "application/x-www-form-urlencoded"
        }
        response = requests.request("POST", url, data=payload, headers=headers)
        self.sessionKey = response.headers["Location"].split('/')[-1]
        print("Session Key:", self.sessionKey)

    def getData(self):
        url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/pricing/uk2/v1.0/"
        queryUrl = url + self.sessionKey
        querystring = {"originAirports":"ICN","destinationAirports":"JFK","pageIndex":"0","pageSize":"10000"}

        headers = {
        'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
        'x-rapidapi-key': "ab2bb01f37msha32356797613784p1c4e2ejsn75d5549b2f53"
        }
        response = requests.request("GET", queryUrl, headers=headers, params=querystring)
        print(response.status_code)
        print(response.text)
        print(response.json())
        resultQuery = response.json()["Query"]
        resultItineraries = response.json()["Itineraries"]
        resultLegs = response.json()["Legs"]
        resultSegments = response.json()["Segments"]
        resultCarriers = response.json()["Carriers"]
        resultAgents = response.json()["Agents"]
        resultPlaces = response.json()["Places"]
        self.apiCallId = self.makeApiId()
        self.rawFlightItineraries = self.makeRawFlightItineraries(iti = resultItineraries, query = resultQuery, apiCallId = self.apiCallId)
        self.rawFlightLegs = self.makeRawFlightLegs(resultLegs, self.apiCallId)
        self.rawFlightSegments = self.makeRawFlightSegments(resultSegments, self.apiCallId)
        self.rawFlightCarriers = self.makeRawFlightCarriers(resultCarriers, self.apiCallId)
        self.rawFlightPlaces = self.makeRawFlightPlaces(resultPlaces, self.apiCallId)
        self.rawFlightAgents = self.makeRawFlightAgents(resultAgents, self.apiCallId)
        print("**************")
        print(self.rawFlightItineraries)
        if len(self.rawFlightItineraries) > 0:
            return True
        else :
            return False

    #TODO : *awg 형식으로 변경, apicallID 생성함수 추가

    def makeIntToString(self,num):
        # 목적은 오직 항상 4자리 string을 주기 위한 것이다.
        # classCounter와 하나의 함수를 만들 수도 있고, 단순한 로직으로 바꿀 수도 있다. 나중에 리팩토링
        print("일단 들어온 숫자는 ", num)
        if num < 10:
            return("000" + str(num))
        elif num < 100 :
            return("00" + str(num))
        elif num < 1000 :
            return("0" + str(num))
        elif num < 10000:
            return(str(num))
        else:
            #1000 초과시 안전을 위해 밑 자리만 자르고 다시 한다!
            print("classCounter가 10000이상이어서 자르고 다시 makeIntToString으로 재귀")
            makeInt(num%10000)
    classCounter = 1
    def makeApiId(self):
        prefix = "flightApiCall"
        id = prefix + "_" + self.makeIntToString(FlightConnector.classCounter) + "_" + str(datetime.now().strftime("%Y%m%d%H%M%S"))
        FlightConnector.classCounter += 1
        print(id)
        return id

    def makeRawFlightItineraries(self, iti, query,apiCallId):
        results = []
        print(apiCallId)
        print("iti의 길이")
        print(len(iti))
        for i in iti:
            result = DatabaseQuery.RawFlightItinerary(
                OutboundLegId = i["OutboundLegId"],
                InboundLegId = i["InboundLegId"],
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
        return results
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
        engine = create_engine(self.enginePath, echo=True)
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add_all(self.rawFlightItineraries)
        session.add_all(self.rawFlightLegs)
        session.add_all(self.rawFlightSegments)
        session.add_all(self.rawFlightCarriers)
        session.add_all(self.rawFlightPlaces)
        session.add_all(self.rawFlightAgents)
        session.commit()
    #     iti는 resultItineraries, query는 resultQuery입니다.


if __name__ == "__main__":
    #TODO : Paging을 써야 함 ㅜ 안그러면 감당을 못하는 듯..
    for i in range(1,1000):
        print(i,"번째")
        flightConnector = FlightConnector(20200106, 20200110,pageIndex=i, pageSize = 10)
        flightConnector.createSession()
        hasResult = flightConnector.getData()
        if hasResult:
            flightConnector.updateDB()
        else:
            break
