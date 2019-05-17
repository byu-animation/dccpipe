import pipe.gui.quick_dialogs as quick_dialogs

def display_message(message, gui):
    if gui:
        quick_dialogs.message(message)
    else:
        print message
