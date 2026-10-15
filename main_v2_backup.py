
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import math


class SerialScopeApp:

    def __init__(self, root):
        self.root = root
        self.root.title("SerialScope 2.0 - Device Monitor")
        self.root.geometry("900x650")
        self.root.minsize(750, 500)

        self.simulation_running = False
        self.sample_number = 0
        self.received_count = 0
        self.sent_count = 0
        self.log_lines = []

        self.create_interface()
        self.write_log("SerialScope 2.0 started.")
        self.write_log("Simulation mode is ready.")

    def create_interface(self):

        # 标题
        title = ttk.Label(
            self.root,
            text="SerialScope",
            font=("Arial", 24, "bold")
        )
        title.pack(pady=12)

        subtitle = ttk.Label(
            self.root,
            text="Serial Communication & Device Monitoring System"
        )
        subtitle.pack()

        # 模式
        self.status_label = ttk.Label(
            self.root,
            text="STATUS: SIMULATION MODE",
            foreground="green"
        )
        self.status_label.pack(pady=8)

        # 参数区域
        settings = ttk.LabelFrame(
            self.root,
            text="Communication Settings",
            padding=10
        )
        settings.pack(fill="x", padx=15, pady=10)

        ttk.Label(settings, text="Mode:").grid(
            row=0, column=0, padx=5
        )

        self.mode_box = ttk.Combobox(
            settings,
            values=["Simulation"],
            state="readonly",
            width=15
        )
        self.mode_box.current(0)
        self.mode_box.grid(row=0, column=1, padx=5)

        ttk.Label(settings, text="Baud Rate:").grid(
            row=0, column=2, padx=5
        )

        self.baud_box = ttk.Combobox(
            settings,
            values=["9600", "19200", "38400", "57600", "115200"],
            state="readonly",
            width=12
        )
        self.baud_box.set("115200")
        self.baud_box.grid(row=0, column=3, padx=5)

        # 控制按钮
        controls = ttk.Frame(self.root)
        controls.pack(pady=8)

        self.start_button = ttk.Button(
            controls,
            text="Start Simulation",
            command=self.start_simulation
        )
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = ttk.Button(
            controls,
            text="Stop Simulation",
            command=self.stop_simulation,
            state="disabled"
        )
        self.stop_button.grid(row=0, column=1, padx=5)

        ttk.Button(
            controls,
            text="Clear",
            command=self.clear_monitor
        ).grid(row=0, column=2, padx=5)

        ttk.Button(
            controls,
            text="Save Log",
            command=self.save_log
        ).grid(row=0, column=3, padx=5)

        # 接收区域
        receive_frame = ttk.LabelFrame(
            self.root,
            text="Receive Monitor",
            padding=8
        )
        receive_frame.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=8
        )

        self.output = tk.Text(
            receive_frame,
            height=16,
            wrap="word",
            font=("Consolas", 10)
        )
        self.output.pack(fill="both", expand=True)

        # 发送区域
        send_frame = ttk.LabelFrame(
            self.root,
            text="Send Data",
            padding=10
        )
        send_frame.pack(fill="x", padx=15, pady=8)

        self.input_box = ttk.Entry(send_frame)
        self.input_box.pack(
            side="left",
            fill="x",
            expand=True,
            padx=5
        )

        self.input_box.bind(
            "<Return>",
            lambda event: self.send_message()
        )

        ttk.Button(
            send_frame,
            text="Send",
            command=self.send_message
        ).pack(side="right", padx=5)

        # 统计区域
        self.stats_label = ttk.Label(
            self.root,
            text="RX: 0 | TX: 0"
        )
        self.stats_label.pack(pady=8)

    def write_log(self, message):

        timestamp = datetime.now().strftime("%H:%M:%S")

        line = f"[{timestamp}] {message}"

        self.output.insert(tk.END, line + "\n")
        self.output.see(tk.END)

        self.log_lines.append(line)

    def start_simulation(self):

        if self.simulation_running:
            return

        self.simulation_running = True

        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")

        self.status_label.config(
            text="STATUS: RUNNING",
            foreground="green"
        )

        self.write_log("Simulation started.")

        self.generate_data()

    def stop_simulation(self):

        self.simulation_running = False

        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")

        self.status_label.config(
            text="STATUS: STOPPED",
            foreground="red"
        )

        self.write_log("Simulation stopped.")

    def generate_data(self):

        if not self.simulation_running:
            return

        self.sample_number += 1

        # 模拟设备产生的数据
        value = 25 + 5 * math.sin(
            self.sample_number * 0.2
        )

        message = (
            f"DEVICE_DATA,"
            f"ID={self.sample_number},"
            f"VALUE={value:.2f}"
        )

        self.received_count += 1

        self.write_log("RX: " + message)

        self.update_statistics()

        # 500 毫秒后再次生成数据
        self.root.after(500, self.generate_data)

    def send_message(self):

        message = self.input_box.get().strip()

        if not message:
            return

        self.sent_count += 1

        self.write_log("TX: " + message)

        self.input_box.delete(0, tk.END)

        self.update_statistics()

    def update_statistics(self):

        self.stats_label.config(
            text=(
                f"RX: {self.received_count} messages"
                f" | TX: {self.sent_count} messages"
            )
        )

    def clear_monitor(self):

        self.output.delete("1.0", tk.END)

        self.log_lines = []

        self.write_log("Monitor cleared.")

    def save_log(self):

        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")],
            initialfile="SerialScope_Log.txt"
        )

        if not filename:
            return

        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as file:

            file.write("\n".join(self.log_lines))

        messagebox.showinfo(
            "Success",
            "Communication log saved successfully!"
        )


if __name__ == "__main__":

    root = tk.Tk()

    app = SerialScopeApp(root)

    root.mainloop()