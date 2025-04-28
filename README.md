# 🖥️ Mini Task Manager 🏯
## 4th Semester Operating Systems Project (C + Python GUI)

A **C** and **Python Tkinter** based Mini Task Manager that allows you to view running processes, kill processes by PID, view threads, and visualize CPU & Memory usage graphs — all inside a smooth graphical interface. 🦠⚡️

Built for my **4th Semester Operating Systems course** at university. 📚🎓

---

## 🔥 Features

### 📃 Process Viewer
- **List Running Processes**: 🏃‍♂️ Displays all active processes with PID, Name, Priority, Memory, and CPU usage.
- **Auto Refresh**: 🔄 Updates process list every second for real-time monitoring.

### 💀 Kill Process
- **Kill by PID**: ❌ Enter a PID and terminate the selected process.

### 🧵 View Threads
- **Thread Visualization**: 🔍 View all threads of a given process.

### 📊 CPU & Memory Usage
- **System Usage Graphs**: 📈 Real-time bar graphs showing CPU and RAM utilization.

---

## 💻 Technologies Used

| Tech Stack | Purpose |
|:---------:|:--------|
| C (POSIX, pthreads, semaphores) | System process management backend |
| Python 3 (Tkinter, Matplotlib, psutil) | GUI frontend and graph plotting |
| Linux `/proc` filesystem | Fetching process and thread information |

---

## 🌐 Getting Started

### 🛠️ Prerequisites
- **Linux-based system** 🐧
- **C compiler** (e.g., `gcc`) 🛠️
- **Python 3.x** 🔵
- Install required Python packages:
  ```bash
  pip install matplotlib psutil
  ```

> If `tkinter` is missing:
> ```bash
> sudo apt-get install python3-tk
> ```

---

## 🔥 Installation & Running

### 📅 Clone the Repository
```bash
git clone https://github.com/your-username/4th-Semester-Operating-System-Project-Mini-Task-Manager-in-C-and-Python.git
cd 4th-Semester-Operating-System-Project-Mini-Task-Manager-in-C-and-Python
```

### ⚙️ Build the C Program
```bash
make
```
> This will create an executable called `task_manager`.

### 🚀 Run the C Backend
```bash
./task_manager
```
> Keeps generating `process_data.txt` every second with updated info.

### 🖥️ Launch the Python GUI
```bash
python3 gui.py
```
> GUI will display process list, kill options, thread viewer, and graphs.

---

## 📸 Screenshots

> *Add GUI screenshots here for more drip!*

---

## 📚 How It Works

The C program continuously reads the system’s `/proc` filesystem to gather process and thread details.  
It dumps this info into `process_data.txt`.  
Meanwhile, the Python GUI reads from this file to show real-time process stats, kill processes, and display CPU/Memory graphs.

**Backend & Frontend working together = Smooth Experience!** 🏯

---

## 🏏 Project Structure

```
Mini-Task-Manager/
├── task_manager.c         # C code to manage processes
├── gui.py                 # Python Tkinter-based GUI
├── Makefile               # Build automation for task_manager
├── process_data.txt       # Live-updated process information (auto-generated)
└── README.md              # Documentation file (this one!)
```

---

## ⚡ Important Notes

- Works only on **Linux/Unix** systems! (not Windows) 🐧
- GUI depends on real-time `process_data.txt` generation.
- Always run both the C backend and Python GUI **simultaneously**.

---

## 🧑‍💻 Developer

- **Name**: Muhammad Taha (aka Tee) 🚀
- **GitHub**: [BoltTaha](https://github.com/BoltTaha)

---

## 🎉 Contribution

Contributions, issues, and feature requests are welcome! 🌟

Feel free to fork the project and open a pull request.

---

## 🛡️ License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## 📢 Contact

- **GitHub**: [BoltTaha](https://github.com/BoltTaha)
- **Email**: *(your email if you want to add)*

---

🌟 **Feel free to explore, star ⭐ the repo, and enjoy building awesome projects!** 💪

