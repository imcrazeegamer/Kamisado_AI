import os
import sys
import colorsys
from kivy.app import App as kvApp
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.graphics import Color, Rectangle, Line, Point, Ellipse, Quad, Triangle, Bezier
from kivy.uix.behaviors.button import ButtonBehavior

from logic.game import Game


FPS = 10
DEFAULT_BG_COLOR = (0, 1, 1, 0.1)


COLORS_DICT = {
    'orange': (1, 0.5, 0.1, 1),
    'blue': (0, 0.2, 1, 1),
    'purple': (0.5, 0, 1, 1),
    'pink': (1, 0.2, 0.6, 1),
    'yellow': (0.8, 0.8, 0, 1),
    'red': (1, 0, 0, 1),
    'green': (0.5, 0.7, 0, 1),
    'brown': (0.4, 0.3, 0, 1),
}
COLORS = list(COLORS_DICT.values())
COLOR_NAMES = list(COLORS_DICT.keys())

class App(kvApp):
    def __init__(self, fps=FPS, **kwargs):
        print(f'Starting App...')
        super().__init__(**kwargs)
        self.title = 'Kamisado'
        self.new_board()
        Clock.schedule_interval(self.mainloop_hook, 1/fps)
        self.create_widgets()

    def new_board(self, black=None, white=None):
        self.board = Game.new_board(black_bot_name=black, white_bot_name=white)

    def mainloop_hook(self, dt):
        self.grid_widget.refresh()
        self.main_menu.refresh()

    def create_widgets(self):
        self.root = BoxLayout(orientation='vertical')
        self.main_menu = MainMenu(self)
        self.grid_widget = Grid(self)
        self.root.add_widget(self.main_menu)
        self.root.add_widget(self.grid_widget)


