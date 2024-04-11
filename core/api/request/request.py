import requests
import re
import json
from datetime import datetime

from core.constants import core_constant
from core.utils.level import level


def send_get_request(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error during requests to {url} : {e}")
        return None


def parse_json(json_string):
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None


def main(*, config):
    ans = send_get_request(
        "{}/list?latest={}".format(core_constant.CWA_REPORT_URL, config['fetch_data_length']))
    if ans:
        data = parse_json(ans)
        if data != None and data["success"]:
            EQList = []
            New_EQList = []
            for eq in data['data']:
                report_ans = send_get_request(
                    "{}/detail?identifier={}".format(core_constant.CWA_REPORT_URL, eq["identifier"]))
                if report_ans:
                    report_data = parse_json(report_ans)
                    if report_data != None and report_data["success"]:

                        max_intensity = 0
                        for max_area in report_data['data']:
                            for station in max_area['eqStation']:
                                if station['stationIntensity'] > max_intensity:
                                    max_intensity = station['stationIntensity']

                        max_intensity_stations = []
                        for max_area in report_data['data']:
                            for station in max_area['eqStation']:
                                if station['stationIntensity'] == max_intensity:
                                    max_intensity_stations.append("{}{}".format(
                                        max_area['areaName'], station['stationName']))

                        EQOriginTime = eq["originTime"]
                        EQOriginYear = int(datetime.strptime(
                            EQOriginTime, "%Y-%m-%d %H:%M:%S").year) - 1911
                        EQOriginDate = datetime.strptime(
                            EQOriginTime, "%Y-%m-%d %H:%M:%S").strftime(f"{EQOriginYear}年 %m月 %d日")
                        EQTime = datetime.strptime(
                            EQOriginTime, "%Y-%m-%d %H:%M:%S").strftime("%H時 %M分 %S秒")
                        EQDateTime = datetime.strptime(
                            EQOriginTime, "%Y-%m-%d %H:%M:%S").strftime(f"%m/%d-%H:%M")

                        EQLon = eq["epicenterLon"]
                        EQLat = eq["epicenterLat"]

                        match = re.search(r'位於(.+?)\)', eq["location"])
                        loc = None
                        if match:
                            loc = match.group(1)
                        CWBContent = None
                        if loc != None:
                            CWBContent = "{}{}發生規模{}有感地震。".format(
                                EQDateTime, loc, f"{eq['magnitudeValue']:.1f}")

                        EQinfo = {
                            "ID": None,
                            "CWBEventID": eq["identifier"],
                            "CWBOriginTime": EQOriginTime,
                            "CWBAnimation": None,
                            "CWBOriginYear": EQOriginYear,
                            "CWBOriginDate": EQOriginDate,
                            "CWBTime": EQTime,
                            "CWBContent": CWBContent,
                            # "CWBContent": "{}{}發生規模{}有感地震，最大震度{}{}。".format(EQDateTime, loc, f"{eq['magnitudeValue']:.1f}", '、'.join(max_intensity_stations), level(max_intensity)),
                            "CWBMsg": "即在 {L}".format(L=eq["location"]),
                            "CWBDepth": eq["depth"],
                            "CWBDepthUnit": "公里",
                            "CWBLon": EQLon,
                            "CWBLat": EQLat,
                            "CWBLocation": "北緯 {}度．東經 {}度".format(f"{EQLat:.2f}", f"{EQLon:.2f}"),
                            "CWBMagnitudeLevel": f"{eq['magnitudeValue']:.1f}",
                            "CWBMagnitudeType": "芮氏規模",
                        }

                        Info = {
                            "ID": None,
                            "Serial": eq["identifier"],
                            "Lat": EQLat,
                            "Lon": EQLon,
                            "Depth": eq["depth"],
                            "Mag": f"{eq['magnitudeValue']:.1f}",
                            "Time": EQOriginTime,
                            "Loc": loc,
                            "Max": report_data['data'][0]['areaIntensity']
                        }

                        EQList.append(EQinfo)
                        New_EQList.append(Info)

            return {"EQList": EQList, "New_EQList": New_EQList}


if __name__ == "__main__":
    pass
