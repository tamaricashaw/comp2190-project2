# Client to implement simplified RSA algorithm and then subsequently send
# encrypted prime numbers to a server. The client says hello to the server
# and indicates
# which cryptographic algorithms it can support. The server picks one
# asymmetric key and one symmetric key algorithm and then responds to the
# client with its public key and a nonce. The client generates a symmetric
# key to send to the server, encrypts the symmetric key with the public key,
# and then encrypts the nonce with the symmetric key.
# If the nonce is verified, then the server will send the "104 Nonce Verified"
# message.

import hashlib
import socket
import math
import random
import sys
import time
import simplified_AES
from NumTheory import NumTheory 

# Author: Tamarica Shaw
# Last modified: 2023-11-22
# Version: 0.1.0
#!/usr/bin/python3



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

class RSAClient:
    def __init__(self, address, port):
        self.address = address
        self.port = int(port)
        self.socket = socket.socket()
        self.lastRcvdMsg = None
        self.sessionKey = None		#For storing the symmetric key
        self.modulus = None		    #For storing the server's n in the public key
        self.serverExponent = None	#For storing the server's e in the public key

    def connect(self):
        """Creates connection  socket"""
        self.socket.connect((self.address, self.port))


    def send(self, message):
        """Used to send messages through socket"""
        self.socket.send(bytes(message,'utf-8'))

    def read(self):
        """Used to read and decode message comming through socket"""
        try:
            data = self.socket.recv(4096).decode('utf-8')
        except BlockingIOError:
            pass
        else:
            if data:
                self.lastRcvdMsg = data
            else:
                raise RuntimeError("Server is unavailable")

    def close(self):
        """This closes the socket that is open"""
        print("closing connection to", self.address)
        try:
            self.socket.close()
        except OSError as e:
            print(
                "error: socket.close() exception for",
                f"{self.address}: {repr(e)}",
            )
        finally:
            # Delete reference to socket object for garbage collection
            self.socket = None

    def RSAencrypt(self, msg):
        """"This function will return (msg^exponent mod modulus) """

        if msg < self.modulus:
            en = NumTheory.expMod(msg,self.serverExponent,self.modulus)
            return en
        else:
            print("The message needs to be less than modulus n")


    def computeSessionKey(self):
        """Computes this node's session key"""
        self.sessionKey = random.randint(1, 65536)
        

    def AESencrypt(self, plaintext):
        """Computes the simplified AES encryption of some plaintext"""
        simplified_AES.keyExp(self.sessionKey) # Generating round keys for AES.
        plaintext_int=int(plaintext)
        ciphertext = simplified_AES.encrypt(plaintext_int) # Running simplified AES.
        return ciphertext
    

    def AESdecrypt(self, cText):
        """Decryption side of AES"""
        simplified_AES.keyExp(self.sessionKey)
        cText_int= int(cText)
        return simplified_AES.decrypt(cText_int)
    
    def serverHello(self):
        """First message sent to client"""
        status = "101 Hello 3DES, AES, RSA16, DH16"
        return status

    def sessionKeyMsg(self,nonce):
        """Function to generate response string to server's hello"""

        if nonce is None:
            raise ValueError("Invalid nonce value")

        # Encrypt session key with server's public key
        encrypted_session_key = self.RSAencrypt(self.sessionKey)

        # Encrypt nonce with session key
        encrypted_nonce = self.AESencrypt(str(nonce))
        return f"103 SessionKey {encrypted_session_key} {encrypted_nonce}"
    
    def prime_encryptedMsg(self,a,b):
        """This fuction encrypts the prime numbers that it got from the client"""

        if is_prime(a) & is_prime(b):
            print(a,b)
            encryp_a = self.AESencrypt(a)
            encryp_b= self.AESencrypt(b)

            return f"108 PrimesEncrypted {encryp_a} {encryp_b}"






    def start(self):
        """Main sending and receiving loop for the client"""
        self.connect()
        self.send(self.serverHello())
        self.read()
        print(self.lastRcvdMsg)


        if self.lastRcvdMsg.startswith("102 Hello AES, RSA16"):
            message_parts = self.lastRcvdMsg.split(" ")
            self.modulus = int(message_parts[4])	   
            self.serverExponent = int(message_parts[5])
            nonce=int(message_parts[6])

            self.computeSessionKey()
            session_key_msg = self.sessionKeyMsg(nonce)
            self.send(session_key_msg)
            
            self.read()
            print(self.lastRcvdMsg)

        if self.lastRcvdMsg.startswith("400 Error"):
            self.close()

        if self.lastRcvdMsg.startswith("104 Nonce"):

            print ("Enter 2 prime numbers one between 211 -281 and the other between 229 and 307.")
            a= int(input('Enter A: '))
            b= int(input('Enter B: '))

            res =self.prime_encryptedMsg(a,b)
            self.send(res)

            self.read()
            print(self.lastRcvdMsg)

            results = NumTheory.lcm(a,b)

            if self.lastRcvdMsg.startswith("109 CompositeEncrypted"):
                
                message_parts = self.lastRcvdMsg.split(" ")
            
                product = int(message_parts[2])
                p= self.AESdecrypt(product)
               
                if results ==p:
                    msg="200 OK"
                    self.send(msg)
                else:
                    msg= "400 Error"
                    self.send(msg)

    
        self.close()
        


def main():
    """Driver function for the project"""
    args = sys.argv
    if len(args) != 3:
        print ("Please supply a server address and port.")
        sys.exit()
    print(f"Client of Tamarica Shaw")
    serverHost = str(args[1])       # The remote host
    serverPort = int(args[2])       # The same port as used by the server

    client = RSAClient(serverHost, serverPort)
    try:
        client.start()
    except (KeyboardInterrupt, SystemExit):
        exit()

if __name__ == "__main__":
    main()
