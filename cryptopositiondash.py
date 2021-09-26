'''
Crypto Position Dashboard
Aaron Price
October 2020
Allows the user to record their positon (ie, the average price at which they acquired a currency),
set a target sell price, and view live-updating prices and percent-gains for a list
of tracked currencies.
This allows the user to track many positions at once, in one UI.
The left-hand panel allows the user to select which currencies to track and to enter their positions and targets.
The right-hand panel shows the tracked currencies, the user's positions in those currencies, the current prices,
and the ratio of current price to the user's position.
The user can save their entries by clicking save, and when they open the program in the future, load them without
needing to reenter their positions.
All price data is received from the Coinbase Pro API, which requires API keys:
https://docs.pro.coinbase.com/
You must set the key, b64secret, and passphrase variables to your keys before using.
'''
import time
import threading
from websocket import create_connection
import json
import os

import dotenv
import tkinter as tk
import cbpro
from cbpro.cbpro_auth import get_auth_headers

#update the ith ui entries to reflect a new price
def updateLine(i,price):
    #price comes in as float
    activeprices[i].set(str(price))
    try:
        pos = float(activepositions[i].get())
    except ValueError:
        pos = price
    if pos<0.0000001:
        pos = price
    change = price/pos
    activechanges[i].set('{:.3f}'.format(change))
    if change<=0.96:
        activechangelabels[i].config(font=('Courier',12,'bold'),fg='#AA0000')
    elif change<=0.98:
        activechangelabels[i].config(font=('Courier',12,'normal'),fg='#AA0000')
    elif change<1.02:
        activechangelabels[i].config(font=('Courier',12,'normal'),fg='#000000')
    elif change<1.04:
        activechangelabels[i].config(font=('Courier',12,'normal'),fg='#009900')
    else:
        activechangelabels[i].config(font=('Courier',12,'bold'),fg='#009900')
def updateLineFromPair(pair, price):
    for i in range(len(activepositions)):
        if activepairs[i].get()==pair:
            updateLine(i, price)
            break
#When the user checks or unchecks a box, reset the output widgets and linked variables
def checkToggled():
    for i in range(len(activepairs)):
        activepairs[i].set('')
        activepositions[i].set('')
        activeprices[i].set('')
        activechanges[i].set('')
    j=0
    for i in range(len(pairs)):
        if pairchecks[i].get()==1:
            activepairs[j].set(pairs[i])
            try:
                activepositions[j].set(str(float(positions[i].get())))
            except ValueError:
                activepositions[j].set('')
            j=j+1
def updateTargetChanges():
    for i in range(len(targetchanges)):
        try:
            targetchanges[i].set('{:.3f}'.format(float(targets[i].get())/float(positions[i].get())))
        except ValueError:
            targetchanges[i].set('1.000')
def positionChanged(*args):
    updateTargetChanges()
    checkToggled()
def targetChanged(*args):
    updateTargetChanges()
#Save and load json that stores current;y checked pairs, positions, etc.
def saveConfig():
    conf = {}
    for i in range(len(pairs)):
        conf[pairs[i]] = [pairchecks[i].get(),positions[i].get(),targets[i].get()]
    with open('pos1.json','w') as fp:
        json.dump(conf,fp,indent=4)
def loadConfig():
    try:
        with open('pos1.json','r') as fp:
            conf = json.load(fp)
        for pair, settings in conf.items():
            for i in range(len(pairs)):
                if pair==pairs[i]:
                    pairchecks[i].set(settings[0])
                    positions[i].set(settings[1])
                    targets[i].set(settings[2])
    except FileNotFoundError:
        print("No save file found, click 'save' first.")

