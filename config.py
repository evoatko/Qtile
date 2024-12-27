#KOPIJA
# Copyright (c) 2010 Aldo Cortesi
# Copyright (c) 2010, 2014 dequis
# Copyright (c) 2012 Randall Ma
# Copyright (c) 2012-2014 Tycho Andersen
# Copyright (c) 2012 Craig Barnes
# Copyright (c) 2013 horsik
# Copyright (c) 2013 Tao Sauvage
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from libqtile import bar, layout, qtile, widget
from libqtile.config import Click, Drag, Group, Key, Match, Screen
from libqtile.lazy import lazy
import os
import socket
import subprocess
from qtile_extras import widget
from libqtile import hook
from libqtile.utils import send_notification
from qtile_extras.widget.groupbox2 import GroupBoxRule
import asyncio
import sys
import qtile_extras.hook



@hook.subscribe.float_change
def float_change():
    send_notification("qtile", "Window float state changed.")

home = os.path.expanduser('~')


def set_label(rule, box):
    if box.focused:
        rule.text = "󰣠"
    elif box.occupied:
        rule.text = "◎"
    else:
        rule.text = "○"

    return True


mod = "mod4"
terminal = "wezterm"

keys = [
    # A list of available commands that can be bound to keys can be found
    # at https://docs.qtile.org/en/latest/manual/config/lazy.html
    # Switch between windows
    Key([mod], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([mod], "l", lazy.layout.right(), desc="Move focus to right"),
    Key([mod], "j", lazy.layout.down(), desc="Move focus down"),
    Key([mod], "k", lazy.layout.up(), desc="Move focus up"),
    Key([mod], "space", lazy.layout.next(), desc="Move window focus to other window"),
    # Move windows between left/right columns or move up/down in current stack.
    # Moving out of range in Columns layout will create new column.
    Key([mod, "shift"], "h", lazy.layout.shuffle_left(), desc="Move window to the left"),
    Key([mod, "shift"], "l", lazy.layout.shuffle_right(), desc="Move window to the right"),
    Key([mod, "shift"], "j", lazy.layout.shuffle_down(), desc="Move window down"),
    Key([mod, "shift"], "k", lazy.layout.shuffle_up(), desc="Move window up"),
    # Grow windows. If current window is on the edge of screen and direction
    # will be to screen edge - window would shrink.
    Key([mod, "control"], "h", lazy.layout.grow_left(), desc="Grow window to the left"),
    Key([mod, "control"], "l", lazy.layout.grow_right(), desc="Grow window to the right"),
    Key([mod, "control"], "j", lazy.layout.grow_down(), desc="Grow window down"),
    Key([mod, "control"], "k", lazy.layout.grow_up(), desc="Grow window up"),
    Key([mod], "n", lazy.layout.normalize(), desc="Reset all window sizes"),
    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    Key(
        [mod, "shift"],
        "Return",
        lazy.layout.toggle_split(),
        desc="Toggle between split and unsplit sides of stack",
    ),
    Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod], "q", lazy.window.kill(), desc="Kill focused window"),
    Key([mod], "f", lazy.window.toggle_fullscreen(), desc="Toggle fullscreen on the focused window",),
    Key([mod], "t", lazy.window.toggle_floating(), desc="Toggle floating on the focused window"),
    Key([mod, "control"], "r", lazy.reload_config(), desc="Reload the config"),
    Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    Key([mod], "r", lazy.spawn("rofi -show drun"), desc="Spawn a command using a prompt widget"),
    Key([mod], "Print", lazy.spawn("scrot /home/evo/scrot/%Y-%m-%d-%T-screenshot.png"), desc="scrot"),
    #Key([mod], "1", lazy.to_screen(0), desc="Switch to Laptop monitor"),
    #Key([mod], "2", lazy.to_screen(1), desc="Switch to external monitor"),
    #Key([mod], "u", lazy.group["u1"].toscreen().when(func=lambda: qtile.current_screen.index == 0), lazy.group["u2"].toscreen().when(func=lambda: qtile.current_screen.index == 1))
]

# Add key bindings to switch VTs in Wayland.
# We can't check qtile.core.name in default config as it is loaded before qtile is started
# We therefore defer the check until the key binding is run by using .when(func=...)
for vt in range(1, 8):
    keys.append(
        Key(
            ["control", "mod1"],
            f"f{vt}",
            lazy.core.change_vt(vt).when(func=lambda: qtile.core.name == "wayland"),
            desc=f"Switch to VT{vt}",
        )
    )


#groups = [Group(i) for i in "123456789"]

groups = [
    Group(name="u", screen_affinity=0),
    Group(name="i", screen_affinity=0),
    Group(name="o", screen_affinity=0),
    Group(name="p", screen_affinity=0),
    Group(name="8", screen_affinity=1),
    Group(name='9', screen_affinity=2),
]

