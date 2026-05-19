import pygame as pg
import sys
import json
import os


# Инициализация звука
pg.mixer.init()

# Создаем папку для звуков если её нет
if not os.path.exists('sounds'):
    os.makedirs('sounds')

# Загрузка звуков с проверкой на существование файлов
def load_sound(filename):
    """Загружает звук если файл существует, пробует разные форматы"""
    # Пробуем загрузить mp3
    try:
        return pg.mixer.Sound(f'sounds/{filename}.mp3')
    except:
        pass
    
    # Пробуем загрузить wav
    try:
        return pg.mixer.Sound(f'sounds/{filename}.wav')
    except:
        pass
    
    # Пробуем загрузить ogg
    try:
        return pg.mixer.Sound(f'sounds/{filename}.ogg')
    except:
        pass
    
    print(f"Звуковой файл {filename} не найден")
    return None

# Загрузка звуковых эффектов
move_sound = load_sound('move')
checkmate_sound = load_sound('checkmate')
game_start_sound = load_sound('game_start')

# Функции для работы с музыкой
def play_background_music():
    """Запускает фоновую музыку"""
    try:
        pg.mixer.music.load('sounds/background_music.mp3')
        pg.mixer.music.set_volume(0.3)  # Громкость 30%
        pg.mixer.music.play(-1)  # -1 означает бесконечное повторение
    except:
        try:
            pg.mixer.music.load('sounds/background_music.wav')
            pg.mixer.music.set_volume(0.3)
            pg.mixer.music.play(-1)
        except:
            try:
                pg.mixer.music.load('sounds/background_music.ogg')
                pg.mixer.music.set_volume(0.3)
                pg.mixer.music.play(-1)
            except:
                print("Фоновая музыка не найдена")

def stop_background_music():
    """Останавливает фоновую музыку"""
    pg.mixer.music.stop()

def play_sound(sound):
    """Безопасное воспроизведение звука"""
    if sound:
        sound.play()