#Extend the WebsocketClient class of package cbpro. This connects to the Coinbase Pro websocker using API credentials, then triggers events based on what it receives.
class myWebsocketClient(cbpro.WebsocketClient):
    def setup(self, _api_key, _api_secret, _api_passphrase,  _trader):
        self.url = "wss://ws-feed.pro.coinbase.com/"
        self.auth = True
        self.api_key = _api_key
        self.api_secret = _api_secret
        self.api_passphrase = _api_passphrase
        self.pm = _trader
    def on_open(self):
        self.products = pairs
        self.channels = ['user','heartbeat','ticker','status']
    def on_message(self, msg):
        #whenever a ticker message is received (ie, the price for one of our pairs has changed), update prices, ui etc
        if msg['type']=='ticker':
            self.pm.tickerUpdate(msg)
    def _connect(self):
        if self.products is None:
            self.products = ["BTC-USD"]
        elif not isinstance(self.products, list):
            self.products = [self.products]
        if self.url[-1] == "/":
            self.url = self.url[:-1]
        if self.channels is None:
            sub_params = {'type': 'subscribe', 'product_ids': self.products}
        else:
            sub_params = {'type': 'subscribe', 'product_ids': self.products, 'channels': self.channels}
        if self.auth:
            timestamp = str(time.time())
            message = timestamp + 'GET' + '/users/self/verify'
            auth_headers = get_auth_headers(timestamp, message, self.api_key, self.api_secret, self.api_passphrase)
            sub_params['signature'] = auth_headers['CB-ACCESS-SIGN']
            sub_params['key'] = auth_headers['CB-ACCESS-KEY']
            sub_params['passphrase'] = auth_headers['CB-ACCESS-PASSPHRASE']
            sub_params['timestamp'] = auth_headers['CB-ACCESS-TIMESTAMP']
        try:
            self.ws = create_connection(self.url)
            self.ws.send(json.dumps(sub_params))
        except:
            self.ws = None
            
#A class that contains the websocket, the API credentials.
class PositionMonitor:
    def __init__(self, _key, _b64secret, _passphrase):
        self.key = _key
        self.b64secret = _b64secret
        self.passphrase = _passphrase
        self.public_client = cbpro.PublicClient()
        self.auth_client = cbpro.AuthenticatedClient(self.key, self.b64secret, self.passphrase)

        self.ws = myWebsocketClient()
        self.ws.setup(self.key, self.b64secret, self.passphrase, self)
        self.updateui = True

    def tickerUpdate(self, msg):
        pid = msg['product_id']
        if self.updateui:
            updateLineFromPair(pid,float(msg['best_bid']))
    def go(self):
        self.ws.start()
    def softStop(self):
        #sets a flag to false so that we can stop trying to update the UI vars ahead of quitting the program
        self.updateui = False

#Create Tk    
root = tk.Tk()
root.title("Crypto Position Dashboard")

#Define crypto pair strings used in labels and requests
fp = open('pairs.json','r')
pairconf = json.load(fp)
pairs=pairconf["pairs"]
cap = pairconf["cap"]
pairs = pairs[:cap]

#tk vars
pairchecks = []
positions = []
targets = []
targetchanges = []
activepairs = []
activepositions = []
activeprices = []
activechanges = []
#tk widgets
paircheckboxes = []
positionentries = []
targetentries = []
targetchangelabels = []
activepairlabels = []
activepositionlabels = []
activepricelabels =[]
activechangelabels = []
#tk frames
topframe = tk.Frame(root)
inputframe = tk.Frame(topframe)
outputframe = tk.Frame(topframe)

