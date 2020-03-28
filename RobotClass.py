#!/usr/bin/env python3

from queue import Queue
import threading
from time import sleep
import time
import socket
import com

class Robot:
    current_position        = {'x':0,'y':0,'theta':0}
    vecteurDeplacement      = {'x':0,'y':0,'theta':0}
    next_position           = {'x':0,'y':0,'theta':0}
    asservissement_status   = 0
    ready_to_start          = 0
    distances               = [0,0,0,0]
    tirette_status          = 0 
    leds                    = [0,0,0,0,0,0,0,0]
    servos_position         = {0,0,0,0,0,0}
    position_glass_detected = 0
    socket_STM32            = None
    q                       = 0
    stop_thread_debug       = 0
    stop_thread_comm        = 0
    stop_thread_info        = 0
    id                      = 0
    list_answers            = {}
    _sentinel               = object() 

#------------------------------------------------------------------------------
    def InitCommSTM32(self):
        """
        Initialize the socket to handle the general communication with the STM32

        This function must be called before any command can be sent to the STM32

        Returns
        -------
        socket_STM32
            socket representing the connection with STM32
        """
        
        TCP_IP = '10.10.0.2'
        TCP_PORT = 7
        BUFFER_SIZE = 1024

        self.socket_STM32 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.socket_STM32.connect((TCP_IP, TCP_PORT))
        except socket.error as msg:
            print("Caught exception socket.error : %s" % msg)
            self.socket_STM32 = None

        return self.socket_STM32



    def EndCommSTM32(self):
        """
        Close the TCP Socket with the STM32
        """
        self.socket_STM32.close()


    def ComThread(self):
        """
        Communicate with the STM32. Assuming that the communication is already opened (TCP)
        """
        
        while (self.stop_thread_comm != 1):

            # Get a command from the FIFO (blocks while no command available)
            command = self.q.get()
            
            # Check for termination 
            if command is self._sentinel: 
                stop_thread_comm = 1
                break   # We end the thread comm

            # Send the command in FIFO
            self.socket_STM32.send(command)

            # Wait for the answer to be received
            answer = self.socket_STM32.recv(1024)
            
            # Decode the answer received from the STM32
            answer = com.DecodeTCP_Frame(answer);

            # Store the answer in a list, the ID is the key
            self.list_answers.update( {str(answer['id']): answer})


        # End the communication with the STM32
        self.EndCommSTM32()
        


#------------------------------------------------------------------------------
    def UpdateInfo(self):
        """
        Request and update of the software representation of the real robot

        Request periodically (~250ms) the value of all variables from the STM32.
        This function append a new command to the queue of command to be sent to the STM32. 

        Returns
        -------
        none
        """
    
        while(self.stop_thread_info != 1):
            start = time.time()
            # Store the ID of the command
            id_last_cmd = self.id;
            
            # Increment the ID for the next command
            self.id = self.id + 1 

            # Add a new command "Get_INFO" to the queue of command to be sent to the STM32
            self.AppendCommand(com.BuildTCP_Frame(id_last_cmd, 0x01,0,[]))
            
            # Wait for the answer from the STM32
            while(str(id_last_cmd) not in  self.list_answers.keys()):
                sleep(0.0005)
            
            # Process the answer and Update all the value of this virtual Robot
            answer = self.list_answers.pop(str(id_last_cmd))
            self.distances = [answer['answer'][3], answer['answer'][4], answer['answer'][5], answer['answer'][6]]
            end = time.time()

            print("--------")
            print(end - start)
            print(repr(answer))
            print("---------")
            
            # Sleep for 250ms
            sleep(0.250)



