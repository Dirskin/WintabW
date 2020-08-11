from PyQt5.QtWidgets import QMainWindow, QApplication
from wintab_params import LOGCONTEXT, AXIS, PACKET
from win32api import GetSystemMetrics
from tkinter import messagebox, Tk
from ctypes.wintypes import DWORD
from PyQt5.QtCore import QTimer
from sys import argv
from ctypes import *


try:
    wintab = WinDLL("wintab32.dll")
except OSError:
    main = Tk()
    main.withdraw()
    messagebox.showerror("Couldn't Load wintab32.dll file!", "wintab32.dll file couldn't be found. "
                                                             "\nTry to install/reinstall Tablet drivers.")
    raise Exception("wintab32 library couldn't load. wintab32.dll file couldn't be found. Try to install Tablet drivers.")

FIX32 = DWORD
WTPKT = FIX32

# Info Category 1 - WTI_INTERFACE, Used when calling WTInfoA to query different tablet information
WTI_INTERFACE       = 1  # Category: Contains global interface identification and capability information.
IFC_WINTABID        = 1  # TCHAR[]  Returns a copy of the null-terminated tablet hardware identification string in the user buffer. includes make, model
IFC_NDEVICES        = 4  # UINT  Returns the number of devices supported.

# Info Category 100 - WTI_DEVICES - Each contains capability and status information for a device.
WTI_DEVICES         = 100
DVC_NAME            = 1   # TCHAR[]Returns a displayable null terminated string describing the device,manufacturer
DVC_X               = 12  # AXIS  Each returns the tablet's range and resolution capabilities, in the x, y, and z axes, respectively.
DVC_Y               = 13
DVC_NPRESSURE       = 15  # AXIS  Each returns the tablet's range and resolution capabilities, for the normal and tangential pressure inputs, respectively.
DVC_TPRESSURE       = 16

# Info category 400 -
WTI_DDCTXS          = 400   # Each contains the current default digitizing logical context for the corresponding device.
WTI_DEFCONTEXT      = 3     # Contains the current default digitizing logical context. According to online resource, this one detaches mouse from tablet on Windows only
WTI_DEFSYSCTX       = 4     # Contains the current default system logical context.

# WTPKT bits
PK_TIME             = 0x0004  # time stamp
PK_CHANGED          = 0x0008  # Specifies which packet data items have changed since the last packet.
PK_SERIAL_NUMBER    = 0x0010  # Packet serial number
PK_CURSOR           = 0x0020  # reporting cursor
PK_BUTTONS          = 0x0040  # button information
PK_X                = 0x0080  # X - Y - Z Axis
PK_Y                = 0x0100
PK_Z                = 0x0200
PK_NORMAL_PRESSURE  = 0x0400  # normal or tip pressure
PK_TANGENT_PRESSURE = 0X0800  # tangential or barrel pressure

# ** Modify PACKETDATA's OR condition to add/remove packet information **
# Don't forget to modify PACKET  (in wintab_params.py) structure fields to match the values below
PACKETDATA = (PK_CHANGED | PK_CURSOR | PK_X | PK_Y | PK_BUTTONS | PK_NORMAL_PRESSURE | PK_SERIAL_NUMBER)

# Context Option values
CXO_SYSTEM          = 0x0001  # Specifies that the context is a system cursor context.
CXO_PEN             = 0x0002  # Specifies that the context is a Pen Windows context, if Pen Windows is installed. The context is also a system cursor context
CXO_MESSAGES        = 0x0004  # Specifies that the context returns WT_PACKET messages to its owner.


# -- Query Connected tablet information --
# Returns Tablet device name, or None if no tablet is connected
def getTabletInfo():
    AttachedDevices = c_uint(0)
    wintab.WTInfoA(WTI_INTERFACE, IFC_NDEVICES, byref(AttachedDevices))  # Query for number of connected tablets
    print("Wintab: Found {} connected devices".format(AttachedDevices.value))
    if AttachedDevices.value == 0:
        return None
    buf_size = wintab.WTInfoA(WTI_DEVICES, DVC_NAME, None)               # Calling with None returns the needed buf size
    DeviceName = create_string_buffer(buf_size)
    wintab.WTInfoA(WTI_DEVICES, DVC_NAME, byref(DeviceName))                  # Get tablet device name
    return str(DeviceName.value, 'utf-8')


# -- Query  tablet axis information --
# Input type: AXIS(). Returns axis information: tablet's range and resolution capabilities.
def getTabletAxisInfo(TabletX, TabletY):
    assert isinstance(TabletX, AXIS), "TabletX must be of type AXIS"
    assert isinstance(TabletY, AXIS), "TabletY must be of type AXIS"
    wintab.WTInfoA(WTI_DEVICES, DVC_X, byref(TabletX))
    wintab.WTInfoA(WTI_DEVICES, DVC_Y, byref(TabletY))


# -- Query  tablet pressure capability/range --
# Input type: AXIS. Returns pressure information: range and resolution capabilities,
# for the normal and tangential pressure
def getTabletPressureInfo(normal_press, tangential_press):
    assert isinstance(normal_press, AXIS), "normal_press must be of type AXIS"
    assert isinstance(tangential_press, AXIS), "tangential_press must be of type AXIS"
    # normal_press = AXIS()
    # tangential_press = AXIS()
    wintab.WTInfoA(WTI_DEVICES, DVC_NPRESSURE, byref(normal_press))
    wintab.WTInfoA(WTI_DEVICES, DVC_TPRESSURE, byref(tangential_press))


