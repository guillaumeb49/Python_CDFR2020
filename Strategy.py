from RobotClass import Robot
import asyncio
import websockets
import json
import threading
import time
import socket
from signal import signal, SIGINT
from sys import exit
import pickle

class Strategy:
    robot       = Robot()
    socket_UI   = None
    socketServer= None


    def handler(self,signal_received, frame):
        # Handle any cleanup here
        print('SIGINT or CTRL-C detected. Exiting gracefully')
        self.socketServer.close()
        exit(0)

#------------------------------------------------------------------------------
    def run(self):
        """
        """

        # Start the virtual robot in a separete thread
        t0 = threading.Thread(target=self.robot.run)
        t0.start()
        
        t1 = threading.Thread(target=self.ManageStrategy)
        t1.start()

        signal(SIGINT, self.handler)

        # Start the threads
        self.ManageUI()

    def HandleBackEndSocketServer(self):
        HOST = 'localhost'        
        PORT = 50007              # Arbitrary non-privileged port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.socketServer:
            self.socketServer.bind((HOST, PORT))
            self.socketServer.listen(1)
            conn, addr = self.socketServer.accept()
            with conn:
                print('Connected by', addr)
                while True:
                    data = conn.recv(1024)
                    if not data: 
                        print("ERROR CONNEXION") 
                        break

                    cmd = pickle.loads(data);

                    #print(f"< {cmd}")

                    answer = {"type":"answer", "cmd":cmd['cmd'], "answer":''}
                    
                    if(cmd['cmd'] == "UpdateRobotUI"):
                        answer['answer'] = self.robot.GetInfo()

                    elif(cmd['cmd'] == "goToInit"):
                        answer['answer'] = 0
                    
                    elif(cmd['cmd'] == "MoveStop"):
                        answer['answer'] = self.robot.SetManualControl(0)

                    elif(cmd['cmd'] == "MoveFoward"):
                        answer['answer'] = self.robot.SetManualControl(1)
                
                    elif(cmd['cmd'] == "MoveBackward"):
                        answer['answer'] = self.robot.SetManualControl(2)
                    
                    elif(cmd['cmd'] == "MoveLeft"):
                        answer['answer'] = self.robot.SetManualControl(3)
                    
                    elif(cmd['cmd'] == "MoveRight"):
                        answer['answer'] = self.robot.SetManualControl(4)

                    conn.sendall(pickle.dumps(answer))
                    #print(f"> {answer}")

    def ManageUI(self):
        self.HandleBackEndSocketServer()

    def ManageStrategy(self):
        a=1

if __name__ == '__main__':

    s = Strategy()
    s.run()