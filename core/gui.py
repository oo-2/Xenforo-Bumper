#!/usr/bin/env python3
import logging
from pathlib import Path

import dearpygui.dearpygui as dpg

from core import bumper

_LOGGER = logging.getLogger(__name__)


def logged_in(bump, gui):
    gui.delete_item("details data")
    with gui.table_row(tag="details data", parent="bumper info"):
        gui.add_text(bump.forum_link.lower())
        print(bump.threads)
        gui.add_text(len(bump.threads))
        gui.add_text(f"{bump.delay} hour(s)")
    gui.configure_item("details", no_close=False)
    gui.configure_item("website", no_close=False)
    gui.configure_item("nav details", show=True)
    gui.configure_item("nav log", show=True)
    gui.configure_item("nav link", show=True)
    gui.configure_item("bumper info", show=True)
    gui.configure_item("bump btn", show=True)


def log_out(bump, gui):
    bump.driver.delete_all_cookies()
    gui.configure_item("website", show=True,)
    gui.configure_item("details", no_close=True, show=False)
    gui.configure_item("details data", show=False)
    gui.configure_item("nav details", show=False)
    gui.configure_item("nav log", show=False)
    gui.configure_item("nav link", show=False)
    gui.configure_item("bumper info", show=False)
    gui.configure_item("bump btn", show=False)


def update_details(bump, gui, is_website):
    gui.delete_item("details data")
    with gui.table_row(tag="details data", parent="bumper info"):
        gui.add_text(bump.forum_link.lower())
        gui.add_text(len(bump.threads))
        gui.add_text(f"{bump.delay} hour(s)")

    if is_website:
        dpg.configure_item("website", show=True)
    else:
        dpg.configure_item("details", show=True)


def get_website(bump, gui, u):
    bump.set_website(gui.get_value(u))
    gui.configure_item("website", show=False)
    if bump.check_login():
        gui.configure_item("login", show=True)
    else:
        if Path("./resources/details.json").is_file():
            bump.update_website()
            logged_in(bump, gui)
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
            if Path("./resources/details.json").is_file():
                logged_in(bump, gui)
            else:
                gui.configure_item("details", show=True)


def get_duo(bump, gui):
    gui.configure_item("failed duo", show=False)
    if bump.check_duo():
        _LOGGER.info("Failed duo push\n")
        gui.configure_item("failed code", show=True)
    else:
        gui.configure_item("duo", show=False, no_close=False)
        if bump.check_two_step():
            gui.configure_item("2fa", show=True)
        else:
            if Path("./resources/details.json").is_file():
                logged_in(bump, gui)
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
        if Path("./resources/details.json").is_file():
            logged_in(bump, gui)
        else:
            gui.configure_item("details", show=True)


def get_details(bump, gui, u):
    bump.set_details(gui.get_values(u))
    gui.configure_item("details", show=False)
    dpg.delete_item("details data")
    logged_in(bump, gui)


def launch_GUI():
    dpg.create_context()
    launch_bumper = bumper.Bumper()

    with dpg.font_registry():
        bold_font = dpg.add_font("./resources/Inter-Bold.ttf", 24)
        regular_font = dpg.add_font("./resources/Inter-Regular.ttf", 16)

    with dpg.window(tag="primary"):
        # Acts as the primary window
        dpg.bind_font(bold_font)
        with dpg.menu_bar(tag="nav", show=False):
            with dpg.menu(label="File"):
                dpg.add_menu_item(label="Update Details", tag="nav details", show=False,
                                  callback=lambda: update_details(launch_bumper, dpg, False))
                dpg.add_menu_item(label="Update Forum Link", tag="nav link", show=False,
                                  callback=lambda: update_details(launch_bumper, dpg, True))
                dpg.add_menu_item(label="Log out", tag="nav log", show=False,
                                  callback=lambda: log_out(launch_bumper, dpg))
                dpg.add_menu_item(label="Exit", callback=lambda: dpg.stop_dearpygui())

        with dpg.table(header_row=True, tag="bumper info", borders_innerH=True,
                       borders_outerH=True, borders_innerV=True, borders_outerV=True, show=False):
            dpg.add_table_column(label="Forum URL")
            dpg.add_table_column(label="Number of Threads")
            dpg.add_table_column(label="Delay")

        dpg.add_button(label="Bump", tag="bump btn", show=False, callback=lambda: launch_bumper.post_timer())

    with dpg.window(label="Website", tag="website", width=200, height=50,
                    no_resize=True, no_close=True, show=False, pos=[100, 50]):

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
            dpg.add_button(label="Approved on Duo", callback=lambda s, a, u: get_duo(launch_bumper, dpg))
            dpg.add_text("Failed Duo Push", tag="failed duo", color=[255, 0, 0], show=False)

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

    if Path("./resources/details.json").is_file():
        launch_bumper.load_details()
        if launch_bumper.check_login() is False:
            logged_in(launch_bumper, dpg)
        else:
            dpg.configure_item("website", show=True)
    else:
        dpg.configure_item("website", show=True)

    dpg.create_viewport(title='Xenforo Bumper', width=600, height=500)
    dpg.setup_dearpygui()
    dpg.set_viewport_large_icon("./resources/xfbump.ico")
    dpg.set_viewport_small_icon("./resources/xfbump.ico")
    dpg.show_viewport()
    dpg.set_primary_window("primary", True)
    dpg.start_dearpygui()
    dpg.destroy_context()
