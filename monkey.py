import subprocess


class Monkey:
    script_file: str = 'monkey.txt'

    def __init__(self, _script_file: str):
        self.script_file = _script_file

    def clear(self):
        open(self.script_file, 'w').close()

    def add(self, text: str):
        with open(self.script_file, "a+") as file_object:
            # Move read cursor to the start of file.
            file_object.seek(0)
            # If file is not empty then append '\n'
            data = file_object.read(100)
            if len(data) > 0:
                file_object.write("\n")
            # Append text at the end of file
            file_object.write(text)

    def tab(self, arr: list, delay, repeat):
        self.add('start data >>')
        for coord in arr:
            self.add('DispatchPointer(0, 0, 0, {x}, {y}, 0, 0, 0, 0, 0, 0, 0)'.format(x=coord[0], y=coord[1]))
            self.add('DispatchPointer(0, 0, 1, {x}, {y}, 0, 0, 0, 0, 0, 0, 0)'.format(x=coord[0], y=coord[1]))
            self.add('UserWait({delay})'.format(delay=delay))

        subprocess.call('adb push monkey.txt /data/', shell=True)
        subprocess.call('adb shell monkey -f /data/monkey.txt {repeat}'.format(repeat=repeat), shell=True)

    def stop(self):
        subprocess.call('adb shell killall -9 com.android.commands.monkey', shell=True)
