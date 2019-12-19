# 일단 아래에 필요한 모든 코드를 한 번에 적는다.
# 동작이 모두 완벽히 잘 되는지 확인한다.
# 객체지향으로 변경한다.
# 모듈화해 문서를 쪼갠다.
# 완성!!

# atom script에서 utf-8을 해결하기 위한 코드 - 시작

import sys
import io
from typing import List, Any

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


Base = declarative_base()
metadata = Base.metadata
#databaseQuery 모듈을 위한 내용들 - 끝

import DatabaseQuery
import requests

# 대충 구조는 비슷한 것 같다.
import xml.etree.ElementTree as ET
import logging
import os,inspect

class WeatherConnector():
    weatherLogger = ""
    rawWeatherSeouls: List[Any] = []
    def __init__(self,url,enginePath):
        self.url = url
        self.enginePath = enginePath
        path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        #Logging 코드 작성
        self.weatherLogger = logging.getLogger("weather")
        self.weatherLogger.setLevel(logging.INFO)
        streamHandler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        streamHandler.setFormatter(formatter)
        self.weatherLogger.addHandler(streamHandler)
        fileHandler = logging.FileHandler(path+"/main.log")
        fileHandler.setFormatter(formatter)
        self.weatherLogger.addHandler(fileHandler)
        self.weatherLogger.info("(1) This is the Initiation : Should Show Once")
        self.alchemyLogger = logging.getLogger('sqlalchemy.engine')
        self.alchemyLogger.setLevel(logging.INFO)
        self.alchemyLogger.addHandler(streamHandler)
        self.alchemyLogger.addHandler(fileHandler)

    def getData(self):
        response = requests.get(self.url)
        root = ET.fromstring(response.text)
        results = root.findall("./channel/item/description/body/data")
        for result in results:
            a = {
                "hour" :result.find(".hour").text,
                "day" : result.find(".day").text,
                "temp" : result.find(".temp").text,
                "tmx" : result.find(".tmx").text,
                "sky" : result.find(".sky").text,
                "pty" : result.find(".pty").text,
                "wfKor" : result.find(".wfKor").text,
                "wfEn" : result.find(".wfEn").text,
                "pop" : result.find(".pop").text,
                "ws" : result.find(".ws").text,
                "wd" : result.find(".wd").text,
                "wdKor" : result.find(".wdKor").text,
                "wdEn" : result.find(".wdEn").text,
                "reh" : result.find(".reh").text
            }
            rawWeatherSeoul = DatabaseQuery.RawWeatherSeoulOnly(**a)
            self.rawWeatherSeouls.append(rawWeatherSeoul)
        self.weatherLogger.info("{url:%s, sizeOfRawWeatherRecords : %d}" %(str(self.url), len(self.rawWeatherSeouls)))
    def updateDB(self):
        if len(self.rawWeatherSeouls) == 0:
            return "없어서 그만"
        engine = create_engine(self.enginePath, echo=True)
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add_all(self.rawWeatherSeouls)
        session.commit()
    def clearVar(self):
        self.rawWeatherSeouls = None