# -- Open Tablet contexts --
# Input: HWND windows handle. Returns hctx - tablet context handle.
def OpenTabletContexts(hWnd):
    lcMine = LOGCONTEXT()   # This structure determines what events an application will get, how they will be processed, and how they will be delivered to the application/window
    foundCtx = wintab.WTInfoA(WTI_DEFCONTEXT, 0, byref(lcMine))  # If the nIndex argument is zero, the function returns all of the information entries in the category in a single data structure
    # print('Wintab: contexts found, buf size: {}, devname: {}'.format(foundCtx, lcMine.lcName))

    lcMine.lcPktData = PACKETDATA
    lcMine.lcOptions |= CXO_MESSAGES    # Adding CXO_PEN will cause the pen to act also as a system cursor.
    lcMine.lcPktMode = 0                # Set all modes to absolute
    lcMine.lcMoveMask = PACKETDATA
    lcMine.lcBtnUpMask = lcMine.lcBtnDnMask

    # Set the Entire Tablet area as active.
    lcMine.lcInOrgX = 0              # specifies the origin of the context's input area in the tablet's native coordinates...
    lcMine.lcInOrgY = 0              # ...Each will be clipped to the tablet native coordinate space when the context is opened or modified:
    TabletX = AXIS()
    TabletY = AXIS()
    getTabletAxisInfo(TabletX, TabletY)
    lcMine.lcInExtX = TabletX.axMax  # specifies the extent of the input area in native coordinates:
    lcMine.lcInExtY = TabletY.axMax

    # Map the coordinate space to contain the whole screen
    SM_XVIRTUALSCREEN  = 76  # From winuser.h: The coordinates for the left side of the virtual screen. The virtual screen is the bounding rectangle of all display monitors.
    SM_YVIRTUALSCREEN  = 77  # The coordinates for the top of the virtual screen.
    SM_CXVIRTUALSCREEN = 78  # The width of the virtual screen, in pixels.
    SM_CYVIRTUALSCREEN = 79  # The height of the virtual screen, in pixels
    # lcMine.lcOutOrgX = GetSystemMetrics(SM_XVIRTUALSCREEN)
    # lcMine.lcOutExtX = GetSystemMetrics(SM_CXVIRTUALSCREEN)
    # This settings controls the output grid limits for X-Y.
    lcMine.lcOutOrgX = 0
    lcMine.lcOutExtX = 1920  # Dual screens might cause issues. Setting hard coded values to prevent issues.
    lcMine.lcOutOrgY = GetSystemMetrics(SM_YVIRTUALSCREEN)
    lcMine.lcOutExtY = - GetSystemMetrics(SM_CYVIRTUALSCREEN)  # In Wintab, the tablet origin is lower left. Move origin to upper left so that it coincides with screen origin.
    #     (0)    X axis----->            (1920)
    #    ______________________________________    (0)
    #   |                                      |    |
    #   |@  The tablet, buttons to the left    |    |   Y Axis
    #   |@                                     |    V
    #   |_____________________________________ |   (1080)
    hctx = wintab.WTOpenA(hWnd, byref(lcMine), 1)
    return hctx


# -- Closes and destroys a tablet context object --
# input: tablet context handle.
def CloseTabletContext(hctx):
    print("Wintab: Closing tablet context")
    wintab.WTClose(hctx)


hctx = None  # Context handle, used across importing modules (recorder.py)


# -- Reads the latest packets the the tablets packet queue --
# use this function after calling OpenTabletContext()
# return lpPkts PACKET array if any packet was received, 0 otherwise.
def GetPackets():
    global hctx
    cMaxPkts = 100
    lpPkts = (PACKET * 100)()
    recv_num = wintab.WTPacketsGet(hctx, cMaxPkts, lpPkts)
    if recv_num > 0:
        return lpPkts
    return 0


# Finally, Open the tablet context. Create Main window for a proper hWnd, create background polling function.
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        global hctx
        tablet_name = getTabletInfo()
        if tablet_name is not None:
            print("WintabW: Tablet Found: {}".format(tablet_name))
        else:
            print("WintabW: No tablet is connected")
        hWnd = int(self.winId())            # Get current window's window handle
        hctx = OpenTabletContexts(hWnd)
        tot_pk = 0
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self.PollForPackets)
        self.poll_timer.start(5)            # poll every 5mS

    def PollForPackets(self):
        lpPkts = (PACKET * 100)()
        lpPkts  = GetPackets()
        if lpPkts == 0:
            return
        print("Packet Serial Number: {} | X: {}, Y:{}, Pressure: {}".format(str(lpPkts[0].pkSerialNumber),
                                                                            str(lpPkts[0].pkX), str(lpPkts[0].pkY),
                                                                            str(lpPkts[0].pkNormalPressure)))


app = QApplication(argv)
m = MainWindow()
m.show()
app.exec_()
CloseTabletContext(hctx)

