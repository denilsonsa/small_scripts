#!/usr/bin/env python
# vi:ts=4 sw=4 et

# Quick and dirty script to keep refreshing a page and telling the user
# whenever it changes. Useful to be notified when your teacher finally
# publishes the grades.
#
# I've originally posted this script at:
# https://gist.github.com/740278

import datetime
import urllib.error
import urllib.request
import tkinter


SITE_URL = "http://equipe.nce.ufrj.br/eber/FES20102/default2.htm"
TIME_BETWEEN_CHECKS = 5*60*1000  # 5min * 60s * 1000ms


def now():
    return datetime.datetime.now().strftime("%H:%M")


class AlertWindow(tkinter.Toplevel):
    def __init__(self, message):
        tkinter.Toplevel.__init__(self)

        self.title(message)

        self.message = tkinter.StringVar()
        self.message.set(message)

        self.message_label = tkinter.Label(self, textvariable=self.message, anchor="w", justify="left", padx=32, pady=32)
        self.message_label.pack(fill="both", expand=1)


class MainWindow(tkinter.Tk):
    def __init__(self):
        tkinter.Tk.__init__(self)

        self.after_id = None
        self.compare_against = ""

        self.title("Watching a site...")

        self.header_label = tkinter.Label(self, text="Watching this URL for changes every {1} seconds:\n{0}".format(SITE_URL, TIME_BETWEEN_CHECKS//1000), anchor="w", justify="left")
        self.header_label.pack(fill="both", expand=1)

        self.message = tkinter.StringVar()
        self.message_label = tkinter.Label(self, textvariable=self.message, anchor="w", justify="left")
        self.message_label.pack(fill="both", expand=1)

        # Global quit handlers
        self.bind_all("<Control-q>", self.quit_handler)
        self.protocol("WM_DELETE_WINDOW", self.quit_handler)

    def quit_handler(self, event=None):
        self.destroy()

    def start_timer(self):
        self.after_id = self.after(TIME_BETWEEN_CHECKS, self.check_for_changes)

    def get_url(self):
        return urllib.request.urlopen(SITE_URL).read()

    def first_check(self):
        try:
            self.message.set("[{0}] Getting the inital data...".format(now()))
            self.compare_against = self.get_url()
            self.start_timer()
            self.message.set("[{0}] Waiting for the next check...".format(now()))
        except urllib.error.URLError as e:
            self.message.set("[{0}] Error while getting the inital data:\n{1}\nThis program won't work, please restart it.".format(now(), e.reason))

    def check_for_changes(self):
        try:
            self.message.set("[{0}] Checking URL...".format(now()))
            new_data = self.get_url()

            if new_data == self.compare_against:
                self.start_timer()
                self.message.set("[{0}] No changes yet. Waiting for the next check...".format(now()))
            else:
                self.message.set("[{0}] The contents have changed! \\o/".format(now()))
                self.message_label.config(fg="red")
                self.alert_window = AlertWindow("[{0}] The contents have changed! \\o/".format(now()))

        except urllib.error.URLError as e:
            self.start_timer()
            self.message.set("[{0}] Error while getting the URL:\n{1}\nTrying again later...".format(now(), e.reason))


def main():
    win = MainWindow()
    win.first_check()
    win.mainloop()


if __name__ == "__main__":
    main()
