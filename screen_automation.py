from pynput.keyboard import Controller as KeyboardController, Listener as KeyboardListener, Key, KeyCode
from pynput.mouse import Controller as MouseController, Listener as MouseListener, Button
import time
import threading
import os
import pyautogui
import shutil


class KeyNameNotFoundError(Exception):
    """Raised when a keyname is not found in either keyboard or mouse mappings"""
    def __init__(self, keyname):
        self.keyname = keyname
        super().__init__(f"Keyname '{keyname}' not found in keyboard or mouse mappings")
    
class KeyBind_Manager:
    _keyboard_buttons = {
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


    _mouse_buttons = {
        "left_m": Button.left,
        "right_m": Button.right,
        "middle_m": Button.middle
    }
    
    def __init__(self, on_key_press = True, on_click = True, on_move = False):
        """Set if necessary input behaviour you want to detect"""
        #here process is a global flag within the obj to shut down every process in case of using stop()
        self._process = threading.Event()
        #controller needed for pressing/releasing buttons
        self._Keyboard = KeyboardController()
        self._Mouse = MouseController()
        
        #this dict is needed for saving the function worker, so it can delete itself by the obj and easy to access
        self._FunctionName_FunctionWorker = {}
        #this dict is used in upload_keybind_function(), and to check if the button press in listeners are present here, 
        #at last it calls the function from _FunctionName_FunctionWorker
        self._KeyboardName_Function = {}
        self._MouseName_Function = {}

        #this flag is used in case the option _multiple_instances = false, if self != none, it send a message and doesn't start the function
        self._last_running_function = None
        #flag used for checking if the last pressed key is the one setted inside a function
        self._last_KeyboardKey_pressed = None
        self._last_MouseButton_pressed = None
        
        #flag to check if listener thread is running
        self._listener_thread = None
        
        self.start(on_key_press = on_key_press, on_click = on_click, on_move = on_move)
        
    def start(self, on_key_press = True, on_click = True, on_move = False):
        #listener thread meaning is to read all mouse/keyboard input
        if self._listener_thread and self._listener_thread.is_alive():
            self._process.clear()
            self._listener_thread.join()
        #set the process true, enable all function to run
        self._process.set()
        # Initialize keyboard and mouse button mappings
        self._keyboard_listener = KeyboardListener(
            on_press=self._on_key_press if on_key_press else None
        )
        
        self._mouse_listener = MouseListener(
            on_click=self._on_click if on_click else None,
            on_move=self._on_move if on_move else None
        )

        # Start listeners in a separate thread
        self._listener_thread = threading.Thread(target=self._run_listeners, daemon=True)
        self._listener_thread.start()

    def _run_listeners(self):
        """Run the listeners in a separate thread"""
        if self._keyboard_listener:
            self._keyboard_listener.start()
        if self._mouse_listener:
            self._mouse_listener.start()
        
        # Keep the thread alive and monitor for process state
        while self._process.is_set():
            time.sleep(0.05)

    def _on_key_press(self, key_obj):
        """Detect keyboard press"""
        #if the process isn't set, it doesn't start
        if not self._process.is_set():
            return None
        try:
            if hasattr(key_obj, 'char'):
                key_name = key_obj.char.lower()
            else:
                key_name = str(key_obj).replace('Key.', '').lower()
                
            self._last_KeyboardKey_pressed = key_name
            #checks if the key_name is associated into any function
            if key_name in self._KeyboardName_Function:
                function = self._KeyboardName_Function[key_name]
                #uses the function name as key for getting the worker, you have to be case sensitive if you want to access the function later
                if function.__name__ in self._FunctionName_FunctionWorker.keys():
                    func_worker = self._FunctionName_FunctionWorker[function.__name__]
                    func_worker.start_function()
                    print(f"Key pressed: {key_name}")
                
        except AttributeError:
            print(f"Special key pressed: {key_obj}")

    def _on_click(self, x, y, button_obj, pressed):
        #same principle as _on_key_press
        """Detect mouse click"""
        if not self._process.is_set():
            return None
        
        if pressed:
            # Convert Button.left to "left_m", Button.right to "right_m", etc.
            button_name = (str(button_obj).replace('Button.', '') + '_m').lower()
            self._last_MouseButton_pressed = button_name
            
            
            if button_name in self._MouseName_Function:
                function = self._MouseName_Function[button_name]
                if function.__name__ in self._FunctionName_FunctionWorker.keys():
                    func_worker = self._FunctionName_FunctionWorker[function.__name__]
                    func_worker.start_function()
                    print(f"Button pressed: {button_name}")

    def _on_move(self, x, y):
        """Detect mouse movement"""
        if not self._process.is_set():
            return False
        print(f"Mouse moved to ({x}, {y})")
    
    def upload_keybind_function(self, button_name, function, *args, multiple_instances = True, togglable=False, loop_delay=0.05):
        button_name = button_name.lower()
        #checks if the button it's either a mouse or keyboard one.
        if button_name in self._keyboard_buttons.keys():
            self._KeyboardName_Function[button_name] = function
        elif button_name in self._mouse_buttons.keys():
            self._MouseName_Function[button_name] = function
        else:
            raise KeyNameNotFoundError(button_name)
        
        #add key value into the dict
        self._FunctionName_FunctionWorker[function.__name__] = Function_Worker(self, function, *args, multiple_instances=multiple_instances, togglable=togglable, loop_delay=loop_delay)
        
    def button_click(self, button_name, delay = 0.1):
        button_name = button_name.lower()
        """Simulate a button click"""
        if not self._process.is_set():
            return None
        if button_name in self._mouse_buttons:
            time.sleep(delay)
            self._Mouse.click(self._mouse_buttons[button_name])
        elif button_name in self._keyboard_buttons:
            time.sleep(delay)
            self._Keyboard.press(self._keyboard_buttons[button_name])
            time.sleep(delay)
            self._Keyboard.release(self._keyboard_buttons[button_name])
        else:
            raise KeyNameNotFoundError(button_name)
        
    def show_mouse_buttons_name(self):
        """Print all available mouse button names"""
        print(self._mouse_buttons.keys())
    
    def show_Keyboard_buttons_name(self):
        """Print all available keyboard key names"""
        print(self._keyboard_buttons.keys())
        
    def press_MouseButton(self, button_name, delay = 0.1):
        button_name = button_name.lower()
        """Press and release a mouse button"""
        if not self._process.is_set():
            return None
        if button_name not in self._mouse_buttons:
            raise KeyNameNotFoundError(button_name)
        
        self._Mouse.press(self._mouse_buttons[button_name])
        time.sleep(delay)
        self._Mouse.release(self._mouse_buttons[button_name])
    
    def press_KeyboardKey(self, key_name, delay = 0.1):
        key_name = key_name.lower()
        """Press and release a keyboard key"""
        if not self._process.is_set():
            return None
        if key_name not in self._keyboard_buttons:
            raise KeyNameNotFoundError(key_name)
        
        self._Keyboard.press(self._keyboard_buttons[key_name])
        time.sleep(delay)
        self._Keyboard.release(self._keyboard_buttons[key_name])
       
    def stop(self):
        """Stop the automation and listeners"""
        self._process.clear()
        self._last_running_function = None
        if self._keyboard_listener:
            self._keyboard_listener.stop()
        if self._mouse_listener:
            self._mouse_listener.stop()
        # Wait for listener thread to finish
        if hasattr(self, '_listener_thread') and self._listener_thread.is_alive():
            self._listener_thread.join(timeout=5.0)
                
            
class Function_Worker():
    def __init__(self, keybind_manager, function, *args, multiple_instances = True, togglable=False, loop_delay=0.05):
        """Worker with multiple tools and option used inside KeyBind_Manager

        Args:
            keybind_manager (obj): keybind_manager used in global case needed
            function (function): function
            multiple_instances (bool, optional): set false if you want this thread to be the only one running, \
            if there are more, it doesn't start. Defaults to True.
            togglable (bool, optional): set true if you want the thread to be in loop, starting the function again \
            will stop it. Defaults to False.
            loop_delay (float, optional): Set delay between the function looping, togglable needs to be set true \
            for this to impact the code. Defaults to 0.05.
        """
        self._keybind_manager = keybind_manager
        self._function = function
        self._args = args
        self._multiple_instances = multiple_instances
        self._toggled = None
        self.loop_delay = loop_delay
        self._thread = None
        self._process = threading.Event()
        if togglable:
            self._toggled = False
 
           
    def start_function(self):
        #checks if _toggled is a bool, hence togglable set to true
        if isinstance(self._toggled, bool):
            self._process.set()
            #switch used for toogle _toggled between true and false
            self._toggled = not self._toggled
            #if _toggled is set to false, if the thread is alive, it clear(set false) the process, 
            #and waits the thread to finish, at the end it always exit the function
            if not self._toggled:
                if self._thread and self._thread.is_alive():
                    self._process.clear()
                    self._thread.join()
                    self._process.set()
                return
            #here if the function should start, if _multiple_instances == false and another function is running, 
            #it just switch again, resetting and exit the function
            if not self._multiple_instances and self._keybind_manager._last_running_function != self._function.__name__:
                self._toggled = not self._toggled
                return
            #thread with specific toggle wrapper started
            self._thread = threading.Thread(target=self._toggle_wrapper, daemon=True)
            self._thread.start()
        else:
            #(case if toggable was false) same check for running function as before
            if not self._multiple_instances and self._keybind_manager._last_running_function != self._function.__name__:
                print(f"Function: {self._keybind_manager._last_running_function} is already running. Can only run one function at time\n")
                return
            #check if the thread is still alive and exit the function
            elif self._thread and self._thread.is_alive():
                print("The function is already running, stop it or change it's behavior")
                return
            #thread started with normal wrapper (non toggable)
            self._thread = threading.Thread(target=self._wrapper, daemon=True)
            self._thread.start()
    
    def _toggle_wrapper(self):
        """Run the function in a loop when toggled"""
        #set the last running function as itself
        self._keybind_manager._last_running_function = self._function.__name__
        #loop with function
        while self._process.is_set():
            self._function(*self._args)
            time.sleep(self.loop_delay)
        #IMPORTANT for _multiple_instances to work, if the loop stops, 
        #if the last function is still itself, it changes the _last_running_function to none, 
        #stating that no other function is running
        if self._keybind_manager._last_running_function == self._function.__name__:
           self._keybind_manager._last_running_function = None
                                   
    def _wrapper(self):
        #same concept as the toggable wrapper, without the loop
        self._keybind_manager._last_running_function = self._function.__name__
        self._function(*self._args)
        if self._keybind_manager._last_running_function == self._function.__name__:
           self._keybind_manager._last_running_function = None
            
    def stop(self,):
        #clears(set false) the process
        self._process.clear()
    
    def delete(self):
        #IMPORTANT in order for this to work, no other refence should exist outside the dict
        #thats why you have so create the object inside the dict and can't do it inside the obj itself
        del self._keybind_manager._FunctionName_FunctionWorker[self._function.__name__]
    
        
            
class Screenshots_Regions():
    def __init__(self, screenshot_path, coords_path):
        """Obj with multiple tools for screenshots with regions, you can change the paths anytime when needed.

        Args:
            screenshot_path (str): folder path used in save_image_region() and ..._cursor(), for saving the image file (.png) with same name as coord file
            coords_path (str): folder path ..... for saving the region file (.txt) with same name as image file
        """
        self._process = threading.Event()
        self._process.set()
        self.screenshot_path = screenshot_path
        self.coords_path = coords_path
    
    def locate_image_with_region(self, path_image, region = (0, 0, 1920, 1080), confidence = 0.8):
        """Locate the given image with given screen region

        Args:
            path_image (str): path of the image
            region (tuple, optional): Box(tuple) with the following coords, left, top, width, height. Defaults to (0, 0, 1920, 1080).
            confidence (float, optional): Set the precision of the image required, value between 0-1. Defaults to 0.8.

        Returns:
            tuple: specific region at which the image was found
        """
        if not self._process.is_set():
            return None
        
        #checks if the path exist
        if not os.path.exists(path_image):
            print(f"Image file not found: {path_image}")
            return None
            
        try:
            #takes screenshot with the region
            zone_check = pyautogui.screenshot(region=region)
            #locates the image
            image_location = pyautogui.locate(path_image, zone_check, confidence=confidence)
            #if found
            if image_location:
                # Convert relative coordinates to absolute screen coordinates
                absolute_location = (
                    int(image_location.left + region[0]),  # Add region's left offset
                    int(image_location.top + region[1]),   # Add region's top offset
                    image_location.width,
                    image_location.height
                )
                print(f"Image found at: {absolute_location}")
                return absolute_location
            return None
            
        except Exception as e:
            print(f"Error locating image: {str(e)}")
            return None
    
    def save_image_region(self, keybind_manager, region, capture_key = 'space', exit_key = 'esc'):
        """Save both the image and region in the respected folder set when created the obj, \
            these file have the same name, so it can be used with locate_image_with_name().

        Args:
            keybind_manager (obj): keyboard_manager used in global file needed for catching the keybind
            region (tuple, optional): Box(tuple) with the following coords, left, top, width, height. Defaults to (0, 0, 1920, 1080).
            capture_key (str, optional): keybind to capture the image within the region set. Defaults to 'space'.
            exit_key (str, optional): To exit the function. Defaults to 'esc'.
        """
        capture_key = capture_key.lower()
        exit_key = exit_key.lower()
        
        #uploading the exit keybind
        keybind_manager.upload_keybind_function(exit_key, self.stop, togglable=False)
        
        while self._process.is_set():
            print(f'Press {exit_key.upper()} to exit the loop...')
            print(f"Press {capture_key.upper()} to capture...")
            
            #taking the single value of the region(box)
            left = region[0]
            top = region[1]
            width = region[2]
            height = region[3]
            
            #loops until the capture key has been pressed
            while self._process.is_set():
                if keybind_manager._last_KeyboardKey_pressed == capture_key:
                    keybind_manager._last_KeyboardKey_pressed = None
                    time.sleep(0.5)
                    break
                time.sleep(0.05)
                
            #makes the screenshot
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            
            #set the name for both files
            print("Insert screenshot name:")
            base_filename = input()
    
            screenshot_filename = base_filename + ".png"
            # Save the screenshot
            screenshot.save(screenshot_filename)
            
            # Save coordinates to text file
            region_filename = f"{base_filename}.txt"
            with open(region_filename, 'w') as f:
                f.write(f"{left}, {top}, {width}, {height}")

            # Create directories if they don't exist
            os.makedirs(self.screenshot_path, exist_ok=True)
            os.makedirs(self.coords_path, exist_ok=True)

            #moves the file into the folders
            shutil.move(screenshot_filename, self.screenshot_path)
            shutil.move(region_filename, self.coords_path)
            
            print(f"\nScreenshot saved as: {screenshot_filename}")
            print(f"Coordinates saved as: {region_filename}")
            
        
    def save_image_region_cursor(self, keybind_manager, capture_key = 'space', exit_key = 'esc'):
        """Save both the image and region in the respected folder set when created the obj, \
            these file have the same name, so it can be used with locate_image_with_name(). \
            First you capture the top left, then the bottom right of the region with the capture key.

        Args:
            keybind_manager (obj): keyboard_manager used in global file needed for catching the keybind
            capture_key (str, optional): keybind to capture first the top left, then the top right \
            region. Defaults to 'space'.
            exit_key (str, optional): To exit the function. Defaults to 'esc'.
        """
        capture_key = capture_key.lower()
        exit_key = exit_key.lower()
        
        self._process.set()
        
        keybind_manager.upload_keybind_function(exit_key, self.stop, togglable=True)
        
        while self._process.is_set():
            print(f'Press {exit_key.upper()} to exit the loop...')
            print(f"Move your mouse to the desired position and press {capture_key.upper()} to capture...")

            #capture top left
            while self._process.is_set():
                if keybind_manager._last_KeyboardKey_pressed == capture_key:
                    left, top = pyautogui.position()
                    print(f"Top-left position captured: ({left}, {top})")
                    keybind_manager._last_KeyboardKey_pressed = None
                    time.sleep(0.5)
                    break
                time.sleep(0.05)
            #capture bottom right
            while self._process.is_set():
                if keybind_manager._last_KeyboardKey_pressed == capture_key:
                    right, bottom = pyautogui.position()
                    print(f"Right-Bottom position captured: ({right}, {bottom})")
                    keybind_manager._last_KeyboardKey_pressed = None
                    time.sleep(0.5)
                    break
                time.sleep(0.05)
    
            if not self._process.is_set():
                break
            
            #calculatet the width and height
            width = right - left
            height = bottom - top
            
            #if the coords saved didn't follow the top left bottom right procedures, it fails and start over
            if width <= 0 or height <= 0:
                print("Invalid region size. Please try again.")
                continue
            

            
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            
            #same concept as save_image_region()
            print("Insert screenshot name:")
            base_filename = input()
            keybind_manager._last_KeyboardKey_pressed = None
    
            screenshot_filename = base_filename + ".png"
            # Save the screenshot
            screenshot.save(screenshot_filename)
            
            # Save coordinates to text file
            region_filename = f"{base_filename}.txt"
            with open(region_filename, 'w') as f:
                f.write(f"{left}, {top}, {width}, {height}")

            # Create directories if they don't exist
            os.makedirs(self.screenshot_path, exist_ok=True)
            os.makedirs(self.coords_path, exist_ok=True)

            shutil.move(screenshot_filename, self.screenshot_path)
            shutil.move(region_filename, self.coords_path)
            
            print(f"\nScreenshot saved as: {screenshot_filename}")
            print(f"Coordinates saved as: {region_filename}")
        
                  
    def locate_image_with_name(self, file_name, confidence = 0.9):
        """Locate the image, using the same file_name for both image and coords.

        Args:
            file_name (str): name of both image and coords saved in the folders path setted during the creation of the obj itself
            confidence (float, optional): Set the precision of the image required, value between 0-1. Defaults to 0.9.

        Returns:
            method: locate_image_with_region() using both images and coords
        """
        try:
            with open(rf'{self.coords_path}\{file_name}.txt', 'r') as file:
                content = file.read()
                region_str = content.strip().split(',')
                region = tuple(int(n.strip()) for n in region_str)
            
            return self.locate_image_with_region(
                rf'{self.screenshot_path}\{file_name}.png',
                region=region,
                confidence=confidence
            )
        except FileNotFoundError:
            print(f"Could not find region file for {file_name}")
            return None
        except ValueError:
            print(f"Invalid region data in file for {file_name}")
            return None
    
    def stop(self):
        self._process.clear()