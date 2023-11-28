# Server to implement the simplified RSA algorithm and receive encrypted
# integers from a client.
# The server waits for the client to say Hello. Once the client says hello,
# the server sends the client a public key. The client uses the public key to
# send a session key with confidentiality to the server.

# Author: 
# Last modified: 2023-11-14
# Version: 0.1.1
#!/usr/bin/python3

import socket
import random
import math
import hashlib
import time
import sys
import simplified_AES
from NumTheory import NumTheory



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
    


class RSAServer(object):
    
    def __init__(self, port, p, q):
        self.socket = socket.socket()
        # The option below is to permit reuse of a socket in less than an MSL
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(("", int(port)))
        self.socket.listen(5)
        self.lastRcvdMsg = None
        self.sessionKey = None		#For storing the symmetric key
        self.modulus = None		#For storing the server's n in the public/private key
        self.pubExponent = None	#For storing the server's e in the public key
        self.privExponent = None	#For storing the server's d in the private key
        self.nonce = None
        # Call the methods to compute the public private/key pairs

             

    def send(self, conn, message):
        """Creates connection  socket"""
        conn.send(bytes(message,'utf-8'))

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
                raise RuntimeError("Client is unavailable")

    def close(self, conn):
        """This closes the socket that is open"""

        print("closing server side of connection")
        try:
            conn.close()
        except OSError as e:
            print(
                "error: socket.close() exception for",
                f" {repr(e)}",
            )
        finally:
            # Delete reference to socket object
            conn = None    

    def RSAencrypt(self, msg):
        """Encryption side of RSA"""
        """"This function will return (msg^exponent mod modulus) """
        
        if msg < self.modulus:
            en = NumTheory.expMod(msg,self.serverExponent,self.modulus)
            return en
        else:
            print("The message needs to be less than modulus n")
        
      

    def RSAdecrypt(self, cText):
        """Decryption side of RSA"""
        """"This function will return (cText^exponent mod modulus) """

        cText = int(cText)  
        decrypt = NumTheory.expMod(cText, self.privExponent, self.modulus)
        return decrypt

    def AESdecrypt(self, cText):
        """Decryption side of AES"""
        simplified_AES.keyExp(self.sessionKey)
        cText_int= int(cText)
        return simplified_AES.decrypt(cText_int)

      

    def AESencrypt(self, plaintext):
        """Computes the simplified AES encryption of some plaintext"""
        simplified_AES.keyExp(self.sessionKey) # Generating round keys for AES.
        ciphertext = simplified_AES.encrypt(plaintext) # Running simplified AES.
        return ciphertext

    def generateNonce(self):
        """This method returns a 16-bit random integer derived from hashing the
            current time. This is used to test for liveness"""
        hash = hashlib.sha1()
        hash.update(str(time.time()).encode('utf-8'))
        self.nonce = int.from_bytes(hash.digest()[:2], byteorder=sys.byteorder)

    def findE(self, phi,n):
        """Method to randomly choose a good e given phi"""
        r = random.randint(2, phi - 1)
        if math.gcd(r, phi) == 1 and r < n:
            return r
        else:
            return None

        

    def genKeys(self, p, q):
        """Generates n, phi(n), e, and d""" 
        phi_n = 0
        e= 0

        if is_prime(p) and is_prime(q):
            phi_n= (p-1) * (q-1)
            self.modulus= p * q

            max_iterations = 100  
            iteration_count = 0
        
            while True:
                if iteration_count >= max_iterations:
                    break

                e = self.findE(phi_n, self.modulus)
                if e is not None:
                    self.pubExponent = e
                    break

                iteration_count += 1
            
            i = NumTheory.ext_Euclid(phi_n, e)
            self.privExponent=i

        return "N:" +str(self.modulus), "Phi N:" +str(phi_n), "Public Key:" +str(self.pubExponent),"Private Key:" + str(self.privExponent)

    def clientHelloResp(self):
        """Generates response string to client's hello message"""
        self.generateNonce()
        status = "102 Hello AES, RSA16 " + str(self.modulus) + " " + \
         str(self.pubExponent) + " " + str(self.nonce)
        return status

    def nonceVerification(self, decrypnonce):
        """Verifies that the transmitted nonce matches that received
        from the client."""

        # Compare the decrypted nonce with the original nonce
        if decrypnonce  == self.nonce:
            return True
        else:
            return False
       


    def start(self,p,q):
        """Main sending and receiving loop"""
    
        primeN = self.genKeys(p, q)
        formatted_output = ", ".join(primeN)
        print(formatted_output)

        while True:
            connSocket, addr = self.socket.accept()
            msg = connSocket.recv(1024).decode('utf-8')
            print (msg)
            self.send(connSocket, self.clientHelloResp())

            msg = connSocket.recv(1024).decode('utf-8')
            print (msg)
            if msg.strip().startswith("103 SessionKey"):
                encrypted_session_key = msg.split()[2]

                # Convert encrypted session key to integer before decryption
                encrypted_session_key = int(encrypted_session_key)

                self.sessionKey = self.RSAdecrypt(encrypted_session_key)  # Decrypt the encrypted session key
                decrypnonce= msg.split()[3]
                decrypted_nonce = self.AESdecrypt(decrypnonce)
            
                if self.nonceVerification(decrypted_nonce):
                    msg = "104 Nonce Verified"
                    self.send(connSocket,msg)
                else:
                    msg= "400 Error"
                    self.send(connSocket,msg)

                msg = connSocket.recv(1024).decode('utf-8')
                print (msg)
                if msg.strip().startswith("108 PrimesEncrypted"):
                    num1=msg.split()[2]
                    num2=msg.split()[3]
                    
                    a=self.AESdecrypt(num1)
                    b=self.AESdecrypt(num2)

                    res = NumTheory.lcm(a,b)
                    encrypted_res = self.AESencrypt(res)
                    

                    # Send "109 CompositeEncrypted" message
                    composite_msg = f"109 CompositeEncrypted {encrypted_res}"
                    print(composite_msg)
                    self.send(connSocket, composite_msg)

                    msg = connSocket.recv(1024).decode('utf-8')
                    print (msg)
                    if "200 OK" in msg:
                        print("Last message is 200 OK")
                    if "400 Error" in msg:
                        print("Last message recieved was a 400 Error")

                

            self.close(connSocket)
            break

def main():
    """Driver function for the project"""
    args = sys.argv
    if len(args) != 2:
        print ("Please supply a server port.")
        sys.exit()
        
    HOST = ''		# Symbolic name meaning all available interfaces
    PORT = int(args[1])     # The port on which the server is listening
    if PORT < 1023 or PORT > 65535:
        print("Invalid port specified.")
        sys.exit()
    print(f"Server of Tamarica Shaw")
    print ("""Enter prime numbers. One should be between 211 and 281,
    and the other between 229 and 307. The product of your numbers should
    be less than 65536""")
    p = int(input('Enter P: '))
    q = int(input('Enter Q: '))

    server = RSAServer(PORT, p, q)
    server.start(p,q)

   

if __name__ == "__main__":
    main()
