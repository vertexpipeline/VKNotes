key = open("access-key").readline()

import VKClient as vk
from datetime import datetime,timedelta, time, date
from time import mktime
from time import strptime
import re as r
import threading

bot = vk.VkClient(key)

notes = []

def messageGot(sender, message):
    def send(msg):
        bot.send(sender, msg)

    request = r.compile("напомни\s(.*)\sв\s([0-9]{1,2}:[0-9]{2}),\s(.*)")
    mt = request.match(message)
    if mt != None:
        sdate = mt.group(1)
        stime =  mt.group(2)
        action = mt.group(3)
        tm = strptime(stime, "%H:%M")
        t = time(tm.tm_hour, tm.tm_min)

        if sdate == "завтра":
            when = datetime.combine(date.today() + timedelta(days=1), t)
        elif sdate == "сегодня":
            when = datetime.combine(date.today(), t)
        elif sdate == "через неделю":
            when = datetime.combine(date.today()+ timedelta(days=7), t)
        else:
            send("Не могу понять дату")
            return

        if(datetime.today() > when):
            send("Упс, но это время ушло...")
            return

        notes.append((when, action, sender))
        send("Хорошо, записал.")
    else:
        send("Не могу понять")

def checkActions():
    global timer
    for note in notes:
        (when, action, sender) = note
        if datetime.today() > when:
            notes.remove(note)
            bot.send(sender, "📅"+action)

    threading.Timer(10, checkActions).start()

checkActions()

bot.listen(messageGot)