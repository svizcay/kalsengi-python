# Dockerfile: template for building images
# Image: template for running containers
# Container: running process

# to run OpenGL's contexts, we need a XServer
# and containers don't have a XServer

# we need to share the host's XServer with the container
# by creating a volume (does it work for windows too?)

# WE STOP.
# since is a python only app (only dealing with python dependecies)
# we are now using virtualenvs provided by anaconda.
# packages that were not directly found in anaconda were installed
# using a terminal for the virtualenv and installing them manually with pip

# latest python version 2021/11/02 -> 3.10
FROM python:latest

ADD example.py .

# dependencies:
# PyOpenGL
# PyGLFW
# Pyrr for linear algebra (based on numpy)
# Pillow for loading images
RUN pip install PyOpenGL glfw pyrr pillow

CMD ["python", "./example.py"]
