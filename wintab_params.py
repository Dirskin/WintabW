from ctypes.wintypes import DWORD, BOOL, HWND, HANDLE, LONG
from ctypes import *
# import wintab

FIX32 = DWORD
WTPKT = FIX32


class AXIS(Structure):
    _fields_ = [("axMin", c_long),    # Specifies the minimum value of the data item in the tablet's native coordinates
                ("axMax", c_long),    # Specifies the maximum value of the data item in the tablet's native coordinates
                ("axUnits", c_uint),  # Indicates the units used in calculating the resolution for the data item: 0-None, 1-Inches, 2-Centimeters.
                ("axResolution", DWORD)]  # Is a fixed-point number giving the number of data item increments per physical unit


class LOGCONTEXT(Structure):
    _fields_ = [("lcName", 40 * c_char), ("lcOptions", c_uint), ("lcStatus", c_uint),
                ("lcLocks", c_uint),     ("lcMsgBase", c_uint), ("lcDevice", c_uint), ("lcPktRate", c_uint),
                ("lcPktData", DWORD),    ("lcPktMode", DWORD),  ("lcMoveMask", DWORD),
                ("lcBtnDnMask", DWORD),  ("lcBtnUpMask", DWORD),
                ("lcInOrgX", c_long),    ("lcInOrgY", c_long),  ("lcInOrgZ", c_long),
                ("lnInExtX", c_long),    ("lcInExtY", c_long),  ("lcInExtZ", c_long),
                ("lcOutOrgX", c_long),   ("lcOutOrgY", c_long), ("lcOutOrgZ", c_long),
                ("lcOutExtX", c_long),   ("lcOutExtY", c_long), ("lcOutExtZ", c_long),
                ("lcSensX", DWORD),      ("lcSensY", DWORD),    ("lcSensZ", DWORD),   ("lcSysMode", BOOL),
                ("lcSysOrgX", c_int),    ("lcSysOrgY", c_int),  ("lcSysExtX", c_int), ("lcSysExtY", c_int),
                ("lcSysSensX", DWORD), ("lcSysSensY", DWORD)]


class ORIENTATION(Structure):
    _fields_ = [("orAzimuth", c_int), ("orAltitude", c_int), ("orTwist", c_int)]


class ROTATION(Structure):
    _fields_ = [("roPitch", c_int),   ("roRoll", c_int),     ("roYaw", c_int)]


class PACKET(Structure):        # Contains only the fields currently in PACKETDATA
    _fields_ = [("pkChanged", WTPKT),           ("pkSerialNumber", c_uint),      ("pkCursor", c_uint),
                ("pkButtons", DWORD),           ("pkX", LONG),                   ("pkY", LONG),
                ("pkNormalPressure", c_uint),]


class FULLPACKET(Structure):       # Contains ALL the possible packet fields.
    _fields_ = [("pkContext", HANDLE),          ("pkStatus", c_uint),         ("pkTime", c_long),
                ("pkChanged", WTPKT),           ("pkSerialNumber", c_uint),   ("pkCursor", c_uint), ("pkButtons", DWORD),
                ("pkX", LONG),                  ("pkY", LONG),                ("pkZ", LONG),
                ("pkNormalPressure", c_uint),   ("pkTangentPressure", c_uint),
                ("pkOrientation", ORIENTATION), ("pkRotation", ROTATION)]


