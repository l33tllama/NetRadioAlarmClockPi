import sqlite3


# SQLite 3 Class for managing net radio settings
class RadioDB:
    def __init__(self, db_filename):
        self.db_filename = db_filename
        self.conn = sqlite3.connect(self.db_filename)

    def _connect(self):
        self.conn = sqlite3.connect(self.db_filename)

    def add_station(self, station_url):
        self._connect()
        c = self.conn.cursor()

        query_text = '''INSERT OR REPLACE INTO saved_stations (url)
                                    VALUES ('{url}')'''.format(
            url=station_url)

        c.execute(query_text)

        self.conn.commit()
        self.conn.close()

    def get_stations(self):
        stations = []
        self._connect()
        c = self.conn.cursor()

        query_text = "SELECT * FROM saved_stations"

        c.execute(query_text)

        for row in c.fetchall():
            stations.append(row[0])

        self.conn.close()

        return stations