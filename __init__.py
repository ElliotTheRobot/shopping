# Copyright 2016 Mycroft AI, Inc.
#
# This file is part of Mycroft Core.
#
# Mycroft Core is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mycroft Core is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.

from os.path import dirname

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

__author__ = 'hschmidt'
LOGGER = getLogger(__name__)


class ShopListSkill(MycroftSkill):

    sId = ""
    sGuid = ""
    sWebService = ""
    sManageItem = ""

    def __init__(self):
        super(ShopListSkill, self).__init__(name="ShopListSkill")

    def initialize(self):
        self.load_data_files(dirname(__file__))
        shopping_list_intent = IntentBuilder("ShopIntent").\
            require("ShopVerb").\
            require("ShopItem").\
            require("ShopLocation").\
            build()
        self.register_intent(shopping_list_intent,
                             self.handle_lets_shop_intent)
        self.loadConf()

    def loadConf(self):
        import shopconf
        self.sId = shopconf.auth['wsid']
        self.sGuid = shopconf.auth['secret']
        self.sWebService = shopconf.auth['webservice']
        self.sManageItem = shopconf.auth['manageitem']
               

    def handle_lets_shop_intent(self, message):
        #self.speak_dialog("item.added", data={"shopitem": message.metadata.get("ShopItem"),\
        #    "shoplocation": message.metadata.get("ShopLocation")})
        qString = self.prepare_querystring(message.metadata.get("ShopVerb"), message.metadata.get("ShopItem"), message.metadata.get("ShopLocation"))
        # send the querystring to the web service
        print(("****QUERYSTRING DEBUG MESSAGE ******\n"))
        print(("Full Querystring: " + str(qString) + "\n"))
        print(("Location variable from metadata: " +  str(message.metadata.get("ShopLocation")).encode("utf-8")))
        print(("**************************************\n"))
        self.speak("See the querystring debug message in the skills terminal")
    

    def prepare_querystring(self, shopVerb, shopItem, shopLocation):
        import base64
        import urllib
        from hashlib import md5
        # prepare the data for the querystring
        sitm = { 'itm' : base64.encodestring(shopItem.encode("utf-8")) }
        sItem = urllib.urlencode(sitm)
        sloc = { 'loc' : shopLocation.encode("utf-8") }
        sLocation = urllib.urlencode(sloc)
        sDate = self.getTodayDate()
        # create the MD5 hash
        stringtoHash = str(self.sGuid) + str(sItem) + str(sLocation) + str(sDate)
        sHash = md5(stringtoHash)
        # Prep the querystring
        # example: ?wsid=1&action=add&itm=b25pb25z%0A&loc=shopping-list&hsh=373e8c57c6da8577f038f194e3d25df3
        sQueryString = "?wsid=" + str(self.sId) + "&action=" + \
            str(shopVerb) + "&" + str(sItem) + "&" + \
            str(sLocation) + "&hsh=" + str(sHash.hexdigest())
        return(sQueryString)

    def getTodayDate(self):
        import os, time
        os.environ['TZ'] = "Europe/London"
        time.tzset()
        localtime = time.localtime()
        timeString = time.strftime('%Y%m%d')
        return(timeString)

    def stop(self):
        pass


def create_skill():
    return ShopListSkill()
