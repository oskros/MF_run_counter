# import ctypes
# from ctypes import WinDLL
# from ctypes import wintypes
# import psutil
# import sys
#
# look here for reading .d2s files: https://github.com/nokka/d2s
#
# # input process name
# nameprocess = "notepad.exe"
#
#
# def getpid():
#     for proc in psutil.process_iter():
#         if proc.name() == nameprocess:
#             return proc.pid
#
#
# PROCESS_ID = getpid()
# PROCESS_HEADER_ADDR = 0x7ff7b81e0000
#
# if PROCESS_ID is None:
#     print("Process was not found")
#     sys.exit(1)
# else:
#     print(PROCESS_ID)
#
#
# # read from addresses
# STRLEN = 255
#
# PROCESS_VM_READ = 0x0010
# k32 = WinDLL('kernel32')
# k32.OpenProcess.argtypes = wintypes.DWORD, wintypes.BOOL, wintypes.DWORD
# k32.OpenProcess.restype = wintypes.HANDLE
# k32.ReadProcessMemory.argtypes = wintypes.HANDLE, wintypes.LPVOID, wintypes.LPVOID, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)
# k32.ReadProcessMemory.restype = wintypes.BOOL
#
# process = k32.OpenProcess(PROCESS_VM_READ, 0, PROCESS_ID)
# buf = ctypes.create_string_buffer(STRLEN)
# s = ctypes.c_size_t()
#
# # if k32.ReadProcessMemory(process, PROCESS_HEADER_ADDR, buf, STRLEN, ctypes.byref(s)):
# #     print(s.value, buf.raw)
#
#
# for i in range(1, 100000):
#     if k32.ReadProcessMemory(process, hex(i), buf, STRLEN, ctypes.byref(s)):
#         print(s.value, buf.raw)

# Will pull memory addresses from https://github.com/Zutatensuppe/DiabloInterface/blob/master/src/D2Reader/GameMemoryTableFactory.cs#L70-L74
import psutil
import pymem
import pymem.process
import pymem.ressources.structure
import re
# tp = pymem.ressources.structure.TOKEN_PRIVILEGES()
# luid = pymem.ressources.structure.LUID()
# pymem.process.set_debug_privilege()


import os
import ctypes


class AdminStateUnknownError(Exception):
    """Cannot determine whether the user is an admin."""
    pass


def is_user_admin():
    # type: () -> bool
    """Return True if user has admin privileges.

    Raises:
        AdminStateUnknownError if user privileges cannot be determined.
    """
    try:
        return os.getuid() == 0
    except AttributeError:
        pass
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() == 1
    except AttributeError:
        raise AdminStateUnknownError


print('User admin: %s' % is_user_admin())


pm = pymem.Pymem('notepad.exe')
# pid = pymem.process.process_from_name('Game.exe').th32ProcessID

pid = pm.process_id
print('Process id: %s' % pid)
base_address = pm.process_base.lpBaseOfDll

# print('Base address: %s' % pm.process_base.lpBaseOfDll)
print('Base address: %s' % base_address)

import ctypes
from ctypes import wintypes

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

kernel32.GetModuleHandleW.restype = wintypes.HMODULE
kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]

hMod = kernel32.GetModuleHandleW('kernel32.dll')
print(hMod)

#
# import win32process
# import win32api
# import pymem
# pid = pymem.process.process_from_name('Game.exe').th32ProcessID
# print('Process id: %s' % pid)
# # pymem.process.process_
# # base_addr = pymem.process.module_from_name()
#
# PROCESS_ALL_ACCESS = 0x1F0FFF
# PROCESS_VM_READ = 0x0010
# PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
# win32api.T
# # processHandle = win32api.OpenProcess(0x0400 | 0x0010, False, pid)
# modules = win32process.EnumProcessModules(processHandle)
# processHandle.close()
# base_addr = modules[0] # for me it worked to select the first item in list...
# print('Base address: %s' % base_addr)
#
# import sys
# sys.exit(1)
# loading = base_adress + 0x30F2C0,
# saving = base_adress + 0x3792F8,
# saving2 = base_adress + 0x3786D0,
# in_game = base_adress + 0x30EE8C,
# in_menu = base_adress + 0x379970,
# print(pm.read_bytes(pm.process_base.EntryPoint, 255))
# print(pm.read_bytes(pm.process_base.process_handle, 4))
read_bytes = pm.read_bytes(base_address, 10000)
# print(read_bytes)
# print(re.sub(b'[^\x00-\x99f9]', b'', read_bytes).replace(b'\x00', b''))


# address = pm.allocate(10)
# print('Allocated address: %s' % address)
# pm.write_int(address, 1337)
# value = pm.read_int(address)
# print('Allocated value: %s' % value)
# pm.free(address)