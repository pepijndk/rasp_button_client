#!/usr/bin/env python3     

import socket
import json
import threading
from subprocess import call, Popen
from datetime import datetime
import tkinter as tk
from tkinter import font
from tkinter.constants import S, YES
HOST = ""  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)


# message format

# msg:
## type: command / log / ping
## message
## settings
# 

settings = {
    'activated_smoke': False,
    'activated_lights_g': True,
    'activated_lights_party':  False,
    'music': 'techno',
    'smoke_interval': 120 # steps: 60, 120, 180, 240, off
}

s = socket.socket(socket.AF_INET,
                      socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen() # backlog is the amount of connections that can be made

# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
# 	s.bind((HOST, PORT))
# 	s.listen() # backlog is the amount of connections that can be made




class GUI:
    def __init__(self):
        window = tk.Tk()
        window.title("Escalatieknop")

        self.frame1 = tk.Frame(master=window, width=600, height=120, bg="red")
        self.frame1.pack(fill=tk.X, padx=50, pady=(20, 0))

        self.frame2 = tk.Frame(master=window, width=600, height=350, bg="yellow")
        self.frame2.pack(fill=tk.X, padx=50, pady=0)

        self.frame3 = tk.Frame(master=window, width=60, height=200, bg="blue")
        self.frame3.pack(fill=tk.X, padx=50, pady=(0, 20))


        # header
        label_escalatieknop = tk.Label(self.frame1, text='Escalatieknop', bg="green", font=("Ariel", 30))
        label_status = tk.Label(self.frame1, text='status: ', bg="purple", font=("Ariel", 10))
        label_datum_contact = tk.Label(self.frame1, text='laatst contact:', bg="orange", font=("Ariel", 10))
        status = tk.Label(self.frame1, text='Niet verbonden', bg="pink", font=("Ariel", 10))
        datum_contact = tk.Label(self.frame1, text='5s geleden', bg="yellow", font=("Ariel", 10))
        info = tk.Label(self.frame1, text='test info', bg="white", font=("Ariel", 10))
        btn_reset = tk.Button(master=self.frame1, text="Reset", width=10)
        btn_restart = tk.Button(master=self.frame1, text="Restart", width=10)

        # header place
        label_escalatieknop.place(x=0, y=0)
        label_status.place(x=0, y=50)
        label_datum_contact.place(x=0, y=70)
        info.place(x=0, y=90)
        status.place(x=50, y=50)
        datum_contact.place(x=100, y=70)
        btn_reset.place(x=500, y=20)
        btn_restart.place(x=500, y=60)


        # body

        #barlampen
        controls_barlampen = tk.Frame(master=self.frame2, width=300, height=70, bg="blue")
        controls_barlampen.place(x=0, y=0)

        label_barlampen = tk.Label(controls_barlampen, text='barlampen ', bg="purple", font=("Ariel", 18))
        btn_barlampen_aan = tk.Button(controls_barlampen, text ="AAN", bg="green", width=5, height=2, font=("Ariel", 10))
        btn_barlampen_uit = tk.Button(controls_barlampen, text ="UIT", bg="red", width=5, height=2, font=("Ariel", 10))
        label_status_barlampen = tk.Label(controls_barlampen, text='status: ', bg="purple", font=("Ariel", 10))

        label_barlampen.place(x=0, y=0)
        label_status_barlampen.place(x=0, y=30)
        btn_barlampen_aan.place(x=180, y=20)
        btn_barlampen_uit.place(x=240, y=20)


        #partylampen
        controls_partylampen = tk.Frame(master=self.frame2, width=300, height=70, bg="blue")
        controls_partylampen.place(x=0, y=90)

        label_partylampen = tk.Label(controls_partylampen, text='partylampen ', bg="purple", font=("Ariel", 18))
        btn_partylampen_aan = tk.Button(controls_partylampen, text ="AAN", bg="green", width=5, height=2, font=("Ariel", 10))
        btn_partylampen_uit = tk.Button(controls_partylampen, text ="UIT", bg="red", width=5, height=2, font=("Ariel", 10))
        label_status_partylampen = tk.Label(controls_partylampen, text='status: ', bg="purple", font=("Ariel", 10))

        label_partylampen.place(x=0, y=0)
        label_status_partylampen.place(x=0, y=30)
        btn_partylampen_aan.place(x=180, y=20)
        btn_partylampen_uit.place(x=240, y=20)

        #rookmachine
        controls_rookmachine = tk.Frame(master=self.frame2, width=300, height=140, bg="blue")
        controls_rookmachine.place(x=0, y=180)

        label_rookmachine = tk.Label(controls_rookmachine, text='rookmachine ', bg="purple", font=("Ariel", 18))
        btn_rookmachine_aan = tk.Button(controls_rookmachine, text ="AAN", bg="green", width=5, height=2, font=("Ariel", 10))
        btn_rookmachine_uit = tk.Button(controls_rookmachine, text ="UIT", bg="red", width=5, height=2, font=("Ariel", 10))
        label_status_rookmachine = tk.Label(controls_rookmachine, text='status: ', bg="purple", font=("Ariel", 10))

        scale_smoke = tk.Scale(controls_rookmachine, from_=60, to=300, length=300,tickinterval=60, orient=tk.HORIZONTAL)
        scale_smoke.set(23)

        label_rookmachine.place(x=0, y=0)
        label_status_rookmachine.place(x=0, y=30)
        btn_rookmachine_aan.place(x=180, y=20)
        btn_rookmachine_uit.place(x=240, y=20)
        scale_smoke.place(x=0, y=70)

        #ledstrip
        controls_ledstrip = tk.Frame(master=self.frame2, width=200, height=300, bg="orange")
        controls_ledstrip.place(x=400, y=0)

        label_ledstrip = tk.Label(controls_ledstrip, text='ledstrip ', bg="purple", font=("Ariel", 18))

        label_scale1 = tk.Label(controls_ledstrip, text='vaak', bg="red", font=("Ariel", 10))
        label_scale2 = tk.Label(controls_ledstrip, text='niet vaak', bg="red", font=("Ariel", 10))

        scale_ledstip = tk.Scale(controls_ledstrip, from_=10, to=0, length=200,tickinterval=60, orient=tk.VERTICAL)
        scale_ledstip.set(23)

        label_ledstrip.place(x=0, y=0)
        scale_ledstip.place(x=10, y=60)
        label_scale1.place(x=80, y=70)
        label_scale2.place(x=80, y=330)

        ### chatbox 

        self.labelHead = tk.Label(self.frame3,
                                bg = "#17202A",
                                fg = "#EAECEE",
                                text = "console" ,
                                font = "Helvetica 13 bold",
                                height = 0,
                                pady = 10)
            
        self.labelHead.place(relwidth = 1)
        self.line = tk.Label(self.frame3,
                            width = 450,
                            bg = "#ABB2B9")
            
        self.line.place(relwidth = 1,
                        rely = 0.17,
                        relheight = 0.012)
            
        self.textCons = tk.Text(self.frame3,
                                width = 20,
                                height = 2,
                                bg = "#17202A",
                                fg = "#EAECEE",
                                font = "Helvetica 14",
                                padx = 5,
                                pady = 5)
            
        self.textCons.place(relheight = 00.82,
                            relwidth = 1,
                            rely = 0.18)
            
            
        # create a scroll bar
        scrollbar = tk.Scrollbar(self.textCons)
            
        # place the scroll bar
        # into the gui window
        scrollbar.place(relheight = 1,
                        relx = 0.974)
            
        scrollbar.config(command = self.textCons.yview)
            
        self.textCons.config(state = tk.DISABLED)

        self.startThread()
        window.mainloop()

    def startThread(self):
        rcv = threading.Thread(target=self.receive)
        rcv.start()

    def log(self, message):
        now = datetime.now()

        current_time = now.strftime("%H:%M:%S")

        self.textCons.config(state = tk.NORMAL)
        self.textCons.insert(tk.END, current_time + ": " + 
                                message+"\n\n")
            
        self.textCons.config(state = tk.DISABLED)
        self.textCons.see(tk.END)


    def receive(self):
        while True:
            self.conn, self.addr = s.accept()
            with self.conn:
                print("Connected by", self.addr)
                while True:
                    print("waiting")
                    data = self.conn.recv(1024)
                    message = data.decode()

                    if not data:
                        break

                    print("incoming: " + str(message))

                    if message == None or len(message) == 0:
                        continue

                    # check format
                    try:
                        json_message = json.loads(message)
                    except ValueError as e:
                        print("not a json")
                        self.log("received message in incorrect format. Message: " +  message)
                        continue

                    # if its a log
                    if json_message['type'] == 'log':
                        self.log(str(json_message['message']))


                    
                    # if command == "quit":
                    #     exit()
                    # elif command == "start":
                    #     #Popen("C:/Users/JVB61/Documents/escalatieknop/start.bat")
                    #     Popen(r'start.bat', shell=True, cwd=r'C:\Users\JVB61\Documents\escalatieknop')
                    #     Popen(r'mute.bat', shell=True, cwd=r'C:\Users\JVB61\Documents\escalatieknop')
                    # elif command == "start tulips":
                    #     print("starting tulips")
                    #     #Popen("C:/Users/JVB61/Documents/escalatieknop/start.bat")
                    #     Popen(r'start_tulips.bat', shell=True, cwd=r'C:\Users\JVB61\Documents\escalatieknop')
                    #     # Popen("mute.bat", cwd=r"C:\Users\JVB61\Documents\escalatieknop")
                    # elif command == "reset":
                    #     print("resetting")
                    #     # Popen("reset.bat", cwd=r"C:\Users\JVB61\Documents\escalatieknop")
                    # elif command == "next":
                    #     print("next song")
                    #     # Popen("next.bat", cwd=r"C:\Users\JVB61\Documents\escalatieknop")
                    # elif command == "stop":
                    #     print("stopping")
                    #     Popen("stop.bat", shell=True, cwd=r"C:\Users\JVB61\Documents\escalatieknop")
                    # elif command == "ping":
                    #     now = datetime.now()
                    #     current_time = now.strftime("%H:%M:%S")
                    #     print("pinged by", addr, "at", current_time)
                    #     print("DIT SCHERM NIET WEGKLIKKEN")
                    # else:
                    #     print("invalid command")

        

    

print("test")
GUI()






# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

	
# 	s.bind((HOST, PORT))
# 	s.listen() # backlog is the amount of connections that can be made
	
# 	while True:
# 		conn, addr = s.accept()
# 		with conn:
# 			print("Connected by", addr)
# 			while True:
# 				data = conn.recv(1024)
# 				command = data.decode()
				
# 				print("command: " + command)
# 				if not data:
# 					break
				
# 				if command == "quit":
# 					exit()
# 				elif command == "start":
# 					#Popen("C:/Users/JVB61/Documents/escalatieknop/start.bat")
# 					Popen(r'start.bat', shell=True, cwd=r'C:\Users\JVB61\Documents\escalatieknop')
# 					Popen(r'mute.bat', shell=True, cwd=r'C:\Users\JVB61\Documents\escalatieknop')
# 				elif command == "start tulips":
# 					print("starting tulips")
# 					#Popen("C:/Users/JVB61/Documents/escalatieknop/start.bat")
# 					Popen(r'start_tulips.bat', shell=True, cwd=r'C:\Users\JVB61\Documents\escalatieknop')
# 					# Popen("mute.bat", cwd=r"C:\Users\JVB61\Documents\escalatieknop")
# 				elif command == "reset":
# 					print("resetting")
# 					# Popen("reset.bat", cwd=r"C:\Users\JVB61\Documents\escalatieknop")
# 				elif command == "next":
# 					print("next song")
# 					# Popen("next.bat", cwd=r"C:\Users\JVB61\Documents\escalatieknop")
# 				elif command == "stop":
# 					print("stopping")
# 					Popen("stop.bat", shell=True, cwd=r"C:\Users\JVB61\Documents\escalatieknop")
# 				elif command == "ping":
# 					now = datetime.now()
# 					current_time = now.strftime("%H:%M:%S")
# 					print("pinged by", addr, "at", current_time)
# 					print("DIT SCHERM NIET WEGKLIKKEN")
# 				else:
# 					print("invalid command")
					

	
	