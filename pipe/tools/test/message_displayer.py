import pipe.gui.quick_dialogs as quick_dialogs

def display_message(message, non_gui):
    if non_gui:
        print message
    else:
        quick_dialogs.message(message)
