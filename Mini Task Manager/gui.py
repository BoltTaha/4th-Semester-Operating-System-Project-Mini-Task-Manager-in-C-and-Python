import subprocess
from tkinter import *
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import psutil

# ---------------------------------------------------------------------------------------------------------------------------------------

pid_entry = None

# Function to list processes (reads from process_data.txt)
def list_processes():

    for widget in frame_right.winfo_children():
        widget.destroy()  


    header = Label(frame_right, text="Processes Info", font=("Arial", 26, "bold"), fg="white", bg="#333333")
    header.pack(pady=(25,45))



    try:
        with open("process_data.txt", "r") as file:
            lines = file.readlines()

            
            col_header = Label(frame_right, text=f"{'PID':<8} {'Name':<30} {'Prio':<6} {'Memory(KB)':<12} {'CPU%'}", font=("Courier", 16, "bold"), fg="white", bg="#1e1e1e")
            col_header.pack(anchor="w", pady=10)
            
            

            # This part creates a scrollable area
            canvas_frame = Frame(frame_right)
            canvas_frame.pack(fill=BOTH, expand=True)



            # The actual Canvas for drawing/scrolling
            canvas = Canvas(canvas_frame, bg="#1e1e1e")
            
            
            
            # vertical scrollbar to the side
            scroll_bar = Scrollbar(canvas_frame, orient=VERTICAL, command=canvas.yview)
            scroll_bar.pack(side=RIGHT, fill=Y)
            
            
            canvas.pack(side=LEFT, fill=BOTH, expand=True)

            canvas.configure(yscrollcommand=scroll_bar.set)

            process_list_frame = Frame(canvas, bg="#1e1e1e")
            canvas.create_window((0, 0), window=process_list_frame, anchor="nw")

            for line in lines:
                parts = line.strip().split(",")
                if len(parts) == 5:
                    pid, name, prio, mem, cpu = parts
                    info = f"{pid:<8} {name:<40} {prio:<6} {mem:<12} {cpu}"
                    process_label = Label(process_list_frame, text=info, font=("Courier", 14), fg="white", bg="#1e1e1e")
                    process_label.pack(anchor="w", pady=5)

            # Update scroll region after adding content
            canvas.update_idletasks()
            canvas.config(scrollregion=canvas.bbox("all"))




    except FileNotFoundError:
        messagebox.showerror("Error", "process_data.txt not found. Please run the C program first.")






# ---------------------------------------------------------------------------------------------------------------------------------------






def kill_process():


    global pid_entry

    for widget in frame_right.winfo_children():
        widget.destroy() 

    Label(frame_right, text="Kill a Process by PID", font=("Arial", 30, "bold"), fg="white", bg="#1e1e1e").pack(pady=(150,50))

    Label(frame_right, text="Enter PID:", font=("Arial", 22), fg="white", bg="#1e1e1e").pack(pady=20)
    
    pid_entry = Entry(frame_right, font=("Arial", 17), width=30,
                      bg="#2c2c2c", fg="white", insertbackground="white", bd=2, relief=FLAT)
    pid_entry.pack(pady=5)
    
    
    kill_process_by_id = Button(frame_right, text="Search", font=("Arial", 18), bg="#00adb5", fg="white", bd=0, command=run_kill_process)
    kill_process_by_id.pack(pady=20, ipadx=30, ipady=10)
    
    
    
    
    
    
# ---------------------------------------------------------------------------------------------------------------------------------------    
    
    
    
    

def run_kill_process():

    pid = pid_entry.get()
    

    if not pid.isdigit():
        messagebox.showerror("Invalid PID", "Please enter a valid numeric PID.")
        return   

    try:
        result = subprocess.run(["./task_manager", pid], capture_output=True, text=True)

        if "does not exist" in result.stdout:
            messagebox.showerror("Error", f"Process {pid} does not exist.")
        elif "killed successfully" in result.stdout:
            messagebox.showinfo("Success", f"Process {pid} killed successfully.")
        else:
            messagebox.showerror("Error", f"Failed to kill process {pid}.")

    except FileNotFoundError:
        messagebox.showerror("Error", "kill_process executable not found. Please compile your C file first.")
    
    
    
    
    
#-----------------------------------------------------------------------------------------------------------------------------------------



