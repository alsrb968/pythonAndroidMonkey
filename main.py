# -*- coding: utf-8 -*-

import os
import subprocess
import threading
from tkinter import *
from tkinter import scrolledtext

from PIL import ImageTk, Image  # Pillow

IMG_DIR = os.path.abspath("img") + '/'

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
        monkey_stop()
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        freq = int(freqText.get(1.0, END).rstrip('\n'))
        repeat = int(repeatText.get(1.0, END).rstrip('\n'))
        print('freq={}, repeat={}'.format(freq, repeat))
        monkey_tab(touch_point, freq, repeat)


thread = TappingWorker('TappingWorker')


def btn_start():
    log('시작')
    monkey_text_clear()

    global thread
    thread = TappingWorker('TappingWorker')
    thread.start()


def btn_end():
    log('종료')

    global thread
    thread.stop()


def log(msg):
    print(msg)
    log_text.configure(state='normal')
    log_text.insert(INSERT, msg + '\n')
    log_text.see(END)
    log_text.configure(state='disabled')  # 텍스트 위젯을 읽기 전용으로 설정


def paint(event):
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


def monkey_text_clear():
    open('monkey.txt', 'w').close()


def monkey_text_add(text):
    with open("monkey.txt", "a+") as file_object:
        # Move read cursor to the start of file.
        file_object.seek(0)
        # If file is not empty then append '\n'
        data = file_object.read(100)
        if len(data) > 0:
            file_object.write("\n")
        # Append text at the end of file
        file_object.write(text)


def monkey_tab(arr: list, delay, repeat):
    monkey_text_add('start data >>')
    for coord in arr:
        monkey_text_add('DispatchPointer(0, 0, 0, {x}, {y}, 0, 0, 0, 0, 0, 0, 0)'.format(x=coord[0], y=coord[1]))
        monkey_text_add('DispatchPointer(0, 0, 1, {x}, {y}, 0, 0, 0, 0, 0, 0, 0)'.format(x=coord[0], y=coord[1]))
        monkey_text_add('UserWait({delay})'.format(delay=delay))

    subprocess.call('adb push monkey.txt /data/', shell=True)
    subprocess.call('adb shell monkey -f /data/monkey.txt {repeat}'.format(repeat=repeat), shell=True)


def monkey_stop():
    subprocess.call('adb shell killall -9 com.android.commands.monkey', shell=True)


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

    labelframe = LabelFrame(root, text='버튼', relief='solid', bd=1)
    labelframe.pack(side='right', anchor='ne')
    Button(labelframe, text='시작', command=btn_start).pack()
    Button(labelframe, text='종료', command=btn_end).pack()

    freqLabelframe = LabelFrame(labelframe, text='주기 ms', relief='solid', bd=1)
    freqLabelframe.pack()
    freqText = Text(freqLabelframe, width=13, height=1)
    freqText.pack()
    freqText.bind("<Tab>", focus_next_widget)

    repeatLabelframe = LabelFrame(labelframe, text='반복', relief='solid', bd=1)
    repeatLabelframe.pack()
    repeatText = Text(repeatLabelframe, width=13, height=1)
    repeatText.pack()
    repeatText.bind("<Tab>", focus_next_widget)

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
    canvas.bind('<ButtonRelease-1>', paint)

    root.mainloop()
