# Screen Automation Module

A Python module for keyboard/mouse automation, keybind management, and screenshot-based image location.

## Features

- **Keybind Management**: Register functions to keyboard/mouse inputs
- **Input Simulation**: Programmatically press keys and click mouse buttons
- **Screenshot Capture**: Capture screen regions and save coordinates
- **Image Location**: Find images on screen using template matching
- **Threading Support**: Run functions in separate threads with toggle/loop options

## Dependencies

```bash
pip install pynput pyautogui
```

## Classes

### `Keybind_Manager`

Manages keyboard and mouse input listeners and keybind-to-function mappings.

#### Methods

##### `__init__()`
Initialize the keybind manager. **Important**: Call `Run_Listeners()` after initialization to start listening.

##### `Run_Listeners(KeyboardInput=True, MouseInput=True, MouseMovement=False)`
Start input listeners.

**Parameters:**
- `KeyboardInput` (bool): Enable keyboard input detection (default: True)
- `MouseInput` (bool): Enable mouse click detection (default: True)
- `MouseMovement` (bool): Enable mouse movement detection (default: False)

##### `Upload_Keybind_Function(KeyName, Function, *Args, MultipleInstances=True, Toggable=False, LoopDelay=0.05)`
Register a function to a keybind.

**Parameters:**
- `KeyName` (str): Key name (see "Supported Keys" below)
- `Function`: Function to call when keybind is pressed
- `*Args`: Arguments to pass to the function
- `MultipleInstances` (bool): Allow multiple instances to run simultaneously (default: True)
- `Toggable` (bool): Enable toggle mode - pressing again stops the function (default: False)
- `LoopDelay` (float): Delay between function calls when `Toggable=True` (default: 0.05)

**Raises:**
- `KeyNameNotFoundError`: If key name is not recognized

##### `ButtonClick(Key, delay=0.1)`
Simulate a button click (keyboard or mouse).

**Parameters:**
- `Key` (str): Key name to click
- `delay` (float): Delay before clicking (default: 0.1)

##### `Press_KeyboardButton(KeyName, Delay=0.1)`
Press and release a keyboard key.

##### `Press_MouseButton(Key, delay=0.1)`
Press and release a mouse button.

##### `Show_KeyboardButtons()`
Print all available keyboard key names.

##### `Show_MouseButtons()`
Print all available mouse button names.

##### `Stop()`
Stop all listeners and automation.

### `Function_Worker`

Internal class that manages function execution in threads. Created automatically by `Keybind_Manager`.

### `Screenshots_Regions`

Manages screenshot capture and image location using template matching.

#### Methods

##### `__init__(ScreenshotPath, CoordsPath)`
Initialize with paths for saving screenshots and coordinate files.

**Parameters:**
- `ScreenshotPath` (str): Folder path for saving screenshot images (.png)
- `CoordsPath` (str): Folder path for saving coordinate files (.txt)

##### `Locate_Image_StaticRegion(ImagePath, Region=(0, 0, 1920, 1080), Confidence=0.8)`
Find an image within a screen region.

**Parameters:**
- `ImagePath` (str): Path to the image file
- `Region` (tuple): Screen region as (left, top, width, height) (default: full screen)
- `Confidence` (float): Matching confidence 0-1 (default: 0.8)

**Returns:**
- `tuple`: (left, top, width, height) of found image, or `None` if not found

##### `Locate_Image_With_Name(FileName, Confidence=0.9)`
Find an image using saved screenshot and coordinate files.

**Parameters:**
- `FileName` (str): Base name (without extension) of image and coordinate files
- `Confidence` (float): Matching confidence 0-1 (default: 0.9)

**Returns:**
- `tuple`: (left, top, width, height) of found image, or `None` if not found

##### `Save_Image_Region_Files(Keybind_Manager, Region, CaptureKey='space', ExitKey='esc')`
Capture and save a screenshot with its coordinates.

