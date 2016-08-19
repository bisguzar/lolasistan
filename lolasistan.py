#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')


import xmpp, sqlite3
from config import *
from lang import *

conn = xmpp.Client("pvp.net", debug=[])
if not conn.connect(server=("chat.tr.lol.riotgames.com", 5223)):
    print (connectFailed[language])
    exit()
else:
    print (connected[language])

if not conn.auth(userID, "AIR_" + passw, "xiff"):
    print (authFailed[language])
    exit()
else:
    print (authSucces[language])

roster = None

def message_handler(conn, msg):

    db = sqlite3.connect("database.sql")
    im = db.cursor()
    im.execute("SELECT * FROM commands")
    commandsGet = im.fetchall()
    commands = []
    for i in commandsGet:
        commands.append(i[0])
    user = roster.getName(str(msg.getFrom()))
    text = msg.getBody().encode('utf-8').lower()

    print ("[{}] {}".format(user, text))

    if text[0] == addCommPrefix:
        if not user in masterAccounts:
            reply = msg.buildReply(master[language])

        elif text == '!':
            reply = msg.buildReply(newCommand[language])
        
        else:
            executed = text.split()
            command  = executed[0][1:len(executed[0])]
            index = text[len(executed[0])+1:]

            if command in commands:
                reply = msg.buildReply(alreadyAdded[language])

            elif command == delCommand:
                if len(index.split(" ")) > 1:
                    reply = msg.buildReply(deleteCom[language].format(addComPrefix, delCommand))
                else:
                    if index not in commands:
                        reply = msg.buildReply(commandNotFound[language].format(index))
                    else:
                        im.execute("DELETE FROM commands WHERE command='{}'".format(index))
                        db.commit()
                        reply = msg.buildReply(commandDeleted[language].format(index))

            # TODO
            #elif command == msgCommand:
            #    split = text.split()
            #    to    = split[1]
            #    msg   = text[6+len(to)]


            else:
                im.execute("INSERT INTO commands VALUES ('{0}', '{1}')".format(command, index))
                db.commit()
                reply = msg.buildReply(commandAdded[language].format(command))
                print (commandCreator[language].format(command)+ user)
    
    elif text in commands:
        im.execute("SELECT * FROM commands WHERE command='{}'".format(text))
        gelen = im.fetchall()[0][1]
        reply = msg.buildReply(gelen)

    elif text == helpCommand[language].decode('utf-8'):
        printComms = usableComms[language]
        for i in commands:
            printComms += i + "\n"
        reply = msg.buildReply(printComms)
    else:
        reply = msg.buildReply(noIdea[language].format(text))

    reply.setType("chat")
    conn.send(reply)

def presence(conn, event):
    if event.getType() == 'subscribe':
        conn.send(xmpp.Presence(to=event.getFrom(), typ='subscribed'))

conn.RegisterHandler('presence', presence)
conn.RegisterHandler("message", message_handler)
conn.sendInitPresence(requestRoster=1)
roster = conn.getRoster()

while conn.isConnected():
    try:
        conn.Process(10)
    except KeyboardInterrupt:
        break