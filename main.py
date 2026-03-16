from concurrent.futures import ThreadPoolExecutor
from pyweixin import Navigator, Monitor
# Independent dialog windows for each friend
dialog_windows = []
friends = ['🐱🐱乖乖🐷🐷一家亲', '好想锤狗大猫鸭']
for friend in friends:
    dialog_window = Navigator.open_seperate_dialog_window(
        friend=friend, window_minimize=True, close_weixin=True)
    dialog_windows.append(dialog_window)
