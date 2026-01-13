# Author: Raj D
# Email: drajesh@hotmail.com

import customtkinter as ctk
import psutil
import os
import threading
import time
import ctypes
from ctypes import wintypes
import tkinter.messagebox
from tkinter import filedialog
import winreg
import tkinter.messagebox
from tkinter import filedialog
import winreg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import subprocess

# --- System API for Memory Cleaning ---
# Uses Windows API 'EmptyWorkingSet' to trim memory usage of processes
psapi = ctypes.WinDLL('psapi.dll')
kernel32 = ctypes.WinDLL('kernel32.dll')

OpenProcess = kernel32.OpenProcess
OpenProcess.restype = wintypes.HANDLE
OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]

EmptyWorkingSet = psapi.EmptyWorkingSet
EmptyWorkingSet.restype = wintypes.BOOL
EmptyWorkingSet.argtypes = [wintypes.HANDLE]

CloseHandle = kernel32.CloseHandle
CloseHandle.restype = wintypes.BOOL
CloseHandle.argtypes = [wintypes.HANDLE]

PROCESS_ALL_ACCESS = 0x1F0FFF
PROCESS_SET_QUOTA = 0x0100
PROCESS_QUERY_INFORMATION = 0x0400

def clean_system_memory():
    """Iterates through all processes and attempts to trim their working set."""
    pids = psutil.pids()
    count = 0
    bytes_freed = 0 # Difficult to calculate exactly without before/after snapshot, simplified here.
    
    for pid in pids:
        try:
            # We need PROCESS_SET_QUOTA to call EmptyWorkingSet
            hProcess = OpenProcess(PROCESS_SET_QUOTA | PROCESS_QUERY_INFORMATION, False, pid)
            if hProcess:
                try:
                    # Get memory before (optional, for stats)
                    # p = psutil.Process(pid)
                    # m1 = p.memory_info().rss
                    
                    if EmptyWorkingSet(hProcess):
                        count += 1
                        
                except Exception:
                    pass
                finally:
                    CloseHandle(hProcess)
        except Exception:
            pass
    return count

