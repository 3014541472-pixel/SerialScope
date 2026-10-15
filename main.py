
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import math
import csv
from datetime import datetime

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from data_parser import parse_sensor_data


class SerialScope:

    def __init__(self, root):
        self.root = root
        self.root.title("SerialScope 4.0")
        self.root.geometry("1150x750")

        # Simulation settings
        self.sample = 0
        self.running = False

        # Data storage
        self.x_data = []
        self.y_data = []
        self.logs = []
        self.csv_data = []

        # Statistics
        self.rx_count = 0
        self.tx_count = 0

        self.build_interface()

    # -------------------------------
    # Build user interface
    # -------------------------------

    def build_interface(self):

        title = tk.Label(
            self.root,
            text="SerialScope 4.0",
            font=("Arial", 20, "bold")
        )
        title.pack(pady=10)

        subtitle = tk.Label(
            self.root,
            text="Serial Data Monitoring and Visualization",
            font=("Arial", 10)
        )
        subtitle.pack()

        # Control buttons
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill="x", padx=15, pady=10)

        ttk.Button(
            control_frame,
            text="Start Simulation",
            command=self.start_simulation
        ).pack(side="left", padx=5)

        ttk.Button(
            control_frame,
            text="Stop Simulation",
            command=self.stop_simulation
        ).pack(side="left", padx=5)

        ttk.Button(
            control_frame,
            text="Clear",
            command=self.clear_data
        ).pack(side="left", padx=5)

        ttk.Button(
            control_frame,
            text="Save Log",
            command=self.save_log
        ).pack(side="left", padx=5)

        ttk.Button(
            control_frame,
            text="Export CSV",
            command=self.export_csv
        ).pack(side="left", padx=5)

        self.status_label = tk.Label(
            control_frame,
            text="Status: Stopped",
            fg="red"
        )
        self.status_label.pack(side="right", padx=10)

        # Statistics
        stats_frame = tk.Frame(self.root)
        stats_frame.pack(fill="x", padx=20, pady=5)

        self.rx_label = tk.Label(
            stats_frame,
            text="RX: 0",
            font=("Arial", 12, "bold")
        )
        self.rx_label.pack(side="left", padx=15)

        self.tx_label = tk.Label(
            stats_frame,
            text="TX: 0",
            font=("Arial", 12, "bold")
        )
        self.tx_label.pack(side="left", padx=15)

        # Main content
        content = tk.Frame(self.root)
        content.pack(fill="both", expand=True, padx=15, pady=10)

        # Chart
        plot_frame = tk.LabelFrame(
            content,
            text="Real-time Sensor Data"
        )
        plot_frame.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)

        self.ax.set_title("Sensor Data")
        self.ax.set_xlabel("Sample Number")
        self.ax.set_ylabel("Sensor Value")
        self.ax.grid(True)

        self.line, = self.ax.plot(
            [], [],
            label="Sensor Value"
        )

        self.ax.legend()

        self.canvas = FigureCanvasTkAgg(
            self.figure,
            master=plot_frame
        )

        self.canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )

        # Receive monitor
        log_frame = tk.LabelFrame(
            content,
            text="Receive Monitor"
        )
        log_frame.pack(
            side="right",
            fill="both",
            expand=True,
            padx=10
        )

        self.log_box = tk.Text(
            log_frame,
            width=45,
            font=("Consolas", 10)
        )

        self.log_box.pack(
            fill="both",
            expand=True
        )

        # Send area
        send_frame = tk.LabelFrame(
            self.root,
            text="Send Data (Simulation Only)"
        )
        send_frame.pack(
            fill="x",
            padx=15,
            pady=10
        )

        self.send_entry = ttk.Entry(send_frame)
        self.send_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=10,
            pady=10
        )

        ttk.Button(
            send_frame,
            text="Send",
            command=self.send_data
        ).pack(side="right", padx=10)

    # -------------------------------
    # Logging
    # -------------------------------

    def add_log(self, message):

        timestamp = datetime.now().strftime("%H:%M:%S")

        log_line = f"[{timestamp}] {message}"

        self.logs.append(log_line)

        self.log_box.insert(
            tk.END,
            log_line + "\n"
        )

        self.log_box.see(tk.END)

    # -------------------------------
    # Start simulation
    # -------------------------------

    def start_simulation(self):

        if self.running:
            return

        self.running = True

        self.status_label.config(
            text="Status: Running (Simulation)",
            fg="green"
        )

        self.add_log("Simulation started")

        self.update_plot()

    # -------------------------------
    # Stop simulation
    # -------------------------------

    def stop_simulation(self):

        self.running = False

        self.status_label.config(
            text="Status: Stopped",
            fg="red"
        )

        self.add_log("Simulation stopped")

    # -------------------------------
    # Generate and parse data
    # -------------------------------

    def update_plot(self):

        if not self.running:
            return

        self.sample += 1

        # Generate raw sensor data
        raw_data = (
            f"DEVICE_DATA,ID={self.sample},"
            f"VALUE={25 + 5 * math.sin(self.sample * 0.2):.2f}"
        )

        # Parse raw data
        result = parse_sensor_data(raw_data)

        if result is not None:

            sensor_id = result["sensor_id"]
            value = result["value"]

            # Store parsed data
            self.x_data.append(sensor_id)
            self.y_data.append(value)

            self.csv_data.append([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                sensor_id,
                value
            ])

            # Keep the latest 50 points
            if len(self.x_data) > 50:
                self.x_data.pop(0)
                self.y_data.pop(0)

            # Update chart
            self.line.set_data(
                self.x_data,
                self.y_data
            )

            self.ax.relim()
            self.ax.autoscale_view()

            self.canvas.draw_idle()

            # Update RX
            self.rx_count += 1

            self.rx_label.config(
                text=f"RX: {self.rx_count}"
            )

            # Update log
            self.add_log(
                f"Received ID={sensor_id}, VALUE={value:.2f}"
            )

        else:

            self.add_log("Invalid sensor data")

        self.root.after(
            200,
            self.update_plot
        )

    # -------------------------------
    # Send simulated data
    # -------------------------------

    def send_data(self):

        message = self.send_entry.get().strip()

        if message:

            self.tx_count += 1

            self.tx_label.config(
                text=f"TX: {self.tx_count}"
            )

            self.add_log(
                f"TX: {message} (simulated only)"
            )

            self.send_entry.delete(0, tk.END)

    # -------------------------------
    # Clear data
    # -------------------------------

    def clear_data(self):

        self.x_data.clear()
        self.y_data.clear()
        self.csv_data.clear()

        self.sample = 0
        self.rx_count = 0
        self.tx_count = 0

        self.rx_label.config(text="RX: 0")
        self.tx_label.config(text="TX: 0")

        self.logs.clear()

        self.log_box.delete(
            "1.0",
            tk.END
        )

        self.line.set_data([], [])

        self.ax.relim()
        self.ax.autoscale_view()

        self.canvas.draw_idle()

    # -------------------------------
    # Save log
    # -------------------------------

    def save_log(self):

        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Text Files", "*.txt")
            ]
        )

        if path:

            with open(
                path,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(
                    "\n".join(self.logs)
                )

            messagebox.showinfo(
                "Success",
                "Log saved successfully!"
            )

    # -------------------------------
    # Export CSV
    # -------------------------------

    def export_csv(self):

        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[
                ("CSV Files", "*.csv")
            ]
        )

        if path:

            with open(
                path,
                "w",
                newline="",
                encoding="utf-8-sig"
            ) as file:

                writer = csv.writer(file)

                writer.writerow([
                    "Timestamp",
                    "Sensor ID",
                    "Sensor Value"
                ])

                writer.writerows(
                    self.csv_data
                )

            messagebox.showinfo(
                "Success",
                "CSV exported successfully!"
            )


# -------------------------------
# Main program
# -------------------------------

if __name__ == "__main__":

    root = tk.Tk()

    app = SerialScope(root)

    root.mainloop()
