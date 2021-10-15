import os
import threading
import time
from tkinter import *
from tkinter import scrolledtext
import platform
from PIL import ImageTk, Image  # Pillow

# if Mac
if platform.system() == "Darwin":
    from tkmacosx import Button

IMG_DIR = os.path.abspath("img") + '/'

touch_point = []
action: bool = False


class TappingWorker(threading.Thread):
    def __init__(self, name):
        super().__init__()
        self.name = name  # thread 이름 지정

    def run(self):
        while True:
            while action:
                for coord in touch_point:
                    adb_tab(coord[0], coord[1])
                    time.sleep(0.5)
            time.sleep(1)


thread = TappingWorker('TappingWorker')
thread.start()


def btn_start():
    log('시작')
    global action
    action = True


def btn_end():
    log('종료')
    global action
    action = False


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


if __name__ == '__main__':
    root = Tk()
    root.title('Android Monkey')
    root.geometry('640x480+1800+800')
    root.resizable(False, False)

    log_text = scrolledtext.ScrolledText(root)
    log_text.config(wrap=WORD, width=100, height=10, font=('Consolas', 11))
    log_text.insert(INSERT, '안녕하세요 환영합니다.\n')
    log_text.configure(state='disabled')  # 텍스트 위젯을 읽기 전용으로 설정
    log_text.pack(side='bottom')

    labelframe = LabelFrame(root, text='버튼', relief='solid', bd=1)
    labelframe.pack(side='right', anchor='ne')
    Button(labelframe, text='시작', command=btn_start).pack()
    Button(labelframe, text='종료', command=btn_end).pack()

    img_name = screen_capture()
    image = Image.open(img_name)

    img_ratio = 2 / 3
    img_width = int(image.width * img_ratio)
    img_height = int(image.height * img_ratio)
    print('{width}, {height}'.format(width=image.width, height=image.height))
    image = image.resize((img_width, img_height))

    photo = ImageTk.PhotoImage(image)

    canvas = Canvas(root, width=img_width, height=img_height, bg='blue')
    canvas.create_image(img_width / 2 + 3, img_height / 2 + 3, image=photo)
    canvas.pack(side='top', anchor='nw')
    canvas.old_coords = None
    canvas.bind('<ButtonRelease-1>', paint)

    root.mainloop()