class MainMenu(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.app = app
        self.size_hint = (1, None)
        self.size = (0, '60dp')
        self.info = Label(text='', size_hint_x=4)
        self.selected_white = 'Player'
        self.selected_black = 'Player'
        self.bot_list = ['Player'] + list(Game.Known_bots.keys())

        top, bot = BoxLayout(), BoxLayout()
        self.add_widget(top)


        white_dd = DropDown()
        black_dd = DropDown()

        def select_bot(btn, text, color):
            setattr(btn, 'text', f'{color}: {text}')
            if color[0].lower() == 'w':
                self.selected_white = text
            elif color[0].lower() == 'b':
                self.selected_black = text
            else:
                raise RuntimeError(f'Unknown color value:', color)

        for cname, dd in (('Black', black_dd), ('White', white_dd)):
            for bot_name in self.bot_list:
                dd_btn = Button(text=bot_name, size_hint_y=None, height=44)
                dd_btn.bind(on_release=lambda x, xd=dd: xd.select(x.text))
                dd.add_widget(dd_btn)

            selector = Button(text=f'{cname}: Player', size_hint_x=2)
            top.add_widget(selector)
            selector.bind(on_release=dd.open)
            dd.bind(on_select=lambda _, x, s=selector, c=cname: select_bot(s, x, c))


        top.add_widget(Button(text='New Game', on_release=lambda *a: self.new_board()))
        top.add_widget(Button(text='Restart', on_release=lambda *a: os.execl(sys.executable, sys.executable, *sys.argv)))
        top.add_widget(Button(text='Quit', on_release=lambda *a: quit()))

        self.add_widget(bot)
        bot.add_widget(self.info)
        bot.add_widget(Button(text='Pass', on_release=lambda *a: self.pass_move()))
        bot.add_widget(Button(text='Bot move', on_release=lambda *a: self.bot_move()))

        for index in range(5):
            dunno_why_but_kivy_wants_5_yes_5_at_least_buttons_not_garbage_collected_for_the_damn_dropdown_to_work = Button()

    def new_board(self):
        black = None if self.selected_black == 'Player' else self.selected_black
        white = None if self.selected_white == 'Player' else self.selected_white
        self.app.new_board(black=black, white=white)

    def pass_move(self):
        self.app.board.pass_turn()

    def bot_move(self):
        self.app.board.bot_move()

    def refresh(self):
        gameover, winner = self.app.board.is_game_over()
        if gameover:
            winner = resolve_player_name(winner)
            turn_count = self.app.board.get_turn_count()
            self.info.text = f'Game over, {winner} wins! ({turn_count} turns)'
            make_bg(self.info, color=(0.5, 0.5, 0.5, 1))
            return

        turn = self.app.board.get_turn()
        turn_color = resolve_player_name(turn)
        if turn:
            bg = (1, 1, 1, 1)
            fg = (0, 0, 0, 1)
        else:
            bg = (0, 0, 0, 1)
            fg = (1, 1, 1, 1)
        bname, wname = self.app.board.player_names()
        info_text = f'{bname} (Black) vs. {wname} (White) | Turn {self.app.board.get_turn_count():>2}: {turn_color}'
        self.info.text = info_text
        make_bg(self.info, color=bg)
        self.info.color = fg


class Grid(GridLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.grid = {}
        self.units = {}
        self.selected_cell = None
        self.create_cells()

    @property
    def board(self):
        return self.app.board

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
                color = COLORS[self.board.board[(y,x)].color_index]
                cell = self.grid[(y,x)] = Cell(color)
                self.add_widget(cell)

                # Register clicks
                cell.bind(on_release=lambda btn, y=y, x=x: self.clicked(y, x))

    def request_move(self, origin, target):
        if origin == target:
            return
        unit = self.resolve_unit(origin)
        if unit:
            self.board.move_logic(unit, target)

    def resolve_unit(self, yx):
        for unit in self.board.get_units():
            if unit.location == yx:
                return unit
        return None

    def clicked(self, y, x):
        yx = (y, x)
        if self.board.game_over:
            print("ggwp")
            return
        self.cell_select(yx)

    def cell_select(self, yx):
        if self.selected_cell:
            # request move from selected cell to clicked cell
            self.request_move(self.selected_cell, yx)
            self.selected_cell = None
            # dehighlight all cells
            self.dehighlight()
            self.show_origins()
        elif yx in self.board.origins_with_legal_moves():
            # set clicked cell as selected cell
            self.selected_cell = yx
            self.grid[yx].highlight()
            self.show_moves(yx)

    def show_origins(self):
        origins = self.board.origins_with_legal_moves()
        for origin in origins:
            self.grid[origin].highlight_soft()

    def show_moves(self, yx):
        targets = self.board.legal_moves(yx)
        for target in targets:
            self.grid[target].highlight_soft()

    def dehighlight(self):
        for cell in self.grid.values():
            cell.dehighlight()

    def refresh(self):
        for cell in self.grid.values():
            cell.remove_unit()
        for unit in self.board.get_units():
            player_color = resolve_player_color(unit.player)
            unit_color = COLORS[unit.color_index]
            self.grid[unit.location].set_unit(player_color=player_color, unit_color=unit_color)
        if self.selected_cell is None and not self.board.is_game_over()[0]:
            self.dehighlight()
            self.show_origins()

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
        self.player_color = (0, 0, 0, 0)
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
        self.canvas_highlight_color.rgba = (0, 0, 0, 1)
        self.highlighted = True

    def highlight_soft(self):
        self.canvas_highlight_color.rgba = (0, 0, 0, 0.35)
        self.highlighted = True

    def dehighlight(self):
        self.canvas_highlight_color.rgba = (0, 0, 0, 0)
        self.highlighted = False

    def remove_unit(self):
        self.set_unit((0, 0, 0, 0), (0, 0, 0, 0))

    def set_unit(self, player_color, unit_color):
        self.canvas_player_color.rgba = self.player_color = player_color
        self.canvas_unit_color.rgba = self.unit_color = unit_color
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
            widget._bg_color.rgba = color
            return color
    with widget.canvas.before:
        widget._bg_color = HSV(*color)
        widget._bg = Rectangle(size=widget.size, pos=widget.pos)
        widget.bind(pos=lambda *a: _update_bg(widget), size=lambda *a: _update_bg(widget))
    return color


def resolve_player_color(player):
    return (1, 1, 1, 1) if player else (0, 0, 0, 1)


def resolve_player_name(player):
    return 'White' if player else 'Black'


def offset_point(point, offset):
    return (point[0]+offset[0], point[1]+offset[1])


def HSV(h, s, v, a=1):
    return Color(*colorsys.hsv_to_rgb(h, s, v), a)