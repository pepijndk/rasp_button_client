import socket
from time import sleep    # configure socket and connect to server  

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 65432

while clientSocket.connect_ex(( "192.168.0.114", port )) != 0:    # keep track of connection status
	print("waiting to connect")
	sleep(5)

connected = True
print( "connected to server" )
i = 0
while True:      # attempt to send and receive wave, otherwise reconnect      
	message = "message" + str(i)
	if i % 5 == 0: 
		message = "quit"
	try:
		clientSocket.send(message.encode())
	except socket.error:          # set connection status and recreate socket
		connected = False
		clientSocket = socket.socket()
		print( "connection lost... reconnecting" )
		while not connected:              # attempt to reconnect, otherwise sleep for 2 seconds
			try:
				clientSocket.connect( ( "192.168.0.114", port ) )
				connected = True                  
				print( "re-connection successful" )
			except socket.error:                  
				sleep( 2 )    
	i = i + 1
	sleep(1)
clientSocket.close(); 