#------------------------------------------------------------------------------
    def SetNextPoint(self, next_point):
        """
        Send the next target point to the STM32

        Parameters
        ----------
        next_point : {x,y,theta}
            Next point represented as a dictionnary( keys are x,y or theta)

        Returns
        -------
        int
            0: next point has been sent to STM32
            1: a problem occured, the STM32 is probably not connected of the socket is down

        """

    def GetPosition(self):
        """
        Get the position of the robot. This value is actualized every 250ms

        Returns
        -------
        int [x,y,theta]
            x: X-position
            y: Y-position
            theta: Theta-position
        """
        return self.current_position

    def SetLeds(self,led_red,led_blue,led_green):
        """
        Set the value of the LEDs

        Parameters
        --------
            1: turn on the LED, 0: turn off the LED, 2: do not modify current state of LED
        """
        # Store the ID of the command
        id_last_cmd = self.id;
            
        # Increment the ID for the next command
        self.id = self.id + 1 

        # Add this command to the list of command to be sent
        self.AppendCommand(PrepareCMD_SetLED(id_last_cmd, led_red,led_blue,led_green))

        # Return the ID of the command
        return id_last_cmd


#------------------------------------------------------------------------------
    def AppendCommand(self, command):
        """
        Add a new command to the list of command to be sent to the robot (FIFO)

        Returns
        -------
        int:
             -1: FIFO is already full
              0: command added
        """

        self.q.put(command)

    def GetCommandFromQueue(self,command):
        """
        Get the first command from the queue
        This method should not be used!

        Returns
        -------
        command or error:
             -1: FIFO is empty
              command
        """
        if(self.q.empty() == False):
            to_be_returned = self.q.get(False)
        else:
            to_be_returned = -1

        return to_be_returned

    def ResetCommandList():
        """
        Reset the list of commnd to be sent to the Robot

        """

        self.q.queue.clear()


#------------------------------------------------------------------------------
    def Robot_Debug(self):
        """
        Debug the Robot Class
        """
        
        while(self.stop_thread_debug == 0):
            print("***** DEBUG ***************")
            print("current_position : "+repr(self.current_position))
            print("vecteurDeplacement : "+repr(self.vecteurDeplacement))
            print("next_position : "+repr(self.next_position))
            print("asservissement_status : "+repr(self.asservissement_status))
            print("ready_to_start : "+repr(self.ready_to_start))
            print("distances : "+repr(self.distances))
            print("tirette_status : "+repr(self.tirette_status))
            print("leds : "+repr(self.leds))
            print("servos_position : "+repr(self.servos_position))
            print("position_glass_detected : "+repr(self.position_glass_detected))
            print("socket_STM32 : "+repr(self.socket_STM32))
            print("q : "+repr(list(self.q.queue)))
            print("list_answers : "+repr(list(self.list_answers)))
            print("***************************")        
            start = time.time()
            sleep(5)
            end = time.time()
            print(end - start)

    def GetDistances(self):
        return self.distances
#------------------------------------------------------------------------------
    def run(self):
        """
        Start the virtual Robot. 
        Once called, this method will invoque the necessary function which will periodically update the Robot variables by connecting to the STM32

        """

        #Initialize the queu
        self.q = Queue()

        retry = 0

        while (self.socket_STM32 == None):
            print("NONE")
            # Try to open the Communication with the STM32 (TCP PORT 7)
            self.InitCommSTM32()

            if(retry != 0):
                sleep(retry)  

            retry = retry + 1

            if(retry > 5):
                retry = 5 #maximum sleep of 5 seconds per attempt

                # if we have reached this limit we have already been waiting for 15 seconds
                # Maybe the STM32 is not connected
                print("Error: Connection to STM32 failed, check that cables")
            
        # The Socket is now opened

        # Start the threads
        t0 = threading.Thread(target=self.ComThread)
        t1 = threading.Thread(target=self.Robot_Debug)
        t2 = threading.Thread(target=self.UpdateInfo)

        t0.start()
        t1.start()
        t2.start()
        
        sleep(25)

        self.stop_thread_debug = 1
        self.stop_thread_info = 1
        self.q.put(self._sentinel)
        self.stop_thread_comm = 1
         

        t0.join()
        t1.join()
        t2.join()

#------------------------------------------------------------------------------
if __name__ == '__main__':
    r = Robot()
    r.run()