# 아래는 database 입출력 관련된 내용만 모아놓는다!s

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


Base = declarative_base()
metadata = Base.metadata


class DBModel:
    def makeIntToString(self,num):
        # 목적은 오직 항상 4자리 string을 주기 위한 것이다.
        # classCounter와 하나의 함수를 만들 수도 있고, 단순한 로직으로 바꿀 수도 있다. 나중에 리팩토링
        if num < 10000 :
            return str(num).zfill(4)
        elif num < 100000000:
            return str(num%10000 + 1).zfill(4)
        else:
            return str(num%100000000 + 1).zfill(4)

    classCounter = 1
    def makeId(self,prefix):
        id = prefix + "_" + self.makeIntToString(DBModel.classCounter) + "_" + str(datetime.now().strftime("%Y%m%d%H%M%S"))
        DBModel.classCounter += 1

        return id

class Exchange(Base):
    __tablename__ = 'exchange'

    exchangeId = Column(String(100), primary_key=True)
    currencyName = Column(String(100))
    todayRate = Column(INTEGER(11))
    weekAgoRate = Column(INTEGER(11))
    monthAgoRate = Column(INTEGER(11))
    rateList = Column(Text)
    rateTitle = Column(Text)
    rateDescription = Column(LONGTEXT)
    created = Column(DateTime, nullable=False)
    dateToShow = Column(DateTime, nullable=False)


class FlightPrice(Base):
    __tablename__ = 'flightPrice'

    flightPriceId = Column(String(100), primary_key=True)
    placeId = Column(String(100))
    flightPriceTitle = Column(Text)
    flightPriceDescription = Column(LONGTEXT)
    flightMonthAgoAverage = Column(INTEGER(11))
    flightMonthAgoMinumum = Column(INTEGER(11))
    flightTodayAverage = Column(INTEGER(11))
    flightTodayMinimum = Column(INTEGER(11))
    created = Column(DateTime, nullable=False)
    dateToShow = Column(DateTime, nullable=False)


class HotelPrice(Base):
    __tablename__ = 'hotelPrice'

    hotelPriceId = Column(String(100), primary_key=True)
    placeId = Column(String(100))
    hotelPriceTitle = Column(Text)
    hotelPriceDescription = Column(LONGTEXT)
    generalAverage = Column(INTEGER(11))
    luxuryAverage = Column(INTEGER(11))
    hostelAverage = Column(INTEGER(11))
    created = Column(DateTime, nullable=False)
    dateToShow = Column(DateTime, nullable=False)


class PlaceMainDesc(Base):
    __tablename__ = 'placeMainDesc'

    placeMainDescId = Column(String(100), primary_key=True)
    score = Column(INTEGER(11))
    placeId = Column(String(100))
    placeMainDescription = Column(LONGTEXT)
    created = Column(DateTime, nullable=False)
    dateToShow = Column(DateTime, nullable=False)


class PlaceOp(Base):
    __tablename__ = 'placeOp'

    placeOpId = Column(String(100), primary_key=True)
    placeId = Column(String(100))
    opMsgTitle = Column(Text)
    opMsgDesc = Column(LONGTEXT)
    created = Column(DateTime, nullable=False)
    dateToShow = Column(DateTime, nullable=False)


class PlaceStatic(Base):
    __tablename__ = 'placeStatic'

    placeId = Column(String(100), primary_key=True)
    countryName = Column(String(100))
    currencyName = Column(String(100))
    subtitle = Column(Text)
    titleKor = Column(String(100))
    titleEng = Column(String(100))
    created = Column(DateTime, nullable=False)


class Weather(Base):
    __tablename__ = 'weather'

    weatherId = Column(String(100), primary_key=True)
    placeId = Column(String(100))
    weatherTitle = Column(Text)
    weatherDescription = Column(LONGTEXT)
    averageTemp = Column(INTEGER(11))
    seoulTemp = Column(INTEGER(11))
    rainDays = Column(INTEGER(11))
    created = Column(DateTime, nullable=False)
    dateToShow = Column(DateTime, nullable=False)

