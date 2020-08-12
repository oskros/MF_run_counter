# import ctypes
# from ctypes import WinDLL
# from ctypes import wintypes
# import psutil
# import sys
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

import pymem
import re

pm = pymem.Pymem('notepad.exe', debug=False)
print('Process id: %s' % pm.process_id)

print('Base address: %s' % pm.process_base.lpBaseOfDll)
# print(pm.read_bytes(pm.process_base.EntryPoint, 255))
# print(pm.read_bytes(pm.process_base.process_handle, 4))
read_bytes = pm.read_bytes(pm.process_base.lpBaseOfDll, 10000)
# print(read_bytes)
# print(re.sub(b'[^\x00-\x99f9]', b'', read_bytes).replace(b'\x00', b''))


# address = pm.allocate(10)
# print('Allocated address: %s' % address)
# pm.write_int(address, 1337)
# value = pm.read_int(address)
# print('Allocated value: %s' % value)
# pm.free(address)