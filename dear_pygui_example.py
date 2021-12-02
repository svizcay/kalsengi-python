import dearpygui.dearpygui as dpg
from dearpygui.demo import show_demo

def save_callback():
    print("Save Clicked")

if __name__ == "__main__":
    dpg.create_context()
    dpg.create_viewport(title="My Engine", width=1024, height=768)
    dpg.setup_dearpygui()   # needs to go before the render loop

    # if we want to make the window the primary window (it's render using the whole viewport)
    # we need to specify a tag to use later in set_primary_window
    with dpg.window(label="Example Window", tag="main"):
        dpg.add_text("Hello world") # items return their tag when they are created
        dpg.add_button(label="Save", callback=save_callback)
        dpg.add_input_text(label="string")
        dpg.add_slider_float(label="float")

    # show_demo()

    dpg.show_viewport()
    
    dpg.set_primary_window("main", True)
    # dpg.start_dearpygui() # render loop is handled here
    # below replaces, start_dearpygui()
    while dpg.is_dearpygui_running():
        # insert here any code you would like to run in the render loop
        # you can manually stop by using stop_dearpygui()
        print("this will run every frame")
        dpg.render_dearpygui_frame()

    dpg.destroy_context()
    print("closing the app")
