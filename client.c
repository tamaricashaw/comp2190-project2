#
#Client to implement a simple program to send two prime numbers to a
#server. The server will compute their LCM and send back to the client.
# If the server-calculated LCM matches what the client computes, the 
# client will send a 200 OK status code to the server. Otherwise a
# Error code is sent to the server.

# Author: fokumdt
# Last modified: 2023-10-09
#!/usr/bin/python3

import socket
import sys


state = {
  "serverHello": "sH",
  "primeNumbers": "pN",
  "prime1": 0,
  "prime2": 0
}

def name_print():
  return "Tamarica Shaw"


def serverHello():
  """Generates server hello message"""
  status = "100 Hello"
  return status

def AllGood():
  """Generates 200 OK"""
  status = "200 OK"
  return status

def ErrorCondition():
  """Generates 400 Error"""
  status = "400 Error"
  return status


def PrimeCollect():
  """Accepts a prime number to send to the server"""
  primeNbr = input("Enter a prime number between 1031 and 6397:")
  return primeNbr

def PrimeMsg(prime1, prime2):
  """Generates the first prime number to send"""
  msg = "105 Primes "+ str(prime1) + " " + str(prime2)
  return msg

def lcm(prime1,prime2):
  """ Calculates the lcm of the 2 prime numbers """ 
  val = int(prime1 )* int(prime2)
  if prime1==prime2:
    return prime1
  return val
  
def is_prime(n):
  """Checks if the number is prime"""
  try:
    n = int(n)
    if type(n) == int:  
      if n <= 1:
          return False
      if n == 2:
          return True
      if n % 2 == 0:
          return False
      for i in range(3, int(n**0.5) + 1, 2):
          if n % i == 0:
              return False
      return True
    else:
      return False
  except ValueError:
    return False
    
    

def is_within_range(n, lowest, upper):
    "Checks if the number is within the specified range of prime numbers accepted"
    n=int(n)
    return lowest <= n <= upper

# s     = socket
# msg   = message being processed
# state = dictionary containing state variables

def processMsgs(s,msg,state):
  """This function processes messages that are read through the socket. It
     returns a status, which is an integer indicating whether the operation
     was successful."""
  
  status = -1

  #first message
  if ("101 Hello Ack"== msg):
    print("The server sent: ",msg)
    prime1= PrimeCollect()
    prime2= PrimeCollect()
    state["prime1"]=prime1
    state["prime2"]=prime2
    if is_prime(state["prime1"]) == False or is_prime(state["prime2"] ==False):
      print("[ERROR] Both numbers should be prime numbers")
      msg = "[ERROR] Both numbers should be prime numbers"
      status = -1
      return status
    else:
      state["prime1"]=int(prime1)
      state["prime2"]=int(prime2)
      if is_within_range(state["prime1"],1031,6397) and is_within_range(state["prime2"],1031,6397):
        primeNums= PrimeMsg(state["prime1"],state["prime2"])
        status = 1
        s.send(primeNums.encode())
        return
  elif "107 LCM" in msg:
    print("The server sent: ",msg)
    msg_split = msg.split()
    s_LCM = int(msg_split[2])
    lcmVal= lcm(int(state["prime1"]), int(state["prime2"]))
    if(s_LCM == lcmVal):
       status = 1
       return status
    else:
       status = 0
       return status
       
  # first request
    

def main():
  """Driver function for the project"""

  args = sys.argv
  if len(args) != 3:
    print("Please supply a server address and port.")
    sys.exit()
  serverHost = str(args[1])  #The remote host
  serverPort = int(args[2])  #The port used by the server
  if (serverPort < 1023 or serverPort > 65535):
    print("Invalid port specified.")
    sys.exit()

  name= name_print()
  print(f"Client of {name}")
  print("""
  The purpose of this program is to collect two prime numbers from the client, and then
  send them to the server. The server will compute their LCM and send it back to the
  client. If the server-computed LCM matches the locally computed LCM, the
  clientsends the server a 200 OK status code. Otherwise it sends a 400 error status code,
  and then closes the socket to the server.
  """)


  #Iinitializing socket sending data into the socket
  client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  client_socket.connect((serverHost,serverPort))
  print(f"Connected to {serverHost} on port {serverPort}\n ")

  
  #Performing handshake with server
  msg = serverHello()
  print("Message sent: ", msg)
  client_socket.send(msg.encode())
  
  #processing msg from server
  
  while True:
    msg= client_socket.recv(1024).decode()
    status = processMsgs(client_socket,msg, state)
    if(status == -1 ):
      client_socket.send("500 Bad Request".encode())
      break
    elif status == 1:
      client_socket.send(AllGood().encode())
      break
    elif status == 0:
      client_socket.send(ErrorCondition().encode())
      break
      
         

  client_socket.close()
  print("Connection terminated on client end")
 



if __name__ == "__main__":
    main()