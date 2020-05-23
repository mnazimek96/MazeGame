import numpy as np

class Board:
    def __init__(self, board):
        """
        Initializes the board with given list of tiles.
        """
        self.board = board
        # actor position is determined based on the position of tile 'B'
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if board[i][j] == 'B':
                    self.actor_pos = (i, j)
        # 'r' is the default passable state
        self.passable = 'r'


    def print_board(self):
        print('passable: ' + self.passable)
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if (i, j) == self.actor_pos:
                    print('@', end='')
                else:
                    print(self.board[i][j], end='')

            print()


    def tile_state(self, pos):
        return self.board[pos[0]][pos[1]]


    def is_tile_free(self, pos):
        """
        Determines whether the actor can enter tile at the given position
        in the current state.
        """
        if self.tile_state(pos) in [' ', 'B', 'E', 'S']:
            return True
        else:
            return self.tile_state(pos) == self.passable



    def is_move_possible(self, move):
        """
        Determine whether the given move is possible in the current state
        and at the current actor position. Returns True or False.
        Throws an error for a nonexisting move.
        """
        if move == 'move up':
            return self.is_tile_free((self.actor_pos[0]-1, self.actor_pos[1]))
        elif move == 'move down':
            return self.is_tile_free((self.actor_pos[0]+1, self.actor_pos[1]))
        elif move == 'move left':
            return self.is_tile_free((self.actor_pos[0], self.actor_pos[1]-1))
        elif move == 'move right':
            return self.is_tile_free((self.actor_pos[0], self.actor_pos[1]+1))
        elif move == 'switch':
            return self.tile_state(self.actor_pos) == 'S'
        elif move == 'finish':
            return self.tile_state(self.actor_pos) == 'E'
        else:
            raise Exception("Unknown move: " + str(move))


    all_moves = ['move up', 'move down', 'move left', 'move right', 'switch',
                 'finish']


    def reverse_move(self, move):
        """
        Determine the move that undoes the given move. All moves are reversible
        except the 'finish' move.
        """
        if move == 'move up':
            return 'move down'
        elif move == 'move down':
            return 'move up'
        elif move == 'move left':
            return 'move right'
        elif move == 'move right':
            return 'move left'
        elif move == 'switch':
            return 'switch'
        else:
            raise Exception('Move not reversible: ' + move)


    def possible_moves(self):
        """
        Calculate the list of moves an actor can perform in the current state.
        """
        return [m for m in Board.all_moves if self.is_move_possible(m)]


    def position_after_move(self, move):
        """
        Calculate the position of the actor after given move.
        """
        if move == 'move up':
            return (self.actor_pos[0]-1, self.actor_pos[1])
        elif move == 'move down':
            return (self.actor_pos[0]+1, self.actor_pos[1])
        elif move == 'move left':
            return (self.actor_pos[0], self.actor_pos[1]-1)
        elif move == 'move right':
            return (self.actor_pos[0], self.actor_pos[1]+1)
        elif move == 'switch':
            return self.actor_pos
        else:
            raise Exception('Not a move move: ' + move)


    def make_move(self, move):
        """
        Make changes in the state corresponding to the given move.
        Raises an exception when the given command does isn't equal
        to one of the valid moves moves.
        Raises an exception when the actor successfully performs the 'finish'
        move.
        Returns True if the move succeeded and False otherwise.
        """
        if not self.is_move_possible(move):
            return False

        if move[:4] == 'move':
            self.actor_pos = self.position_after_move(move)
        elif move == 'switch':
            if self.passable == 'r':
                self.passable = 'g'
            else:
                self.passable = 'r'
        elif move == 'finish':
            if self.tile_state(self.actor_pos) == 'E':
                raise Exception("You won!")
        else:
            raise Exception("Unknown move: " + str(move))

        return True

    # changes ---------------------------- DONE !!!!

    def player_position(self):
        return self.actor_pos

    def exit_position(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if self.board[i][j] == 'E':
                    return i, j
        raise Exception("No exit on board")

    def start_position(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if self.board[i][j] == 'B':
                    return i, j
        raise Exception("No begin on board")

    def around_player(self, position):
        return dict(left=self.board[position[0]][position[1] - 1], up=self.board[position[0] - 1][position[1]],
                    right=self.board[position[0]][position[1] + 1], down=self.board[position[0] + 1][position[1]])

    # -----------------------------------


class BacktrackingAgent:
    """
    An agent that explores the environment using backtracking.
    """
    def __init__(self, init_board):
        # if init_board != None:
        #     self.set_board(init_board)
        self.actor_position = init_board.player_position()
        self.begin_position = init_board.start_position()
        self.exit_position = init_board.exit_position()

    def set_board(self, init_board):
        """
        Initializes the agent with the given board. This board is an internal
        representation that is disjoint from the one maintained in the
        environment.
        Also stores a board-like list of lists ('visited') that stores
        in which states ('r' or 'g') was the given tile visited.
        Possible values are '' (empty string) when a tile was never visited,
        'r', 'rg' or 'gr' when it was visited in the 'r' state and
        'g', 'rg' or 'gr' when it was visited in the 'g' state.
        'state_stack' holds performed moves that will be undone while
        backtracking. The 'mode' variable determines whether the agent
        currently explores forward or backtracks.
        """
        # jezeli gdzis obok na planszy jest W albo B albo E to sie wyświetlni przy inicjowaniu planszy ---- DONE!!!
        r, c = np.asarray(init_board.board).shape
        empty_board = [['W' if i in [0, c - 1] or j in [0, r - 1] else ' ' for i in range(c)] for j in range(r)]
        empty_board[self.begin_position[0]][self.begin_position[1]] = 'B'
        empty_board[self.exit_position[0]][self.exit_position[1]] = 'E'
        # -----------

        self.board = Board(empty_board)
        self.visited = [['' for c in r] for r in init_board.board]
        self.state_stack = []
        self.mode = 'forward'

        # Pokazuje tylko to co jest w kazdym kierunku i wyswietla na planszy
        init_surroudings = init_board.around_player(self.actor_position)
        self.update_surroundings(init_surroudings)
        # -------------------------

    def reaches_new_state(self, move):
        """
        Determines whether the given move moves the actor to an unvisited state.
        """
        pam = self.board.position_after_move(move)
        vb = self.visited[pam[0]][pam[1]]
        return self.board.passable not in vb


    def move(self, env):
        """
        Determines the next move of the actor. Uses 'env' only to retrieve
        a list of currently possible moves.
        """
        possible_moves = env.possible_moves()
        print(str(self.state_stack))
        # we want to finish as soon as it's possible
        if 'finish' in possible_moves:
            return 'finish'
        elif self.mode == 'forward':
            # if finishing is not possible and we aren't backtracking, we should
            # try moving forward
            print('going forward')
            pmoves = [m for m in possible_moves if self.reaches_new_state(m)]
            print('pmoves: ' + str(pmoves))
            # if there are no possible moves that reach a new state, we will
            # backtrack
            if len(pmoves) == 0:
                self.mode = 'backtrack'
                taken_move = self.state_stack[-1]['taken move']
                return self.board.reverse_move(taken_move)

            # otherwise go forward and record taken move and other possible
            # moves on the state stack
            [taken_move, other_moves] = self.choose_move(pmoves)
            self.state_stack.append({'taken move': taken_move,
                                     'other moves': other_moves})

            return taken_move

        elif self.mode == 'backtrack':
            print('backtracking')
            print()
            # when backtracking and we have exhausted the entire state stack
            # then there is no path that leads to the end state
            if len(self.state_stack) == 0:
                raise Exception('Goal is not reachable :(')

            # if the stack is not empty, take its top element
            top = self.state_stack.pop()
            btr_possible_moves = top['other moves']
            # if there are no other possible moves at this level of backtracking
            # then backtrack further
            if len(btr_possible_moves) == 0:
                return self.board.reverse_move(self.state_stack[-1]['taken move'])
            else:
                # if there are other options go forward
                self.mode = 'forward'
                self.state_stack.append({'taken move': btr_possible_moves[0],
                                         'other moves': btr_possible_moves[1:]})

                return btr_possible_moves[0]

    # changes ----------------------------------

    def choose_move(self, possible_moves):
        distances = list()
        for move in possible_moves:
            distances.append(self.calculate_distance(self.get_potential_position(move), self.board.exit_position()))

        chosen_move_idx = distances.index(min(distances))
        chosen_move = possible_moves[chosen_move_idx]
        del[possible_moves[chosen_move_idx]]
        return chosen_move, possible_moves

    def get_potential_position(self, move):
        position_after_move = self.actor_position
        if move == 'move up':
            position_after_move = tuple((position_after_move[0]-1, position_after_move[1]))
        elif move == 'move down':
            position_after_move = tuple((position_after_move[0]+1, position_after_move[1]))
        elif move == 'move left':
            position_after_move = tuple((position_after_move[0], position_after_move[1]-1))
        elif move == 'move right':
            position_after_move = tuple((position_after_move[0], position_after_move[1]+1))
        elif move == 'switch':
            position_after_move = tuple((1000, 1000))
        return position_after_move

    def calculate_distance(self, first_position, second_position):
        return abs(first_position[0] - second_position[0]) + abs(first_position[1] - second_position[1])

    def update_position(self, actor_position):
        self.actor_position = actor_position

    def update_surroundings(self, surrounding):
        for key, value in surrounding.items():
            if key == 'left':
                self.update_blind_board([self.actor_position[0], self.actor_position[1] - 1], value)
            elif key == 'up':
                self.update_blind_board([self.actor_position[0] - 1, self.actor_position[1]], value)
            elif key == 'right':
                self.update_blind_board([self.actor_position[0], self.actor_position[1] + 1], value)
            elif key == 'down':
                self.update_blind_board([self.actor_position[0] + 1, self.actor_position[1]], value)

    def update_blind_board(self, coordinates, type):
        self.board.board[coordinates[0]][coordinates[1]] = type

    # --------------------------------

    def percept(self, data=None, board=None):
        """
        Informs the agent about changes in the environment.
        At this moment it only tells whether the agent actually moved
        and whether the switching was successful.
        """
        if data:
            if data['type'][:4] == 'move':
                pos = self.board.actor_pos
                if self.board.passable not in self.visited[pos[0]][pos[1]]:
                    self.visited[pos[0]][pos[1]] += self.board.passable
                self.board.make_move(data['type'])
            elif data['type'] == 'switch':
                self.board.make_move('switch')
        if board:
            surroudings = board.around_player(self.actor_position)
            self.update_surroundings(surroudings)


class Environment:
    def __init__(self, board, ai):
        self.board = board
        self.ai = ai

    def extract_player_board(self, board):
        return Board(board.board)

    def possible_moves(self):
        return self.board.possible_moves()

    def play_game(self, max_moves=100, wait_after_step=False):
        """
        Plays the game for at most max_moves. When wait_after_step is True
        then after each move of the agent the user is expected to press enter
        before the game continues.
        """
        self.ai.set_board(self.extract_player_board(self.board))

        for i in range(max_moves):
            print()
            print('Move ' + str(i))
            print('Possible moves: ' + str(self.board.possible_moves()))
            self.ai.board.print_board()
            self.ai.update_position(self.board.actor_pos)
            sel_move = self.ai.move(self)
            print('Move: ' + sel_move)
            result = self.board.make_move(sel_move)
            print('Move result: ' + str(result))
            self.ai.percept({'type': sel_move})
            self.ai.percept(board=self.board)
            if wait_after_step:
                a = input()
                if a == 'F':
                    wait_after_step = False


board1 = Board([['W', 'W', 'W', 'W', 'W'],
                ['W', ' ', ' ', 'E', 'W'],
                ['W', 'g', 'W', 'W', 'W'],
                ['W', ' ', ' ', 'S', 'W'],
                ['W', 'W', 'r', 'W', 'W'],
                ['W', 'B', ' ', ' ', 'W'],
                ['W', 'W', 'W', 'W', 'W']])


board2 = Board([['W', 'W', 'W', 'W', 'W', 'W', 'W', 'W', 'W', 'W'],
                ['W', ' ', ' ', ' ', ' ', 'g', ' ', ' ', 'S', 'W'],
                ['W', 'W', ' ', 'W', ' ', 'W', 'W', ' ', 'W', 'W'],
                ['W', ' ', 'g', 'W', 'S', 'r', 'W', 'r', 'W', 'W'],
                ['W', 'W', ' ', 'W', 'W', ' ', 'W', ' ', 'E', 'W'],
                ['W', 'B', ' ', ' ', 'S', ' ', 'W', ' ', 'W', 'W'],
                ['W', 'W', 'W', 'W', 'W', 'W', 'W', 'W', 'W', 'W']])


# starting a game when the script runs
if __name__ == "__main__":
    env = Environment(board2, BacktrackingAgent(board2))
    try:
        env.play_game(wait_after_step=True)
    except Exception as e:
        print('Exception happened: ' + str(e))