class RawExchange(Base, DBModel):
    __tablename__ = 'rawExchange'

    rawExchangeId = Column(String(100), primary_key=True)
    result = Column(INTEGER(11))
    currencyUnit = Column(String(100))
    currencyName = Column(String(100))
    transferBuying = Column(String(100))
    transferSelling = Column(String(100))
    basicRate = Column(String(100))
    bookRate = Column(String(100))
    yearRate = Column(String(100))
    tenDaysRate = Column(String(100))
    korBasicRate = Column(String(100))
    korBookRate = Column(String(100))
    writeDate = Column(DateTime)
    rateDate = Column(DateTime)

    classCounter = 1
    prefix = "rawExchange"


    def __init__(self,rateDate, result, cur_unit, cur_nm, ttb, tts, deal_bas_r, bkpr, yy_efee_r, ten_dd_efee_r,kftc_bkpr,kftc_deal_bas_r):
        self.currencyUnit = cur_unit
        self.currencyName = cur_nm #cur_nm이 완전 한국어네 curUnit을 주로 쓰자
        self.transferBuying = ttb
        self.transferSelling = tts
        self.basicRate = deal_bas_r
        self.bookRate = bkpr
        self.yearRate = yy_efee_r
        self.tenDaysRate = ten_dd_efee_r
        self.korBasicRate = kftc_bkpr
        self.korBookRate = kftc_deal_bas_r
        # 그 외 함께 입력 필요한 값들
        self.writeDate = date.today()
        # print("이번에 들어갈 id 숫자는 ", makeIntToString(classCounter))
        self.prefix = self.__tablename__[0].lower() + self.__tablename__[1:]
        self.rawExchangeId = self.makeId(self.prefix)
        # classCounter는 instance가 아니라 원본 class의 것이기 때문
        RawExchange.classCounter += 1
        self.rateDate = rateDate


class RawWeatherSeoulOnly(Base,DBModel):
    __tablename__ = 'rawWeatherSeoulOnly'

    rawWeatherSeoulId = Column(String(100), primary_key=True)
    temperature = Column(Float)
    temperatureMax = Column(Float)
    skyCode = Column(INTEGER(11))
    waterfallCode = Column(INTEGER(11))
    waterfallKor = Column(String(100))
    waterfallEng = Column(String(100))
    waterfallProb = Column(Float)
    windSpeed = Column(INTEGER(11))
    windDirection = Column(INTEGER(11))
    windDirectionKor = Column(String(100))
    windDirectionEng = Column(String(100))
    humidity = Column(Float)
    writeDate = Column(DateTime)
    forcastDate = Column(DateTime)


    classCounter = 1

    def makeForcastDate(self,hour, day):
        now = datetime.now()
        hourInt = int(hour)
        if hourInt == 24:
            now.replace(day = now.day + 1)
            hourInt = 0
            now = now.replace(hour = hourInt)
            now = now.replace(minute = 0)
            now = now.replace(second = 0)
            return now
        else :
            now = now.replace(day = now.day + int(day))
            now = now.replace(hour = hourInt)
            now = now.replace(minute = 0)
            now = now.replace(second = 0)
            return now

    def __init__(self,hour, day, temp, tmx, sky, pty, wfKor, wfEn, pop, ws, wd, wdKor, wdEn, reh):
        # init할 때 API의 명칭을 readable하게 바꿈.
        # json의 순서에 영향을 받는지 확인하자
        # result는 무시하기 위해 받는다.

        # API 결과 -> mysql 형태
        self.prefix = self.__tablename__[0].lower() + self.__tablename__[1:]
        self.forcastDate = self.makeForcastDate(hour,day)
        self.temperature = temp
        self.temperatureMax = tmx #cur_nm이 완전 한국어네 curUnit을 주로 쓰자
        self.skyCode = sky
        self.waterfallCode = pty
        self.waterfallKor = wfKor
        self.waterfallEng = wfEn
        self.waterfallProb = pop
        self.windSpeed = ws
        self.windDirection = wd
        self.windDirectionKor = wdKor
        self.windDirectionEng = wdEn
        self.humidity = reh

        # 그 외 함께 입력 필요한 값들
        self.writeDate = datetime.now()
        # print("이번에 들어갈 id 숫자는 ", makeIntToString(classCounter))
        self.rawWeatherSeoulId = self.makeId(self.prefix)
        # classCounter는 instance가 아니라 원본 class의 것이기 때문
        # RawWeatherSeoulOnly.classCounter += 1

class RawFlightAgent(Base,DBModel):
    __tablename__ = 'RawFlightAgents'

    rawFlightAgentsId = Column(String(100), primary_key=True)
    agentsId = Column(INTEGER(11))
    carrierImageUrl = Column(String(100))
    writeDate = Column(DateTime)
    apiCallId = Column(String(100))


    def __init__(self, Id, Name, ImageUrl, Status, OptimisedForMobile, Type, apiCallId):
        # init할 때 API의 명칭을 readable하게 바꿈.
        # json의 순서에 영향을 받는지 확인하자
        # prefix는 table명 첫글자 소문자화
        self.prefix = self.__tablename__[0].lower() + self.__tablename__[1:]
        self.rawFlightAgentsId = self.makeId(self.prefix)
        # API 결과 -> mysql 형태
        self.agentsId = Id
        self.agentImageUrl = ImageUrl
        self.OptimisedForMobile = OptimisedForMobile #cur_nm이 완전 한국어네 curUnit을 주로 쓰자
        self.type = Type
        self.writeDate = datetime.now()
        self.apiCallId = apiCallId
        self.rawWeatherSeoulId = self.makeId(self.prefix)