#Set up ui widgets and linked variables
for i in range(len(pairs)):
    #set up variable lists
    pairchecks.append(tk.IntVar())
    positions.append(tk.StringVar())
    targets.append(tk.StringVar())
    targetchanges.append(tk.StringVar())
    activepairs.append(tk.StringVar())
    activepositions.append(tk.StringVar())
    activeprices.append(tk.StringVar())
    activechanges.append(tk.StringVar())
    #entry traces
    positions[i].trace_add("write", positionChanged)
    targets[i].trace_add("write", targetChanged)
    #initialize widgets
    legendpair = tk.Label(inputframe,text="Pair")
    legendposition = tk.Label(inputframe,text="Position")
    legendtarget = tk.Label(inputframe,text="Target")
    legendtargetchange = tk.Label(inputframe,text="target%")
    legendactivepair = tk.Label(outputframe,text="Pair",font=('Courier',12),width=8)
    legendactiveposition = tk.Label(outputframe,text="Position",font=('Courier',12),width=8)
    legendactiveprice = tk.Label(outputframe,text="Price",font=('Courier',12),width=8)
    legendactivechange = tk.Label(outputframe,text="%",font=('Courier',12),width=6)
    paircheckboxes.append(tk.Checkbutton(inputframe,text=pairs[i],variable=pairchecks[i],command=checkToggled))
    positionentries.append(tk.Entry(inputframe,textvariable=positions[i],width=7))
    targetentries.append(tk.Entry(inputframe,textvariable=targets[i],width=7))
    targetchangelabels.append(tk.Label(inputframe,textvariable=targetchanges[i]))
    activepairlabels.append(tk.Label(outputframe,textvariable=activepairs[i],font=('Courier',12),width=8))
    activepositionlabels.append(tk.Label(outputframe,textvariable=activepositions[i],font=('Courier',12),width=8))
    activepricelabels.append(tk.Label(outputframe,textvariable=activeprices[i],font=('Courier',12),width=8))
    activechangelabels.append(tk.Label(outputframe,textvariable=activechanges[i],font=('Courier',12),width=6))
    #put widgets into frames
    legendpair.grid(column=0,row=0,sticky='w')
    legendposition.grid(column=1,row=0)
    legendtarget.grid(column=2,row=0)
    legendtargetchange.grid(column=3,row=0)
    legendactivepair.grid(column=0,row=0)
    legendactiveposition.grid(column=1,row=0)
    legendactiveprice.grid(column=2,row=0)
    legendactivechange.grid(column=3,row=0)
    paircheckboxes[i].grid(column=0,row=i+1,sticky='w')
    positionentries[i].grid(column=1,row=i+1)
    targetentries[i].grid(column=2,row=i+1)
    targetchangelabels[i].grid(column=3,row=i+1)
    activepairlabels[i].grid(column=0,row=i+1,padx=10)
    activepositionlabels[i].grid(column=1,row=i+1,padx=10)
    activepricelabels[i].grid(column=2,row=i+1,padx=10)
    activechangelabels[i].grid(column=3,row=i+1,padx=10)
    
#Configure packing of ui widgets
inputframe.pack(side='left')
outputframe.pack(side='left')
topframe.pack(side='top')

def quitDashboard():
    pm.softStop() #stops updating the UI when socket receives messages, so it won't get upset when the UI is destroyed and it's still trying to update it.
    time.sleep(0.5)
    pm.ws.close()
    root.quit()
    root.update()
def threadedQuit():
    #This is called when the window manager tries to quit (ie, the "x" button)
    quitthread = threading.Thread(target=quitDashboard)
    quitthread.start()

#configure and add save and load widgets
configframe = tk.Frame(root)
saveconfigbutton = tk.Button(configframe,text="Save",command=saveConfig)
loadconfigbutton = tk.Button(configframe,text="Load",command=loadConfig)
quitButton = tk.Button(configframe,text="Quit",command=quitDashboard)
#Believe it or not, below is the best way to do an expanding spacer in tk... a long string of spaces.
dummy = tk.Label(configframe,text='                                                                                                                                                                                  ')
saveconfigbutton.pack(side='left')
loadconfigbutton.pack(side='left')
quitButton.pack(side='left')
dummy.pack(side='left')
configframe.pack(side='top')

#load environment variables containing my Coinbase API keys
dotenv.load_dotenv()

#Set Coinbase API keys from environment
key = os.getenv("coinbase_key")
b64secret = os.getenv("coinbase_b64secret")
passphrase = os.getenv("coinbase_passphrase")

#Create and  PositionMonitor which listens to the Coinbase websocket, and starts after the tk window has been created.
pm = PositionMonitor(key, b64secret, passphrase)
def startSocket():
    pm.go()
root.protocol("WM_DELETE_WINDOW", threadedQuit)
root.after(1000,startSocket)
root.mainloop()