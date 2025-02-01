import ctypes
import time
from threading import Timer, Thread
from queue import Queue


class Timeout(Exception):
    """Prilagođeni izuzetak za signalizaciju vremenskih ograničenja."""
    pass


def send_thread_exception(*args):
    """
    Šalje izuzetak niti koja je prekoračila vremensko ograničenje.
    """
    for t_id in args:
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(t_id), ctypes.py_object(Timeout))
        if not res:
            print(f"Greška: Niti {t_id} nije pronađena")
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(t_id, 0)
            print(f"Greška: Nije uspelo slanje izuzetka za niti {t_id}")


class TimedFunction(Thread):
    """
    Izvršava funkciju u određenom vremenskom ograničenju.
    Ako funkcija prekorači vremensko ograničenje, baca se `Timeout` izuzetak.
    """
    def __init__(self, queue: Queue, max_time_sec: int, method, *args):
        super().__init__()
        self.queue = queue
        self.max_time_sec = max_time_sec
        self.method = method
        self.args = args

    def run(self) -> None:
        """
        Izvršava zadatu metodu uz poštovanje vremenskog ograničenja.
        """
        timer = None
        if self.max_time_sec:
            timer = Timer(self.max_time_sec, send_thread_exception, [self.ident])
            timer.start()

        try:
            start_time = time.time()
            result = self.method(*self.args)
            elapsed_time = time.time() - start_time
            self.queue.put((result, elapsed_time), block=False)
        except Timeout:
            self.queue.put(("Timeout", None), block=False)
        except Exception as e:
            self.queue.put((e, None), block=False)
        finally:
            if timer:
                timer.cancel()
