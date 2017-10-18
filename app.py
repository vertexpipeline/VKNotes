key = open("access-key").readline()

import VKClient as vk
from datetime import datetime,timedelta, time, date
from time import mktime
from time import strptime
import re as r
import threading
import json

bot = vk.VkClient(key)

bodyr = r.compile(r"(?P<target>[^\s]+)(\s*(?P<condition>.*)\s*-\s*(?P<action>.*)|(?P<service>.*))")
datetimer = r.compile(r"((?P<date>.*)\s+)?(?P<type>(в|через)){1}(?P<time>.*)")
indentr = r.compile("(?P<time>[0-9]{1,2})\s*((?P<min>мину)(т|ты|)|(?P<hour>час(|а|ов)))")
dater = r.compile("[0-9]{1,2}\.[0-9]{2}")

notes = []

class Note:
    def __init__(self, when, owner, action):
        self.when = when
        self.owner = owner
        self.action = action

def parsedate(string):
    if string == "завтра":
        return date.today() + timedelta(days=1)
    elif string == "сегодня":
        return date.today()
    elif string == "через неделю":
       return date.today() + timedelta(days=7)
    elif string =="":
        return date.today()
    elif dater.match(string):
        splitted = string.split(".")
        day = int(splitted[0])
        month = int(splitted[1])
        return date(date.today().year, day= day, month=month)
    else:
        return None

def parsetime(t):
    timer = r.compile("([0-9]{1,2}:[0-9]{2})")
    match = timer.match(t.strip())
    if(match != None):
        timestring = str(t.strip())
        try:
            tm = strptime(timestring, "%H:%M")
        except Exception as ex:
            print(ex)
        return time(tm.tm_hour, tm.tm_min)
    else:
        return None

def parseindent(t):
    mt = indentr.match(t.strip())
    curtime = datetime.now().time()

    try:
        value = int(mt.group("time"))
    except Exception:
        return None

    hr = mt.group("hour")

    if(mt.group("hour") != None):
        return time(hour = value + curtime.hour, minute = curtime.minute)
    elif mt.group("min") != None:
        return time(minute = value + curtime.minute, hour = curtime.hour)
    else:
        return None


def parsedatetime(dt):
    mt = datetimer.match(dt)

    hasdate = False
    curtime = None
    curdate = None

    if mt.group("date")==None:
        curdate = date.today()
    else:
        curdate = parsedate(mt.group("date"))
        hasdate = True

    if mt.group("time").strip() == "":
        curtime = time(hour=12)
    else:
        if mt.group("type") == "в":
            curtime = parsetime(mt.group("time"))
        elif not hasdate:
            curtime = parseindent(mt.group('time'))
        else:
            return None

    if (curtime == None) or (curdate == None):
        return None

    return datetime.combine(curdate, curtime)

def notejsonconverter(o):
    if isinstance(o, datetime):
        return o.__str__()
    elif isinstance(o, Note):
        return o.__dict__

def backupNotes():
    open("notes.json", "w").write(json.dumps(notes, default=notejsonconverter))
    pass

def init():
    for note in json.loads(open("notes.json", "r").read()):
        #2017-10-15 22:38:00
        notes.append(Note(datetime.strptime(note["when"], "%Y-%m-%d %H:%M:%S"), note["owner"], note["action"]))

def getusernodes(user):
    filtered = []
    for note in notes:
        if user == note.owner:
            filtered.append(note)
    return filtered

def listNotes(sendF, sender):
    filtered = getusernodes(sender)
    result = ""
    result += "Найдено {} напоминаний🙄\n".format(filtered.__len__())
    for note in filtered:
        result += "📅{} - {}\n".format(str(note.when), str(note.action))
    sendF(result)

def remember(sendF, datetime, sender, action):
    if datetime == None:
        sendF("Не могу понять дату и время...")
        return
    elif datetime< datetime.today():
        sendF("Увы, но это время уже не вернуть...")
        return
    else:
        notes.append(Note(datetime, sender, action))
        sendF("Хорошо, я запомнил😇")
        return
    sendF("Я тебя не понимаю, как со мной общаться можно узнать у меня на странице.")


def messageGot(sender, message):
    print("Got message: {}".format(message))
    def send(msg):
        print("Sending "+msg)
        bot.send(sender, msg)

    message = message.lower()

    body = bodyr.match(message)
    if(body != None):
        target = body.group("target")
        if (target == "напомни") and (body.group("action") != None):
            remember(send, parsedatetime(body.group("condition")), sender,  body.group("action"))

        elif target == "покажи":
            action = body.group("service")
            if action != None:
                if action.strip() == "напоминания":
                    listNotes(send, sender)
                else:
                    send("Я не могу такое показать(")

        elif target == "удали":
            action = body.group("service")
            if (action != None) and (action == "напоминания"):
                filtered = getusernodes(sender)
                send("Окей, я удалил {} записей😉".format(filtered.__len__()))
                for note in filtered:
                    notes.remove(note)
                backupNotes()
            else:
                send("Нет у меня такого🙃")



    backupNotes()

def checkActions():
    global timer
    for note in notes:
        if datetime.today() > note.when:
            notes.remove(note)
            bot.send(note.owner,str(note.when.__format__("%X")[:-2]) + " 📅: "+note.action)
            backupNotes()

    threading.Timer(60, checkActions).start()

init()
checkActions()

threading.Thread(target=bot.listen, args=(messageGot, False)).start()