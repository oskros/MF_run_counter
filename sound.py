import os
import queue
import sys
import threading
import winsound


class ThreadedSound(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        winsound.PlaySound(os.path.join(getattr(sys, '_MEIPASS', os.path.abspath('.')), 'run_sound.wav'), winsound.SND_FILENAME)
        self.queue.put("Task finished")


def queue_sound(self):
    self.queue = queue.Queue(maxsize=2)
    ThreadedSound(self.queue).start()
    self.master.after(100, lambda: process_queue(self))


def process_queue(self):
    try:
        self.queue.get(False)
    except queue.Empty:
        self.master.after(50, lambda: process_queue(self))