class RawFlightCarrier(Base,DBModel):
    __tablename__ = 'RawFlightCarriers'

    rawFlightCarriersId = Column(String(100), primary_key=True)
    carrierId = Column(INTEGER(11))
    carrierCode = Column(String(100))
    carrierName = Column(String(100))
    carrierImageUrl = Column(String(100))
    writeDate = Column(DateTime)
    apiCallId = Column(String(100))


    def __init__(self,Id, DisplayCode, Code, Name, ImageUrl, apiCallId):
        # prefix는 table명 첫글자 소문자화
        # DisplayCode는 유입시 에러 안나게

        self.prefix = self.__tablename__[0].lower() + self.__tablename__[1:]
        self.rawFlightCarriersId = self.makeId(self.prefix)
        self.carrierId = Id
        self.carrierCode = Code
        self.carrierName = Name
        self.carrierImageUrl = ImageUrl
        self.writeDate = datetime.now()
        self.apiCallId = apiCallId


class RawFlightItinerary(Base, DBModel):
    __tablename__ = 'RawFlightItineraries'

    rawFlightItinerariesId = Column(String(100), primary_key=True)
    outboundLegId = Column(String(100))
    inboundLegId = Column(String(100))
    pricingOptions = Column(Text)
    bookingDetailsLink = Column(Text)
    apiCallId = Column(String(100))
    queryAdults = Column(INTEGER(11))
    queryChildren = Column(INTEGER(11))
    queryOriginPlace = Column(String(100))
    queryDestinationPlace = Column(String(100))
    queryOutboundDate = Column(DateTime)
    queryInboundDate = Column(DateTime)
    queryCabinClass = Column(String(100))
    queryGroupingPricing = Column(TINYINT(1))
    writeDate = Column(DateTime)



    def __init__(self,OutboundLegId, InboundLegId, PricingOptions, BookingDetailsLink, Adults, Children, OriginPlace, DestinationPlace, OutboundDate, InboundDate, CabinClass, GroupPricing, apiCallId):

        # prefix는 table명 첫글자 소문자화
        self.prefix = self.__tablename__[0].lower() + self.__tablename__[1:]

        self.rawFlightItinerariesId = self.makeId(self.prefix)
        self.outboundLegId = str(OutboundLegId)
        self.inboundLegId = str(InboundLegId)
        # self.pricingOptions = str(PricingOptions)
        self.bookingDetailsLink = str(BookingDetailsLink)
        self.queryAdults = str(Adults)
        self.queryChildren = str(Children)
        self.queryOriginPlace = str(OriginPlace)
        self.queryDestinationPlace = str(DestinationPlace)
        self.queryOutboundDate = datetime.strptime(OutboundDate,'%Y-%m-%d')
        self.queryInboundDate = datetime.strptime(InboundDate,'%Y-%m-%d')
        self.queryCabinClass = str(CabinClass)
        self.queryGroupPricing = int(GroupPricing)
        self.apiCallId = apiCallId
        self.writeDate = datetime.now()


class RawFlightPricingOption(Base, DBModel):
    __tablename__ = 'RawFlightPricingOptions'

    rawFlightPricingOptionsId = Column(String(100), primary_key=True)
    rawFlightItinerariesId = Column(String(100))
    agents = Column(Text)
    price = Column(Float)
    deepLinkUrl = Column(Text)
    writeDate = Column(DateTime)
    def __init__(self,rawFlightItinerariesId, agents, price, deepLinkUrl):
        # prefix는 table명 첫글자 소문자화
        self.prefix = self.__tablename__[0].lower() + self.__tablename__[1:]
        self.rawFlightPricingOptionsId = self.makeId(self.prefix)
        self.rawFlightItinerariesId = rawFlightItinerariesId
        self.agents = str(agents)
        self.price = float(price)
        self.deepLinkUrl = str(deepLinkUrl)


