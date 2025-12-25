from pynput.keyboard import Controller as KeyboardController, Listener as KeyboardListener, Key, KeyCode
from pynput.mouse import Controller as MouseController, Listener as MouseListener, Button
import time
import threading
import os
import pyautogui
import shutil


class KeyNameNotFoundError(Exception):
    """Raised when a keyname is not found in either keyboard or mouse mappings"""
    def __init__(self, KeyName):
        super().__init__(f"Keyname '{KeyName}' not found in keyboard or mouse mappings")
    
class Keybind_Manager:
    _KeyboardButtons = {
        # Tasti speciali
        "alt": Key.alt,
        "alt_l": Key.alt_l,
        "alt_r": Key.alt_r,
        "backspace": Key.backspace,
        "caps_lock": Key.caps_lock,
        "cmd": Key.cmd,
        "cmd_l": Key.cmd_l,
        "cmd_r": Key.cmd_r,
        "ctrl": Key.ctrl,
        "ctrl_l": Key.ctrl_l,
        "ctrl_r": Key.ctrl_r,
        "delete": Key.delete,
        "down": Key.down,
        "end": Key.end,
        "enter": Key.enter,
        "esc": Key.esc,
        "f1": Key.f1,
        "f2": Key.f2,
        "f3": Key.f3,
        "f4": Key.f4,
        "f5": Key.f5,
        "f6": Key.f6,
        "f7": Key.f7,
        "f8": Key.f8,
        "f9": Key.f9,
        "f10": Key.f10,
        "f11": Key.f11,
        "f12": Key.f12,
        "home": Key.home,
        "insert": Key.insert,
        "left": Key.left,
        "page_down": Key.page_down,
        "page_up": Key.page_up,
        "right": Key.right,
        "shift": Key.shift,
        "shift_l": Key.shift_l,
        "shift_r": Key.shift_r,
        "space": Key.space,
        "tab": Key.tab,
        "up": Key.up,

        # Tasti alfanumerici (usano KeyCode)
        "a": KeyCode.from_char('a'),
        "b": KeyCode.from_char('b'),
        "c": KeyCode.from_char('c'),
        "d": KeyCode.from_char('d'),
        "e": KeyCode.from_char('e'),
        "f": KeyCode.from_char('f'),
        "g": KeyCode.from_char('g'),
        "h": KeyCode.from_char('h'),
        "i": KeyCode.from_char('i'),
        "j": KeyCode.from_char('j'),
        "k": KeyCode.from_char('k'),
        "l": KeyCode.from_char('l'),
        "m": KeyCode.from_char('m'),
        "n": KeyCode.from_char('n'),
        "o": KeyCode.from_char('o'),
        "p": KeyCode.from_char('p'),
        "q": KeyCode.from_char('q'),
        "r": KeyCode.from_char('r'),
        "s": KeyCode.from_char('s'),
        "t": KeyCode.from_char('t'),
        "u": KeyCode.from_char('u'),
        "v": KeyCode.from_char('v'),
        "w": KeyCode.from_char('w'),
        "x": KeyCode.from_char('x'),
        "y": KeyCode.from_char('y'),
        "z": KeyCode.from_char('z'),

        "0": KeyCode.from_char('0'),
        "1": KeyCode.from_char('1'),
        "2": KeyCode.from_char('2'),
        "3": KeyCode.from_char('3'),
        "4": KeyCode.from_char('4'),
        "5": KeyCode.from_char('5'),
        "6": KeyCode.from_char('6'),
        "7": KeyCode.from_char('7'),
        "8": KeyCode.from_char('8'),
        "9": KeyCode.from_char('9'),

        # Simboli comuni
        "comma": KeyCode.from_char(','),
        "dot": KeyCode.from_char('.'),
        "slash": KeyCode.from_char('/'),
        "backslash": KeyCode.from_char('\\'),
        "semicolon": KeyCode.from_char(';'),
        "quote": KeyCode.from_char('\''),
        "bracket_left": KeyCode.from_char('['),
        "bracket_right": KeyCode.from_char(']'),
        "minus": KeyCode.from_char('-'),
        "equals": KeyCode.from_char('='),
        "space_char": KeyCode.from_char(' '),
    }


    _MouseButtons = {
        "left_m": Button.left,
        "right_m": Button.right,
        "middle_m": Button.middle
    }
    
    def __init__(self):
        """run the method Run_Listeners() to start"""
        #here process is a global flag within the obj to shut down every process in case of using Stop()
        self._Process = threading.Event()
        #controller needed for pressing/releasing buttons
        self._Keyboard = KeyboardController()
        self._Mouse = MouseController()
        
        #this dict is needed for saving the Function worker, so it can delete itself by the obj and easy to access
        self._FunctionName_FunctionWorker = {}
        #this dict is used in Upload_Keybind_Function(), and to check if the button press in listeners are present here, 
        #at last it calls the Function from _FunctionName_FunctionWorker
        self._KeyboardName_Function = {}
        self._MouseName_Function = {}

        #this flag is used in case the option _MultipleInstances = false, if self != none, it send a message and doesn't start the Function
        self._Current_Running_Function = None
        #flag used for checking if the last pressed key is the one setted inside a Function
        self._Last_KeyboardInput = None
        self._Last_MouseInput = None
        
        #flag to check if listener thread is running
        self._Listener_Thread = None
        
        
    def Run_Listeners(self, KeyboardInput = True, MouseInput = True, MouseMovement = False):
        """it start the listeners of which will detect various input depending on the flags set

        Args:
            KeyboardInput (bool, optional): detect keyboard input. Defaults to True.
            MouseInput (bool, optional): detect mouse input. Defaults to True.
            MouseMovement (bool, optional): detect mouse movement. Defaults to False.
        """
        #listener thread meaning is to read all mouse/keyboard input
        if self._Listener_Thread and self._Listener_Thread.is_alive():
            self._Process.clear()
            self._Listener_Thread.join()
        #set the process true, enable all Function to run
        self._Process.set()
        # Initialize keyboard and mouse button mappings
        self._KeyboardListener = KeyboardListener(
            on_press=self._On_KeyboardInput if KeyboardInput else None
        )
        
        self._MouseListener = MouseListener(
            on_click=self._On_MouseInput if MouseInput else None,
            on_move=self._On_MouseMovement if MouseMovement else None
        )

        # Start listeners in a separate thread
        self._Listener_Thread = threading.Thread(target=self._Wrapper_Run_Listeners, daemon=True)
        self._Listener_Thread.start()

    def _Wrapper_Run_Listeners(self):
        """Run the listeners in a separate thread"""
        if self._KeyboardListener:
            self._KeyboardListener.start()
        if self._MouseListener:
            self._MouseListener.start()
        
        # Keep the thread alive and monitor for process state
        while self._Process.is_set():
            time.sleep(0.05)

    def _On_KeyboardInput(self, KeyObject):
        """Detect keyboard press"""
        #if the process isn't set, it doesn't start
        if not self._Process.is_set():
            return None
        try:
            if hasattr(KeyObject, 'char') and KeyObject.char is not None:
                KeyName = KeyObject.char.lower()
            else:
                KeyName = str(KeyObject).replace('Key.', '').lower()
                
            self._Last_KeyboardInput = KeyName
            #checks if the KeyName is associated into any Function
            if KeyName in self._KeyboardName_Function:
                Function = self._KeyboardName_Function[KeyName]
                #uses the Function name as key for getting the worker, you have to be case sensitive if you want to access the Function later
                if Function.__name__ in self._FunctionName_FunctionWorker.keys():
                    FunctionWorker = self._FunctionName_FunctionWorker[Function.__name__]
                    FunctionWorker.Start()
                    print(f"Key pressed: {KeyName}")
                
        except AttributeError:
            print(f"Special key pressed: {KeyObject}")

    def _On_MouseInput(self, x, y, KeyObject, Pressed):
        #same principle as _On_KeyboardInput
        """Detect mouse click"""
        if not self._Process.is_set():
            return None
        
        if Pressed:
            # Convert Button.left to "left_m", Button.right to "right_m", etc.
            KeyName = (str(KeyObject).replace('Button.', '') + '_m').lower()
            self._Last_MouseInput = KeyName
            
            
            if KeyName in self._MouseName_Function:
                Function = self._MouseName_Function[KeyName]
                if Function.__name__ in self._FunctionName_FunctionWorker.keys():
                    FunctionWorker = self._FunctionName_FunctionWorker[Function.__name__]
                    FunctionWorker.Start()
                    print(f"Button pressed: {KeyName}")

    def _On_MouseMovement(self, x, y):
        """Detect mouse movement"""
        if not self._Process.is_set():
            return False
        print(f"Mouse moved to ({x}, {y})")
    
    def Upload_Keybind_Function(self, KeyName, Function, *Args, MultipleInstances = True, Toggable=False, LoopDelay=0.05):
        KeyName = KeyName.lower()
        #checks if the button it's either a mouse or keyboard one.
        if KeyName in self._KeyboardButtons.keys():
            self._KeyboardName_Function[KeyName] = Function
        elif KeyName in self._MouseButtons.keys():
            self._MouseName_Function[KeyName] = Function
        else:
            raise KeyNameNotFoundError(KeyName)
        
        #add key value into the dict
        self._FunctionName_FunctionWorker[Function.__name__] = Function_Worker(self, Function, *Args, MultipleInstances=MultipleInstances, Toggable=Toggable, LoopDelay=LoopDelay)
        
    def ButtonClick(self, Key, delay = 0.1):
        Key = Key.lower()
        """Simulate a button click"""
        if not self._Process.is_set():
            return None
        if Key in self._MouseButtons:
            time.sleep(delay)
            self._Mouse.click(self._MouseButtons[Key])
        elif Key in self._KeyboardButtons:
            time.sleep(delay)
            self._Keyboard.press(self._KeyboardButtons[Key])
            time.sleep(delay)
            self._Keyboard.release(self._KeyboardButtons[Key])
        else:
            raise KeyNameNotFoundError(Key)
        
    def Show_MouseButtons(self):
        """Print all available mouse button names"""
        print(self._MouseButtons.keys())
    
    def Show_KeyboardButtons(self):
        """Print all available keyboard key names"""
        print(self._KeyboardButtons.keys())
        
    def Press_MouseButton(self, Key, delay = 0.1):
        Key = Key.lower()
        """Press and release a mouse button"""
        if not self._Process.is_set():
            return None
        if Key not in self._MouseButtons:
            raise KeyNameNotFoundError(Key)
        
        self._Mouse.press(self._MouseButtons[Key])
        time.sleep(delay)
        self._Mouse.release(self._MouseButtons[Key])
    
    def Press_KeyboardButton(self, KeyName, Delay = 0.1):
        KeyName = KeyName.lower()
        """Press and release a keyboard key"""
        if not self._Process.is_set():
            return None
        if KeyName not in self._KeyboardButtons:
            raise KeyNameNotFoundError(KeyName)
        
        self._Keyboard.press(self._KeyboardButtons[KeyName])
        time.sleep(Delay)
        self._Keyboard.release(self._KeyboardButtons[KeyName])
       
    def Stop(self):
        """Stop the automation and listeners"""
        self._Process.clear()
        self._Current_Running_Function = None
        if self._KeyboardListener:
            self._KeyboardListener.Stop()
        if self._MouseListener:
            self._MouseListener.Stop()
        # Wait for listener thread to finish
        if hasattr(self, '_Listener_Thread') and self._Listener_Thread.is_alive():
            self._Listener_Thread.join(timeout=5.0)
                
            
