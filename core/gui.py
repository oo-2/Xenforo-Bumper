#!/usr/bin/env python3
from pathlib import Path
import logging

import dearpygui.dearpygui as dpg
from core import bumper

_LOGGER = logging.getLogger(__name__)


def get_login(bump, gui, u):
    bump.set_login(gui.get_values(u))
    gui.configure_item("login", no_close=False)


def get_two_factor(bump, gui, u):
    bump.set_login(gui.get_values(u))
    gui.configure_item("2fa", no_close=False)


def get_details(bump, gui, u):
    bump.set_login(gui.get_values(u))
    gui.configure_item("details", no_close=False)


def launch_GUI():
    dpg.create_context()
    launch_bumper = bumper.Bumper()

    with dpg.font_registry():
        bold_font = dpg.add_font("./resources/Inter-Bold.ttf", 24)
        regular_font = dpg.add_font("./resources/Inter-Regular.ttf", 16)

    with dpg.window(tag="Logger"):
        # Acts as the primary window
        with dpg.menu_bar():
            with dpg.menu(label="File"):
                dpg.add_menu_item(label="Update Login", callback=lambda: dpg.configure_item("login", show=True))
                dpg.add_menu_item(label="Update Details", callback=lambda: dpg.configure_item("details", show=True))
                dpg.add_menu_item(label="Forget Login", callback=lambda: Path("./cookies.pkl").unlink(missing_ok=True))
                dpg.add_menu_item(label="Forget Details",
                                  callback=lambda: Path("./details.pkl").unlink(missing_ok=True))
                dpg.add_menu_item(label="Exit", callback=lambda: dpg.stop_dearpygui())

        with dpg.table(header_row=True, row_background=True,
                       borders_innerH=True, borders_outerH=True, borders_innerV=True,
                       borders_outerV=True):
            header = dpg.add_table_column(label="Log Messages")
            dpg.bind_item_font(header, bold_font)
            # Dynamically creates rows with updates from the logger
            with dpg.table_row():
                dpg.add_text("Receiving Log Updates")

    with dpg.window(label="Login", tag="login", width=250, height=175,
                    no_resize=True, no_close=True, show=True, pos=[100, 50]):
        dpg.bind_font(regular_font)
        with dpg.group():
            with dpg.group(horizontal=True):
                dpg.add_text("Forum URL")
                url = dpg.add_input_text(source="string_value")

            with dpg.group(horizontal=True):
                dpg.add_text("Forum User")
                user = dpg.add_input_text(source="string_value")

            with dpg.group(horizontal=True):
                dpg.add_text("Forum Pass")
                password = dpg.add_input_text(source="string_value", password=True)

            remember_session = dpg.add_checkbox(label="Remember session?", source="bool_value")
            dpg.add_button(label="Submit", user_data=(url, user, password, remember_session),
                           callback=lambda s, a, u: get_login(launch_bumper, dpg, u))

    with dpg.window(label="2FA", tag="2fa", width=100, height=50,
                    no_resize=True, no_close=True, show=True):
        dpg.bind_font(regular_font)
        with dpg.group():
            with dpg.group(horizontal=True):
                dpg.add_text("2FA")
                two_factor = dpg.add_input_int(step=0, max_value=999_999, min_value=0, max_clamped=True)
            dpg.add_button(label="Submit", user_data=two_factor,
                           callback=lambda s, a, u: get_two_factor(launch_bumper, dpg, u))

    with dpg.window(label="Details", tag="details", width=350, height=305,
                    no_resize=True, no_close=True, show=True):
        dpg.bind_font(regular_font)

        with dpg.group():
            with dpg.group(horizontal=True):
                dpg.add_text("Thread IDs")
                threads = dpg.add_input_text(source="string_value")
            dpg.add_text("Separate IDs with commas")

            with dpg.group(horizontal=True):
                dpg.add_text("Message")
                message = dpg.add_input_text(source="string_value", multiline=True)

            with dpg.group(horizontal=True):
                dpg.add_text("Delay (Hours)")
                timer = dpg.add_input_int(step=0, max_value=24, min_value=1, max_clamped=True)

            remember_details = dpg.add_checkbox(label="Remember details?", source="bool_value")
            dpg.add_button(label="Submit", user_data=(threads, message, timer, remember_details),
                           callback=lambda s, a, u: get_details(launch_bumper, dpg, u))

    dpg.create_viewport(title='Xenforo Bumper', width=600, height=500)
    dpg.setup_dearpygui()
    dpg.set_viewport_large_icon("./resources/xfbump.ico")
    dpg.set_viewport_small_icon("./resources/xfbump.ico")
    dpg.show_viewport()
    dpg.set_primary_window("Logger", True)
    dpg.start_dearpygui()
    dpg.destroy_context()
