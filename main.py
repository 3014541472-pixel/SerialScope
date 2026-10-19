"""SerialScope: simulation and real serial acquisition, without blocking reads."""
import csv
import math
import tkinter as tk
from collections import deque
from datetime import datetime
from tkinter import ttk, filedialog, messagebox
import serial
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from data_parser import parse_sensor_data
from serial_manager import SerialManager


class SerialScope:
    LIMIT = 100000

    def __init__(self, root):
        self.root = root
        root.title('SerialScope — STM32 Data Monitor')
        root.geometry('1100x750')
        self.manager = SerialManager()
        self.mode = 'stopped'
        self.sample = self.rx_count = self.tx_count = self.invalid = 0
        self.points = deque(maxlen=200)
        self.records = deque(maxlen=self.LIMIT)
        self.logs = deque(maxlen=2000)
        self.port = tk.StringVar()
        self.baud = tk.StringVar(value='115200')
        self.status = tk.StringVar(value='Stopped')
        self.stats = tk.StringVar()
        top = ttk.Frame(root, padding=10)
        top.pack(fill='x')
        self.ports = ttk.Combobox(top, textvariable=self.port, width=18)
        self.ports.pack(side='left')
        for label, command in [('Refresh', self.refresh)]:
            ttk.Button(top, text=label, command=command).pack(side='left', padx=3)
        ttk.Combobox(top, textvariable=self.baud, values=['9600', '19200', '57600', '115200'], width=9).pack(side='left')
        for label, command in [('Connect', self.connect), ('Stop / Disconnect', self.stop),
                               ('Simulate', self.simulate), ('Clear', self.clear)]:
            ttk.Button(top, text=label, command=command).pack(side='left', padx=3)
        ttk.Label(root, textvariable=self.status).pack()
        ttk.Label(root, textvariable=self.stats).pack()
        figure = Figure(figsize=(8, 4), dpi=100)
        self.ax = figure.add_subplot(111)
        self.ax.set(xlabel='Sequence (ID)', ylabel='Value (V for supplied ADC firmware)', title='Latest 200 samples')
        self.ax.grid(True)
        self.line, = self.ax.plot([], [])
        self.canvas = FigureCanvasTkAgg(figure, master=root)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        self.log_box = tk.Text(root, height=9, state='disabled')
        self.log_box.pack(fill='x', padx=10)
        bottom = ttk.Frame(root, padding=10)
        bottom.pack(fill='x')
        self.entry = ttk.Entry(bottom)
        self.entry.pack(side='left', fill='x', expand=True)
        for label, command in [('Send', self.send), ('Export CSV', self.export), ('Save Log', self.save_log)]:
            ttk.Button(bottom, text=label, command=command).pack(side='left', padx=3)
        root.protocol('WM_DELETE_WINDOW', self.close)
        self.refresh()
        self.update_stats()
        self.timer = root.after(50, self.poll)

    def log(self, message):
        line = f'[{datetime.now().isoformat(timespec="seconds")}] {message}'
        self.logs.append(line)
        self.log_box.configure(state='normal')
        self.log_box.insert('end', line + '\n')
        # Bound visible log as well as in-memory log.
        if int(self.log_box.index('end-1c').split('.')[0]) > 201:
            self.log_box.delete('1.0', '2.0')
        self.log_box.see('end')
        self.log_box.configure(state='disabled')

    def update_stats(self):
        self.stats.set(f'Valid frames: {self.rx_count} | Invalid frames: {self.invalid} | Sent messages: {self.tx_count} | Saved samples: {len(self.records)} / {self.LIMIT}')

    def refresh(self):
        try:
            ports = self.manager.list_ports()
            self.ports['values'] = ports
            if ports and not self.port.get():
                self.port.set(ports[0])
        except (OSError, serial.SerialException) as error:
            self.log(f'Port scan: {error}')

    def stop(self):
        self.mode = 'stopped'
        try:
            self.manager.disconnect()
        except (OSError, serial.SerialException) as error:
            self.log(f'Disconnect: {error}')
        self.status.set('Stopped')

    def connect(self):
        self.stop()
        if not self.port.get().strip():
            messagebox.showerror('Connection', 'Select a serial port first.')
            return
        ok, detail = self.manager.connect(self.port.get().strip(), self.baud.get())
        self.log(detail)
        if ok:
            self.mode = 'serial'
            self.status.set(f'Real serial: {self.port.get()} / {self.baud.get()} baud, 8N1')
        else:
            messagebox.showerror('Connection failed', detail)

    def simulate(self):
        self.stop()
        self.mode = 'simulation'
        self.status.set('Simulation — generated values, not hardware measurements')
        self.log('Simulation started')

    def accept(self, raw):
        parsed = parse_sensor_data(raw)
        if parsed is None:
            self.invalid += 1
            self.log(f'Invalid frame: {raw[:100]}')
            return
        self.rx_count += 1
        self.points.append((parsed['sensor_id'], parsed['value']))
        self.records.append((datetime.now().isoformat(timespec='milliseconds'), self.mode,
                             parsed['sensor_id'], parsed['value']))
        self.log(f'{self.mode}: {raw}')

    def poll(self):
        try:
            if self.mode == 'simulation':
                self.sample += 1
                self.accept(f'DEVICE_DATA,ID={self.sample},VALUE={1.65 + math.sin(self.sample * .1):.3f}')
            elif self.mode == 'serial':
                for raw in self.manager.read_lines():
                    self.accept(raw)
            if self.points:
                x, y = zip(*self.points)
                self.line.set_data(x, y)
                self.ax.relim()
                self.ax.autoscale_view()
                self.canvas.draw_idle()
            self.update_stats()
        except (serial.SerialException, OSError) as error:
            self.log(f'Serial error: {error}; reconnect with Connect')
            self.stop()
        finally:
            self.timer = self.root.after(50, self.poll)

    def send(self):
        text = self.entry.get().strip()
        if not text:
            return
        if self.mode != 'serial':
            self.log('Send requires a real serial connection')
            return
        try:
            if self.manager.send_data(text):
                self.tx_count += 1
                self.log(f'TX: {text}')
                self.entry.delete(0, 'end')
                self.update_stats()
        except (serial.SerialException, OSError) as error:
            self.log(f'Send failed: {error}')
            self.stop()

    def clear(self):
        self.points.clear()
        self.records.clear()
        self.logs.clear()
        self.rx_count = self.tx_count = self.invalid = 0
        self.line.set_data([], [])
        self.canvas.draw_idle()
        self.log_box.configure(state='normal')
        self.log_box.delete('1.0', 'end')
        self.log_box.configure(state='disabled')
        self.update_stats()

    def export(self):
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV', '*.csv')])
        if path:
            try:
                with open(path, 'w', newline='', encoding='utf-8-sig') as output:
                    writer = csv.writer(output)
                    writer.writerow(['timestamp', 'source', 'sequence_id', 'value'])
                    writer.writerows(self.records)
            except OSError as error:
                messagebox.showerror('Export failed', str(error))

    def save_log(self):
        path = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text', '*.txt')])
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as output:
                    output.write('\n'.join(self.logs))
            except OSError as error:
                messagebox.showerror('Save failed', str(error))

    def close(self):
        self.root.after_cancel(self.timer)
        self.stop()
        self.root.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    SerialScope(root)
    root.mainloop()
