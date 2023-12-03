import os
import time
import psutil
import pyautogui
from pywinauto.application import Application


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


# 위험고지 확인창 닫기
def close_risk_notice_popup(main_window):
    popup_button = find_controls_recursively(main_window, "Button")
    temp_checkbox = [control for control in popup_button if "위험고지 확인창" in control.window_text()]
    if len(temp_checkbox) > 0:
        temp_checkbox[0].set_focus()
        temp_checkbox[0].click()
    temp_button = [control for control in popup_button if "닫  기" in control.window_text()]
    if len(temp_button) > 0:
        temp_button[0].set_focus()
        temp_button[0].click()


def check_meme_gubun():
    button_controls = find_controls_recursively(mini_order_window, "Button")
    meme_gubun = ""
    idx = 3
    meme_button = None
    for button in button_controls:
        if button.window_text().startswith("매수"):
            meme_button = button
            meme_gubun = "매수"
            idx = 3
            break
        elif button.window_text().startswith("매도"):
            meme_button = button
            meme_gubun = "매도"
            idx = 4
            break
        else:
            meme_gubun = ""
    return meme_gubun, idx, meme_button


# order 폴더 만들기
if not os.path.exists("order"):
    os.mkdir("order")

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
            break

input_field = None
if menus:
    input_field = menus.children()[0].children()[0]

# 2012 미니주문
input_field.set_focus()
input_field.type_keys('2102')
time.sleep(2)

mini_order_window = None
for child in screen_area.children():
    if child.window_text().startswith("[2102]"):
        mini_order_window = child
        break

if mini_order_window:
    user_meme_gubun = "매수"
    user_ticker = 'SOXL'
    user_qty = 2

    meme_gubun, idx, meme_button = check_meme_gubun()

    while True:
        if meme_gubun != user_meme_gubun:
            if user_meme_gubun == "매수":
                image_filename = 'images/mesu.png'
            else:
                image_filename = 'images/medo.png'

            # 모니터가 여러개일 경우 이미지를 못 찾을 수 있음.
            try:
                menu_location = pyautogui.locateCenterOnScreen(image_filename, confidence=0.9)
                if menu_location:
                    pyautogui.click(menu_location)
                    time.sleep(1)
            except:
                break
        # 체크
        temp_meme_gubun, _, _ = check_meme_gubun()
        if temp_meme_gubun == user_meme_gubun:
            break

    while True:
        if user_meme_gubun == "매수":
            image_filename = 'images/auto_mesu.png'
        else:
            image_filename = 'images/auto_medo.png'
        try:
            check_location = pyautogui.locateCenterOnScreen(image_filename, confidence=0.95)
            button_controls = find_controls_recursively(mini_order_window, "Button")
            if check_location:
                for button in button_controls:
                    if "현재가" in button.window_text():
                        button.click()
                        time.sleep(0.5)
                        break
        except:
            break

    # 내가 입력한 티커가 잘 선택되었는지 확인 (티커를 잘 못 설정할 수 있으므로 10회만 반복)
    for i in range(0, 10):
        edit_controls = find_controls_recursively(mini_order_window, "Edit")
        edit_controls[idx].type_keys(user_ticker, pause=0.3).type_keys('{ENTER}')
        time.sleep(1)

        print(f"매매 : {meme_gubun}")
        print(f"티커 : {edit_controls[idx].get_value()}")
        print(f"가격 : {edit_controls[idx+2].get_value()}")
        print(f"수량 : {edit_controls[idx+3].get_value()}")
        if edit_controls[idx].get_value() == user_ticker:
            break

    # 매매 종류 설정 방법 - 지정가로 우선 설정
    edit_controls = find_controls_recursively(mini_order_window, "Edit")
    for i in range(0, 10):
        if edit_controls[idx + 1].get_value() == "지정가":
            break
        else:
            edit_controls[idx + 1].parent().set_focus()
            edit_controls[idx + 1].parent().type_keys('{UP}')
            close_risk_notice_popup(main_window)
            time.sleep(0.5)
    for i in range(0, 10):
        if edit_controls[idx + 1].get_value() == "시장가":
            break
        else:
            edit_controls[idx + 1].parent().set_focus()
            edit_controls[idx + 1].parent().type_keys('{DOWN}')
            time.sleep(0.5)

    # 수량 설정
    for i in range(0, 10):
        edit_controls[idx + 3].set_focus()
        edit_controls[idx + 3].type_keys(str(user_qty))
        time.sleep(1)
        print(f"설정수량 : {edit_controls[idx + 3].get_value()}")

        if edit_controls[idx + 3].get_value() == str(user_qty):
            break

    meme_button.click()
    time.sleep(2)

    # 매매 확인창
    mini_order_confirm_window = None
    for child in main_window.children():
        if child.window_text().startswith("해외주식"):
            mini_order_confirm_window = child
            break

    # 거래 스크린샷
    screenshot = mini_order_confirm_window.capture_as_image()
    screenshot_file = f"order/mini_order_confirm_window_screenshot_{int(time.time())}.png"
    screenshot.save(screenshot_file)

    # 확인 버튼 클릭
    for btn in find_controls_recursively(mini_order_confirm_window, "Button"):
        if "확인" in btn.window_text():
            btn.click()

    print(1)