def go_to_group(name: str):
    def _inner(qtile):
        if len(qtile.screens) == 1:
            qtile.groups_map[name].toscreen()
            return
   
        if name in 'uiop':
            qtile.focus_screen(0)
            qtile.groups_map[name].toscreen()
        else:
            if name in '8':
                qtile.focus_screen(1)
                qtile.groups_map[name].toscreen()
            else:
                if name in '9':
                    qtile.focus_screen(2)
                    qtile.groups_map[name].toscreen()
    return _inner


for i in groups:
    keys.append(Key([mod], i.name, lazy.function(go_to_group(i.name))))

def go_to_group_and_move_window(name: str):
    def _inner(qtile):
        if len(qtile.screens) == 1:
            qtile.current_window.togroup(name, switch_group=True)
            return

        if name in "uiop":
            qtile.current_window.togroup(name, switch_group=False)
            qtile.focus_screen(0)
            qtile.groups_map[name].toscreen()
        else:
            if name in "8":
                qtile.current_window.togroup(name, switch_group=False)
                qtile.focus_screen(1)
                qtile.groups_map[name].toscreen()
            else:
                if name in "9":
                    qtile.current_window.togroup(name, switch_group=False)
                    qtile.focus_screen(2)
                    qtile.groups_map[name].toscreen()

    return _inner

for i in groups:
    keys.append(Key([mod, "shift"], i.name, lazy.function(go_to_group_and_move_window(i.name))))


# Code incorrect - does not work as intended --> START
groupbox1 = widget.GroupBox2(visible_groups=['u', 'i', 'o', 'p'])
groupbox2 = widget.GroupBox2(visible_groups=['8'])
groupbox3 = widget.GroupBox2(visible_groups=['9'])

@hook.subscribe.screens_reconfigured
async def _():
    if len(qtile.screens) > 1:
        groupbox1.visible_groups = ['u', 'i', 'o', 'p']
    else:
        groupbox1.visible_groups = ['u', 'i', 'o', 'p', '8']
    if len(qtile.screens) > 2:
        groupbox1.visible_groups = ['u', 'i', 'o', 'p', '8']
    else:
        groupbox1.visible_groups = ['u', 'i', 'o', 'p', '8', '9']
    if hasattr(groupbox1, 'bar'):
        groupbox1.bar.draw()
# Code incorrect - does not work as intended <-- END

layouts = [
    layout.Columns(
        border_focus=["#363646", "#363646"],
        #border_focus=["#d75f5f", "#8f3d3d"],
        border_normal=["#0e0b0b", "#0e0b0b"],
        border_width=2,
        margin=10,
        margin_on_single=30
    ),
    layout.Floating(
        border_focus=["#949eb4", "#949eb4"],
    ),
    layout.Max(),
]

widget_defaults = dict(
    font="Hack Nerd Font",
    fontsize=20,
    padding=3,
)
extension_defaults = widget_defaults.copy()

