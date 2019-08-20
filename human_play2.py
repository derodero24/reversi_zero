from kivy.animation import Animation
from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line
from kivy.uix.widget import Widget
from tensorflow.keras.models import load_model

from game import State
from pv_mcts import pv_mcts_action
from time import sleep

model = load_model('./model/best_org.h5')
state = State()
next_action = pv_mcts_action(model, 0.0)


class MyWedget(Widget):

    def reset(self):
        self.canvas.clear()
        with self.canvas:
            Color(0, 0, 0, 1)
            for i in range(7):
                Line(points=[0, i*80, 480, i*80], width=2, close='True')
                Line(points=[i*80, 0, i*80, 480], width=2, close='True')

        self.draw_piece()


    def on_touch_down(self, touch):
        ''' クリックイベント '''
        self.turn_of_human(touch)

    # 人間のターン
    def turn_of_human(self, touch):
        global state

        # ゲーム終了時
        if state.is_done():
            state = State()
            self.reset()
            return

        # 先手でない時
        if not state.is_first_player():
            return

        # クリック位置を行動に変換
        x = int(touch.pos[0] / 80)
        y = int(touch.pos[1] / 80)
        action = x + y * 6

        if x < 0 or 5 < x or y < 0 or 5 < y: # 範囲外
            return

        # 合法手でない時
        legal_actions = state.legal_actions()
        if legal_actions == [36]:
            action = 36 # パス
        if action != 36 and not (action in legal_actions):
            return

        # 次の状態の取得
        state = state.next(action)

        # 丸追加
        self.draw_piece()
        sleep(1)

        # AIのターン
        self.turn_of_ai()

    # AIのターン
    def turn_of_ai(self):
        global state

        # ゲーム終了時
        if state.is_done():
            return

        # 行動の取得
        action = next_action(state)

        # 次の状態の取得
        state = state.next(action)

        # バツ追加
        self.draw_piece()

    def draw_piece(self):
        global state

        with self.canvas:
            for i in range(36):
                if state.pieces[i] == 1:
                    Color(0, 0, 0, 1)
                elif state.enemy_pieces[i] == 1:
                    Color(1, 1, 1, 1)
                else:
                    continue

                x = (i % 6) * 80 + 10
                y = int(i / 6) * 80 + 10
                Ellipse(pos=(x, y), size=(60, 60))


class GameUI(App):
    def build(self):
        Window.size = (240, 240)
        Window.clearcolor = (0.7, 0.5, 0.3, 1)
        widget = MyWedget()
        widget.reset()
        return widget


if __name__ == "__main__":
    GameUI().run()
