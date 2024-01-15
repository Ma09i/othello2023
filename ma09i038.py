# 危険エリア回避
class NamachaAI(OthelloAI):
    def __init__(self, face, name):
        self.face = face
        self.name = name

    def move(self, board: np.array, piece: int)->tuple[int, int]:
        best_moves = self.get_best_moves(board, piece)
        return best_moves[0]

    def get_yellow_area(self, N):
        return [(0, 1), (0, N-2), (1, 0), (1, N-1), (N-2, 0), (N-2, N-1), (N-1, 1), (N-1, N-2)]

    def get_red_area(self, N):
        return [(1, 1), (1, N-2), (N-2, 1), (N-2, N-2)]

    def get_best_moves(self, board, player, N=6):
        #置ける場所を取得する
        valid_moves = get_valid_moves(board, player)

        #角に置かれる可能性があるエリアを除外
        #参考(https://www.bodoge-intl.com/strategy/reverse/)
        removed_danger_area = [piece for piece in valid_moves if piece not in self.get_red_area(N) and piece not in self.get_yellow_area(N)]
        if removed_danger_area:
            return removed_danger_area
        else:
            #レッドエリアのみ除外
            removed_red_area = [piece for piece in valid_moves if piece not in self.get_red_area(N)]
            if removed_red_area:
                return removed_red_area
            else:
                return valid_moves



# ゲーム木・ミニマックス法

def display_move_no_display(board, row, col, player):
    """
    ゲーム木のノード作成のために石を置いた後の盤面をシミュレートする
    """
    stones_to_flip = flip_stones(board, row, col, player)
    board[row, col] = player
    #display_board(board, sleep=0.3)
    for r, c in stones_to_flip:
        board[r, c] = player
        #display_board(board, sleep=0.1)
    #display_board(board, sleep=0.6)

class GameTreeNode:
    def __init__(self, board, player, move=None):
        self.board = board
        self.player = player
        self.move = move
        self.children = []
        self.score = None

    def create_children(self, depth):
        """
        ゲーム木を再起呼び出しで作成する
        """
        if depth == 0 or count_board(self.board, EMPTY) == 0:
            self.score = evaluate_board(self.board)
            return

        for move in get_valid_moves(self.board, self.player):
            new_board = self.board.copy()
            display_move_no_display(new_board, *move, self.player)
            child_node = GameTreeNode(new_board, -self.player, move)
            self.children.append(child_node)
            child_node.create_children(depth - 1)

def evaluate_board(board):
    """
    ゲーム木のノードのスコアを算出する評価関数
    """
    return count_board(board, BLACK) - count_board(board, WHITE)

def minimax(node, depth, maximizingPlayer, alpha=float('-inf'), beta=float('inf')):
    """
    ミニマックスアルゴリズムでスコアを算出する
    """
    if depth == 0 or node.children == []:
        return evaluate_board(node.board)

    if maximizingPlayer:
        maxEval = float('-inf')
        for child in node.children:
            eval = minimax(child, depth-1, False, alpha, beta)
            maxEval = max(maxEval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return maxEval
    else:
        minEval = float('inf')
        for child in node.children:
            eval = minimax(child, depth-1, True, alpha, beta)
            minEval = min(minEval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return minEval

class NamachaAI2(OthelloAI):
    def __init__(self, face, name, depth=6):
        super().__init__(face, name)
        self.depth = depth

    def move(self, board, piece):
        # 現在の盤面で有効な手のリストを取得
        valid_moves = get_valid_moves(board, piece)

        # 有効な手がない場合はNoneを返す
        if not valid_moves:
            return None

        # 各有効な手に対してミニマックスアルゴリズムを適用し、最善の手を決定
        best_move = None
        best_score = float('-inf') if piece == BLACK else float('inf')

        for move in valid_moves:
            new_board = board.copy()
            # 有効な手を適用して新しい盤面を生成
            display_move_no_display(new_board, move[0], move[1], piece)
            # 新しい盤面に基づいてゲーム木のノードを生成
            node = GameTreeNode(new_board, -piece)
            node.create_children(self.depth - 1)
            # ミニマックスアルゴリズムでスコアを計算
            score = minimax(node, self.depth - 1, piece != BLACK)
            # 最適な手を更新
            if (piece == BLACK and score > best_score) or (piece != BLACK and score < best_score):
                best_move = move
                best_score = score

        r, c = best_move
        if board[r, c] != 0:
            print('invalid!')

        return best_move
