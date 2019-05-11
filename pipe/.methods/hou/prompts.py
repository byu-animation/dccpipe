import pipe.am as am
import pipe.tools.general.prompts as general_prompts

filter = ({
        "programs": ["houdini"]
        })

def SelectBody(tool, finished):
    global filter
    general_prompts.SelectBody(tool, finished, filter)

def SelectElementFromBody(tool, finished):
    global filter
    general_prompts.SelectElementFromBody(tool, finished, filter)

def SelectElementOrCommit(tool, finished):
    global filter
    general_prompts.SelectElementOrCommit(tool, finished, filter)

def SelectCommit(tool, finished):
    global filter
    general_prompts.SelectCommit(tool, finished, filter)
