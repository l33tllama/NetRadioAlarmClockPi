import sqlite3

# SQLite 3 Class for managing net radio settings
class RadioDB:
    def __init__(self, db_filename):
        self.db_filename = db_filename
        self.conn = sqlite3.connect(self.db_filename)

    def _connect(self):
        self.conn = sqlite3.connect(self.db_filename)

    def add_station(self, station_url, stream_title):
        self._connect()
        c = self.conn.cursor()

        query_text = '''INSERT OR REPLACE INTO saved_stations (url, title)
                                    VALUES ('{url}', '{title}')'''.format(
            url=station_url, title=stream_title)

        c.execute(query_text)

        self.conn.commit()
        self.conn.close()

    def get_stations(self):
        stations = []
        self._connect()
        c = self.conn.cursor()

        print(c)

        query_text = "SELECT * FROM saved_stations"

        c.execute(query_text)

        for row in c.fetchall():
            stations.append([row[0], row[1]])

        self.conn.close()

        return stations

    def set_current_station(self, station_url):
        self._connect()
        c = self.conn.cursor()

        print("Setting current station: " + station_url)

        query_text_1 = "DELETE FROM current_station"
        query_text_2 = " INSERT INTO current_station (url) VALUES ('{url}')".format(url=station_url)

        c.execute(query_text_1)
        c.execute(query_text_2)
        self.conn.commit()
        self.conn.close()

    def get_current_station(self):
        self._connect()
        c = self.conn.cursor()

        query_text = "SELECT * from current_station"

        c.execute(query_text)
        station_url = c.fetchone()

        if len(station_url) == 1:
            station_url = station_url[0]

        if station_url is None:
            station_url = ""

        self.conn.close()

        return station_url

    def get_title_for_station_url(self, station_url):
        self._connect()
        c = self.conn.cursor()

        print("Station url: " + str(station_url))

        query_text = "SELECT * from saved_stations WHERE url = '{url}'".format(url=station_url)
        print(query_text)

        c.execute(query_text)
        title = c.fetchone()

        if title is None:
            title = ""
        else:
            title = title[1]

        self.conn.close()

        return title

    def update_station_title(self, station_url, title):
        self._connect()

        c = self.conn.cursor()

        query_text = "UPDATE saved_stations SET title = '{title}' WHERE url = '{url}'".format(title=title, url=station_url)

        c.execute(query_text)

        self.conn.commit()
        self.conn.close()
