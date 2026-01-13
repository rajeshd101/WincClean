# WincClean - Windows System Optimizer

WincClean is a modern, lightweight, and powerful system optimization tool built for Windows using Python and CustomTkinter. It helps you reclaim memory, clean junk files, manage startup applications, and optimize background services to ensure your PC runs smoother and faster.

## 🚀 Features

### 1. **System Overview & Quick Actions**
*   **Real-time Monitoring**: View live CPU and RAM usage statistics.
*   **RAM Optimizer**: Instantly trim the working set of all running processes to free up available physical memory.
*   **Temp Cleaner**: Scan and delete temporary files (`%TEMP%`) to reclaim disk space.

### 2. **Process Manager (with Visual Map)**
*   **Top Memory Consumers**: View a list of processes consuming the most RAM.
*   **Physical Memory Map**: A visual, horizontal bar chart resembling a physical RAM stick, showing exactly how your memory is distributed between Apps, System, and Free space.
*   **Smart Termination**: 
    *   Safely "End Task" for user applications.
    *   Prevents accidental termination of critical System processes (greyed out).
    *   Auto-elevation to Administrator if required to kill stubborn processes.

### 3. **Startup Manager**
*   **full Control**: View applications configured to start with Windows (Registry Run keys).
*   **Toggle/Remove**: easily remove unwanted apps from startup to improve boot times.
*   **Add New Apps**: Select any `.exe` on your system and set it to auto-start with a single click.
*   **System-Level Access**: specific handling for both User and System-wide startup items.

### 4. **Service Optimizer**
*   **Performance Tuning**: Disable unnecessary background services that consume CPU and Disk I/O.
    *   **SysMain (Superfetch)**: Disable to free up RAM (useful for SSDs).
    *   **Telemetry (DiagTrack)**: Disable to stop background data collection and save resources.
    *   **Windows Search**: Disable if you don't use file search often to save disk/indexing power.
*   **One-Click Toggle**: Enable or Disable services instantly (requires Admin rights).

## 🛠️ Installation

1.  **Prerequisites**: Ensure you have [Python 3.8+](https://www.python.org/downloads/) installed.
2.  **Clone/Download** this repository.
3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

##  ▶️ Usage

Run the main application script:

```bash
python main.py
```

**Note**: WincClean allows you to perform actions that may require Administrator privileges (e.g., disabling system services or killing system processes). If an action requires elevation, the app will automatically prompt you with a standard Windows UAC dialog.

## 📦 Dependencies

*   [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter): Modern UI components.
*   [psutil](https://github.com/giampaolo/psutil): System monitoring and process management.
*   [Matplotlib](https://matplotlib.org/): Data visualization for the Memory Map.
*   [pywin32](https://github.com/mhammond/pywin32): Windows API access.

## ⚠️ Disclaimer

This tool makes changes to your system configuration (Registry, Services, Processes). While designed to be safe, always use caution when disabling services or ending system processes. The authors are not responsible for any data loss or system instability.


## ✍️ Author

*   **Raj D**
*   **Email**: drajesh@hotmail.com

---
*Built with ❤️ for Windows Power Users.*
