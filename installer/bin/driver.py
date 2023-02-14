from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from time import sleep


class Driver:
    class Logging:
        trying = lambda msg: print("[TRY] {}".format(msg))
        loading = lambda msg: print("[LOAD] {}".format(msg))
        success = lambda msg: print("[SUCCESS] {}".format(msg))
        failed = lambda msg: print("[FAILED] {}".format(msg))

    def __init__(self, max_tries:int=20, timeout:int=200):
        self.max_tries:int = max_tries
        self.timeout:float = timeout/1000
        self.__init()

    def __init(self):
        self.driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))
        self.driver.fullscreen_window()
    
    def get(self, url) -> bool:
        for _ in range(self.max_tries):
            try:
                self.driver.get(url)
                return True
            except Exception:
                self.Logging.failed("An error occurred fetching {}".format(url))
                sleep(self.timeout)
        return False

if __name__ == "__main__":
    driver = Driver()
    driver.get("F:\MONITOR_CHEF\philips\pdf\BILD_TEST.pdf")