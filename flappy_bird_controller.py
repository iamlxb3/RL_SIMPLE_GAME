import win32com.client as comctl
import time


class PlayerController:
    def __init__(self, app):
        self.app = app
        self.wsh = comctl.Dispatch("WScript.Shell")

    def activate_chrome(self):
        self.wsh.AppActivate(self.app)

    def _press_key_space(self, space_timer):
        self.wsh.SendKeys("{ }")
        space_timer.t1 = time.time()

    def press_key_space_n_times(self, n):
        interval_t = 0.1
        for i in range(n):
            time.sleep(interval_t)
            self.wsh.SendKeys("{ }")
