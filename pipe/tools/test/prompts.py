import pipe.gui as gui

def TestInput(tool, finished):
    tool.TestInputDialog = gui.write_message.WriteMessage(
        title="Please enter a string:"
    )
    tool.TestInputDialog.submitted.connect(submitted)
    tool.TestInputDialog.cancelled.connect(cancelled)

    def submitted(message):
        finished(message=message)

    def cancelled():
        finished(cancelled=True)