**Parameters:**
- `Keybind_Manager`: Keybind manager instance
- `Region` (tuple): Screen region as (left, top, width, height)
- `CaptureKey` (str): Key to press to capture (default: 'space')
- `ExitKey` (str): Key to press to exit (default: 'esc')

##### `Save_Image_Region_Files_CursorPosition(Keybind_Manager, CaptureKey='space', ExitKey='esc')`
Capture screenshot by selecting region with cursor.

**Parameters:**
- `Keybind_Manager`: Keybind manager instance
- `CaptureKey` (str): Key to press to mark top-left, then bottom-right corners
- `ExitKey` (str): Key to press to exit (default: 'esc')

##### `Stop()`
Stop screenshot capture operations.

## Supported Keys

### Keyboard Keys

**Special Keys:**
- `alt`, `alt_l`, `alt_r`
- `backspace`, `caps_lock`
- `cmd`, `cmd_l`, `cmd_r`
- `ctrl`, `ctrl_l`, `ctrl_r`
- `delete`, `down`, `end`, `enter`, `esc`
- `f1` through `f12`
- `home`, `insert`
- `left`, `page_down`, `page_up`, `right`
- `shift`, `shift_l`, `shift_r`
- `space`, `tab`, `up`

**Alphanumeric:**
- `a` through `z`
- `0` through `9`

**Symbols:**
- `comma`, `dot`, `slash`, `backslash`
- `semicolon`, `quote`
- `bracket_left`, `bracket_right`
- `minus`, `equals`, `space_char`

### Mouse Buttons

- `left_m` - Left mouse button
- `right_m` - Right mouse button
- `middle_m` - Middle mouse button

## Usage Examples

### Basic Keybind Setup

```python
from screen_automation import Keybind_Manager

def my_function():
    print("Function called!")

KB = Keybind_Manager()
KB.Upload_Keybind_Function('f1', my_function)
KB.Run_Listeners()

# Keep script running
import time
time.sleep(60)
KB.Stop()
```

### Toggle Function

```python
def toggle_function():
    print("Running...")

KB = Keybind_Manager()
KB.Upload_Keybind_Function('v', toggle_function, Toggable=True, LoopDelay=0.1)
KB.Run_Listeners()
```

### Screenshot Capture

```python
from screen_automation import Keybind_Manager, Screenshots_Regions

KB = Keybind_Manager()
KB.Run_Listeners()

screenshots = Screenshots_Regions('photos', 'photos_position')
# Capture region using cursor position
screenshots.Save_Image_Region_Files_CursorPosition(KB)
```

### Image Location

```python
screenshots = Screenshots_Regions('photos', 'photos_position')

# Find image using saved files
location = screenshots.Locate_Image_With_Name('play-button')
if location:
    print(f"Found at: {location}")

# Find image with custom region
location = screenshots.Locate_Image_StaticRegion(
    'path/to/image.png',
    Region=(100, 100, 800, 600),
    Confidence=0.9
)
```

### Simulate Input

```python
KB = Keybind_Manager()
KB.Run_Listeners()

# Click a key
KB.ButtonClick('enter', delay=0.1)

# Press mouse button
KB.Press_MouseButton('left_m')

# Press keyboard key
KB.Press_KeyboardButton('space')
```

## Exceptions

### `KeyNameNotFoundError`

Raised when a key name is not found in keyboard or mouse mappings.

```python
try:
    KB.Upload_Keybind_Function('invalid_key', my_function)
except KeyNameNotFoundError as e:
    print(e)  # "Keyname 'invalid_key' not found in keyboard or mouse mappings"
```

## Notes

- Always call `Run_Listeners()` after registering keybinds
- Use `Stop()` to properly clean up listeners
- When `MultipleInstances=False`, only one function can run at a time
- When `Toggable=True`, pressing the keybind again stops the function
- Screenshot coordinate files are saved as: `left, top, width, height`
- Image matching uses template matching with confidence threshold

