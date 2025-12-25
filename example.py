import time
import pygetwindow as gw
import pyautogui
import logging
from screen_automation import Keybind_Manager
from threading import Event
import math

#this script is used for playing a mobile game using an emulator. This game uses a joystick and this emulator is setted 
#for replicating an invisible joystick at center, that sends the input to the real joystick at a different position.
#the problem is that while playing, the cursor has no bound and can go anywhere, so it can be way off set and if you
#want to direct the joystick to the opposite direction, it takes too long and makes the experience very unpleasent

#this script resolves the issue by bounding the cursor into a circle, if it goes outside of it, it will be sent back.
#The condition for this to happen is that the game must be the current active window and the flag must be set, using
#a keybind

    


WindowName = "Brawlstars"
DistanceCenter_Percentage_HeightBased = 37

class Main:
    #flag for stopping all processes running
    Process = Event()
    Process.set()
    #flag for keybind to decleare whenever the cursor must be bounded to the circle
    InGame = Event()
    ScreenWidth, ScreenHeight = pyautogui.size()
    #getting middle point of the screen
    Middle_X = int(ScreenWidth / 2)
    Middle_Y = int(ScreenHeight / 2)
    
    def __init__(self, WindowName, DistanceCenter_Percentage_HeightBased, InGame_Keybind = 'v', Set_Cursor_Center_Keybind = 'middle_m'):
        #window name that must be case sensitive, so it checks if the active window has the same name
        self.WindowName = WindowName
        #used for the radius of the circle, based on the percentage of the current height of the screen
        self.DistanceCenter = DistanceCenter_Percentage_HeightBased
        self.InGame_Keybind = InGame_Keybind
        self.Set_Cursor_Center_Keybind = Set_Cursor_Center_Keybind
        #radius of the circle
        self.DistanceCenter = int(self.ScreenHeight / 100 * DistanceCenter_Percentage_HeightBased)
        self.LeftFurther_Edge = self.Middle_X - self.DistanceCenter  
        self.RightFurther_Edge = self.Middle_X + self.DistanceCenter  
        self.TopFurther_Edge = self.Middle_Y - self.DistanceCenter 
        self.BottomFurther_Edge = self.Middle_Y + self.DistanceCenter
        #list of all edge coords of the circle
        self.EdgeCoords = self.CircleEdge()
    
    def Start(self):
        KB = Keybind_Manager()
        KB.Upload_Keybind_Function(self.InGame_Keybind, self.Toggle_InGame)
        KB.Upload_Keybind_Function(self.Set_Cursor_Center_Keybind, self.Set_Cursor_Center)
        KB.Run_Listeners()
        
        logging.basicConfig(level=logging.INFO)
        logging.info(f"Waiting for {self.WindowName} to Start...")

        #waits for the window to appear
        while not self.Find_Window():
            time.sleep(0.7)

        logging.info(f"{self.WindowName} detected! Monitoring Started.")

        try:
            while self.Process.is_set():
                #if the window is in the list of running window
                if self.Find_Window():
                    #takes active window
                    ActiveWindow = gw.getActiveWindow()
                    #if there is a window active or is the same as WindowName set and the flag is set, it returns
                    #the cursor inside the circle
                    if ActiveWindow and ActiveWindow.title.strip() == self.WindowName and self.InGame.is_set():
                        x, y= pyautogui.position()
                        self.Return_Cursor_CircleEdge(x, y)
                else:
                    logging.info(f"{self.WindowName} closed. Exiting script.")
                    self.Process.clear()
                time.sleep(0.05)
        except Exception as E:
            logging.error(f"An error occurred: {E}")
        finally:
            logging.info("Script stopped.")
    
    def CircleEdge(self):
        """
        Returns a list of coordinates (x, y) of pixels on the edge of a circle.
        """
        Points = set()
        for Deg in range(360):
            Rad = math.radians(Deg)
            x = round(self.Middle_X + self.DistanceCenter * math.cos(Rad))
            y = round(self.Middle_Y + self.DistanceCenter * math.sin(Rad))
            Points.add((x, y))
        return sorted(Points)

    def Return_Cursor_CircleEdge(self, x: int, y: int):
        """
        If the point (x, y) is outside the circle with center (cx, cy) and radius `radius`,
        move the mouse to the nearest point on the edge.
        """
        dx = x - self.Middle_X
        dy = y - self.Middle_Y
        Distance = math.sqrt(dx*dx + dy*dy)

        # if the cursor is inside the circle, exit.
        if Distance <= self.DistanceCenter:
            return

        # if it's outside, it finds the closest coords between the cursor and the set of pixels
        Closest = min(self.EdgeCoords, key=lambda p: (p[0] - x)**2 + (p[1] - y)**2)
        pyautogui.moveTo(Closest[0], Closest[1])

    def Find_Window(self):
        #if the window is present in all windows, returns true
        return any(Title.strip() == self.WindowName for Title in gw.getAllTitles())

    def Toggle_InGame(self):
        #flag toggle used in keybind
        if self.InGame.is_set():
            self.InGame.clear()
            return
        self.InGame.set()

        
    def Set_Cursor_Center(self):
        #set the cursor to the middle
        pyautogui.moveTo(self.Middle_X, self.Middle_Y)
        
if __name__ == "__main__":
    Main(WindowName, DistanceCenter_Percentage_HeightBased).Start()
    