class Function_Worker():
    def __init__(self, Keybind_Manager, Function, *Args, MultipleInstances = True, Toggable=False, LoopDelay=0.05):
        """Worker with multiple tools and option used inside Keybind_Manager

        Args:
            Keybind_Manager (obj): Keybind_Manager used in global case needed
            Function (Function): Function
            MultipleInstances (bool, optional): set false if you want this thread to be the only one running, \
            if there are more, it doesn't start. Defaults to True.
            Toggable (bool, optional): set true if you want the thread to be in loop, starting the Function again \
            will Stop it. Defaults to False.
            LoopDelay (float, optional): Set delay between the Function looping, Toggable needs to be set true \
            for this to impact the code. Defaults to 0.05.
        """
        self._Keybind_Manager = Keybind_Manager
        self._Function = Function
        self._Args = Args
        self._MultipleInstances = MultipleInstances
        self._Toggled = None
        self.LoopDelay = LoopDelay
        self._Thread = None
        self._Process = threading.Event()
        if Toggable:
            self._Toggled = False
 
           
    def Start(self):
        #checks if _Toggled is a bool, hence Toggable set to true
        if isinstance(self._Toggled, bool):
            self._Process.set()
            #switch used for toogle _Toggled between true and false
            self._Toggled = not self._Toggled
            #if _Toggled is set to false, if the thread is alive, it clear(set false) the process, 
            #and waits the thread to finish, at the end it always exit the Function
            if not self._Toggled:
                if self._Thread and self._Thread.is_alive():
                    self._Process.clear()
                    self._Thread.join()
                    self._Process.set()
                return
            #here if the Function should start, if _MultipleInstances == false and another Function is running, 
            #it just switch again, resetting and exit the Function
            if not self._MultipleInstances and self._Keybind_Manager._Current_Running_Function != self._Function.__name__:
                self._Toggled = not self._Toggled
                return
            #thread with specific toggle wrapper started
            self._Thread = threading.Thread(target=self._Wrapper_ToggleCase, daemon=True)
            self._Thread.start()
        else:
            #(case if toggable was false) same check for running Function as before
            if not self._MultipleInstances and self._Keybind_Manager._Current_Running_Function != self._Function.__name__:
                print(f"Function: {self._Keybind_Manager._Current_Running_Function} is already running. Can only run one Function at time\n")
                return
            #check if the thread is still alive and exit the Function
            elif self._Thread and self._Thread.is_alive():
                print("The Function is already running, Stop it or change it's behavior")
                return
            #thread started with normal wrapper (non toggable)
            self._Thread = threading.Thread(target=self._Wrapper_Non_ToggleCase, daemon=True)
            self._Thread.start()
    
    def _Wrapper_ToggleCase(self):
        """Run the Function in a loop when toggled"""
        #set the last running Function as itself
        self._Keybind_Manager._Current_Running_Function = self._Function.__name__
        #loop with Function
        while self._Process.is_set():
            self._Function(*self._Args)
            time.sleep(self.LoopDelay)
        #IMPORTANT for _MultipleInstances to work, if the loop Stops, 
        #if the last Function is still itself, it changes the _Current_Running_Function to none, 
        #stating that no other Function is running
        if self._Keybind_Manager._Current_Running_Function == self._Function.__name__:
           self._Keybind_Manager._Current_Running_Function = None
                                   
    def _Wrapper_Non_ToggleCase(self):
        #same concept as the toggable wrapper, without the loop
        self._Keybind_Manager._Current_Running_Function = self._Function.__name__
        self._Function(*self._Args)
        if self._Keybind_Manager._Current_Running_Function == self._Function.__name__:
           self._Keybind_Manager._Current_Running_Function = None
            
    def Stop(self):
        #clears(set false) the process
        self._Process.clear()
    
    def Delete(self):
        #IMPORTANT in order for this to work, no other refence should exist outside the dict
        #thats why you have so create the object inside the dict and can't do it inside the obj itself
        del self._Keybind_Manager._FunctionName_FunctionWorker[self._Function.__name__]
    
        
            
