# Server to implement a simple program to receive two prime numbers from a
# client. The server will compute their LCM and send it back to the client.
# If the server-calculated LCM matches what the client computes, the client
# will send a 200 OK status code to the server. Otherwise a 400 Error code is
# sent to the server.

# Author: fokumdt
# Last modified: 2023-10-09
#!/usr/bin/python3

import socket
import sys
from curses.ascii import isdigit



def name_print():
  return "Tamarica Shaw"


def clientHello():
  """Generates an acknowledgement for the client hello message"""
  msg = "101 Hello Ack"
  return msg


def generateLCMstring(lcm):
  """Generates the 107 LCM string"""
  msg = "107 LCM " + str(lcm)
  return msg

def lcm(prime1,prime2):
  val = int(prime1 )* int(prime2)
  return val



#s      = socket
#msg    = message being processed
#state  = dictionary containing state variables
def processMsgs(s,msg, state):
  """This function processes messages that are read through the socket. It returns
     a status, which is an integer indicating whether the operation was successful."""
  status=-1 #unsuccessful

  #first reply
  if "500 Bad Request" in msg:
    print(msg)
    status = -1

  elif state=="hello":
    s.send(msg.encode())
    status=1     #1 is success
  
  #sending response of request 
  elif state=="prime":
    print("The client sent:", msg)


    if msg==" [ERROR] Numbers were not in the range":
      status= -1
      s.close()
    

    elif msg=="[ERROR] Both numbers should be prime numbers":
      status =-1
      s.close()

    else:
      split_num = msg.split(' ')
      print(split_num)
      if (not (split_num[2]).isdigit()) or (not(split_num[3]).isdigit()) :
        status= -1
        s.send("500 Bad Request".encode())

      else:
          prime1= split_num[2]
          prime2= split_num[3]
          lcmVal= lcm(prime1, prime2)
          prime= generateLCMstring(lcmVal)
          message= prime
          print(message)

          s.send(message.encode())
          status=1
  if status == 1:
    print("This process was successful")
  else:
    print("Sorry, this process was unsuccessful")
  return status
      

  


def main():
  """Driver function for the server."""
  args = sys.argv
  if len(args) != 2:
    print ("Please supply a server port.")
    sys.exit()
  HOST = ''            #Symbolic name meaning all available interfaces
  PORT = int(args[1])    #The port on which the server is listening.
  if (PORT < 1023 or PORT > 65535):
    print("Invalid port specified.")
    sys.exit()

  name = name_print()
  print(f"Server of {name}")
  '''specify socket parameters to use TCP'''
  print(f"Server is listening on host {HOST} and  port {PORT}\n")
 
  with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
    s.bind((HOST,PORT))
    s.listen()
    print("The server is ready to recieve")
    # accepting connections using socket
    conn, addr = s.accept()
    with conn:
      print("Connected from: ", addr)
      
      #handshake
      
      msg = conn.recv(1024).decode()
      if msg != "100 Hello" :
        conn.send("500 Bad Request".encode())
      else:
        print("You are in luck, the client said:",msg)
        message= clientHello()
        status= processMsgs(conn,message, state="hello")
        if status == -1:
          sys.exit()
        
        # first request from client
        msg=conn.recv(1024).decode()
        status= processMsgs(conn,msg,state="prime")
        print("Status: "+ str(status))
        if status == -1:
          sys.exit()
        msg=conn.recv(1024).decode()
        print("Received from client: ", msg)

      
        print("Connection terminated on server end")
  
if __name__ == "__main__":
    main()