# Advanced Parking Automation System
A complete parking management application demonstrating Data Structures & Algorithms (DSA) in C and Python. Features a C backend for efficient operations and a Tkinter GUI frontend for user interaction. Supports VIP priority, real-time billing, and visual slot tracking across 3 basements with 30 parking slots 10 slots in each basement.

# Features
- Dynamic Slot Allocation: Min-heap assigns lowest available slot (1-30).
- Parked Car Tracking: Linked list stores Car ID, owner, VIP status, timestamps, and auto-calculated bills.
- VIP Priority Queue: Waiting cars; VIPs jump to front when slots free up.
- Billing System: ₹20/hr regular (₹15/hr VIP), minimum 30min charge.
- Interactive GUI: Hover tooltips, color-coded slots (green=occupied, yellow=VIP, gray=empty), park/remove with validation.
- Cross-Platform: Uses ctypes for C-Python FFI (DLL/SO).
​
# Tech Stack
Component	Language	Key DSA
Backend	C	Min-Heap, Linked List, Queue​
Frontend	Python	Tkinter GUI, ctypes FFI​
​
# Quick Start
Compile Backend:
# Linux/macOS
gcc -shared -o parking.so -fPIC Backendd.c
# Windows (MinGW)
gcc -shared -o parking.dll Backendd.c
Place lib in same folder as Frontend.py.

#python Frontend.py
## Usage
Park: Enter plate/owner, toggle VIP → assigns slot, logs arrival.
Remove: Enter plate → computes bill (with times), frees slot.
View: Hover slots for details; displays parked list on changes.
