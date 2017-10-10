import requests as req
import json

class VkClient:
    def __init__(self, key):
        print("Starting bot")
        self.access_token = key
        self.user = json.loads(req.get("https://api.vk.com/method/users.get?v=5.38&access_token="+self.access_token).content)
        self.id = self.user["response"][0]["id"]
        print("User checked")


    def getmethod(self, method, params):
        req_params = ""
        for (key, value) in params.items():
            req_params += "&{}={}".format(key, value)

        return json.loads(req.get(
            "https://api.vk.com/method/"+method+"?v=5.38&access_token=" + self.access_token + req_params).content)


    def send(self, peer_id, text):
        req.get(
            "https://api.vk.com/method/messages.send?v=5.38&access_token=" + self.access_token + "&message=" + text + "&peer_id=" + str(
                peer_id))


    def listen(self, method, listenSelf = False):
        print("Getting server")
        server = json.loads(
            req.get(
                "https://api.vk.com/method/messages.getLongPollServer?access_token="+self.access_token).content)
        print("Starting pool")
        lastTs = server["response"]["ts"]

        while True:
            longpool = "https://" + str(server["response"]["server"]) + "?act=a_check&key=" + str(
                server["response"]["key"]) + "&ts=" + str(lastTs) + "}&wait=25&mode=2&version=1"

            response = json.loads(req.get(longpool).content)

            for event in response["updates"]:
                if (event[0] == 4) and not (int(event[2]) & 2 == 2):
                        print("Got a message")
                        method(int(event[3]), str(event[6]))

            lastTs = response["ts"]


    def getgroup(self, ids):
        group = self.getmethod("groups.getById",{"group_ids":ids})
        return group["response"][0]


    def getwall(self, id, count, offset):
        return self.getmethod("wall.get", {"owner_id":-int(id), "count":count, "offset":offset})["response"]

