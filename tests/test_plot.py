
import tkinter as tk
import math

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


root = tk.Tk()
root.title("SerialScope - Live Data Plot")
root.geometry("800x500")

# 创建绘图区域
figure = Figure(figsize=(8, 4), dpi=100)
ax = figure.add_subplot(111)

ax.set_title("Simulated Sensor Data")
ax.set_xlabel("Sample Number")
ax.set_ylabel("Sensor Value")
ax.grid(True)

line, = ax.plot([], [], label="Sensor Value")
ax.legend()

canvas = FigureCanvasTkAgg(figure, master=root)
canvas.get_tk_widget().pack(fill="both", expand=True)

# 数据存储
x_data = []
y_data = []

sample = 0


def update_plot():

    global sample

    sample += 1

    value = 25 + 5 * math.sin(sample * 0.2)

    x_data.append(sample)
    y_data.append(value)

    # 只保留最近 50 个数据点
    if len(x_data) > 50:
        x_data.pop(0)
        y_data.pop(0)

    line.set_data(x_data, y_data)

    ax.relim()
    ax.autoscale_view()

    canvas.draw_idle()

    root.after(200, update_plot)


update_plot()

root.mainloop()
