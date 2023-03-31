#!/usr/bin/env python3
import logging
from pathlib import Path

import dearpygui.dearpygui as dpg

from core import bumper

_LOGGER = logging.getLogger(__name__)


def get_website(bump, gui, u):
    bump.set_website(gui.get_value(u))
    gui.configure_item("website", show=False)
    if bump.check_login():
        gui.configure_item("login", show=True)
    else:
        if Path("./resources/details.json").is_file():
            bump.load_details()
        else:
            gui.configure_item("details", show=True)


def get_login(bump, gui, u):
    bump.set_login(gui.get_values(u))
    gui.configure_item("failed login", show=False)

    if bump.login():
        if bump.check_duo():
            gui.configure_item("login", show=False)
            gui.configure_item("duo", show=True)
        else:
            _LOGGER.info("Failed to login\n")
            gui.configure_item("failed login", show=True)
    else:
        gui.configure_item("login", show=False)
        if bump.check_two_step():
            gui.configure_item("2fa", show=True)
        else:
            gui.configure_item("details", show=True)


def get_duo(bump, gui):
    gui.configure_item("failed duo", show=False)
    if bump.check_duo():
        _LOGGER.info("Failed DUO push\n")
        gui.configure_item("failed code", show=True)
    else:
        gui.configure_item("duo", show=False, no_close=False)
        if bump.check_two_step():
            gui.configure_item("2fa", show=True)
        else:
            gui.configure_item("details", show=True)


def get_two_factor(bump, gui, u):
    gui.configure_item("failed code", show=False)
    if bump.two_factor(gui.get_value(u)):
        _LOGGER.info("Invalid 2FA code\n")
        gui.configure_item("failed code", show=True)
    else:
        gui.configure_item("2fa", show=False, no_close=False)
        gui.configure_item("failed code", show=False)
        gui.configure_item("details", show=True)


def get_details(bump, gui, u):
    bump.set_details(gui.get_values(u))
    gui.configure_item("details", no_close=False)
    bump.post_timer()


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
                dpg.add_menu_item(label="Exit", callback=lambda: dpg.stop_dearpygui())

    with dpg.window(label="Website", tag="website", width=200, height=50,
                    no_resize=True, no_close=True, show=True, pos=[100, 50]):
        dpg.bind_font(regular_font)
        with dpg.group():
            with dpg.group(horizontal=True):
                dpg.add_text("Forum URL")
                url = dpg.add_input_text(source="string_value")
            dpg.add_button(label="Submit", user_data=url,
                           callback=lambda s, a, u: get_website(launch_bumper, dpg, u))

    with dpg.window(label="Login", tag="login", width=250, height=115,
                    no_resize=True, no_close=True, show=False, pos=[100, 50]):
        dpg.bind_font(regular_font)
        with dpg.group():
            with dpg.group(horizontal=True):
                dpg.add_text("Forum User")
                user = dpg.add_input_text(source="string_value")

            with dpg.group(horizontal=True):
                dpg.add_text("Forum Pass")
                password = dpg.add_input_text(source="string_value", password=True)

            with dpg.group(horizontal=True):
                dpg.add_button(label="Submit", user_data=(user, password),
                               callback=lambda s, a, u: get_login(launch_bumper, dpg, u))
                dpg.add_text("Failed to login", tag="failed login", color=[255, 0, 0], show=False)

    with dpg.window(label="Duo", tag="duo", width=150, height=30,
                    no_resize=True, no_close=True, show=False, pos=[150, 75]):
        dpg.bind_font(regular_font)
        with dpg.group(horizontal=True):
            dpg.add_button(label="Approved on DUO", callback=lambda s, a, u: get_duo(launch_bumper, dpg))
            dpg.add_text("Failed DUO Push", tag="failed duo", color=[255, 0, 0], show=False)

    with dpg.window(label="2FA", tag="2fa", width=150, height=50,
                    no_resize=True, no_close=True, show=False, pos=[150, 75]):
        dpg.bind_font(regular_font)
        with dpg.group():
            with dpg.group(horizontal=True):
                dpg.add_text("2FA")
                two_factor = dpg.add_input_int(step=0, max_value=999_999, min_value=0, max_clamped=True)

        with dpg.group(horizontal=True):
            dpg.add_button(label="Submit", user_data=two_factor,
                           callback=lambda s, a, u: get_two_factor(launch_bumper, dpg, u))
            dpg.add_text("Invalid Code", tag="failed code", color=[255, 0, 0], show=False)

    with dpg.window(label="Details", tag="details", width=350, height=305,
                    no_resize=True, no_close=True, show=False, pos=[100, 50]):
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
            dpg.add_button(label="Submit", user_data=(threads, message, timer),
                           callback=lambda s, a, u: get_details(launch_bumper, dpg, u))

    dpg.create_viewport(title='Xenforo Bumper', width=600, height=500)
    dpg.setup_dearpygui()
    dpg.set_viewport_large_icon("./resources/xfbump.ico")
    dpg.set_viewport_small_icon("./resources/xfbump.ico")
    dpg.show_viewport()
    dpg.set_primary_window("Logger", True)
    dpg.start_dearpygui()
    dpg.destroy_context()