class Figure:
    screen = [['🙩'] * 8 for _ in range(8)]
    figures = []
    kings = []
    rooks = []
    turn = "White"

    def __init__(self, name, x, y, color):
        self.icon = "🙾"
        self.x = x
        self.y = y
        self.name = name
        self.color = color
        self.is_moved = False
        self.status = "Alive"
        if self.name != "Non-existent":
            Figure.figures.append(self)

    def __str__(self):
        return f"Объект класса {self.name}, координаты ({self.x}, {self.y})"

    def draw(self):
        if self.status == "Killed" or self.status == "Moving":
            return
        font = pg.font.Font('./lib/CASEFONT.TTF', 72)
        icon = self.icon[1]
        text1 = font.render(icon, True, (26, 13, 0))
        # Визуально переворачиваем доску в зависимости от флага
        if board_flipped:
            draw_x = 7 - self.x
            draw_y = 7 - self.y
        else:
            draw_x = self.x
            draw_y = self.y
        sc.blit(text1, (120 + draw_x * 70, 70 + draw_y * 70))

    def move(self, coord):
        paths = self.paths
        global counter, turns, per, ko, game_over, winner_color, board_flipped, two_players, clock
        new_x, new_y = coord[0], coord[1]
        path = paths[new_y][new_x]
        s = self.icon[0]
        sep = '-'
        end = ''
        
        if path in ["1", "2", "3", "4"]:
            # Сохраняем начальные координаты для анимации
            start_x, start_y = self.x, self.y
            
            # Временно убираем фигуру с начальной позиции
            temp_status = self.status
            self.status = "Moving"
            
            if path == "2":
                Figure_to_kill = Figure.check_for_figure((new_x, new_y))
                Figure_to_kill.kill()
                sep = ':'
                play_sound(move_sound)  # Звук взятия
            if path == "3":
                # рокировка с анимацией
                rook = Figure.check_for_figure((0 if new_x == 2 else 7, self.y))
                rook_start_x = rook.x
                rook_end_x = (self.x + new_x) // 2
                
                # Временно убираем ладью
                rook_temp_status = rook.status
                rook.status = "Moving"
                
                # Анимация перемещения ладьи
                steps = 15
                for step in range(steps + 1):
                    t = step / steps
                    anim_x = rook_start_x + (rook_end_x - rook_start_x) * t
                    
                    # Очищаем и перерисовываем
                    update(figures, background, image, counter)
                    
                    # Рисуем ладью в промежуточной позиции
                    font = pg.font.Font('./lib/CASEFONT.TTF', 72)
                    icon = rook.icon[1]
                    text1 = font.render(icon, True, (26, 13, 0))
                    if board_flipped:
                        draw_x = 7 - anim_x
                        draw_y = 7 - rook.y
                    else:
                        draw_x = anim_x
                        draw_y = rook.y
                    sc.blit(text1, (120 + draw_x * 70, 70 + draw_y * 70))
                    pg.display.update()
                    clock.tick(120)
                
                rook.status = rook_temp_status
                rook.x = rook_end_x
                play_sound(move_sound)  # Звук рокировки
            if path == "4":  # взятие на проходе
                Figure_to_kill = Figure.check_for_figure((new_x, self.y))
                Figure_to_kill.kill()
                play_sound(move_sound)  # Звук взятия
            
            # Звук обычного хода (если не было других звуков)
            if path == "1":
                play_sound(move_sound)
            
            # Анимация перемещения фигуры
            steps = 15
            for step in range(steps + 1):
                t = step / steps
                # Плавное перемещение по линейной интерполяции
                anim_x = start_x + (new_x - start_x) * t
                anim_y = start_y + (new_y - start_y) * t
                
                # Очищаем и перерисовываем доску
                update(figures, background, image, counter)
                
                # Рисуем движущуюся фигуру в промежуточной позиции
                font = pg.font.Font('./lib/CASEFONT.TTF', 72)
                icon = self.icon[1]
                text1 = font.render(icon, True, (26, 13, 0))
                if board_flipped:
                    draw_x = 7 - anim_x
                    draw_y = 7 - anim_y
                else:
                    draw_x = anim_x
                    draw_y = anim_y
                sc.blit(text1, (120 + draw_x * 70, 70 + draw_y * 70))
                pg.display.update()
                clock.tick(120)
            
            # Возвращаем статус и устанавливаем новые координаты
            self.status = temp_status
            self.x, self.y = new_x, new_y
            counter += 1
            
            # Небольшая пауза после анимации
            pg.time.wait(150)
            
            # Перерисовываем финальное состояние
            update(figures, background, image, counter)
            pg.display.update()
            
            if type(self) in [Pawn, Rook, King]:
                self.is_moved = True
                if type(self) == Pawn:
                    self.step += 1
                    if self.y in [0, 7]:  # замена пешки на другую фигуру
                        self.promotion()
            if self.enemy_king.strike_check()[0]:
                end = '+' * len(self.enemy_king.strike_check()[1])
            if counter % 2 != 0:
                if path == '3':
                    if new_x == 2:
                        per = '0-0-0'
                    else:
                        per = '0-0'
                else:
                    per = s + chr(coords[0] + 97) + str(8 - coords[1]) + sep + chr(new_x + 97) + str(8 - new_y) + end
                turns[ko] = per
            else:
                if path == '3':
                    if new_x == 2:
                        per_2 = '0-0-0'
                    else:
                        per_2 = '0-0'
                else:
                    per_2 = s + chr(coords[0] + 97) + str(8 - coords[1]) + sep + chr(new_x + 97) + str(8 - new_y) + end
                turns[ko] = per + ' ' + per_2
                ko += 1
            Figure.turn = "Black" if Figure.turn == "White" else "White"
            
            # Пауза перед переворотом доски в режиме на двоих
            if two_players:
                pg.time.wait(300)  # Пауза 300 мс перед переворотом
                board_flipped = not board_flipped
                update(figures, background, image, counter)
                pg.display.update()
            
            # Проверяем на мат после хода
            if Figure.checkmate():
                game_over = True
                winner_color = "Black" if Figure.turn == "White" else "White"
                turns[counter//2+1] = turns.get(counter//2+1, '') + '#'
                play_sound(checkmate_sound)  # Звук мата
                stop_background_music()  # Останавливаем музыку при мате
        else:
            pass

    def promotion(self):  # замена пешки на другую фигуру
        print("Доступные фигуры: ", end="")
        for cls in Figure.__subclasses__():  # получает все подклассы в виде: <class '__main__.Pawn'>
            if not (str(cls)[17:-2] in ["Pawn", "King"]):
                print(str(cls)[17:-2], end=" ")
        flag = True
        while flag:
            new_class = input("\nВыберите фигуру >> ")
            for cls in Figure.__subclasses__():  # получает все подклассы в виде: <class '__main__.Pawn'>
                if str(cls)[17:-2] == new_class:
                    x, y, color = self.x, self.y, self.color
                    flag = False
                    break
        self.kill()
        figures[0].append("fig")
        figures[0][-1] = cls(new_class, x, y, color)
        figures[0][-1].draw()
        update(figures, background, image, counter)
        pg.display.update()

    @classmethod
    def print_screen(cls):
        for _ in range(8):
            print("  ".join(cls.screen[_]))
        print()

    @staticmethod
    def check_for_figure(coord):
        x, y = coord[0], coord[1]
        for _ in Figure.figures:
            if (x, y) == (_.x, _.y):
                return _
        return False

    @staticmethod
    def print(screen):
        for _ in range(8):
            print("  ".join(screen[_]))
        print()

    def kill(self):
        global stat
        self.status = "Killed"
        self.x, self.y = 8, 8

    @staticmethod
    def play():
        global coords, game_over, winner_color, board_flipped, two_players, clock
        # Получаем координаты клика с учетом переворота доски
        mouse_x, mouse_y = pg.mouse.get_pos()
        click_x = (mouse_x - 120) // 70
        click_y = (mouse_y - 70) // 70
        
        # Если доска перевернута, преобразуем координаты обратно
        if board_flipped:
            click_x = 7 - click_x
            click_y = 7 - click_y
        
        figure = Figure.check_for_figure((click_x, click_y))
        if figure:
            coords = (click_x, click_y)
            if figure.color == Figure.turn:
                paths = figure.paths
                if sum(sum(j == "0" for j in i) for i in paths) == 63:
                    return
                highlight = pg.image.load("lib/highlight.png")
                # Отрисовка подсветки с учетом переворота
                if board_flipped:
                    hl_x = 7 - coords[0]
                    hl_y = 7 - coords[1]
                else:
                    hl_x = coords[0]
                    hl_y = coords[1]
                sc.blit(highlight, (hl_x * 70 + 120, hl_y * 70 + 70))
                pg.display.update()
                b_circle = pg.image.load('lib/blue.png')
                r_circle = pg.image.load('lib/red.png')
                castling_circle = pg.image.load('lib/castling.png')
                in_passing = pg.image.load('lib/in_passing.png')
                for i in range(8):
                    for j in range(8):
                        if paths[i][j] == '1':
                            if board_flipped:
                                sc.blit(b_circle, ((7-j) * 70 + 120, (7-i) * 70 + 70))
                            else:
                                sc.blit(b_circle, (j * 70 + 120, i * 70 + 70))
                        elif paths[i][j] == '2':
                            if board_flipped:
                                sc.blit(r_circle, ((7-j) * 70 + 120, (7-i) * 70 + 70))
                            else:
                                sc.blit(r_circle, (j * 70 + 120, i * 70 + 70))
                        elif paths[i][j] == '3':
                            if board_flipped:
                                sc.blit(castling_circle, ((7-j) * 70 + 120, (7-i) * 70 + 70))
                            else:
                                sc.blit(castling_circle, (j * 70 + 120, i * 70 + 70))
                        elif paths[i][j] == '4':
                            if board_flipped:
                                sc.blit(in_passing, ((7-j) * 70 + 120, (7-i) * 70 + 70))
                            else:
                                sc.blit(in_passing, (j * 70 + 120, i * 70 + 70))
                pg.display.update()
                k = 0
                while k != 1:
                    for i in pg.event.get():
                        if i.type == pg.MOUSEBUTTONDOWN:
                            # При клике для хода тоже учитываем переворот
                            mouse_x2, mouse_y2 = pg.mouse.get_pos()
                            move_x = (mouse_x2 - 120) // 70
                            move_y = (mouse_y2 - 70) // 70
                            if board_flipped:
                                move_x = 7 - move_x
                                move_y = 7 - move_y
                            figure.move((move_x, move_y))
                            k += 1
                            update(figures, background, image, counter)
                            pg.display.update()
            else:
                pass
        else:
            pass
        d_circle = pg.image.load('lib/danger_filled.png')
        d_circle = pg.transform.scale(d_circle, (35, 35))
        check = pg.image.load('lib/check_filled.png')
        check = pg.transform.scale(check, (35, 35))
        if figure:
            K = figure.enemy_king
            king_check = K.strike_check()[0]
            if Figure.checkmate():
                game_over = True
                winner_color = "Black" if Figure.turn == "White" else "White"
                ch = f"Checkmate, {winner_color} wins!"
                checkmate_str = norm_font.render(ch, True, (255, 255, 255))
                turns[counter//2+1] = turns.get(counter//2+1, '') + '#'
                global back
                back = back.convert_alpha()
                back.fill((0, 0, 0, 150))
                sc.blit(back, (0, 0))
                sc.blit(checkmate_str, (30, 320))
                pg.display.update()
            elif king_check:
                # Отрисовка знака шаха с учетом переворота
                if board_flipped:
                    sc.blit(check, ((7-K.x) * 70 + 120, (7-K.y) * 70 + 105))
                else:
                    sc.blit(check, (K.x * 70 + 120, K.y * 70 + 105))
            else:
                for enemy in Figure.figures:
                    if enemy.status == 'Alive':
                        if enemy.color != Figure.turn:
                            for y in range(8):
                                for x in range(8):
                                    if enemy.possible_paths[y][x] == '2':
                                        if (x, y) != (K.x, K.y):
                                            if board_flipped:
                                                sc.blit(d_circle, ((7-x) * 70 + 120, (7-y) * 70 + 105))
                                            else:
                                                sc.blit(d_circle, (x * 70 + 120, y * 70 + 105))
                                        pg.display.update()

    @staticmethod
    def checkmate():
        for figure in Figure.figures:
            if (figure.color, figure.status) == (Figure.turn, "Alive"):
                for row in figure.paths:
                    if "1" in row or "2" in row:
                        return False
        return True

    @staticmethod
    def combine_paths(path1, path2):
        new_path = [["0"] * 8 for _ in range(8)]
        for i in range(8):
            for j in range(8):
                if path1[i][j] != "0":
                    new_path[i][j] = path1[i][j]
                if path2[i][j] != "0":
                    new_path[i][j] = path2[i][j]
        return new_path

    def strike_check(self):
        threatening_figures = []
        for figure in Figure.figures:
            if figure.status == "Alive":
                if figure.color != self.color:
                    if figure.possible_paths[self.y][self.x] == "2":
                        threatening_figures.append(figure)
        if threatening_figures:
            return True, threatening_figures
        else:
            return False, []

    def check(self, x, y):
        temp_x, temp_y = self.x, self.y
        self.x, self.y = x, y
        K = self.king
        if K.strike_check()[0]:
            self.x, self.y = temp_x, temp_y
            return '0'
        else:
            self.x, self.y = temp_x, temp_y
            return '1'

    def kill_check(self, x, y):
        to_kill = Figure.check_for_figure((x, y))
        if to_kill.name == 'King':
            return '0'
        t_x, t_y = to_kill.x, to_kill.y
        to_kill.kill()
        check = self.check(x, y)
        to_kill.status, to_kill.x, to_kill.y = "Alive", t_x, t_y
        if check == '1':
            return '2'
        else:
            return '0'

    def passing_check(self, x, y):
        enemy_x, enemy_y = x, self.y
        to_kill = Figure.check_for_figure((enemy_x, enemy_y))
        if to_kill.name == 'King':
            return '0'
        to_kill.kill()
        check = self.check(x, y)
        to_kill.status, to_kill.x, to_kill.y = "Alive", enemy_x, enemy_y
        if check == '1':
            return '4'
        else:
            return '0'

    @property  # возвращает все возможные пути фигуры
    def possible_paths(self):
        return [['1'] * 8 for _ in range(8)]

    @property  # возвращает короля цвета фигуры self
    def king(self):
        for K in Figure.kings:
            if K.color == self.color:
                return K

    @property  # возвращает короля противоположного цвета
    def enemy_king(self):
        for K in Figure.kings:
            if K.color != self.color:
                return K

    @property  # возвращает все возможные пути с учётом шаха королю
    def paths(self):
        paths = list(self.possible_paths)
        for y in range(8):
            for x in range(8):
                if paths[y][x] == '1':
                    paths[y][x] = self.check(x, y)
                elif paths[y][x] == '2':
                    paths[y][x] = self.kill_check(x, y)
                elif paths[y][x] == '3':
                    paths[y][x] = '3' if self.check(x, y) else '0'
                elif paths[y][x] == '4':
                    paths[y][x] = '4' if self.passing_check(x, y) else '0'
                else:
                    pass
        if self.name == "King":
            check = self.strike_check()[0]
            for y in [0, 7]:
                for x in [2, 6]:
                    if paths[y][x] == '3':
                        if check:
                            paths[y][x] = '0'
                        elif paths[y][(4 + x) // 2] == "0":
                            paths[y][x] = '0'
        return paths


class Pawn(Figure):  # пешка
    def __init__(self, name, x, y, color):
        super().__init__(name, x, y, color)
        self.icon = 'pp' if self.color == "White" else "po"
        self.step = 0

    @property
    def possible_paths(self):
        paths = [['0'] * 8 for _ in range(8)]
        paths[self.y][self.x] = "P"
        direction = 1 if self.color == "White" else -1
        for i in range(2 - self.is_moved):
            t_y = self.y - (1 + i) * direction
            t_x = self.x
            if t_y < 0 or t_y > 7 or t_x < 0 or t_x > 7:
                return paths
            if_figure = Figure.check_for_figure((t_x, t_y))
            if if_figure:
                break
            else:
                paths[t_y][t_x] = '1'
        for t_x in [self.x - 1, self.x + 1]:
            t_y = self.y - 1 * direction
            if_figure = Figure.check_for_figure((t_x, t_y))
            if if_figure:
                if if_figure.color != self.color:
                    paths[t_y][t_x] = '2'
        if (self.y, self.color) == (3, "White") or (self.y, self.color) == (4, "Black"):
            for t_x in [self.x - 1, self.x + 1]:
                try:
                    figure = Figure.check_for_figure((t_x, self.y))
                    if type(figure) == Pawn:
                        if figure.color != self.color and figure.step == 1:
                            paths[self.y - 1 * direction][t_x] = "4"
                except IndexError:
                    pass
        return paths


class Rook(Figure):  # ладья
    def __init__(self, name, x, y, color):
        super().__init__(name, x, y, color)
        self.icon = "rr" if self.color == "White" else "rt"
        if self.name != "Non-existent":
            Figure.rooks.append(self)

    @property
    def possible_paths(self):
        paths = [['0'] * 8 for _ in range(8)]
        paths[self.y][self.x] = "R"
        directions = [1, -1]
        for x_dir in directions:
            for x in range(self.x + x_dir, 8 if x_dir == 1 else -1, x_dir):
                figure = Figure.check_for_figure((x, self.y))
                if figure:
                    paths[self.y][x] = "0" if figure.color == self.color else "2"
                    break
                paths[self.y][x] = "1"
        for y_dir in directions:
            for y in range(self.y + y_dir, 8 if y_dir == 1 else -1, y_dir):
                figure = Figure.check_for_figure((self.x, y))
                if figure:
                    paths[y][self.x] = "0" if figure.color == self.color else "2"
                    break
                paths[y][self.x] = "1"
        return paths


class Knight(Figure):  # конь
    def __init__(self, name, x, y, color):
        super().__init__(name, x, y, color)
        self.icon = "nn" if self.color == "White" else "nm"

    @property
    def possible_paths(self):
        paths = [['0'] * 8 for _ in range(8)]
        paths[self.y][self.x] = "N"
        directions = [(1, -2), (1, 2), (-1, -2), (-1, 2), (2, -1), (2, 1), (-2, -1), (-2, 1)]
        for x, y in directions:
            x, y = self.x + x, self.y + y
            if x > 7 or y > 7 or x < 0 or y < 0:
                continue
            figure = Figure.check_for_figure((x, y))
            if figure:
                paths[y][x] = "2" if figure.color != self.color else "0"
            else:
                paths[y][x] = "1"
        return paths


class Bishop(Figure):  # слон
    def __init__(self, name, x, y, color):
        super().__init__(name, x, y, color)
        self.icon = "bb" if self.color == "White" else "bv"

    @property
    def possible_paths(self):
        paths = [['0'] * 8 for _ in range(8)]
        paths[self.y][self.x] = "B"
        directions = [(1, -1), (1, 1), (-1, 1), (-1, -1)]
        for dx, dy in directions:
            x, y = self.x + dx, self.y + dy
            while 0 <= x <= 7 and 0 <= y <= 7:
                figure = Figure.check_for_figure((x, y))
                if figure:
                    paths[y][x] = "2" if figure.color != self.color else "0"
                    break
                else:
                    paths[y][x] = "1"
                    x += dx
                    y += dy
        return paths


class Queen(Figure):  # королева / ферзь
    def __init__(self, name, x, y, color):
        super().__init__(name, x, y, color)
        self.icon = "qq" if self.color == "White" else "qw"

    @property
    def possible_paths(self):
        paths1 = Bishop("Non-existent", self.x, self.y, self.color).possible_paths
        paths2 = Rook("Non-existent", self.x, self.y, self.color).possible_paths
        paths = Figure.combine_paths(paths1, paths2)
        paths[self.y][self.x] = "Q"
        return paths


class King(Figure):  # король
    def __init__(self, name, x, y, color):
        super().__init__(name, x, y, color)
        self.icon = "kk" if self.color == "White" else "kl"
        if self.name != "Non-existent":
            Figure.kings.append(self)

    @property
    def possible_paths(self):
        paths = [['0'] * 8 for _ in range(8)]
        paths[self.y][self.x] = "K"
        directions = [(1, -1), (1, 1), (-1, 1), (-1, -1), (-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            x, y = self.x + dx, self.y + dy
            if 0 <= x <= 7 and 0 <= y <= 7:
                figure = Figure.check_for_figure((x, y))
                if figure:
                    paths[y][x] = "2" if figure.color != self.color else "0"
                else:
                    paths[y][x] = "1"
        # Castling / рокировка
        if not self.is_moved:
            for rook in Figure.rooks:
                if (not rook.is_moved) and (rook.color == self.color):
                    if (rook.x, rook.y) == (0, self.y):
                        k = 0
                        for x in range(self.x - 1, 0, -1):
                            if Figure.check_for_figure((x, self.y)):
                                k += 1
                        if k == 0:
                            paths[self.y][2] = '3'
                    elif (rook.x, rook.y) == (7, self.y):
                        k = 0
                        for x in range(self.x + 1, 7, 1):
                            if Figure.check_for_figure((x, self.y)):
                                k += 1
                        if k == 0:
                            paths[self.y][6] = '3'
        return paths


def update(figures, background, image, counter):
    text_counter = norm_font.render(str(counter), True, (200, 200, 200))
    sc.blit(background, (0, 0))
    sc.blit(image, (85, 35))
    # sc.blit(text_counter, (720, 50))
    for i in figures:
        for j in i:
            if j != "0":
                if j.status == "Alive":
                    j.draw()


def get_player_name(winner_color):
    """Получает имя победителя"""
    input_box = pg.Rect(200, 350, 400, 60)
    color_inactive = pg.Color('lightskyblue3')
    color_active = pg.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    done = False
    
    title_font = pg.font.Font('./lib/arial.ttf', 48)
    input_font = pg.font.Font('./lib/arial.ttf', 36)
    small_font = pg.font.Font('./lib/arial.ttf', 24)
    
    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pg.KEYDOWN:
                if active:
                    if event.key == pg.K_RETURN:
                        if text.strip():
                            done = True
                    elif event.key == pg.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        if len(text) < 30:
                            text += event.unicode
        
        # Отрисовка
        overlay = pg.Surface((800, 700))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(220)
        sc.blit(overlay, (0, 0))
        
        # Заголовок
        title = title_font.render("ИГРА ЗАКОНЧЕНА!", True, (255, 215, 0))
        title_rect = title.get_rect(center=(400, 100))
        sc.blit(title, title_rect)
        
        # Победитель
        winner_text = title_font.render(f"Победили {winner_color}!", True, (255, 255, 255))
        winner_rect = winner_text.get_rect(center=(400, 180))
        sc.blit(winner_text, winner_rect)
        
        # Подсказка
        prompt = input_font.render("Введите имя и фамилию победителя:", True, (200, 200, 200))
        prompt_rect = prompt.get_rect(center=(400, 280))
        sc.blit(prompt, prompt_rect)
        
        # Поле ввода
        txt_surface = input_font.render(text, True, color)
        width = max(400, txt_surface.get_width()+10)
        input_box.w = width
        input_box.centerx = 400
        sc.blit(txt_surface, (input_box.x+10, input_box.y+10))
        pg.draw.rect(sc, color, input_box, 3)
        
        # Инструкция
        inst_text = small_font.render("Нажмите Enter для подтверждения", True, (150, 150, 150))
        inst_rect = inst_text.get_rect(center=(400, 480))
        sc.blit(inst_text, inst_rect)
        
        pg.display.flip()
    
    return text


def show_menu():
    """Показывает главное меню"""
    menu_surface = pg.Surface((800, 700))
    menu_surface.fill((50, 50, 50))
    
    title_font = pg.font.Font('./lib/arial.ttf', 72)
    button_font = pg.font.Font('./lib/arial.ttf', 48)
    
    title = title_font.render("ШАХМАТЫ", True, (255, 215, 0))
    menu_surface.blit(title, (250, 50))
    
    buttons = [
        ("Игра с самим собой", (250, 180)),
        ("Игра на двоих", (250, 270)),
        ("Таблица рекордов", (250, 360)),
        ("Справка", (250, 450)),
        ("Выход", (250, 540))
    ]
    
    button_rects = []
    for text, pos in buttons:
        button_surf = button_font.render(text, True, (255, 255, 255))
        button_rect = button_surf.get_rect(topleft=pos)
        button_rects.append((button_rect, text))
        
        # Рисуем рамку вокруг кнопки
        pg.draw.rect(menu_surface, (100, 100, 100), button_rect.inflate(20, 10), 2)
        menu_surface.blit(button_surf, pos)
    
    sc.blit(menu_surface, (0, 0))
    pg.display.update()
    
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos = pg.mouse.get_pos()
                for rect, text in button_rects:
                    if rect.collidepoint(mouse_pos):
                        if text == "Игра с самим собой":
                            return "play_solo"
                        elif text == "Игра на двоих":
                            return "play_duo"
                        elif text == "Таблица рекордов":
                            return "records"
                        elif text == "Справка":
                            return "rules"
                        elif text == "Выход":
                            pg.quit()
                            sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    sys.exit()


def show_rules():
    """Показывает справку с правилами игры"""
    rules_surface = pg.Surface((800, 700))
    rules_surface.fill((50, 50, 50))
    
    title_font = pg.font.Font('./lib/arial.ttf', 48)
    text_font = pg.font.Font('./lib/arial.ttf', 24)
    
    title = title_font.render("Правила игры в шахматы", True, (255, 255, 255))
    rules_surface.blit(title, (200, 30))
    
    rules_text = [
        "• Цель игры - поставить мат королю противника",
        "• Фигуры ходят по очереди, белые начинают первыми",
        "• Пешка ходит вперёд на 1 клетку, бьёт по диагонали",
        "• Ладья ходит по вертикали и горизонтали",
        "• Конь ходит буквой 'Г'",
        "• Слон ходит по диагоналям",
        "• Ферзь объединяет ходы ладьи и слона",
        "• Король ходит на 1 клетку в любую сторону",
        "• Рокировка - специальный ход короля и ладьи",
        "• Взятие на проходе - особый ход пешки",
        "• Пешка может превратиться в любую фигуру",
        "",
        "Условные обозначения:",
        "Синий кружок - возможный ход",
        "Красный кружок - взятие фигуры",
        "Желтый кружок - рокировка",
        "Зеленый кружок - взятие на проходе",
        "Знак восклицания - король под шахом",
        "",
        "Нажмите ESC для возврата в меню"
    ]
    
    y_pos = 100
    for line in rules_text:
        text = text_font.render(line, True, (200, 200, 200))
        rules_surface.blit(text, (50, y_pos))
        y_pos += 35
    
    sc.blit(rules_surface, (0, 0))
    pg.display.update()
    
    waiting = True
    while waiting:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    waiting = False
            if event.type == pg.MOUSEBUTTONDOWN:
                waiting = False


def show_records():
    """Показывает таблицу рекордов"""
    records_surface = pg.Surface((800, 700))
    records_surface.fill((50, 50, 50))
    
    title_font = pg.font.Font('./lib/arial.ttf', 48)
    text_font = pg.font.Font('./lib/arial.ttf', 30)
    small_font = pg.font.Font('./lib/arial.ttf', 24)
    
    title = title_font.render("ТАБЛИЦА РЕКОРДОВ", True, (255, 215, 0))
    records_surface.blit(title, (200, 30))
    
    # Загружаем рекорды из файла
    if os.path.exists('records.json'):
        with open('records.json', 'r') as f:
            records_data = json.load(f)
    else:
        records_data = {}
    
    if records_data:
        # Сортируем игроков по количеству побед
        sorted_players = sorted(records_data.items(), key=lambda x: x[1]['wins'], reverse=True)
        
        y_pos = 120
        # Заголовки колонок
        header_name = small_font.render("Игрок", True, (255, 215, 0))
        records_surface.blit(header_name, (50, y_pos))
        header_wins = small_font.render("Победы", True, (255, 215, 0))
        records_surface.blit(header_wins, (500, y_pos))
        header_games = small_font.render("Игр", True, (255, 215, 0))
        records_surface.blit(header_games, (620, y_pos))
        y_pos += 50
        
        for i, (player, data) in enumerate(sorted_players[:15]):
            if y_pos > 620:
                break
            
            # Подсвечиваем топ-3
            if i < 3:
                color = (255, 215, 0)  # Золотой для топ-3
                medal = ["🥇", "🥈", "🥉"][i]
                player_display = f"{medal} {player}"
            else:
                color = (200, 200, 200)
                player_display = f"{i+1}. {player}"
            
            player_text = text_font.render(player_display, True, color)
            records_surface.blit(player_text, (50, y_pos))
            
            wins_text = text_font.render(str(data['wins']), True, color)
            records_surface.blit(wins_text, (530, y_pos))
            
            games_text = text_font.render(str(data.get('games', data['wins'])), True, color)
            records_surface.blit(games_text, (640, y_pos))
            
            y_pos += 45
    else:
        no_records = text_font.render("Рекордов пока нет", True, (200, 200, 200))
        records_surface.blit(no_records, (250, 300))
        hint = small_font.render("Сыграйте игру, чтобы добавить рекорд!", True, (150, 150, 150))
        records_surface.blit(hint, (220, 370))
    
    back_text = small_font.render("Нажмите ESC или кликните для возврата в меню", True, (150, 150, 150))
    records_surface.blit(back_text, (180, 660))
    
    sc.blit(records_surface, (0, 0))
    pg.display.update()
    
    waiting = True
    while waiting:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    waiting = False
            if event.type == pg.MOUSEBUTTONDOWN:
                waiting = False


def save_game_result(winner_color, player_name, moves_count):
    """Сохраняет результат игры в рекорды"""
    records_data = {}
    if os.path.exists('records.json'):
        with open('records.json', 'r') as f:
            records_data = json.load(f)
    
    # Ищем игрока по имени (без учета регистра)
    player_key = None
    for key in records_data.keys():
        if key.lower() == player_name.lower():
            player_key = key
            break
    
    if player_key is None:
        player_key = player_name
        records_data[player_key] = {
            'wins': 0,
            'games': 0,
            'total_moves': 0,
            'wins_as_white': 0,
            'wins_as_black': 0
        }
    
    records_data[player_key]['wins'] += 1
    records_data[player_key]['games'] = records_data[player_key].get('games', 0) + 1
    records_data[player_key]['total_moves'] = records_data[player_key].get('total_moves', 0) + moves_count
    
    if winner_color == "White":
        records_data[player_key]['wins_as_white'] = records_data[player_key].get('wins_as_white', 0) + 1
    else:
        records_data[player_key]['wins_as_black'] = records_data[player_key].get('wins_as_black', 0) + 1
    
    with open('records.json', 'w') as f:
        json.dump(records_data, f, indent=2, ensure_ascii=False)
    
    return player_key


if __name__ == "__main__":
    pg.font.init()
    turns = {}

    pg.display.set_caption("CHESS")
    clock = pg.time.Clock()

    background = pg.image.load('lib/wood.jpg')

    font = pg.font.Font('./lib/CASEFONT.TTF', 72)
    norm_font = pg.font.Font('./lib/arial.ttf', 68)
    sc = pg.display.set_mode((800, 700))

    instruction = pg.image.load('lib/instruction.PNG')
    back = pg.Surface((800, 700))
    back.fill((255, 255, 255))
    button = pg.image.load('lib/butt.jfif')
    button = pg.transform.scale(button, (100, 100))
    
    # Запускаем фоновую музыку при старте игры
    play_background_music()
    
    # Главный цикл меню
    while True:
        action = show_menu()
        
        if action == "rules":
            show_rules()
        elif action == "records":
            show_records()
        elif action in ["play_solo", "play_duo"]:
            # Определяем режим игры
            two_players = (action == "play_duo")
            
            # Воспроизводим звук начала игры
            play_sound(game_start_sound)
            
            # Начинаем игру
            Figure.figures = []
            Figure.kings = []
            Figure.rooks = []
            Figure.turn = "White"
            turns = {}
            counter = 0
            ko = 1
            game_over = False
            winner_color = None
            board_flipped = False  # В начале игры белые снизу
            
            # Показываем экран инструкции
            sc.blit(back, (0, 0))
            sc.blit(instruction, (132, 141))
            sc.blit(button, (650, 550))
            pg.display.update()
            q = True
            while q:
                for i in pg.event.get():
                    if i.type == pg.QUIT:
                        pg.quit()
                        sys.exit()
                    if i.type == pg.MOUSEBUTTONDOWN:
                        q = 0

            sc.blit(background, (0, 0))
            image = pg.image.load('lib/main.jpg')
            image = pg.transform.scale(image, (630, 630))
            sc.blit(image, (85, 35))
            pg.display.update()
            c = 0

            stat = {
                'Pawn': 0,
                'Knight': 0,
                'Bishop': 0,
                'Rook': 0,
                'Queen': 0,
                'King': 0
            }
            
            # Игровой цикл
            while not game_over:
                for i in pg.event.get():
                    if c == 0:
                        figures = [["0"] * 8 for _ in range(8)]
                        for x_ in range(8):
                            figures[1][x_] = Pawn("Pawn", x_, 1, "Black")
                            figures[1][x_].draw()
                            figures[6][x_] = Pawn("Pawn", x_, 6, "White")
                            figures[6][x_].draw()
                        for x_ in [0, 7]:
                            figures[0][x_] = Rook("Rook", x_, 0, "Black")
                            figures[0][x_].draw()
                            figures[7][x_] = Rook("Rook", x_, 7, "White")
                            figures[7][x_].draw()
                        for x_ in [1, 6]:
                            figures[0][x_] = Knight("Knight", x_, 0, "Black")
                            figures[0][x_].draw()
                            figures[7][x_] = Knight("Knight", x_, 7, "White")
                            figures[7][x_].draw()
                        for x_ in [2, 5]:
                            figures[0][x_] = Bishop("Bishop", x_, 0, "Black")
                            figures[0][x_].draw()
                            figures[7][x_] = Bishop("Bishop", x_, 7, "White")
                            figures[7][x_].draw()
                        figures[0][3] = Queen("Queen", 3, 0, "Black")
                        figures[0][3].draw()
                        figures[7][3] = Queen("Queen", 3, 7, "White")
                        figures[7][3].draw()
                        figures[0][4] = King("King", 4, 0, "Black")
                        figures[0][4].draw()
                        figures[7][4] = King("King", 4, 7, "White")
                        figures[7][4].draw()
                        c += 1
                        update(figures, background, image, counter)
                        pg.display.update()
                    if i.type == pg.QUIT:
                        pg.quit()
                        sys.exit()
                    if i.type == pg.KEYDOWN:
                        if i.key == pg.K_ESCAPE:
                            game_over = True
                    if i.type == pg.MOUSEBUTTONDOWN and not game_over:
                        if 120 < pg.mouse.get_pos()[0] < 680 and 70 < pg.mouse.get_pos()[1] < 630:
                            new_x, new_y = (pg.mouse.get_pos()[0] - 120) // 70, (pg.mouse.get_pos()[1] - 70) // 70
                            Figure.play()
                
                # Показываем знак шаха, если король под шахом
                if not game_over:
                    for king in Figure.kings:
                        if king.status == "Alive" and king.strike_check()[0]:
                            check_img = pg.image.load('lib/check_filled.png')
                            check_img = pg.transform.scale(check_img, (35, 35))
                            if board_flipped:
                                sc.blit(check_img, ((7-king.x) * 70 + 120, (7-king.y) * 70 + 105))
                            else:
                                sc.blit(check_img, (king.x * 70 + 120, king.y * 70 + 105))
                            pg.display.update()
                
                clock.tick(10)
            
            # Сохраняем запись игры
            with open('notation.txt', mode='w') as file:
                for item in turns.items():
                    file.write(str(item[0]) + ' ' + item[1] + '\n')
            
            # Если игра закончилась матом (а не выходом по ESC)
            if winner_color:
                # Получаем имя победителя
                player_name = get_player_name(winner_color)
                
                # Сохраняем результат
                save_game_result(winner_color, player_name, counter // 2)
            
            # Перезапускаем фоновую музыку после игры
            play_background_music()