class Screenshots_Regions():
    def __init__(self, ScreenshotPath, CoordsPath):
        """Obj with multiple tools for screenshots with Regions, you can change the paths anytime when needed.

        Args:
            ScreenshotPath (str): folder path used in save_image_Region() and ..._cursor(), for saving the image file (.png) with same name as coord file
            CoordsPath (str): folder path ..... for saving the Region file (.txt) with same name as image file
        """
        self._Process = threading.Event()
        self._Process.set()
        self.ScreenshotPath = ScreenshotPath
        self.CoordsPath = CoordsPath
    
    def Locate_Image_StaticRegion(self, ImagePath, Region = (0, 0, 1920, 1080), Confidence = 0.8):
        """Locate the given image with given screen Region

        Args:
            ImagePath (str): path of the image
            Region (tuple, optional): Box(tuple) with the following coords, left, top, width, height. Defaults to (0, 0, 1920, 1080).
            Confidence (float, optional): Set the precision of the image required, value between 0-1. Defaults to 0.8.

        Returns:
            tuple: specific Region at which the image was found
        """
        if not self._Process.is_set():
            return None
        
        #checks if the path exist
        if not os.path.exists(ImagePath):
            print(f"Image file not found: {ImagePath}")
            return None
            
        try:
            #takes screenshot with the Region
            Screenshot = pyautogui.screenshot(Region=Region)
            #locates the image
            ImageLocation = pyautogui.locate(ImagePath, Screenshot, Confidence=Confidence)
            #if found
            if ImageLocation:
                # Convert relative coordinates to absolute screen coordinates
                AbsoluteLocation = (
                    int(ImageLocation.left + Region[0]),  # Add Region's left offset
                    int(ImageLocation.top + Region[1]),   # Add Region's top offset
                    ImageLocation.width,
                    ImageLocation.height
                )
                print(f"Image found at: {AbsoluteLocation}")
                return AbsoluteLocation
            return None
            
        except Exception as e:
            print(f"Error locating image: {str(e)}")
            return None
    
    def Save_Image_Region_Files(self, Keybind_Manager, Region, CaptureKey = 'space', ExitKey = 'esc'):
        """Save both the image and Region in the respected folder set when created the obj, \
            these file have the same name, so it can be used with Locate_Image_With_Name().

        Args:
            Keybind_Manager (obj): keyboard_manager used in global file needed for catching the keybind
            Region (tuple, optional): Box(tuple) with the following coords, left, top, width, height. Defaults to (0, 0, 1920, 1080).
            CaptureKey (str, optional): keybind to capture the image within the Region set. Defaults to 'space'.
            ExitKey (str, optional): To exit the Function. Defaults to 'esc'.
        """
        CaptureKey = CaptureKey.lower()
        ExitKey = ExitKey.lower()
        
        #uploading the exit keybind
        Keybind_Manager.Upload_Keybind_Function(ExitKey, self.Stop, Toggable=False)
        
        while self._Process.is_set():
            print(f'Press {ExitKey.upper()} to exit the loop...')
            print(f"Press {CaptureKey.upper()} to capture...")
            
            #taking the single value of the Region(box)
            Left = Region[0]
            Top = Region[1]
            Width = Region[2]
            Height = Region[3]
            
            #loops until the capture key has been pressed
            while self._Process.is_set():
                if Keybind_Manager._Last_KeyboardInput == CaptureKey:
                    Keybind_Manager._Last_KeyboardInput = None
                    time.sleep(0.5)
                    break
                time.sleep(0.05)
                
            #makes the screenshot
            Screenshot = pyautogui.screenshot(Region=(Left, Top, Width, Height))
            
            #set the name for both files
            print("Insert screenshot name:")
            Base_FileName = input()
    
            Screenshot_FileName = Base_FileName + ".png"
            # Save the screenshot
            Screenshot.save(Screenshot_FileName)
            
            # Save coordinates to text file
            Region_filename = f"{Base_FileName}.txt"
            with open(Region_filename, 'w') as f:
                f.write(f"{Left}, {Top}, {Width}, {Height}")

            # Create directories if they don't exist
            os.makedirs(self.ScreenshotPath, exist_ok=True)
            os.makedirs(self.CoordsPath, exist_ok=True)

            #moves the file into the folders
            shutil.move(Screenshot_FileName, self.ScreenshotPath)
            shutil.move(Region_filename, self.CoordsPath)
            
            print(f"\nScreenshot saved as: {Screenshot_FileName}")
            print(f"Coordinates saved as: {Region_filename}")
            
        
    def Save_Image_Region_Files_CursorPosition(self, Keybind_Manager, CaptureKey = 'space', ExitKey = 'esc'):
        """Save both the image and Region in the respected folder set when created the obj, \
            these file have the same name, so it can be used with Locate_Image_With_Name(). \
            First you capture the top left, then the bottom right of the Region with the capture key.

        Args:
            Keybind_Manager (obj): keyboard_manager used in global file needed for catching the keybind
            CaptureKey (str, optional): keybind to capture first the top left, then the top right \
            Region. Defaults to 'space'.
            ExitKey (str, optional): To exit the Function. Defaults to 'esc'.
        """
        CaptureKey = CaptureKey.lower()
        ExitKey = ExitKey.lower()
        
        self._Process.set()
        
        Keybind_Manager.Upload_Keybind_Function(ExitKey, self.Stop, Toggable=True)
        
        while self._Process.is_set():
            print(f'Press {ExitKey.upper()} to exit the loop...')
            print(f"Move your mouse to the desired position and press {CaptureKey.upper()} to capture...")

            #capture top left
            while self._Process.is_set():
                if Keybind_Manager._Last_KeyboardInput == CaptureKey:
                    Left, Top = pyautogui.position()
                    print(f"Top-Left position captured: ({Left}, {Top})")
                    Keybind_Manager._Last_KeyboardInput = None
                    time.sleep(0.5)
                    break
                time.sleep(0.05)
            #capture bottom right
            while self._Process.is_set():
                if Keybind_Manager._Last_KeyboardInput == CaptureKey:
                    Right, Bottom = pyautogui.position()
                    print(f"Right-Bottom position captured: ({Right}, {Bottom})")
                    Keybind_Manager._Last_KeyboardInput = None
                    time.sleep(0.5)
                    break
                time.sleep(0.05)
    
            if not self._Process.is_set():
                break
            
            #calculatet the width and height
            Width = Right - Left
            Height = Bottom - Top
            
            #if the coords saved didn't follow the top left bottom right procedures, it fails and start over
            if Width <= 0 or Height <= 0:
                print("Invalid Region size. Please try again.")
                continue
            

            
            Screenshot = pyautogui.screenshot(Region=(Left, Top, Width, Height))
            
            #same concept as save_image_Region()
            print("Insert screenshot name:")
            Base_FileName = input()
            Keybind_Manager._Last_KeyboardInput = None
    
            Screenshot_FileName = Base_FileName + ".png"
            # Save the screenshot
            Screenshot.save(Screenshot_FileName)
            
            # Save coordinates to text file
            Region_filename = f"{Base_FileName}.txt"
            with open(Region_filename, 'w') as f:
                f.write(f"{Left}, {Top}, {Width}, {Height}")

            # Create directories if they don't exist
            os.makedirs(self.ScreenshotPath, exist_ok=True)
            os.makedirs(self.CoordsPath, exist_ok=True)

            shutil.move(Screenshot_FileName, self.ScreenshotPath)
            shutil.move(Region_filename, self.CoordsPath)
            
            print(f"\nScreenshot saved as: {Screenshot_FileName}")
            print(f"Coordinates saved as: {Region_filename}")
        
                  
    def Locate_Image_With_Name(self, FileName, Confidence = 0.9):
        """Locate the image, using the same FileName for both image and coords.

        Args:
            FileName (str): name of both image and coords saved in the folders path setted during the creation of the obj itself
            Confidence (float, optional): Set the precision of the image required, value between 0-1. Defaults to 0.9.

        Returns:
            method: Locate_Image_StaticRegion() using both images and coords
        """
        try:
            with open(rf'{self.CoordsPath}\{FileName}.txt', 'r') as File:
                Content = File.read()
                Region_str = Content.strip().split(',')
                Region = tuple(int(n.strip()) for n in Region_str)
            
            return self.Locate_Image_StaticRegion(
                rf'{self.ScreenshotPath}\{FileName}.png',
                Region=Region,
                Confidence=Confidence
            )
        except FileNotFoundError:
            print(f"Could not find Region file for {FileName}")
            return None
        except ValueError:
            print(f"Invalid Region data in file for {FileName}")
            return None
    
    def Stop(self):
        self._Process.clear()
