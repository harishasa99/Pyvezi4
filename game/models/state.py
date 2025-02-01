from .config import M, N, WIN_CNT


class State:
    @staticmethod
    def get_all_win_states():
        win_indexes = []

        # Column wins
        indexes = filter(lambda sub_l: len(set(s // M for s in sub_l if s < M * N)) == 1,
                         [[i + j for j in range(WIN_CNT)]
                          for i in range(M * N - WIN_CNT + 1)])
        win_indexes.extend(indexes)

        # Row wins
        indexes = filter(lambda sub_l: len(sub_l) == len([s for s in sub_l if s < M * N]),
                         [[j * M + i for j in range(WIN_CNT)]
                          for i in range(M * N - WIN_CNT + 1)])
        win_indexes.extend(indexes)

        # Main diagonal wins
        indexes = filter(lambda sub_l: (length := len(sub_l)) == len(
            ind := set(s // M for s in sub_l if s < M * N)) and length == len(
            range(min(ind), max(ind) + 1)),
                         [[j * (M - 1) + i for j in range(WIN_CNT)]
                          for i in range(M * N - WIN_CNT + 1)])
        win_indexes.extend(indexes)

        # Anti-diagonal wins
        indexes = filter(lambda sub_l: (length := len(sub_l)) == len(
            ind := set(s // M for s in sub_l if s < M * N)) and length == len(
            range(min(ind), max(ind) + 1)),
                         [[j * (M + 1) + i for j in range(WIN_CNT)]
                          for i in range(M * N - WIN_CNT + 1)])
        win_indexes.extend(indexes)

        win_masks_set = set()
        for sub_list in win_indexes:
            win_mask = 0
            for sub in sub_list:
                win_mask |= 1 << sub
            win_masks_set.add(win_mask)
        return win_masks_set

    DRAW_MASK = (1 << (M * N)) - 1
    win_masks = get_all_win_states()
    RED = 0
    YEL = 1
    DRAW = 2

    def __init__(self):
        self.checkers_red = 0 & State.DRAW_MASK
        self.checkers_yellow = 0 & State.DRAW_MASK
        self.next_on_move = State.RED

    def __str__(self):
        return '\n'.join([' '.join(['X' if ((mask := 1 << (i + j * M)) & self.checkers_red) == mask else
                                    'O' if (mask & self.checkers_yellow) == mask else '_' for j in range(N)])
                          for i in range(M - 1, -1, -1)])

    def get_checkers(self, ident):
        if ident == State.RED:
            return self.checkers_red
        elif ident == State.YEL:
            return self.checkers_yellow
        else:
            return None

    def get_int_state(self):
        return self.checkers_red | self.checkers_yellow

    def get_next_on_move(self):
        return self.next_on_move

    def get_state_status(self):
        if self.get_int_state() == State.DRAW_MASK:
            return State.DRAW
        for mask in self.win_masks:
            if (self.checkers_red & mask) == mask:
                return State.RED
            if (self.checkers_yellow & mask) == mask:
                return State.YEL
        return None

    def get_win_checkers_positions(self):
        positions = []
        if self.get_state_status() is not None:
            for mask in self.win_masks:
                if (self.checkers_red & mask) == mask or (self.checkers_yellow & mask) == mask:
                    while mask:
                        temp = mask & -mask
                        pos = temp.bit_length() - 1
                        positions.append((M - 1 - pos % M, pos // M))
                        mask ^= temp
                    break
        return positions

    def get_possible_columns(self):
        state_int = self.get_int_state()
        mask = 1 << (M - 1)
        possible_columns = []
        for col in range(N):
            if not (state_int & mask):
                possible_columns.append(col)
            mask <<= M
        return possible_columns

    def generate_successor_state(self, column):
        if self.get_state_status() is not None:
            raise Exception(f'State is finite!\n{self}')
        if column is None or column < 0 or column >= N:
            raise Exception(f'Column {column} out of bounds [0 - {N - 1}]!')
        copy_state = State()
        copy_state.checkers_red = self.checkers_red
        copy_state.checkers_yellow = self.checkers_yellow
        state_int = self.get_int_state()
        mask = 1 << (column * M)
        for _ in range(M):
            if not (state_int & mask):
                if self.next_on_move == State.RED:
                    copy_state.checkers_red |= mask
                else:
                    copy_state.checkers_yellow |= mask
                copy_state.next_on_move = State.YEL if self.next_on_move == State.RED else State.RED
                return copy_state
            mask <<= 1
        raise Exception(f'Column {column} is full!\n{self}')

    def get_column_height(self, column):
        if column is None or column < 0 or column >= N:
            raise Exception(f'Column {column} out of bounds [0 - {N - 1}]!')
        state = self.get_int_state()
        mask = 1 << (column * M)
        height = 0
        for _ in range(M):
            if state & mask:
                height += 1
            else:
                break
            mask <<= 1
        return height

    def to_dict(self):
        board = [[0 for _ in range(N)] for _ in range(M)]
        for i in range(M):
            for j in range(N):
                mask = 1 << (i + j * M)
                if (self.checkers_red & mask) == mask:
                    board[i][j] = 1  # Red checker
                elif (self.checkers_yellow & mask) == mask:
                    board[i][j] = 2  # Yellow checker
        return {
            "board": board,
            "next_on_move": self.next_on_move
        }

    @staticmethod
    def from_dict(data):
        state = State()
        board = data.get("board", [])
        for i in range(M):
            for j in range(N):
                if board[i][j] == 1:  # Red checker
                    mask = 1 << (i + j * M)
                    state.checkers_red |= mask
                elif board[i][j] == 2:  # Yellow checker
                    mask = 1 << (i + j * M)
                    state.checkers_yellow |= mask
        state.next_on_move = data.get("next_on_move", State.RED)
        return state
