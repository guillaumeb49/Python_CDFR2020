from RobotClass import Robot
import asyncio
import websockets
import json
import threading


class Strategy:
    robot       = Robot()
    socket_UI   = None

#------------------------------------------------------------------------------
    def run(self):
        """
        """

        # Start the virtual robot in a separete thread
        t0 = threading.Thread(target=self.robot.run)
        t0.start()
        
        t1 = threading.Thread(target=self.manaManageStrategy)
        t1.start()

        # Start the threads
        self.ManageUI()



    async def HandleWebSocketServer(self, websocket, path):
        while True:
            cmd = await websocket.recv()
            # Retreve JSON parsed data
            cmd = json.loads(cmd);

            print(f"< {cmd}")

            answer = {"type":"answer", "id":cmd['id'], "cmd":cmd['cmd'], "answer":''}
            
            if(cmd['cmd'] == "getInfo"):
                answer['answer'] = self.robot.GetDistances()
            
            elif(cmd['cmd'] == "goToInit"):
                answer['answer'] = 0
            
            elif(cmd['cmd'] == "foward"):
                answer['answer'] = self.robot.SetLeds(1,0,0)

            elif(cmd['cmd'] == "backward"):
                answer['answer'] = self.robot.SetLeds(0,1,0)
            
            elif(cmd['cmd'] == "left"):
                answer['answer'] = self.robot.SetLeds(0,0,1)
            
            elif(cmd['cmd'] == "right"):
                answer['answer'] = self.robot.SetLeds(0,0,1)

            await websocket.send(json.dumps(answer))
            print(f"> {answer}")

    def ManageUI(self):
        start_server = websockets.serve(self.HandleWebSocketServer, "0.0.0.0", 1234)

        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    def ManageStrategy(self):
        #MARIO CODE!!!
        #self.robot.SetLeds(0,0,1)

    



if __name__ == '__main__':
    s = Strategy()
    s.run()