def show_threads_in_frame(pid):
    result = subprocess.run(["./task_manager", "--threads", str(pid)], capture_output=True, text=True)
    output = result.stdout

    # Clear the right frame first
    for widget in frame_right.winfo_children():
        widget.destroy()

    # Show each line as a label in the frame
    for line in output.strip().split('\n'):
        label = Label(frame_right, text=line, anchor='w', justify='left')
        label.pack(fill='x', padx=10, pady=2)
        
        
#------------------------------------------------------------------------------------------------------------------------------------------


def view_thread():
    for widget in frame_right.winfo_children():
        widget.destroy()

    Label(frame_right, text="View Threads of a Process", font=("Arial", 30, "bold"), fg="white", bg="#1e1e1e").pack(pady=(150, 50))

    Label(frame_right, text="Enter PID:", font=("Arial", 22), fg="white", bg="#1e1e1e").pack(pady=20)

    thread_pid_entry = Entry(frame_right, font=("Arial", 17), width=30,
                             bg="#2c2c2c", fg="white", insertbackground="white", bd=2, relief=FLAT)
    thread_pid_entry.pack(pady=5)
    
    
    
    
    

    def fetch_threads():
        pid = thread_pid_entry.get()
        if not pid.isdigit():
            messagebox.showerror("Invalid PID", "Please enter a valid numeric PID.")
            return
        show_threads_in_frame(pid)

    Button(frame_right, text="Show Threads", font=("Arial", 18), bg="#00adb5", fg="white", bd=0,
           command=fetch_threads).pack(pady=20, ipadx=30, ipady=10)
           
                               
    
    
#------------------------------------------------------------------------------------------------------------------------------------------    
    
# Placeholder for CPU/Memory Graph


def show_graph():
    for widget in frame_right.winfo_children():
        widget.destroy()

    # Get overall CPU and memory usage
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    memory_usage = memory.percent

    # Bigger figure to suit 1300x800 frame
    fig, ax = plt.subplots(figsize=(13, 7.5), dpi=100)

    # Plot bars
    bars = ax.bar(["CPU Usage", "Memory Usage"], [cpu_usage, memory_usage], color=["#1f77b4", "#ff7f0e"], width=0.4)

    # Annotate values on top
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 2, f'{height:.1f}%', ha='center', fontsize=18, fontweight='bold')

    ax.set_ylim(0, 100)
    ax.set_ylabel("Usage (%)", fontsize=14)
    ax.set_title("Overall System Usage", fontsize=20, pad=20)
    ax.grid(axis='y', linestyle='--', alpha=0.6)
    ax.tick_params(axis='both', labelsize=14)

    plt.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=frame_right)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=10)








# ---------------------------------------------------------------------------------------------------------------------------------------




# Main window
root = Tk()
root.title("Task Manager - Main")
root.geometry("1900x1000")
root.configure(bg="#252525")

frame_left = Frame(root, bg="#2c2c2c", bd=2, relief=RAISED)
frame_left.place(relx=0.12, rely=0.5, anchor=CENTER, width=350, height=800)

lbl_title = Label(frame_left, text="Task Manager", font=("Arial", 22, "bold"), fg="white", bg="#2c2c2c")
lbl_title.pack(pady=70)

view_process_button = Button(frame_left, text="View Processes", font=("Arial", 14), bg="#00adb5", fg="white", bd=0, command=list_processes)
view_process_button.pack(pady=20, ipadx=30, ipady=10)

graph_button = Button(frame_left, text="CPU/Memory Graph", font=("Arial", 14), bg="#00adb5", fg="white", bd=0, command=show_graph)
graph_button.pack(pady=20, ipadx=10, ipady=10)


kill_process_button = Button(frame_left, text="Kill Process", font=("Arial", 14), bg="#00adb5", fg="white", bd=0, command=kill_process)
kill_process_button.pack(pady=20, ipadx=30, ipady=10)

thread_button = Button(frame_left, text="View threads", font=("Arial", 14), bg="#00adb5", fg="white", bd=0, command=view_thread)
thread_button.pack(pady=20, ipadx=10, ipady=10)


refresh_button = Button(frame_left, text="Refresh", font=("Arial", 14), bg="#00adb5", fg="white", bd=0, command=list_processes)
refresh_button.pack(pady=(155, 0), ipadx=30, ipady=10)


frame_right = Frame(root, bg="#1e1e1e", bd=2, relief=RIDGE)
frame_right.place(relx=0.60, rely=0.5, anchor=CENTER, width=1300, height=800)

initial_label = Label(frame_right, text="Select an action from the sidebar", font=("Arial", 18), fg="white", bg="#1e1e1e")
initial_label.pack(expand=True)

root.mainloop()
