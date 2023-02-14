import os
import requests
from time import sleep, time
from driver import Driver
from moviepy.editor import VideoFileClip
from threading import Thread
from datetime import datetime
import socket
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
import pythoncom
import psutil

URL = "10.10.5.221:80"


class Main:
    def __init__(self):
        self.accepted_ext_pic = ["jpg", "png", "jpeg", "jfif"]
        self.accepted_ext_vid = ["mp4", "avi"]
        self.refresh_rate = 1

        self.on = True
        self.slide_speed = 0
        self.filepath = "//ocapp.corp.schatte.de/monitor_data"
        self.from_ = "00:00"
        self.to_ = "00:00"
        self.play_news = True
        self.driver = Driver()

        self.connect()

    def init(self):
        while True:
            for path, _, files in os.walk(self.filepath):
                for f in files:
                    try:
                        if not self.on:
                            self.driver.get(
                                os.path.abspath("./assets/black.jpg"))
                            while not self.on:
                                pass
                        ext = f.split(".")[-1]
                        if ext in self.accepted_ext_pic:
                            self.driver.get("file:\\\\\\" + path + "\\" + f)
                            sleep(self.slide_speed)
                        if ext in self.accepted_ext_vid:
                            news = False
                            if f == "news.mp4":
                                news = True
                                if not self.play_news:
                                    continue
                            clp = VideoFileClip(path + "\\" + f)
                            self.driver.get("file:\\\\\\" + path + "\\" + f)
                            if news:
                                now = time()
                                while self.play_news and time() - now <= clp.duration:
                                    sleep(1)
                            else:
                                sleep(clp.duration)
                        if ext == "pdf":
                            pass
                    except Exception:
                        print("File cannot be displayed")

    def connect(self):
        mac_addy = psutil.net_if_addrs()['Ethernet'][0].address.replace("-", ":")
        resp = requests.post("http://{}/update".format(URL), json={
            "pc_name": socket.gethostname(),
            "ip": socket.gethostbyname(socket.gethostname()),
            "mac_address": mac_addy
        })
        if resp.status_code == 200:
            if resp.text != "Monitor created":
                data = resp.json()
                self.on = data["on"]
                self.slide_speed = int(data["play_time"])
                self.from_ = data["news_from"]
                self.to_ = data["news_to"]
                self.play_news = data["play_news"]
        else:
            print("Error connecting the monitor to the database")
            quit()
        Thread(target=self.update, daemon=True).start()
        Thread(target=self.audio_control, daemon=True).start()

    def update(self):
        resp = False
        while True:
            sleep(self.refresh_rate)
            resp = requests.get(
                "http://{}/update?monitor=".format(URL)+socket.gethostname())
            if resp.status_code == 200:
                resp = resp.json()
                if not resp["on"] and resp["on"] != self.on:
                    os.system("shutdown -f -s -t 0")
                self.on = resp["on"]
                self.slide_speed = int(resp["play_time"])
                self.from_ = resp["news_from"]
                self.to_ = resp["news_to"]
                self.play_news = resp["play_news"]
                resp = None
            else:
                if not resp:
                    resp = None
                    print("Could not fetch new updates!")

    def audio_control(self):
        pythoncom.CoInitialize()
        while True:
            hour = int(datetime.now().strftime("%H"))
            sessions = AudioUtilities.GetAllSessions()
            for session in sessions:
                volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                if session.Process and session.Process.name() == "firefox.exe":
                    if hour < int(self.to_.split(":")[0]) and hour >= int(self.from_.split(":")[0]):
                        volume.SetMasterVolume(1.0, None)
                    else:
                        volume.SetMasterVolume(0.0, None)

    def stop(self):
        self.driver.driver.quit()


if __name__ == "__main__":
    main = Main()
    try:
        main.init()
    except:
        main.stop()
