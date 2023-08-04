from PyP100 import PyP110
import psutil
import time
import atexit
import threading
import json
import tkinter as tk
import tkinter.messagebox as messagebox


def load_credentials_from_json(file_path):
    with open(file_path) as json_file:
        data = json.load(json_file)

        ip = data.get("ip")
        login = data.get("login")
        password = data.get("password")

        return ip, login, password


file_path = "credentials.json"
ip, login, password = load_credentials_from_json(file_path)
p110 = PyP110.P110(ip, login, password)


def how_to_use(log_text):
    f = open('how_to_use.txt', 'r')
    file_contents = f.read()
    update_logs(log_text, file_contents)
    f.close()


def update_logs(log_text, message):
    log_text.config(state=tk.NORMAL)
    log_text.insert('1.0', message + "\n")
    log_text.config(state=tk.DISABLED)


def show_dialog_and_play_sound(Title, Text):
    messagebox.showinfo(Title, Text)


power_manager_running = False
power_indicator_running = False
button3_active = False


def run_power_manager(log_text):

    p110.handshake()
    p110.login()
    p110.turnOff()

    global power_manager_running

    update_logs(log_text, "Active control is running.")

    while power_manager_running:
        battery = psutil.sensors_battery()
        percent = battery.percent
        percentToString = str(percent)

        update_logs(log_text, "Battery level: " + percentToString + "%")

        def goodbye():
            update_logs(log_text, "Goodbye.")
            p110.turnOff()

        if percent >= 80:
            update_logs(log_text, "Charger is unplugged.")
            p110.turnOff()
        elif percent <= 30:
            update_logs(log_text, "Charger is plugged.")
            p110.turnOn()

        atexit.register(goodbye)
        time.sleep(120)  # 2 minutes


def start_power_manager(log_text, start_button, stop_button):
    global power_manager_running

    if not power_manager_running:
        power_manager_running = True

        start_button.config(state=tk.DISABLED)

        stop_button.config(state=tk.NORMAL)

        power_manager_thread = threading.Thread(
            target=run_power_manager, args=(log_text,))
        power_manager_thread.start()


def stop_power_manager(log_text, start_button, stop_button):
    global power_manager_running

    if power_manager_running:
        power_manager_running = False

        stop_button.config(state=tk.DISABLED)

        start_button.config(state=tk.NORMAL)

        update_logs(
            log_text, "Active control was stopped by the user. Charging stopped.")
        p110.turnOff()


def check_battery_level(log_text):
    global power_indicator_running

    update_logs(log_text, "Power level indicator is running.")

    def battery_level_thread():
        while power_indicator_running:
            battery = psutil.sensors_battery()
            percentage = battery.percent
            percentToString = str(percentage)

            update_logs(log_text, "Battery level: " + percentToString + "%")

            if percentage >= 80:
                show_dialog_and_play_sound(
                    "Alert", "Battery level is 80% or higher!")
            elif percentage <= 30:
                show_dialog_and_play_sound(
                    "Alert", "Battery level is 30% or lower!")

            time.sleep(300)

    battery_thread = threading.Thread(target=battery_level_thread)
    battery_thread.start()

    button4.config(
        state=tk.NORMAL if power_indicator_running and not button3_active else tk.DISABLED)


def enable_check_battery_level():
    global power_indicator_running, button3_active
    update_logs(log_text, "Power level indicator was started.")
    power_indicator_running = True
    button3_active = True
    check_battery_level(log_text)
    button3.config(state=tk.DISABLED)
    button4.config(state=tk.NORMAL)


def disable_check_battery_level():
    button4.config(state=tk.DISABLED)
    global power_indicator_running, button3_active
    button3_active = False
    button3.config(state=tk.NORMAL)
    update_logs(log_text, "Power level indicator was stopped by the user.")
    power_indicator_running = False


def start_charging(log_text):
    update_logs(log_text, "Charging started.")
    p110.turnOn()


def stop_charging(log_text):
    update_logs(log_text, "Charging stopped.")
    p110.turnOff()


window = tk.Tk()
window.iconbitmap("pmIco.ico")
window.title("Power Manager")
window.resizable(0, 0)

top_label = tk.Label(window, text="Power Manager v.1.0")
top_label.pack()

second_label = tk.Label(window, text="by Paweł Baraszkiewicz")
second_label.pack()

third_label = tk.Label(window, text="https://github.com/pbaraszkiewicz2")
third_label.pack()

button_frame = tk.Frame(window)
button_frame.pack()

log_text = tk.Text(window, height=26, state=tk.DISABLED)
scrollbar = tk.Scrollbar(window, command=log_text.yview)
log_text.config(yscrollcommand=scrollbar.set)
log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

button1 = tk.Button(button_frame, text="Run active control",
                    command=lambda: start_power_manager(log_text, button1, button2))
button1.pack(side=tk.LEFT)

button2 = tk.Button(button_frame, text="Stop active control", state=tk.DISABLED,
                    command=lambda: stop_power_manager(log_text, button1, button2))
button2.pack(side=tk.LEFT)

button3 = tk.Button(button_frame, text="Run power level indicator",
                    command=enable_check_battery_level)
button3.pack(side=tk.LEFT)

button4 = tk.Button(button_frame, text="Stop power level indicator", state=tk.DISABLED,
                    command=disable_check_battery_level)
button4.pack(side=tk.LEFT)

button5 = tk.Button(button_frame, text="Start charging",
                    command=lambda: start_charging(log_text))
button5.pack(side=tk.LEFT)

button6 = tk.Button(button_frame, text="Stop charging",
                    command=lambda: stop_charging(log_text))
button6.pack(side=tk.LEFT)

button7 = tk.Button(button_frame, text="How to use?",
                    command=lambda: how_to_use(log_text))
button7.pack(side=tk.LEFT)

how_to_use(log_text)

window.mainloop()
