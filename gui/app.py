import os
import sys
import colorsys
from kivy.app import App as kvApp
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle, Line, Point, Ellipse, Quad, Triangle, Bezier
from kivy.uix.behaviors.button import ButtonBehavior
from kivy.utils import get_color_from_hex

from logic import board

#TODO:
# -Show who's turn it is,
# -Add way to choose game_mode,
# -Add game_over indicator,
# -Add restart functionality,
# -Show turn counter,
# -In PvP and PvE modes, when unit is selected, highlight possible moves


FPS = 10
DEFAULT_BG_COLOR = (0, 1, 0.1)
colors = {
    "orange":"#EF8D1F",
    "blue":"#1F35EF",
    "purple":"#A93CF1",
    "pink":"#F13CB6",
    "yellow":"#DFEF0D",
    "red":"#DA100D",
    "green":"#79C10D",
    "brown":"#5E340C",
}
#gamemode: 0 = PvP,1 = PvE,2 = EvE

class App(kvApp):
    def __init__(self, board, fps=FPS, **kwargs):
        print(f'Starting App...')
        super().__init__(**kwargs)
        self.title = 'Kamisado'
        self.board = board
        Clock.schedule_interval(self.mainloop_hook, 1/fps)
        self.create_widgets()

    def mainloop_hook(self, dt):
        # print(f'refreshing.. ({round(dt, 3)} ms frame)')
        self.grid_widget.refresh()

    def create_widgets(self):
        self.root = BoxLayout(orientation='vertical')
        self.root.add_widget(MainMenu(self))
        self.grid_widget = Grid(self.board)
        self.root.add_widget(self.grid_widget)


class MainMenu(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.size_hint = (1, None)
        self.size = (0, '30dp')
        self.add_widget(Button(text='Restart', on_release=lambda *a: os.execl(sys.executable, sys.executable, *sys.argv)))
        self.add_widget(Button(text='Quit', on_release=lambda *a: quit()))


class Grid(GridLayout):
    def __init__(self, board, **kwargs):
        super().__init__(**kwargs)
        self.board = board
        self.game_mode = board.game_mode
        self.grid = {}
        self.units = {}
        self.selected_cell = None
        self.create_cells()

    def refresh_units(self, units):
        for uid, unit in self.units.items():
            # undraw the unit
            pass
        for unit in units:
            uid = f'{unit.player}{unit.color_index}'
            # cache new units
            if uid not in self.units:
                self.units[uid] = unit
            # redraw unit
            #self.units[uid]


    def create_cells(self):
        height, width = self.board.board_size
        self.cols = width
        for y in range(height):
            for x in range(width):
                # Make the cell
                color = get_color_from_hex(self.board.board_colors[self.board.board[(y,x)].color_index])
                cell = self.grid[(y,x)] = Cell(color)
                self.add_widget(cell)

                # Register clicks
                cell.bind(on_release=lambda btn, y=y, x=x: self.clicked(y, x))

    def request_move(self, origin, target):
        if origin == target:
            return
        unit = self.resolve_unit(origin)
        if unit:
            print(f'Requesting move unit: {unit} from {origin} to {target}')
            self.board.move_logic(unit, target)

    def request_bot_move(self):
        self.board.move_logic()

    def resolve_unit(self, yx):
        for unit in self.board.get_units():
            if unit.location == yx:
                return unit
        return None

    def clicked(self, y, x):
        yx = (y, x)
        # print(f'clicked {yx}')
        if self.board.game_over:
            print("GGWP")
            return
        #players move
        if self.game_mode == 0 or (self.game_mode == 1 and self.board.turn == self.board.player_color):
            if self.selected_cell:
                # request move from selected cell to clicked cell
                self.request_move(self.selected_cell, yx)
                self.selected_cell = None
                # dehighlight all cells
                for cell in self.grid.values():
                    cell.dehighlight()
            else:
                # set clicked cell as selected cell
                self.selected_cell = yx
                print(f'Selected: {yx}')
                self.grid[yx].highlight()
        #Bots move
        else:
            self.request_bot_move()
    def refresh(self):
        for cell in self.grid.values():
            cell.remove_unit()
        for unit in self.board.get_units():
            player_color = resolve_player_color(unit.player)
            unit_color = resolve_unit_color(unit.color_index)
            self.grid[unit.location].set_unit(player_color=player_color, unit_color=unit_color)

    def clear(self):
        for cell in self.grid.values():
            cell.remove_unit()


class Cell(ButtonBehavior, BoxLayout):
    def __init__(self, color, **kwargs):
        super().__init__(**kwargs)
        # Cell color
        self.cell_color = color
        self.highlighted = False
        make_bg(self, self.cell_color, hsv=False)
        self.player_color = (1, 1, 1, 0)
        self.unit_color = (0, 0, 0, 0)
        # Make cell unit graphics
        with self.canvas:
            self.canvas_highlight_color = Color(0, 0, 0, 0)
            self.canvas_highlight_circle = Ellipse(pos=self.pos, size=(60, 60))
            self.canvas_player_color = Color(*self.player_color)
            self.canvas_player_circle = Ellipse(pos=self.pos, size=(40, 40))
            self.canvas_unit_color = Color(*self.unit_color)
            self.canvas_unit_circle = Ellipse(pos=self.pos, size=(20, 20))

    def highlight(self):
        # make_bg(self, (0.5, 0.5, 0.5), hsv=False)
        self.canvas_highlight_color.rgba = (0, 0, 0, 1)
        self.highlighted = True

    def dehighlight(self):
        # make_bg(self, self.cell_color, hsv=False)
        self.canvas_highlight_color.rgba = (0, 0, 0, 0)
        self.highlighted = False

    def remove_unit(self):
        self.set_unit((0, 0, 0, 0), (0, 0, 0, 0))

    def set_unit(self, player_color, unit_color):
        self.player_color = player_color
        self.canvas_player_color.rgba = self.player_color
        self.unit_color = unit_color
        self.canvas_unit_color.rgba = self.unit_color
        self.refresh()

    def refresh(self):
        self.canvas_highlight_circle.pos = self.pos
        self.canvas_player_circle.pos = offset_point(self.pos, (10, 10))
        self.canvas_unit_circle.pos = offset_point(self.pos, (20, 20))


def _update_bg(widget, *args):
    widget._bg.pos = widget.pos
    widget._bg.size = widget.size

def make_bg(widget, color=None, hsv=True):
    if hsv is False and color:
        color = (*colorsys.rgb_to_hsv(*color[:3]), *color[3:])
    color = DEFAULT_BG_COLOR if color is None else color
    if hasattr(widget, '_bg') and widget._bg_color is not None:
        if isinstance(widget._bg_color, Color):
            widget._bg_color.hsv = color
            return color
    with widget.canvas.before:
        widget._bg_color = Color(*color, mode='hsv')
        widget._bg = Rectangle(size=widget.size, pos=widget.pos)
        widget.bind(pos=lambda *a: _update_bg(widget), size=lambda *a: _update_bg(widget))
    return color

def resolve_player_color(player):
    return (0.75, 0.75, 0.75, 1) if player else (0, 0, 0, 1)

def resolve_unit_color(unit_index):
    return get_color_from_hex(board.COLORS[unit_index])

def offset_point(point, offset):
    return (point[0]+offset[0], point[1]+offset[1])