def get_temp_size():
    temp_path = os.getenv('TEMP')
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(temp_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
            except Exception:
                pass
    return total_size / (1024 * 1024) # MB

def clean_temp_files():
    temp_path = os.getenv('TEMP')
    deleted_files = 0
    bytes_cleared = 0
    
    for dirpath, dirnames, filenames in os.walk(temp_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                size = os.path.getsize(fp)
                os.remove(fp)
                deleted_files += 1
                bytes_cleared += size
            except Exception:
                # File is likely in use
                pass
    return deleted_files, bytes_cleared / (1024 * 1024)

# --- GUI Application ---

class CatcheWayApp(ctk.CTk):
    def __init__(self):
        super().__init__()


        # Setup Window
        self.title("WincClean - System Optimizer")
        self.geometry("800x600")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")

        # Layout Configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar_label = ctk.CTkLabel(self.sidebar, text="WincClean", font=ctk.CTkFont(size=20, weight="bold"))
        self.sidebar_label.grid(row=0, column=0, padx=20, pady=20)

        self.btn_overview = ctk.CTkButton(self.sidebar, text="Overview", command=self.show_overview)
        self.btn_overview.grid(row=1, column=0, padx=20, pady=10)
        
        self.btn_processes = ctk.CTkButton(self.sidebar, text="Process Manager", command=self.show_processes, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.btn_processes.grid(row=2, column=0, padx=20, pady=10)

        self.btn_startup = ctk.CTkButton(self.sidebar, text="Startup Manager", command=self.show_startup, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.btn_startup.grid(row=3, column=0, padx=20, pady=10)

        self.btn_optimizer = ctk.CTkButton(self.sidebar, text="System Services", command=self.show_optimizer, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.btn_optimizer.grid(row=4, column=0, padx=20, pady=10)

        # Main Content Area - We'll swap frames here
        self.current_frame = None
        self.show_overview()

    def clear_main_area(self):
        if self.current_frame:
            self.current_frame.destroy()

    def show_overview(self):
        self.clear_main_area()
        self.current_frame = OverviewFrame(self)
        self.current_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # Update sidebar button styles
        self.btn_overview.configure(fg_color=["#3B8ED0", "#1F6AA5"], text_color="white") # Primary
        self.btn_processes.configure(fg_color="transparent", text_color=("gray10", "#DCE4EE"))
        self.btn_startup.configure(fg_color="transparent", text_color=("gray10", "#DCE4EE"))
        self.btn_startup.configure(fg_color="transparent", text_color=("gray10", "#DCE4EE"))
        self.btn_optimizer.configure(fg_color="transparent", text_color=("gray10", "#DCE4EE"))

    def show_processes(self):
        self.clear_main_area()
        self.current_frame = ProcessFrame(self)
        self.current_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Update sidebar button styles
        self.btn_overview.configure(fg_color="transparent", text_color=("gray10", "#DCE4EE"))
        self.btn_processes.configure(fg_color=["#3B8ED0", "#1F6AA5"], text_color="white")
        self.btn_startup.configure(fg_color="transparent", text_color=("gray10", "#DCE4EE"))
        self.btn_optimizer.configure(fg_color="transparent", text_color=("gray10", "#DCE4EE"))

    def show_startup(self):
        self.clear_main_area()
        self.current_frame = StartupFrame(self)
        self.current_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Update sidebar button styles
        self.btn_overview.configure(fg_color="transparent", text_color=("gray10", "#DCE4EE"))
        self.btn_processes.configure(fg_color="transparent", text_color=("gray10", "#DCE4EE"))
        self.btn_startup.configure(fg_color=["#3B8ED0", "#1F6AA5"], text_color="white")
        self.btn_optimizer.configure(fg_color="transparent", text_color=("gray10", "#DCE4EE"))

    def show_optimizer(self):
        self.clear_main_area()
        self.current_frame = OptimizerFrame(self)
        self.current_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Update sidebar button styles
        self.btn_overview.configure(fg_color="transparent", text_color=("gray10", "#DCE4EE"))
        self.btn_processes.configure(fg_color="transparent", text_color=("gray10", "#DCE4EE"))
        self.btn_startup.configure(fg_color="transparent", text_color=("gray10", "#DCE4EE"))
        self.btn_optimizer.configure(fg_color=["#3B8ED0", "#1F6AA5"], text_color="white")


class OverviewFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Header
        self.header = ctk.CTkLabel(self, text="System Status", font=ctk.CTkFont(size=24, weight="bold"))
        self.header.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w")

        # Stats Cards
        self.cpu_card = StatsCard(self, "CPU Usage", "0%")
        self.cpu_card.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        self.ram_card = StatsCard(self, "RAM Usage", "0%")
        self.ram_card.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # Actions
        self.action_label = ctk.CTkLabel(self, text="Quick Actions", font=ctk.CTkFont(size=18, weight="bold"))
        self.action_label.grid(row=2, column=0, columnspan=2, padx=20, pady=(30, 10), sticky="w")

        self.btn_clean_ram = ctk.CTkButton(self, text="Optimize RAM (WincClean)", height=50, font=ctk.CTkFont(size=16), command=self.run_memory_clean)
        self.btn_clean_ram.grid(row=3, column=0, columnspan=2, padx=20, pady=10, sticky="ew")

        self.btn_clean_temp = ctk.CTkButton(self, text="Clean Temp Files", height=50, fg_color="#E04F5F", hover_color="#C03947", font=ctk.CTkFont(size=16), command=self.run_temp_clean)
        self.btn_clean_temp.grid(row=4, column=0, columnspan=2, padx=20, pady=10, sticky="ew")

        # Status Log
        self.log_text = ctk.CTkTextbox(self, height=150)
        self.log_text.grid(row=5, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")
        self.log("Welcome to WincClean. Ready to optimize.")

        # Start Monitor
        self.update_stats()

    def log(self, message):
        self.log_text.insert("end", f"> {message}\n")
        self.log_text.see("end")

    def update_stats(self):
        if not self.winfo_exists():
            return
            
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        
        self.cpu_card.set_value(f"{cpu}%")
        self.ram_card.set_value(f"{ram}%")
        
        self.after(2000, self.update_stats)

    def run_memory_clean(self):
        self.log("Starting Memory Optimization...")
        def task():
            before_ram = psutil.virtual_memory().percent
            count = clean_system_memory()
            time.sleep(1) # Let system settle
            after_ram = psutil.virtual_memory().percent
            
            self.after(0, lambda: self.log(f"Optimization Complete. Trimmed {count} processes."))
            self.after(0, lambda: self.log(f"RAM Usage: {before_ram}% -> {after_ram}%"))
            self.after(0, lambda: self.cpu_card.set_value(f"{psutil.cpu_percent()}%"))
            self.after(0, lambda: self.ram_card.set_value(f"{after_ram}%"))

        threading.Thread(target=task, daemon=True).start()

    def run_temp_clean(self):
        size_mb = get_temp_size()
        self.log(f"Found approx {size_mb:.2f} MB of temp files.")
        
        def task():
            count, size = clean_temp_files()
            self.after(0, lambda: self.log(f"Cleaned {count} files ({size:.2f} MB freed)."))
        
        threading.Thread(target=task, daemon=True).start()


class StatsCard(ctk.CTkFrame):
    def __init__(self, master, title, value):
        super().__init__(master)
        self.lbl_title = ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=14))
        self.lbl_title.pack(pady=(10, 0))
        self.lbl_value = ctk.CTkLabel(self, text=value, font=ctk.CTkFont(size=32, weight="bold"), text_color="#3B8ED0")
        self.lbl_value.pack(pady=(0, 10))
    
    def set_value(self, value):
        self.lbl_value.configure(text=value)


SYSTEM_PROCESSES = [
    "system", "registry", "smss.exe", "csrss.exe", "wininit.exe", "services.exe",
    "lsass.exe", "svchost.exe", "fontdrvhost.exe", "winlogon.exe", "dwm.exe",
    "spoolsv.exe", "memory compression", "taskmgr.exe", "explorer.exe",
    "searchindexer.exe", "applicationframehost.exe", "startmenuexperiencehost.exe",
    "ctfmon.exe", "sihost.exe", "runtimebroker.exe"
]

class ProcessFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=3) # List
        self.grid_columnconfigure(1, weight=2) # Chart
        
        self.selected_proc_data = None
        self.selected_widget = None

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=10)
        
        lbl = ctk.CTkLabel(header_frame, text="Top Memory Consumers", font=ctk.CTkFont(size=20, weight="bold"))
        lbl.pack(side="left")

        # Legend
        legend_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        legend_frame.pack(side="right", padx=10)
        ctk.CTkLabel(legend_frame, text="■ User Apps", text_color="#3B8ED0", font=ctk.CTkFont(size=12)).pack(side="left", padx=5)
        ctk.CTkLabel(legend_frame, text="■ System", text_color="gray60", font=ctk.CTkFont(size=12)).pack(side="left", padx=5)

        btn_refresh = ctk.CTkButton(header_frame, text="Refresh", width=80, command=self.load_processes)
        btn_refresh.pack(side="right")
        
        self.btn_kill = ctk.CTkButton(header_frame, text="End Task", width=140, command=self.kill_selected_proc, fg_color="#E04F5F", hover_color="#C03947", state="disabled")
        self.btn_kill.pack(side="right", padx=10)

        # Process List
        self.scrollable = ctk.CTkScrollableFrame(self, label_text="Processes")
        self.scrollable.grid(row=1, column=0, sticky="nsew", padx=(20, 10), pady=10)
        
        # Chart Frame
        self.chart_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.chart_frame.grid(row=1, column=1, sticky="nsew", padx=(0, 20), pady=10)
        
        self.load_processes()

    def load_processes(self):
        self.selected_proc_data = None
        self.selected_widget = None
        self.btn_kill.configure(state="disabled")
        
        # Clear existing list
        for widget in self.scrollable.winfo_children():
            widget.destroy()
            
        # Get Processes
        procs = []
        for p in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                procs.append(p.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Sort by Memory
        procs.sort(key=lambda x: x['memory_info'].rss, reverse=True)
        
        # Show Top 20 in list
        for p in procs[:20]:
            mem_mb = p['memory_info'].rss / (1024 * 1024)
            self.create_proc_row(p['pid'], p['name'], mem_mb)
            
        # Update Chart
        self.update_chart(procs)

    def update_chart(self, procs):
        # Clear old chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
            
        # Data Prep
        vm = psutil.virtual_memory()
        total_ram_gb = vm.total / (1024**3)
        used_ram_gb = vm.used / (1024**3)
        
        # We need to distribute 'Used' into: Top Apps + System/Others
        top_apps = procs[:5]
        app_data = [] # (name, gb_size, color)
        
        # Consistent colors
        colors = ['#4E9FDF', '#E04F5F', '#2CC985', '#F2C94C', '#9B51E0'] 
        
        top_apps_sum_gb = 0
        for i, p in enumerate(top_apps):
            gb = p['memory_info'].rss / (1024**3)
            app_data.append( (p['name'], gb, colors[i % len(colors)]) )
            top_apps_sum_gb += gb
            
        # System/Others
        system_gb = used_ram_gb - top_apps_sum_gb
        if system_gb < 0: system_gb = 0 # Should not happen unless race condition
        
        # Plotting
        # Dark PCB Green background style or Sleek Dark Grey
        fig_bg = "#2b2b2b" 
        plot_bg = "#1e1e1e"
        text_color = "#DCE4EE"
        
        fig, ax = plt.subplots(figsize=(6, 2.5), facecolor=fig_bg)
        ax.set_facecolor(plot_bg)
        
        # 1. Base 'Stick' (Free Space) - Draw outline or distinct bg
        # We draw a full bar for TOTAL capacity
        ax.barh(0, total_ram_gb, height=0.6, color="#252526", edgecolor="#404040", linewidth=1, label="Free")
        
        # 2. Fill it up
        # Start from "Address 0" (left)
        current_addr = 0
        
        # Plot System first (simulating kernel/os low memory)
        ax.barh(0, system_gb, left=current_addr, height=0.6, color="gray", alpha=0.9, edgecolor=fig_bg, label="System/Other")
        # Add text for System if big enough
        if system_gb > 0.5:
             ax.text(current_addr + system_gb/2, 0, "System", ha='center', va='center', color='white', fontsize=10, fontweight='bold')
        current_addr += system_gb
        
        # Plot Apps
        for name, size_gb, color in app_data:
            ax.barh(0, size_gb, left=current_addr, height=0.6, color=color, edgecolor=fig_bg)
            
            # Label on the bar part? Only if wide enough
            # We will rely on legend for reading, but addresses on X axis help location
            
            current_addr += size_gb

        # Styling to look like memory map
        ax.set_ylim(-0.5, 0.5)
        ax.set_xlim(0, total_ram_gb)
        
        # X-Axis Addresses
        ticks = list(range(0, int(total_ram_gb) + 2, 4)) # Every 4GB
        if total_ram_gb < 8: ticks = list(range(0, int(total_ram_gb) + 2, 2)) # Every 2GB for small RAM
        
        ax.set_xticks(ticks)
        ax.set_xticklabels([f"{t} GB" for t in ticks], color="gray", fontsize=11)
        ax.tick_params(axis='x', colors='gray')
        ax.get_yaxis().set_visible(False)
        
        # Remove spines
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.spines['bottom'].set_visible(True)
        ax.spines['bottom'].set_color('gray')

        plt.title(f"Physical Memory Map (Total: {total_ram_gb:.1f} GB)", color=text_color, fontsize=14, pad=10, loc='left')
        
        # Create Custom Legend handles because we iterated
        import matplotlib.patches as mpatches
        legend_handles = [mpatches.Patch(color='gray', label='System/Other')]
        for name, size, color in app_data:
            legend_handles.append(mpatches.Patch(color=color, label=f"{name} ({size*1024:.0f} MB)"))
        
        # Legend below
        ax.legend(handles=legend_handles, loc='upper center', bbox_to_anchor=(0.5, -0.25), 
                  ncol=3, frameon=False, labelcolor=text_color, fontsize=10)
        
        # Adjust layout
        plt.subplots_adjust(bottom=0.35, top=0.85, left=0.05, right=0.95)

        # Create Canvas
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def create_proc_row(self, pid, name, mem_mb):
        is_system = name.lower() in SYSTEM_PROCESSES
        
        # Style based on type
        if is_system:
            row_fg = "transparent"
            text_col = "gray60"
        else:
            row_fg = ["#ebebeb", "#2b2b2b"] # Highlight user apps
            text_col = "#3B8ED0" # Blue highlight for text

        row = ctk.CTkFrame(self.scrollable, fg_color=row_fg)
        row.pack(fill="x", pady=2)
        
        # Click handler
        def on_click(event):
            self.select_item(row, pid, name, is_system, row_fg)

        row.bind("<Button-1>", on_click)
        
        lbl_name = ctk.CTkLabel(row, text=f"{name} ({pid})", anchor="w", width=300, text_color=text_col)
        lbl_name.pack(side="left", padx=10)
        lbl_name.bind("<Button-1>", on_click)
        
        lbl_mem = ctk.CTkLabel(row, text=f"{mem_mb:.1f} MB", width=100, text_color=text_col)
        lbl_mem.pack(side="left", padx=10)
        lbl_mem.bind("<Button-1>", on_click)

    def select_item(self, widget, pid, name, is_system, default_fg):
        # Reset previous
        if self.selected_widget:
            # We need to restore the correct color based on whether it was system or user app
            # To simplify, we reload the list or store the original color. 
            # Storing original color in widget tag or similar is cleaner, but for now:
            prev_is_sys = self.selected_proc_data[2]
            prev_fg = "transparent" if prev_is_sys else ["#ebebeb", "#2b2b2b"]
            self.selected_widget.configure(fg_color=prev_fg)

        self.selected_widget = widget
        self.selected_proc_data = (pid, name, is_system)
        
        # Highlight new
        self.selected_widget.configure(fg_color=["#d6d6d6", "#3a3a3a"])
        
        # Enable kill button only if not system
        if is_system:
            self.btn_kill.configure(state="disabled")
        else:
            self.btn_kill.configure(state="normal")

    def kill_selected_proc(self):
        if not self.selected_proc_data:
            return
        
        pid, name, is_system = self.selected_proc_data
        self.kill_proc(pid, name)

    def kill_proc(self, pid, name):
        if not tkinter.messagebox.askyesno("Confirm End Task", f"Are you sure you want to end {name} ({pid})?"):
            return

        try:
            p = psutil.Process(pid)
            p.terminate()
            try:
                p.wait(timeout=2)
            except psutil.TimeoutExpired:
                if tkinter.messagebox.askyesno("Force Kill", f"{name} is not responding. Force kill?"):
                    p.kill()
            
            self.load_processes()
            tkinter.messagebox.showinfo("Success", f"Process {name} ended.")
        except psutil.AccessDenied:
             if tkinter.messagebox.askyesno("Access Denied", f"Cannot end {name} with current permissions.\n\nDo you want to try blocking it as Administrator?"):
                try:
                    # 'runas' verb prompts for UAC
                    # nShowCmd=0 hides the cmd window
                    ctypes.windll.shell32.ShellExecuteW(None, "runas", "taskkill", f"/F /PID {pid}", None, 0)
                    # We can't wait on ShellExecute, so schedule a refresh
                    self.after(2000, self.load_processes) 
                except Exception as e:
                    tkinter.messagebox.showerror("Elevation Error", str(e))
        except psutil.NoSuchProcess:
             tkinter.messagebox.showwarning("Process Not Found", f"{name} is no longer running.")
             self.load_processes()
        except Exception as e:
            tkinter.messagebox.showerror("Error", f"Could not end task: {e}")


class StartupFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.selected_item_data = None
        self.selected_widget = None

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        
        lbl = ctk.CTkLabel(header_frame, text="Startup Applications", font=ctk.CTkFont(size=20, weight="bold"))
        lbl.pack(side="left")

        # Buttons
        btn_refresh = ctk.CTkButton(header_frame, text="Refresh", width=80, command=self.load_startup_apps)
        btn_refresh.pack(side="right", padx=(5, 0))
        
        btn_add = ctk.CTkButton(header_frame, text="+ Add App", width=100, command=self.add_startup_app, fg_color="#2CC985", hover_color="#2FA572")
        btn_add.pack(side="right", padx=(5, 0))
        
        self.btn_remove = ctk.CTkButton(header_frame, text="Disable/Remove", width=160, command=self.remove_selected_app, fg_color="#E04F5F", hover_color="#C03947", state="disabled")
        self.btn_remove.pack(side="right")

        # Startup List
        self.scrollable = ctk.CTkScrollableFrame(self, label_text="Apps starting with Windows")
        self.scrollable.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        self.load_startup_apps()

    def load_startup_apps(self):
        self.selected_item_data = None
        self.selected_widget = None
        self.btn_remove.configure(state="disabled")
        
        for widget in self.scrollable.winfo_children():
            widget.destroy()
            
        # Check HKCU
        self.read_registry_key(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", "User")
        
        # Check HKLM
        try:
            self.read_registry_key(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", "System")
        except Exception:
            pass # Almost certainly permission denied or key missing if not admin

    def read_registry_key(self, hive, path, scope):
        try:
            with winreg.OpenKey(hive, path, 0, winreg.KEY_READ) as key:
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        self.create_startup_row(name, value, hive, path, scope)
                        i += 1
                    except OSError:
                        break
        except Exception:
            pass

    def create_startup_row(self, name, path_val, hive, key_path, scope):
        row = ctk.CTkFrame(self.scrollable)
        row.pack(fill="x", pady=2)
        
        # Click handler
        def on_click(event):
            self.select_item(row, name, hive, key_path)

        row.bind("<Button-1>", on_click)
        
        # Scope icon/text
        color = "#3B8ED0" if scope == "User" else "gray60"
        lbl_scope = ctk.CTkLabel(row, text=scope, width=60, text_color=color, font=ctk.CTkFont(weight="bold"))
        lbl_scope.pack(side="left", padx=5)
        lbl_scope.bind("<Button-1>", on_click)

        lbl_name = ctk.CTkLabel(row, text=name, anchor="w", width=200, font=ctk.CTkFont(weight="bold"))
        lbl_name.pack(side="left", padx=10)
        lbl_name.bind("<Button-1>", on_click)
        
        # Truncate long paths for display
        display_path = (path_val[:60] + '...') if len(path_val) > 63 else path_val
        lbl_path = ctk.CTkLabel(row, text=display_path, anchor="w", width=400, text_color="gray70")
        lbl_path.pack(side="left", padx=10)
        lbl_path.bind("<Button-1>", on_click)

    def select_item(self, widget, name, hive, key_path):
        # Reset previous selection
        if self.selected_widget:
            self.selected_widget.configure(fg_color=["#ebebeb", "#2b2b2b"]) # Default

        self.selected_widget = widget
        self.selected_item_data = (hive, key_path, name)
        
        # Highlight new
        self.selected_widget.configure(fg_color=["#d6d6d6", "#3a3a3a"])
        self.btn_remove.configure(state="normal")

    def remove_selected_app(self):
        if not self.selected_item_data:
            return
            
        hive, key_path, name = self.selected_item_data
        
        if not tkinter.messagebox.askyesno("Confirm Removal", f"Are you sure you want to prevent '{name}' from starting with Windows?\n\nThis will delete the registry entry."):
            return

        try:
            # Try normal delete
            with winreg.OpenKey(hive, key_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, name)
            self.load_startup_apps()
            tkinter.messagebox.showinfo("Success", f"{name} removed from startup.")
        except PermissionError:
             if tkinter.messagebox.askyesno("Access Denied", f"Needs Administrator rights to remove '{name}'.\n\nTry removing as Admin?"):
                self.remove_as_admin(hive, key_path, name)
        except Exception as e:
            tkinter.messagebox.showerror("Error", f"Failed to remove: {e}")

    def remove_as_admin(self, hive, key_path, name):
        # Construct reg delete command
        # HKLM or HKCU
        root = "HKLM" if hive == winreg.HKEY_LOCAL_MACHINE else "HKCU"
        full_path = f"{root}\\{key_path}"
        
        try:
            # We use 'reg' command line tool to delete the key with elevated privileges
            ctypes.windll.shell32.ShellExecuteW(None, "runas", "reg", f'delete "{full_path}" /v "{name}" /f', None, 0)
            
            # Since ShellExecute is async and we can't easily wait for it without more complex code,
            # we ask the user to confirm they've handled the UAC prompt. This acts as a manual 'wait'.
            tkinter.messagebox.showinfo("Admin Action", "WincClean has requested Administrator permissions to remove this item.\n\nPlease accept the Windows prompt (UAC), then click OK here to refresh the list.")
            
            self.load_startup_apps()
        except Exception as e:
             tkinter.messagebox.showerror("Elevation Error", str(e))

    def add_startup_app(self):
        file_path = filedialog.askopenfilename(filetypes=[("Executables", "*.exe"), ("All Files", "*.*")])
        if not file_path:
            return
        
        # Default name is filename without ext
        name = os.path.splitext(os.path.basename(file_path))[0]
        # Normalize path
        file_path = os.path.normpath(file_path)
        
        try:
             # Write to HKCU (doesn't need admin)
             key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
             with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                 winreg.SetValueEx(key, name, 0, winreg.REG_SZ, f'"{file_path}"')
             
             self.load_startup_apps()
             tkinter.messagebox.showinfo("Success", f"Added '{name}' to startup!")
        except Exception as e:
            tkinter.messagebox.showerror("Error", f"Could not add startup item: {e}")


class OptimizerFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        self.header = ctk.CTkLabel(self, text="System Services Optimization", font=ctk.CTkFont(size=24, weight="bold"))
        self.header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        self.desc = ctk.CTkLabel(self, text="Disable unnecessary Windows services to reclaim RAM and CPU.", font=ctk.CTkFont(size=14))
        self.desc.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")

        # Scrollable area
        self.scrollable = ctk.CTkScrollableFrame(self)
        self.scrollable.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        self.grid_rowconfigure(2, weight=1)

        # Services to manage
        self.services = [
            ("SysMain", "Superfetch (SysMain)", "Preloads apps into RAM. Disable to free massive RAM, but apps may launch slightly slower."),
            ("DiagTrack", "Telemetry (DiagTrack)", "Background data collection. Disable to save CPU/RAM and privacy."),
            ("WSearch", "Windows Search", "File indexing. heavy Disk/RAM usage. Disable if you don't use Search often.")
        ]
        
        self.refresh_services()

    def refresh_services(self):
        for widget in self.scrollable.winfo_children():
            widget.destroy()
            
        for svc_name, display_name, desc in self.services:
            self.create_service_row(svc_name, display_name, desc)

    def get_service_status(self, svc_name):
        try:
            # sys.stdout is hidden in GUI apps usually, capture output
            output = subprocess.check_output(f"sc query {svc_name}", shell=True, text=True)
            if "RUNNING" in output:
                return "Running"
            elif "STOPPED" in output:
                return "Stopped"
            else:
                return "Unknown"
        except:
            return "Not Found"

    def create_service_row(self, svc_name, display_name, desc):
        status = self.get_service_status(svc_name)
        
        row = ctk.CTkFrame(self.scrollable)
        row.pack(fill="x", pady=5)
        
        # Text Info
        info_frame = ctk.CTkFrame(row, fg_color="transparent")
        info_frame.pack(side="left", padx=10, pady=10, fill="x", expand=True)
        
        ctk.CTkLabel(info_frame, text=display_name, font=ctk.CTkFont(size=16, weight="bold"), anchor="w").pack(fill="x")
        ctk.CTkLabel(info_frame, text=desc, font=ctk.CTkFont(size=12), text_color="gray70", anchor="w", wraplength=400).pack(fill="x")
        
        # Status/Action
        action_frame = ctk.CTkFrame(row, fg_color="transparent")
        action_frame.pack(side="right", padx=10)
        
        status_color = "#2CC985" if status == "Running" else "#E04F5F"
        ctk.CTkLabel(action_frame, text=status, text_color=status_color, font=ctk.CTkFont(weight="bold")).pack(side="top", pady=5)
        
        btn_text = "Disable" if status == "Running" else "Enable"
        btn_color = "#E04F5F" if status == "Running" else "#3B8ED0"
        btn_hover = "#C03947" if status == "Running" else "#1F6AA5"
        
        ctk.CTkButton(action_frame, text=btn_text, width=100, fg_color=btn_color, hover_color=btn_hover,
                      command=lambda: self.toggle_service(svc_name, status)).pack(side="bottom", pady=5)

    def toggle_service(self, svc_name, current_status):
        if not tkinter.messagebox.askyesno("Confirm Service Change", f"Do you want to { 'DISABLE' if current_status == 'Running' else 'ENABLE' } {svc_name}?"):
            return
            
        action = "disable" if current_status == "Running" else "enable"
        
        # We need to construct a command string to run as admin
        if action == "disable":
            # stop and disable
            cmd_str = f"cmd /c net stop {svc_name} & sc config {svc_name} start= disabled"
        else:
            # enable (auto) and start
            cmd_str = f"cmd /c sc config {svc_name} start= auto & net start {svc_name}"
            
        try:
             tkinter.messagebox.showinfo("Admin Required", "This action requires Administrator privileges.\nPlease accept the prompt.")
             ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd", f"/c {cmd_str}", None, 0)
             
             # Wait a bit then refresh
             self.after(2000, self.refresh_services)
        except Exception as e:
            tkinter.messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    app = CatcheWayApp()
    app.mainloop()
