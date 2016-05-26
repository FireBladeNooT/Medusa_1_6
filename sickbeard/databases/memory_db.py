# coding=utf-8

# Author: p0psicles
# URL: http://github.com/pymedusa/SickRage
#
# This file is part of SickRage.
#
# SickRage is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SickRage is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SickRage. If not, see <http://www.gnu.org/licenses/>.

from sickbeard import db


# Add new migrations at the bottom of the list; subclass the previous migration.
class InitialSchema(db.SchemaUpgrade):
    def test(self):
        return self.hasTable("rss_cache")

    def execute(self):
        queries = [
            ('CREATE TABLE rss_cache (rss_cache_id INTEGER PRIMARY KEY, name TEXT, url TEXT, '
             'time NUMERIC DEFAULT 0, provider_id TEXT NOT NULL);',),
        ]
        for query in queries:
            if len(query) == 1:
                self.connection.action(query[0])
            else:
                self.connection.action(query[0], query[1:])
