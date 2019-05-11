import pipe.gui as gui
import pipe.am as am

def SelectBody(tool, finished, filter, select_multiple=False):
    body_list = am.filter_bodies(filter)
    tool.SelectBodyDialog = gui.SelectFromList(
        labels=body_list,
        values=body_list
        )

    tool.SelectBodyDialog.submitted.connect(selected)
    tool.SelectBodyDialog.cancelled.connect(cancelled)

    def selected(selection):
        if len(selection) == 1:
            finished(
                body=am.get_body(selection[0])
                )
        elif len(selection) > 1:
            finished(
                bodies=[am.get_body(x) for x in selection]
                )
        else:
            finished(
                body=None,
                bodies=None
                )

    def cancelled():
        finished(
            cancelled=True
            )

def SelectElement(tool, finished, filter):
    element_list = am.filter_bodies()

def SelectElementFromBody(tool, finished, body):
    tool.SelectElementFromBodyDialog = gui.SelectFromSeveralButtons(
        labels=[ x.title for x in body.get_departments() ]
        values=body.get_departments()
        )

    tool.SelectElementFromBodyDialog.submitted.connect(selected)
    tool.SelectElementFromBodyDialog.cancelled.connect(cancelled)

    def selected(selection):
        element = body.get_element(selection)
        finished(
            element=element
            )

    def cancelled():
        finished(
            cancelled=True
            )

def SelectElementOrCommit(tool, finished, filter):
    # Make sure the GUI is tied to an object in memory or else
    # it will be garbage collected in programs like Maya
    departments = am.filter_departments(filter)
    body_filter = { "departments" : departments }
    body_filter.update(filter)
    tool.SelectElementDialog = gui.SelectFromMultipleListsWithOptions(
        category_labels=am.filter_departments(filter),
        lists=am.filter_bodies(filter, separate_lists=True),
        options=[
            ("Clone a previous version", False)
            ]
        )
    tool.SelectElementDialog.submitted.connect(selectedElement)
    tool.SelectElementDialog.cancelled.connect(cancelled)

    def selected(selection):
        if len(selection) > 0:
            finished({"element" : am.get_element(selection[0][0], selection[0][1])})
        else:
            finished({"element" : None})

    def cancelled():
        finished({"cancelled" : True})

def SelectCommit(tool, finished, element):
    tool.SelectCommitDialog = SelectCommit(element)
    tool.SelectCommitDialog.submitted.connect(selectedCommit)
    tool.SelectCommitDialog.cancelled.connect(cancelled)

    def selectedCommit(version_number):
        finished({"version_number" : version_number})

    def cancelled():
        finished({"cancelled" : True})
