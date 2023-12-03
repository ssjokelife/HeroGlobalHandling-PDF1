import time
import os
import psutil
import pyperclip
import pytesseract
from pywinauto.application import Application
import pywinauto.mouse
import pywinauto.clipboard


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def find_controls_recursively(control, class_name):
    found_controls = []
    for child in control.children():
        if child.class_name() == class_name:
            found_controls.append(child)
        # 자식 컨트롤들에 대해서도 재귀적으로 탐색
        found_controls.extend(find_controls_recursively(child, class_name))
    return found_controls


def find_controls_recursively_friendly(control, class_name):
    found_controls = []
    for child in control.children():
        if child.friendly_class_name() == class_name:
            found_controls.append(child)
        # 자식 컨트롤들에 대해서도 재귀적으로 탐색
        found_controls.extend(find_controls_recursively_friendly(child, class_name))
    return found_controls


# result 폴더 만들기
if not os.path.exists("result"):
    os.mkdir("result")

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
# main_window.maximize()
time.sleep(1)

# 각 자식 컨트롤의 정보 출력
screen_area = None
menutoolbar = None
for child in main_window.children():
    if child.window_text() == "메뉴툴바":
        menutoolbar = child

    if child.class_name() == "MDIClient": # 작업 영역
        screen_area = child

# 메뉴툴바로 부터 메뉴를 호출 할 예정
menus = None
if menutoolbar:
    menutoolbar_children = menutoolbar.children()
    for child in menutoolbar_children:
        if len(child.children()) == 4:
            menus = child

if menus:
    input_field = menus.children()[0].children()[0]

# 2150 계좌정보
input_field.set_focus()
input_field.type_keys('2150')
time.sleep(2)

account_info_window = None
for child in screen_area.children():
    if child.window_text().startswith("[2150]"):
        account_info_window = child
        break

pane_control = find_controls_recursively_friendly(account_info_window, "Pane")[0]
pywinauto.mouse.right_click(coords=(pane_control.rectangle().left + 50, pane_control.rectangle().bottom - 50))
pywinauto.keyboard.send_keys('Z')
print(pyperclip.paste())

# screenshot = pane_control.capture_as_image()
# screenshot_file = f"pane_screenshot_{int(time.time())}.png"
# screenshot.save(f"result/{screenshot_file}")
#
# image = cv2.imread(f"result/{screenshot_file}")
# gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
# cv2.imwrite(f"result/gray_{screenshot_file}", gray)
#
# config = ('-l kor+eng --oem 3 --psm 6') # 6
# text = pytesseract.image_to_string(image=gray, config=config)
# print(text)

