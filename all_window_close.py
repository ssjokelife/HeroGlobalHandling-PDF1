import time
import psutil
from pywinauto.application import Application


def all_windows_close(screen_area):
    for screen in screen_area.children():
        screen.close()


# 영웅문 process id 찾기
process_id = 0
for process in psutil.process_iter(['pid', 'name']):
    if process.info['name'] == 'nfrunlite.exe':
        process_id = process.info['pid']
        break

# 실행 중인 어플리케이션에 연결
app = Application(backend="uia").connect(process=process_id)

# 메인 윈도우 핸들링
main_window = app.window(title='영웅문Global')
main_window.maximize()
time.sleep(1)

# 각 자식 컨트롤의 정보 출력
screen_area = None
for child in main_window.children():
    if child.class_name() == "MDIClient": # 작업 영역
        screen_area = child
        break

all_windows_close(screen_area)
