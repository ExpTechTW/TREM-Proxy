import sys
import time

from core.config import Config
from core.state import State

from core.api.sql.sql import SQL
from core.api.request.request import main
from core.utils.logger import Log
from core.constants import core_constant
from core.api.query.query import FileHandler
from core.utils.line import send
from core.utils.level import level


def rm_tag(id):
    return id.replace(
        "CWB-EQ", "").replace(
        "CWA-EQ", "")


class CWAReportSQL:
    def __init__(self, *, generate_default_only: bool = False, initialize_environment: bool = False):
        self.log = Log()
        self.log.logger.info("Start {} {}".format(
            core_constant.NAME, core_constant.VERSION))

        self.state = State.INITIALIZING
        self.config = Config()

        if generate_default_only:
            self.config.save_default()
            return

        if initialize_environment:
            if not self.config.file_presents():
                self.config.save_default()

        try:
            self.log.logger.info("Config File Reading...")
            self.config.read_config(allowed_missing_file=False)
            self.log.logger.info("Config File Readed")

            self.log.logger.setLevel(self.config._data['log_level'])
            self.log.logger.day = self.config._data['log_save_days']
            self.log.clean_old_logs()

            if self.config._data['discord_webhook']['enable']:
                self.log.setup_discord(
                    url=self.config._data['discord_webhook']['url'], level=self.config._data['discord_webhook']['log_level'])
        except Exception as e:
            self.log.logger.error(
                "Please use the [init] command to initialize the project")
            sys.exit(1)

    def is_initialized(self) -> bool:
        if self.state == State.INITIALIZED:
            return True
        else:
            return False

    def run(self):
        SQL_config = self.config._data['SQL']
        sql_instance = None
        query_sql = False
        query_sql_new = False

        while True:
            if SQL_config['enable']:
                if sql_instance is None:
                    self.log.logger.debug("Enable SQL")
                    self.log.logger.debug(
                        "Connecting to SQL {}".format(SQL_config['address']))
                    sql_instance = SQL(user=SQL_config['user'], password=SQL_config['password'],
                                       address=SQL_config['address'], port=SQL_config['port'], database=SQL_config['database'])
            else:
                self.log.logger.warn("Disenable SQL")

            self.log.logger.info("Fetching CWA Report Data...")
            res = main(config=self.config._data)
            self.log.logger.info("Fetched CWA Report Data")

            file = FileHandler()
            file_txt = file.read()

            if res is None:
                self.log.logger.warn("Unable to obtain data from CWA")
                time.sleep(self.config._data['request_delay'])
            else:
                for ans in res["EQList"]:
                    insert_query = f"""
                    INSERT INTO {SQL_config['table']} (ID, CWBEventID, CWBOriginTime, CWBAnimation, CWBOriginYear, CWBOriginDate, CWBTime, CWBContent, CWBMsg, CWBDepth, CWBDepthUnit, CWBLon, CWBLat, CWBLocation, CWBMagnitudeLevel, CWBMagnitudeType) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

                    if sql_instance and sql_instance.is_connected():

                        if (self.config._data['query_mode'] == "sql" or file_txt == "" or query_sql):
                            query_sql = False
                            sql_instance.cursor.execute(
                                f"SELECT CWBEventID FROM {SQL_config['table']}")
                            cwb_event_ids = [row[0]
                                             for row in sql_instance.cursor.fetchall()]
                            cwb_event_id_strings = [rm_tag(item.decode(
                                'utf-8')) for item in cwb_event_ids]
                            txt = ','.join(cwb_event_id_strings)
                            file.write(txt)
                            file_txt = txt
                            self.log.logger.debug("[query_mode] => sql")
                        else:
                            self.log.logger.debug("[query_mode] => local")
                            cwb_event_id_strings = file.read().split(',')
                        tag = rm_tag(ans['CWBEventID'])
                        if tag not in cwb_event_id_strings:
                            try:
                                sql_instance.cursor.execute(
                                    insert_query, tuple(ans.values()))
                                sql_instance.conn.commit()
                                txt = ",{}".format(tag)
                                file_txt += txt
                                file.write(txt)
                                self.log.logger.info(
                                    "Success Writting Data to SQL => {}".format(ans['CWBEventID']))
                            except Exception as e:
                                query_sql = True
                                self.log.logger.error(
                                    "Failed Writting Data to SQL {}".format(e))
                    elif sql_instance:
                        self.log.logger.error("Disconnected SQL")
                        sql_instance = None

                file = FileHandler("./query_new.tmp")
                file_txt = file.read()

                for ans in res["New_EQList"]:
                    insert_query = f"""
                    INSERT INTO {SQL_config['new_table']} (ID, Serial, Lat, Lon, Depth, Mag, Time, Loc, Max) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

                    if sql_instance and sql_instance.is_connected():

                        if (self.config._data['query_mode'] == "sql" or file_txt == "" or query_sql_new):
                            query_sql_new = False
                            sql_instance.cursor.execute(
                                f"SELECT Serial FROM {SQL_config['new_table']}")
                            cwb_event_ids = [row[0]
                                             for row in sql_instance.cursor.fetchall()]
                            cwb_event_id_strings = [
                                rm_tag(item) for item in cwb_event_ids]
                            txt = ','.join(cwb_event_id_strings)
                            file.write(txt)
                            file_txt = txt
                            self.log.logger.debug("[query_mode] => sql")
                        else:
                            self.log.logger.debug("[query_mode] => local")
                            cwb_event_id_strings = file.read().split(',')
                        tag = rm_tag(ans['Serial'])
                        if tag not in cwb_event_id_strings:
                            try:
                                sql_instance.cursor.execute(
                                    insert_query, tuple(ans.values()))
                                sql_instance.conn.commit()
                                txt = ",{}".format(tag)
                                file_txt += txt
                                file.write(txt)
                                self.log.logger.info(
                                    "Success Writting Data to SQL => {}".format(ans['Serial']))

                                send("deEXRdErleZ0ZKCJJo9pojeoOeYVy3k3K9PgR3g9mIf", "\n地震報告\n{}左右，{}發生地震，震源深度{}公里，地震規模M{}，最大震度{}".format(
                                    ans["Time"].replace("-", "/"), ans["Loc"], ans["Depth"], ans["Mag"], level(ans["Max"])), "https://www.cwa.gov.tw/Data/earthquake/img/{}.png".format(ans["Serial"].replace("CWA-", "")))
                            except Exception as e:
                                query_sql_new = True
                                self.log.logger.error(
                                    "Failed Writting Data to SQL {}".format(e))
                    elif sql_instance:
                        self.log.logger.error("Disconnected SQL")
                        sql_instance = None

                if query_sql or query_sql_new:
                    time.sleep(1)
                else:
                    if self.config._data['work_mode'] == 'once':
                        self.log.logger.info("Exit [work_mode] => once")
                        break
                    else:
                        time.sleep(self.config._data['request_delay'])
