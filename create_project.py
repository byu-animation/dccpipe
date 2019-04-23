import pipe.am.pipeline_io as pipeline_io
import os

def create_project():
    project_dir = os.getenv("MEDIA_PROJECT_DIR")
    pipe_dict = pipeline_io.readfile(".project")

    pipeline_io.mkdir(pipe_dict["production_dir"])
    pipeline_io.mkdir(pipe_dict["assets_dir"])
    pipeline_io.mkdir(pipe_dict["crowds_dir"])
    pipeline_io.mkdir(pipe_dict["shots_dir"])
    pipeline_io.mkdir(pipe_dict["tools_dir"])
    pipeline_io.mkdir(pipe_dict["users_dir"])
    pipeline_io.mkdir(pipe_dict["hda_dir"])

create_project()
