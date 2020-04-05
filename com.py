#!/usr/bin/env python3

# Communication layer 
# STM32 <--> RaspberryPi <--> WebApp
#
#
#   Communication STM32 <--> RaspberryPi 
#       * TCP
#
#   
#   Communication RaspberryPi <--> WebApp
#       * WebSocket (server: this script / client : WebApp (Javascript))
#
#


import asyncio
import websockets
import json
import socket
from struct import *
from collections import namedtuple

##
#   @def 
#   @params:
#       'id'       : id of the TCP packet
#       'cmd'      : cmd
#       'nb_parameters' : N parameters
#       'params':       : [param1, param2, .... paramN]
def BuildTCP_Frame(id, command_no,nb_parameters,params):
    tcp_trame = [];
    tcp_trame = pack("III%dI" % int(len(params)),id,command_no,nb_parameters,*params);
    return tcp_trame;

##
#   @def 
#   @params:
#       'id'            : id of the TCP packet
#       'command_no'      : total number of bytes = id + nb_bytes + nb_parameters + param1 + param2 + ... + paramN
#       'nb_parameters' : N parameters
#       'params':       : [param1, param2, .... paramN]
#
def DecodeTCP_Frame(data):
    data_decoded = {'id': 0, 'cmd': 0, 'code':0,'size_answer': 0, 'answer':0};
    data_unpacked = unpack('%dI' % int(len(data)/4), data);

    if(len(data_unpacked) >= 5):
        data_decoded["id"] = data_unpacked[0];
        data_decoded["code"] = data_unpacked[1];
        data_decoded["cmd"] = data_unpacked[2];
        data_decoded["size_answer"] = data_unpacked[3];
        data_decoded["answer"] = data_unpacked[4:4+len(data_unpacked)];    
    

    return data_decoded;


#   @def : PrepareCMD_GetInfo(id)
#   Prepare a TCP Frame to send a GET INFO command to the STM32
#   @params :  - id: ID of the TCP frame
#              - led_red:  1: turn on the RED LED, 0: turn off the RED LED, 2: do not modify current state of RED LED  
#              - led_blue: 1: turn on the BLUE LED, 0: turn off the BLUE LED, 2: do not modify current state of BLUE LED   
#              - led_green:1: turn on the GREEN LED, 0: turn off the GREEN LED, 2: do not modify current state of GREEN LED   
#
#   @return : return the TCP frame ready to be sent to the STM32
def PrepareCMD_GetInfo(id):
    frame_get_info = BuildTCP_Frame(id,0x01,0,None);
    return frame_get_info;

#   @def : PrepareCMD_SetLED(id, led_red,led_blue,led_green)
#   Prepare a TCP Frame to send a SET LED command to the STM32
#   @params :  - id: ID of the TCP frame
#              - led_red:  1: turn on the RED LED, 0: turn off the RED LED, 2: do not modify current state of RED LED  
#              - led_blue: 1: turn on the BLUE LED, 0: turn off the BLUE LED, 2: do not modify current state of BLUE LED   
#              - led_green:1: turn on the GREEN LED, 0: turn off the GREEN LED, 2: do not modify current state of GREEN LED   
#
#   @return : return the TCP frame ready to be sent to the STM32
def PrepareCMD_SetLED(id, led_red,led_blue,led_green):
    param = (led_red << 16) + (led_blue << 8) + (led_green)

    frame_set_led = BuildTCP_Frame(id,0x02,1,[param]);
    return frame_set_led;





import time

def executeSomething(s):
    n = 0;
    BUFFER_SIZE = 1024
    while True:
        #code here
        test = PrepareCMD_SetLED(n, 2,1,0);

        s.send(test)
        data = s.recv(BUFFER_SIZE)
        test_decoded_data = DecodeTCP_Frame(data);
        print ("received data2:"+ repr(test_decoded_data))    
        n = n+1;
        time.sleep(0.100);

        test = PrepareCMD_SetLED(n, 2,0,1);

        s.send(test)
        data = s.recv(BUFFER_SIZE)
        test_decoded_data = DecodeTCP_Frame(data);
        print ("received data2:"+ repr(test_decoded_data))
        n = n+1;
        time.sleep(0.100);
    

#
#   Manage the TCP connection between the Raspberry (Python) and the STM32
#
#
#
def HandleTCP_STM32():
    TCP_IP = '10.10.0.2'
    TCP_PORT = 7
    BUFFER_SIZE = 1024
    MESSAGE = "Hello, World!"

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))

    executeSomething(s);
    test = BuildTCP_Frame(0,1,2,[3, 4, 5, 6]);
    test = PrepareCMD_SetLED(2500, 1,1,1);
    print ("received data:"+ repr(test))
    s.send(test)
    data = s.recv(BUFFER_SIZE)
    s.close()


    print ("received data:"+ repr(data))
    test_decoded_data = DecodeTCP_Frame(data);
    print ("received data2:"+ repr(test_decoded_data))
    print ("received data: answer:"+ repr(test_decoded_data["answer"]))

    HandleTCP_STM32()





# Handle the request of the WebApp (user interface)
# List of cmd defined:
# - status              : status (connection with STM32 + script running)  
# - pos                 : current position of the robot
# - led                 : status of the LEDs on the STM32
# - tirette             : status of the tirette
# - strategy            : transmit the strategy chosen 
# - color               : transmit the color chosen
# - goToInit[x,y,theta] : Ask the robot to go to Inital Position
# - goToPos[x,y,theta]  : Ask the robot to go to a specific position
#
#   Javascript definition of a message:
#       var msg = 
#       {
#           type: "cmd",
#           cmd: cmd,
#           param1: param1,
#           param2: param2,
#           param3: param3,
#           id:   clientID,
#           date: Date.now()
#       };
#



async def HandleWebSocketServer(websocket, path):
   while True:
        cmd = await websocket.recv()

        # Retreve JSON parsed data
        cmd = json.loads(cmd);

        print(f"< {cmd}")

    # switch(cmd.cmd){
    #     case :
    #     break;
    # }
        


        await websocket.send(json.dumps(cmd))
        print(f"> {cmd}")

#start_server = websockets.serve(HandleWebSocketServer, "localhost", 1234)

#asyncio.get_event_loop().run_until_complete(start_server)
#asyncio.get_event_loop().run_forever()


