# -*- coding: utf-8 -*-

import os
import threading
from tkinter import *
from tkinter import scrolledtext
from PIL import ImageTk, Image  # Pillow
from monkey import Monkey
import platform

# if Mac
if platform.system() == "Darwin":
    from tkmacosx import Button

IMG_DIR = os.path.abspath("img") + '/'
SCRIPT_FILE = 'monkey.txt'
monkey: Monkey = Monkey(SCRIPT_FILE)

touch_point = []


def focus_next_widget(event):
    event.widget.tk_focusNext().focus()
    return ("break")


class TappingWorker(threading.Thread):
    def __init__(self, name):
        super().__init__()
        self._stop_event = threading.Event()
        self.name = name  # thread 이름 지정

    def stop(self):
        monkey.stop()
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        freq = int(freq_text.get(1.0, END).rstrip('\n'))
        repeat = int(repeat_text.get(1.0, END).rstrip('\n'))
        print('freq={}, repeat={}'.format(freq, repeat))
        monkey.tab(touch_point, freq, repeat)


thread: TappingWorker


def on_start():
    log('시작')
    monkey.clear()

    global thread
    thread = TappingWorker('TappingWorker')
    thread.start()


def on_end():
    log('종료')

    global thread
    thread.stop()


def on_restart():
    on_end()
    """Restarts the current program.
    Note: this function does not return. Any cleanup action (like
    saving data) must be done before calling this function."""
    python = sys.executable
    os.execl(python, python, * sys.argv)


def log(msg):
    print(msg)
    log_text.configure(state='normal')
    log_text.insert(INSERT, msg + '\n')
    log_text.see(END)
    log_text.configure(state='disabled')  # 텍스트 위젯을 읽기 전용으로 설정


def on_draw_dot(event):
    radius = 4
    x1, y1 = (event.x - radius), (event.y - radius)
    x2, y2 = (event.x + radius), (event.y + radius)
    canvas.create_oval(x1, y1, x2, y2, fill='green')
    print('x={x}, y={y}'.format(x=event.x / img_ratio, y=event.y / img_ratio))
    touch_point.append((event.x / img_ratio, event.y / img_ratio))

    log('touch_point=' + str(touch_point))


def clear_img():
    if os.path.exists(IMG_DIR):
        for file_name in os.listdir(IMG_DIR):
            file_path = os.path.join(IMG_DIR, file_name)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
    else:
        os.mkdir(IMG_DIR)


def screen_capture() -> str:
    clear_img()
    capture_path = '/data/media/0/Download/'
    __file = 'monkey_screen.png'  # time.strftime('%Y%m%d_%H%M%S.png', time.localtime())
    os.system('adb shell screencap -p {capture_path}{file_name}'.format(
        capture_path=capture_path,
        file_name=__file))
    os.system('adb pull {capture_path}{file_name} {pull_path}{file_name}'.format(
        capture_path=capture_path,
        file_name=__file,
        pull_path=IMG_DIR))

    out_path = '{path}{file_name}'.format(file_name=__file, path=IMG_DIR)

    if os.path.exists(out_path) is False:
        print('screen capture fail')
        return ''

    print("screen capture path = {0}".format(out_path))
    return out_path


def adb_tab(x, y):
    os.system('adb shell input tap {x} {y}'.format(x=x, y=y))
    log_text.insert(END, 'tap {x} {y}'.format(x=x, y=y))


if __name__ == '__main__':
    root = Tk()
    root.title('Android Monkey')
    root.geometry('650x550+500+500')
    # root.resizable(False, False)

    log_text = scrolledtext.ScrolledText(root)
    log_text.config(wrap=WORD, width=100, height=10, font=('Consolas', 11))
    log_text.insert(INSERT, '안녕하세요 환영합니다.\n')
    log_text.configure(state='disabled')  # 텍스트 위젯을 읽기 전용으로 설정
    log_text.pack(side='bottom')

    root_frame = LabelFrame(root)
    root_frame.pack(side='right', anchor='ne')
    button_frame = LabelFrame(root_frame, text='버튼', relief='solid', bd=1)
    button_frame.pack()
    Button(button_frame, text='시작', command=on_start).pack()
    Button(button_frame, text='종료', command=on_end).pack()
    Button(button_frame, text='초기화', command=on_restart).pack()

    freq_frame = LabelFrame(root_frame, text='주기 ms', relief='solid', bd=1)
    freq_frame.pack()
    freq_text = Text(freq_frame, width=11, height=1)
    freq_text.insert(CURRENT, '200')
    freq_text.pack()
    freq_text.bind("<Tab>", focus_next_widget)

    repeat_frame = LabelFrame(root_frame, text='반복', relief='solid', bd=1)
    repeat_frame.pack()
    repeat_text = Text(repeat_frame, width=11, height=1)
    repeat_text.insert(CURRENT, '1000')
    repeat_text.pack()
    repeat_text.bind("<Tab>", focus_next_widget)

    img_name = screen_capture()
    image = Image.open(img_name)

    img_ratio = 2 / 3
    img_width = int(image.width * img_ratio)
    img_height = int(image.height * img_ratio)
    print('{width}, {height}'.format(width=image.width, height=image.height))
    image = image.resize((img_width, img_height))

    photo = ImageTk.PhotoImage(image)

    canvas = Canvas(root, width=img_width, height=img_height, bg='blue')
    canvas.create_image(img_width / 2 + 2, img_height / 2 + 3, image=photo)
    canvas.pack(side='top', anchor='nw')
    canvas.old_coords = None
    canvas.bind('<ButtonRelease-1>', on_draw_dot)

    root.mainloop()
