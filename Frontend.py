import tkinter as tk
from tkinter import messagebox
import ctypes
import sys
import os
import time

# ---------- Load Backend ----------
is_windows = sys.platform.startswith("win")
libname = "./parking.dll" if is_windows else "./parking.so"
lib = ctypes.CDLL(libname)

lib.insertCar.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
lib.extractMin.restype = ctypes.c_int
lib.enqueue.argtypes = [ctypes.c_char_p, ctypes.c_int]
lib.freeSlot.argtypes = [ctypes.c_int]
lib.removeCarWithBill.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
lib.removeCarWithBill.restype = ctypes.c_double

lib.initHeap(30)

slot_labels = []
slot_info = {}

# ---------- Colors ----------
BG = "#1A2733"
TEXT = "#DDEAFF"
HEADING = "#33C2FF"
BTN_BG = "#67C8FF"
BTN_FG = "#000000"

EMPTY_BG = "#C1CCD9"
EMPTY_BORDER = "#8BB3CC"

OCC_GREEN = "#14A76C"
VIP_YELLOW = "#EFBF37"

REMOVE_BTN_BG = "#FFA447"

# ---------- TOOLTIP ----------
tooltip = None

def show_tooltip(widget, slot_num):
    global tooltip

    if tooltip:
        tooltip.destroy()

    info = slot_info[slot_num]

    tooltip = tk.Toplevel(widget)
    tooltip.wm_overrideredirect(True)
    tooltip.configure(bg="#111111", padx=8, pady=6)

    text = (
        f"Slot: {slot_num}\n"
        f"Status: {info['status']}\n"
        f"Car: {info['car']}\n"
        f"Owner: {info['owner']}\n"
        f"VIP: {info['vip']}\n"
        f"Arrival: {info['arrival']}"
    )

    tk.Label(
        tooltip,
        text=text,
        fg="white",
        bg="#111111",
        justify="left",
        font=("Arial", 10)
    ).pack()

    x = widget.winfo_rootx() + 80
    y = widget.winfo_rooty() + 10
    tooltip.geometry(f"+{x}+{y}")

def hide_tooltip(e=None):
    global tooltip
    if tooltip:
        tooltip.destroy()
        tooltip = None


# ---------- PARK CAR ----------
def park_car():
    plate = entry_plate.get().strip()
    owner_name = entry_owner.get().strip()
    vip = vip_var.get()

    if not plate or not owner_name:
        messagebox.showwarning("Input Error", "Enter Car Number Plate and Owner Name!")
        return

    slot = lib.extractMin()
    if slot == -1:
        lib.enqueue(plate.encode(), vip)
        messagebox.showinfo("Full", "Parking full! Added to queue.")
        return

    lib.insertCar(plate.encode(), slot, vip)

    color = VIP_YELLOW if vip == 1 else OCC_GREEN

    slot_labels[slot - 1].config(
        text=f"{owner_name}\n{plate}",
        bg=color,
        fg="black",
        highlightbackground=color
    )

    slot_info[slot] = {
        "status": "occupied",
        "car": plate,
        "owner": owner_name,
        "vip": "Yes" if vip == 1 else "No",
        "arrival": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    entry_plate.delete(0, tk.END)
    entry_owner.delete(0, tk.END)
    vip_var.set(0)


# ---------- REMOVE CAR ----------
def remove_car():
    plate = entry_remove.get().strip()

    if not plate:
        messagebox.showwarning("Input Error", "Enter Car Number Plate!")
        return

    arrival_buf = ctypes.create_string_buffer(50)
    exit_buf = ctypes.create_string_buffer(50)

    bill = lib.removeCarWithBill(plate.encode(), arrival_buf, exit_buf)

    if bill < 0:
        messagebox.showinfo("Error", "Car not found!")
        return

    for i, lbl in enumerate(slot_labels):
        if plate in lbl.cget("text"):
            slot_num = i + 1
            lbl.config(
                text=f"Slot {slot_num}\nEmpty",
                bg=EMPTY_BG,
                fg="black",
                highlightbackground=EMPTY_BORDER
            )

            slot_info[slot_num] = {
                "status": "empty",
                "car": "",
                "owner": "",
                "vip": "No",
                "arrival": "-"
            }
            break

    messagebox.showinfo(
        "Car Removed",
        f"Car: {plate}\n\n"
        f"Arrival: {arrival_buf.value.decode()}\n"
        f"Exit: {exit_buf.value.decode()}\n"
        f"Total Bill: ₹{bill:.2f}"
    )

    entry_remove.delete(0, tk.END)


# ---------- UI (Same Layout) ----------
root = tk.Tk()
root.title("Advance Parking Automation System")
root.geometry("850x750")
root.configure(bg=BG)

frame_top = tk.Frame(root, bg=BG)
frame_top.pack(pady=10)

tk.Label(frame_top, text="Plate:", fg=TEXT, bg=BG).grid(row=0, column=0, padx=5)
entry_plate = tk.Entry(frame_top)
entry_plate.grid(row=0, column=1, padx=5)

tk.Label(frame_top, text="Owner:", fg=TEXT, bg=BG).grid(row=0, column=2, padx=5)
entry_owner = tk.Entry(frame_top)
entry_owner.grid(row=0, column=3, padx=5)

vip_var = tk.IntVar()
tk.Checkbutton(frame_top, text="VIP", variable=vip_var, bg=BG,
               fg=TEXT, selectcolor=BG).grid(row=0, column=4, padx=5)

tk.Button(frame_top, text="Park Car", command=park_car,
          bg=BTN_BG, fg=BTN_FG).grid(row=0, column=5, padx=5)

frame_slots = tk.Frame(root, bg=BG)
frame_slots.pack(pady=20)

slot_number = 1

# Initialize empty slot info
for i in range(1, 31):
    slot_info[i] = {
        "status": "empty",
        "car": "",
        "owner": "",
        "vip": "No",
        "arrival": "-"
    }

for b in range(3):
    tk.Label(frame_slots, text=f"Basement {b+1}", font=("Arial", 14, "bold"),
             fg=HEADING, bg=BG).pack(pady=5)

    basement_frame = tk.Frame(frame_slots, bg=BG)
    basement_frame.pack(pady=5)

    for r in range(2):
        row = tk.Frame(basement_frame, bg=BG)
        row.pack()

        for c in range(5):
            sn = slot_number

            lbl = tk.Label(
                row,
                text=f"Slot {sn}\nEmpty",
                width=15,
                height=3,
                bg=EMPTY_BG,
                fg="black",
                relief="ridge",
                highlightthickness=3,
                highlightbackground=EMPTY_BORDER
            )
            lbl.pack(side="left", padx=5, pady=5)

            # HOVER EVENTS
            def enter(e, slot=sn, widget=lbl):
                show_tooltip(widget, slot)

            def leave(e):
                hide_tooltip()

            lbl.bind("<Enter>", enter)
            lbl.bind("<Leave>", leave)

            slot_labels.append(lbl)
            slot_number += 1


frame_bottom = tk.Frame(root, bg=BG)
frame_bottom.pack(pady=20)

tk.Label(frame_bottom, text="Remove Car:", fg=TEXT, bg=BG).grid(row=0, column=0, padx=5)
entry_remove = tk.Entry(frame_bottom)
entry_remove.grid(row=0, column=1, padx=5)

tk.Button(frame_bottom, text="Remove Car", command=remove_car,
          bg=REMOVE_BTN_BG, fg="black").grid(row=0, column=2, padx=5)

root.mainloop()