class RawFlightLeg(Base, DBModel):
    __tablename__ = 'RawFlightLegs'

    rawFlightLegsId = Column(String(100), primary_key=True)
    legId = Column(String(100))
    segmentsIds = Column(Text)
    originStation = Column(String(100))
    destinationStation = Column(String(100))
    departureDatetime = Column(DateTime)
    arrivalDatetime = Column(DateTime)
    duration = Column(INTEGER(11))
    journeyMode = Column(String(100))
    stops = Column(Text)
    carriers = Column(Text)
    operatingCarriers = Column(Text)
    directionality = Column(String(100))
    flightNumbers = Column(Text)
    writeDate = Column(DateTime)
    apiCallId = Column(String(100))


    def __init__(self, Id, SegmentIds, OriginStation, DestinationStation, Departure, Arrival, Duration, JourneyMode, Stops, Carriers, OperatingCarriers, Directionality, FlightNumbers, apiCallId):

        # prefix는 table명 첫글자 소문자화
        self.prefix = self.__tablename__[0].lower() + self.__tablename__[1:]

        self.rawFlightLegsId = self.makeId(self.prefix)
        self.legId = str(Id)
        self.segmentsIds = str(SegmentIds)
        self.originStation = str(OriginStation)
        self.destinationStation = str(DestinationStation)
        self.departureDatetime = datetime.strptime(Departure,'%Y-%m-%dT%H:%M:%S')
        self.arrivalDatetime = datetime.strptime(Arrival,'%Y-%m-%dT%H:%M:%S')
        self.duration = int(Duration)
        self.journeyMode = str(JourneyMode)
        self.stops = str(Stops)
        self.carriers = str(Carriers)
        self.operatingCarriers = str(OperatingCarriers)
        self.directionality = str(Directionality)
        self.flightNumbers = str(FlightNumbers)
        self.writeDate = datetime.now()
        self.apiCallId = apiCallId




class RawFlightSegment(Base, DBModel):
    __tablename__ = 'RawFlightSegments'

    rawFlightSegmentsId = Column(String(100), primary_key=True)
    segId = Column(String(100))
    originStation = Column(String(100))
    destinationStation = Column(String(100))
    departureDatetime = Column(DateTime)
    arrivalDatetime = Column(DateTime)
    carrier = Column(String(100))
    operatingCarrier = Column(String(100))
    duration = Column(INTEGER(11))
    flightNumber = Column(String(100))
    journeyMode = Column(String(100))
    directionality = Column(String(100))
    writeDate = Column(DateTime)
    apiCallId = Column(String(100))


    def __init__(self, Id, OriginStation, Directionality, DestinationStation, DepartureDateTime, ArrivalDateTime, Duration, JourneyMode,Carrier, OperatingCarrier, FlightNumber, apiCallId):

        # prefix는 table명 첫글자 소문자화
        self.prefix = self.__tablename__[0].lower() + self.__tablename__[1:]

        self.rawFlightSegmentsId = self.makeId(self.prefix)
        self.segId = str(Id)
        self.originStation = str(OriginStation)
        self.destinationStation = str(DestinationStation)
        self.departureDatetime = datetime.strptime(DepartureDateTime,'%Y-%m-%dT%H:%M:%S')
        self.arrivalDatetime = datetime.strptime(ArrivalDateTime,'%Y-%m-%dT%H:%M:%S')
        self.duration = int(Duration)
        self.journeyMode = str(JourneyMode)
        self.carrier = str(Carrier)
        self.operatingCarrier = str(OperatingCarrier)
        self.flightNumber = str(FlightNumber)
        self.directionality = str(Directionality)
        self.writeDate = datetime.now()
        self.apiCallId = apiCallId

class RawFlightPlace(Base, DBModel):
    __tablename__ = 'RawFlightPlaces'

    rawFlightPlacesId = Column(String(100), primary_key=True)
    skyscannerPlaceId = Column(INTEGER(11))
    skyscannerPlaceParentId = Column(INTEGER(11))
    skyscannerPlaceCode = Column(String(100))
    skyscannerPlaceType = Column(String(100))
    skyscannerPlaceName = Column(String(100))
    apiCallId = Column(String(100))
    writeDate = Column(DateTime)

    def __init__(self, Id,  Type, Name, apiCallId, ParentId = 0, Code = "0"):
        assert apiCallId != None
        # ParentId가 없는 경우, 0으로 채움
        self.prefix = self.__tablename__[0].lower() + self.__tablename__[1:]
        self.rawFlightPlacesId = self.makeId(self.prefix)
        self.skyscannerPlaceId = Id
        self.skyscannerPlaceParentId = ParentId
        self.skyscannerPlaceCode = Code
        self.skyscannerPlaceType = Type
        self.skyscannerPlaceName = Name
        self.apiCallId = apiCallId
        self.writeDate = datetime.now()


# if __name__ == "__main__":
#     # engine = create_engine('mysql+pymysql://root
#     :1234567890@localhost/eightDays', echo=True)
#     # Session = sessionmaker(bind=engine)
#     # session = Session()
#     # session.add(RawExchange(rawExchangeId = "32"))
#
