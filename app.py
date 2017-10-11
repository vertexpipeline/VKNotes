key = open("access-key").readline()

import VKClient as vk
from datetime import datetime,timedelta, time, date
from time import mktime
from time import strptime
import re as r
import threading
import json

bot = vk.VkClient(key)

notes = []

def parsedate(string):
    if string == "завтра":
        return date.today() + timedelta(days=1)
    elif string == "сегодня":
        return date.today()
    elif string == "через неделю":
       return date.today() + timedelta(days=7)
    elif string =="":
        return date.today()
    else:
        return None

def parsetime(t):
    timer = r.compile("([0-9]{1,2}:[0-9]{2})")
    match = timer.match(t)
    if(match != None):
        tm = strptime(str(match.group(0)), "%H:%M")
        return time(tm.tm_hour, tm.tm_min)
    else:
        return None

def backup():
    pass
    #open("notes.json").write(json.dumps(notes))


def messageGot(sender, message):
    def send(msg):
        bot.send(sender, msg)

    body = r.compile("напомни\s*(.*)\s+в\s+(.*)\s+что\s+(.+)")
    list = r.compile("покажи\s*список\s*напоминаний")
    #
    mt = body.match(message.lower())
    if mt != None:
        date = mt.group(1)
        time =  mt.group(2)
        action = mt.group(3)

        date = parsedate(date)
        time = parsetime(time)

        if(time == None):
            send("Не понимаю время😬")
        elif date == None:
            send("Не понимаю дату😬")
        else:
            when = datetime.combine(date, time)

            if(datetime.today() > when):
                send("Упс, но это время ушло...🙌")
                return

            notes.append((when, action, sender))
            send("Хорошо, записал.📎")
    elif list.match(message.strip()):
        filtered = []
        for note in notes:
            (when, action, owner) = note
            if sender == owner:
                filtered.append(note)
        result = ""
        result += "Найдено {} оповещений.\n".format(filtered.__len__())
        for (w,a,o) in filtered:
            result += "📅{} - {}\n".format(str(w), str(a))
        send(result)
    else:
        send("Я тебя не понимаю, вот схема https://vk.com/public154877060?z=photo-154877060_456239019%2Falbum-154877060_00%2Frev ☝")

    backup()

def checkActions():
    global timer
    for note in notes:
        (when, action, sender) = note
        if datetime.today() > when:
            notes.remove(note)
            bot.send(sender,str(when.__format__("%X")[:-2]) + " 📅: "+action)

    threading.Timer(60, checkActions).start()

checkActions()

bot.listen(messageGot)