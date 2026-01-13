class StartupFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        
        lbl = ctk.CTkLabel(header_frame, text="Startup Applications", font=ctk.CTkFont(size=20, weight="bold"))
        lbl.pack(side="left")

        btn_refresh = ctk.CTkButton(header_frame, text="Refresh", width=100, command=self.load_startup_apps)
        btn_refresh.pack(side="right")

        # Startup List
        self.scrollable = ctk.CTkScrollableFrame(self, label_text="Apps starting with Windows")
        self.scrollable.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        self.load_startup_apps()

    def load_startup_apps(self):
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
        
        # Scope icon/text
        color = "#3B8ED0" if scope == "User" else "gray60"
        lbl_scope = ctk.CTkLabel(row, text=scope, width=60, text_color=color, font=ctk.CTkFont(weight="bold"))
        lbl_scope.pack(side="left", padx=5)

        lbl_name = ctk.CTkLabel(row, text=name, anchor="w", width=200, font=ctk.CTkFont(weight="bold"))
        lbl_name.pack(side="left", padx=10)
        
        lbl_path = ctk.CTkLabel(row, text=path_val, anchor="w", width=300, text_color="gray70")
        lbl_path.pack(side="left", padx=10)
        
        btn_del = ctk.CTkButton(row, text="Remove", width=80, fg_color="#E04F5F", hover_color="#C03947",
                                command=lambda: self.remove_app(hive, key_path, name))
        btn_del.pack(side="right", padx=10)

    def remove_app(self, hive, key_path, name):
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
            ctypes.windll.shell32.ShellExecuteW(None, "runas", "reg", f'delete "{full_path}" /v "{name}" /f', None, 0)
            self.after(2000, self.load_startup_apps)
        except Exception as e:
             tkinter.messagebox.showerror("Elevation Error", str(e))