screens = [
    Screen(
        top=bar.Bar(
            [
                #widget.UPowerWidget(battery_height=12, battery_width=24, battery_name=1, border_charge_colour='72798c', border_colour='5a6356', border_critical_colour='904b4b'),
                widget.Spacer(),
                widget.WidgetBox(text_closed='󰐗 ' ,text_open='󰍶 ', foreground='5a6356', widgets=[
                    widget.Sep(linewidth=15, foreground='0e0b0b'),
                    widget.Wttr(location={'Klaipeda': 'Home'}, foreground='5a6356'),
                    widget.Sep(linewidth=25, background='0e0b0b', foreground='0e0b0b'),
                    widget.CheckUpdates(distro='FreeBSD', colour_have_updates='710603', colour_no_updates='5a6356', no_update_string='No updates', update_interval=604800),
                ]),                
                #widget.WindowTabs(max_chars=35, foreground='000000'),
                widget.Spacer(),
                widget.Clock(format="%y/%m/%d %a %H:%M", foreground="5a6356"),
            ],
            25,
	    background='#0e0b0b',
        ),
        bottom=bar.Bar(
            [
                widget.CurrentLayoutIcon(background="#0e0b0b", scale=0.8, foreground="#363646", use_mask=True),
                widget.Sep(linewidth=15, foreground='0e0b0b'),
#                widget.LaunchBar(padding=10, icon_size=34,
#                                progs=[
#                                    ('~/.config/icons/png/neovim.png', 'wezterm -e nvim', 'launch neovim'),
#                                    ('~/.config/icons/png/folder.png', 'wezterm -e mc', 'launch Midnight Commander'),
#                                    ('~/.config/icons/png/firefox.png', 'firefox', 'launch firefox'),
#                                    ('~/.config/icons/png/ai.png', 'wezterm -e oatmeal -c /home/evo/.config/oatmeal/coding.toml', 'launch ollama deepseek-coder'),
#                                    ('~/.config/icons/png/head.png', 'wezterm -e oatmeal -c /home/evo/.config/oatmeal/config.toml', 'launch ollama gemma2'),
#                                    ('~/.config/icons/png/database.png', 'wezterm -e oatmeal -c /home/evo/.config/oatmeal/sql.toml', 'launch ollama sql'),
#                                    ('~/.config/icons/png/radiation.png', 'wezterm -e oatmeal -c /home/evo/.config/oatmeal/uncensored.toml', 'launch llama2-uncensored'),
#                                    ('~/.config/icons/png/desktop.png', 'wezterm -e ssh evo@192.168.1.100', 'launch WS'),
#                                    ('~/.config/icons/png/gimp.png', 'gimp', 'launch gimp'),
#                                ],
#                                 background='#0e0b0b'
#                                ),
                widget.Spacer(),
                widget.GroupBox2(
                    visible_groups=['u', 'i', 'o', 'p'],
                    fontsize=20,
                    padding_x=5,
                    rules=[
                        GroupBoxRule().when(func=set_label),
                        GroupBoxRule(text_colour="710603").when(screen=GroupBoxRule.SCREEN_THIS),
                        GroupBoxRule(text_colour="c4746e").when(screen=GroupBoxRule.SCREEN_OTHER),
                        GroupBoxRule(text_colour="c4746e")  #2aa198 b58900
                    ]
                ),
                #widget.Spacer(),
                #widget.Notify(action=True, fontsize=14),
                #widget.Battery(show_short_text=False, low_percentage=0.10, low_foreground='904b4b', empty_char="󰁺", charge_char="󰂅", discharge_char="󰂌", full_char='󰁹', battery=0, foreground="5a6356"),
                #widget.Battery(show_short_text=False, low_percentage=0.10, low_foreground='904b4b', empty_char="󰁺", charge_char="󰂅", discharge_char="󰂌", full_char='󰁹', battery=1, foreground="5a6356"),
                # NB Systray is incompatible with Wayland, consider using StatusNotifier instead
                # widget.StatusNotifier(),
                widget.Systray(),
            ],
            34,
	    background='#0e0b0b',
        ),
#        wallpaper='~/.config/.wall/imthinkingcorrectly.png',
        background='#0e0b0b'
        # You can uncomment this variable if you see that on X11 floating resize/moving is laggy
        # By default we handle these events delayed to already improve performance, however your system might still be struggling
        # This variable is set to None (no cap) by default, but you can set it to 60 to indicate that you limit it to 60 events per second
        #x11_drag_polling_rate = 60,
    ),
    Screen(
        bottom=bar.Bar(
            [
                widget.CurrentLayoutIcon(background="#0e0b0b", scale=0.8, foreground="#363646", use_mask=True),
                widget.Sep(linewidth=15, foreground='0e0b0b'),
                widget.GroupBox2(visible_groups=['8'],
                    fontsize=20,
                    padding_x=5,
                    rules=[
                        GroupBoxRule().when(func=set_label),
                        GroupBoxRule(text_colour="710603").when(screen=GroupBoxRule.SCREEN_THIS),
                        GroupBoxRule(text_colour="c4746e").when(screen=GroupBoxRule.SCREEN_OTHER),
                        GroupBoxRule(text_colour="c4746e")
                    ]
                ),
            ],
            34,
        background='0e0b0b',
        ),
        background='0e0b0b',
        #x11_drag_polling_rate = 24,
    ),
    Screen(
        top=bar.Bar(
            [
                widget.CurrentLayoutIcon(background="#0e0b0b", scale=0.8, foreground="#363646", use_mask=True),
                widget.Sep(linewidth=15, foreground='0e0b0b'),
                widget.GroupBox2(visible_groups=['9'],
                    fontsize=20,
                    padding_x=5,
                    rules=[
                        GroupBoxRule().when(func=set_label),
                        GroupBoxRule(text_colour="710603").when(screen=GroupBoxRule.SCREEN_THIS),
                        GroupBoxRule(text_colour="c4746e").when(screen=GroupBoxRule.SCREEN_OTHER),
                        GroupBoxRule(text_colour="c4746e")
                    ]
                ),
            ],
            34,
        background='0e0b0b',
        ),
        background='0e0b0b',
    ),
]

# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = True
bring_front_click = False
floats_kept_above = True
cursor_warp = False
floating_layout = layout.Floating(
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
    ]
)
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

# When using the Wayland backend, this can be used to configure input devices.
wl_input_rules = None

# xcursor theme (string or None) and size (integer) for Wayland backend
wl_xcursor_theme = None
wl_xcursor_size = 24

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"
