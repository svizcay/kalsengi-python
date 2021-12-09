import OpenGL.GL as gl
from OpenGL.GL.shaders import compileProgram, compileShader

# for watchdog file modified event
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

# for paths (python 3.5)
from pathlib import PurePath

# the confirm watchdog is running in a 2nd thread
import threading

# it looks like watchdog's on_modified is running in a different thread
# which fails to call opengl functions
# confirmed!
class MyHandler(FileSystemEventHandler):
    def __init__(self, shader):
        super().__init__()
        self.shader = shader
# class MyHandler(FileModifiedEvent):
    def on_modified(self, event):
        # if (event.is_directory):
        #     return
        # print(f'event type: {event.event_type}  path : {event.src_path}')


        if (self.shader.vertex_file is not None and self.shader.fragment_file is not None):
            vertex = PurePath(self.shader.vertex_file)
            fragment = PurePath(self.shader.fragment_file)
            # print("checking for {} and {}".format(vertex.name, fragment.name))
            if (event.src_path.endswith(vertex.name) or event.src_path.endswith(fragment.name)):
                # print("reloading shader {}".format(event.src_path))
                # print("watchdog thread id={}".format(threading.get_ident()))
                self.shader.dirty = True
                # self.shader.reload()

class Shader:

    # we want vertex and fragment shader to be mandatory
    # and they can be provided using positional arguments.
    # but those shader can be supplied either by src or by path to file.
    # let's make by default the path to srcs because it's most commonly used.
    # but if they decided to be passed explicitly using keywords, it's also fine
    # how can we have an overloaded method that takes a path rather than the context of the text file?

    # update:
    # rather than accepting many different parameters all default to None in __init__
    # we are going to use classmethod to create from_file or from_source_text
    # now the constructor is going to take the sources as mandatory and the files as optional
    def __init__(self, vertex_src, fragment_src, vertex_file = None, fragment_file = None, *additional_shaders):
        # we will save it for reloading
        self.vertex_file = vertex_file
        self.fragment_file = fragment_file

        # watchdog stuff
        # event_handler = MyHandler("engine/shaders/fragment/flat_color.glsl")
        event_handler = MyHandler(self)
        observer = Observer()
        # observer.schedule(event_handler, path="engine/shaders/fragment/flat_color.glsl", recursive=False)
        # observer.schedule(event_handler, "engine/shaders/fragment/", True)
        observer.schedule(event_handler, "engine/shaders/", True)
        observer.start()
        # i also need to join the thread!!
        # observer.stop()
        # observer.join() when finishing the program

        print("main thread id={}".format(threading.get_ident()))

        self._compile(vertex_src, fragment_src, *additional_shaders)

    @classmethod
    # mandatory parameters: vertex and fragment shaders
    def from_file(cls, vertex_file, fragment_file, *additional_shaders):
        if (vertex_file is None or fragment_file is None):
            raise ArgumentError("Missing vertex or fragment source files")

        # we should check if file exist
        vertex_src = None
        fragment_src = None

        with open(vertex_file, 'r') as file:
            vertex_src = file.read()

        with open(fragment_file, 'r') as file:
            fragment_src = file.read()

        return cls(vertex_src, fragment_src, vertex_file, fragment_file, *additional_shaders)

    @classmethod
    # mandatory parameters: vertex and fragment shaders
    def from_string(cls, vertex_src, fragment_src, *additional_shaders):
        if (vertex_src is None or fragment_src is None):
            raise ArgumentError("Missing vertex or fragment source text")

        return cls(vertex_src, fragment_src, None, None, *additional_shaders)

    def use(self):
        gl.glUseProgram(self.program)

    def _compile(self, vertex_src, fragment_src, *additional_srcs):
        # if we dont succeed compiling the shader,
        # we should use an error shader
        # add try-catch
        vertex_shader = compileShader(vertex_src, gl.GL_VERTEX_SHADER)
        frag_shader = compileShader(fragment_src, gl.GL_FRAGMENT_SHADER)
        self.program = compileProgram(vertex_shader, frag_shader)
        self.dirty = False

    def reload(self):
        # if we have stored the file, read it again, and recreate the shader program
        if (self.vertex_file is not None and self.fragment_file is not None):
            with open(self.vertex_file, 'r') as file:
                vertex_src = file.read()

            with open(self.fragment_file, 'r') as file:
                fragment_src = file.read()

            self._compile(vertex_src, fragment_src)


