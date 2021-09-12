from random import randint


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "You're trying to shoot out of board"


class BoardUsedException(BoardException):
    def __str__(self):
        return "You've already shot at this point"


class BoardWrongShipException(BoardException):
    pass


class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shot(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid
        self.count = 0

        self.field = [["O"] * size for _ in range(size)]

        self.busy = []
        self.ships = []

        self.str_board_repr = [f"{i} " for i in range(1, self.size + 1)]
        self.str_board_repr = "    " + "| ".join(self.str_board_repr) + "|"
        for i, row in enumerate(self.field):
            self.str_board_repr += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            self.str_board_repr = self.str_board_repr.replace("■", "O")

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    @property
    def get_str_repr(self):
        self.str_board_repr = [f"{i} " for i in range(1, self.size + 1)]
        self.str_board_repr = "    " + "| ".join(self.str_board_repr) + "|"
        for i, row in enumerate(self.field):
            self.str_board_repr += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            self.str_board_repr = self.str_board_repr.replace("■", "O")
        return self.str_board_repr.split("\n")

    @property
    def busy_points(self):
        return self.busy

    def __str__(self):
        return self.str_board_repr

    def print_both_board(self, other):
        for i in zip(self.get_str_repr, other.get_str_repr):
            print("\t\t".join(i))

    def out(self, d):
        return not (0 <= d.x < self.size and 0 <= d.y < self.size)

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if ship.shot(d):
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Ship destroyed!")
                    return False
                else:
                    print("Ship hit!")
                    return True

        self.field[d.x][d.y] = "."
        print("Miss!")
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Computer turn: {d.x + 1} {d.y + 1}")
        return d

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class User(Player):
    def ask(self):
        while True:
            cords = input("Your turn: ").split()

            if len(cords) != 2:
                print(" Enter 2 coordinates! ")
                continue

            x, y = cords

            if not (x.isdigit() and y.isdigit()):
                print(" Enter numbers! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        player = self.random_board()
        computer = self.random_board()
        computer.hid = True

        self.ai = AI(computer, player)
        self.us = User(player, computer)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                bow = Dot(randint(0, self.size), randint(0, self.size))
                if bow in board.busy_points:
                    continue
                ship = Ship(bow, l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    @staticmethod
    def greet():
        print("-------------------")
        print("  Welcome to the  ")
        print("  Sea Battle game  ")
        print("-------------------")
        print(" input format: x y ")
        print("  x - row number  ")
        print("  y - col number ")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print(f"User board:\t\t\t\t\t\tComputer board:")
            self.us.board.print_both_board(self.ai.board)
            if num % 2 == 0:
                print("-" * 20)
                print("User turn")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Computer turn")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("User wins!")
                break

            if self.us.board.count == 7:
                print("-" * 20)
                print("Computer wins!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
