import chess
import random
from typing import List, Optional

class ChessBot:
    def __init__(self, max_depth=3):  # Increased to 3 for better AI
        self.max_depth = max_depth
        self.piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000
        }
        
        # Piece-square tables for positional evaluation
        self.pawn_table = [
            0,  0,  0,  0,  0,  0,  0,  0,
            50, 50, 50, 50, 50, 50, 50, 50,
            10, 10, 20, 30, 30, 20, 10, 10,
            5,  5, 10, 25, 25, 10,  5,  5,
            0,  0,  0, 20, 20,  0,  0,  0,
            5, -5,-10,  0,  0,-10, -5,  5,
            5, 10, 10,-20,-20, 10, 10,  5,
            0,  0,  0,  0,  0,  0,  0,  0
        ]
        
        self.knight_table = [
            -50,-40,-30,-30,-30,-30,-40,-50,
            -40,-20,  0,  0,  0,  0,-20,-40,
            -30,  0, 10, 15, 15, 10,  0,-30,
            -30,  5, 15, 20, 20, 15,  5,-30,
            -30,  0, 15, 20, 20, 15,  0,-30,
            -30,  5, 10, 15, 15, 10,  5,-30,
            -40,-20,  0,  5,  5,  0,-20,-40,
            -50,-40,-30,-30,-30,-30,-40,-50
        ]
        
        self.bishop_table = [
            -20,-10,-10,-10,-10,-10,-10,-20,
            -10,  0,  0,  0,  0,  0,  0,-10,
            -10,  0,  5, 10, 10,  5,  0,-10,
            -10,  5,  5, 10, 10,  5,  5,-10,
            -10,  0, 10, 10, 10, 10,  0,-10,
            -10, 10, 10, 10, 10, 10, 10,-10,
            -10,  5,  0,  0,  0,  0,  5,-10,
            -20,-10,-10,-10,-10,-10,-10,-20
        ]
        
        # Transposition table for caching evaluations
        self.transposition_table = {}
        self.nodes_searched = 0

    def evaluate_board(self, board: chess.Board) -> float:
        """Fast board evaluation with material and positional scoring."""
        if board.is_checkmate():
            return -100000 if board.turn else 100000
        if board.is_stalemate() or board.is_insufficient_material():
            return 0
        
        score = 0
        piece_map = board.piece_map()
        
        # Material evaluation with positional bonuses
        for square, piece in piece_map.items():
            value = self.piece_values[piece.piece_type]
            
            # Add positional bonus
            positional_bonus = self.get_positional_bonus(piece, square)
            
            if piece.color == chess.WHITE:
                score += value + positional_bonus
            else:
                score -= value + positional_bonus
        
        # Mobility (simple count of legal moves)
        mobility = board.legal_moves.count()
        if board.turn == chess.WHITE:
            score += mobility * 5
        else:
            score -= mobility * 5
        
        # Pawn structure (simple evaluation)
        score += self.evaluate_pawn_structure_simple(board)
        
        return score / 100.0

    def get_positional_bonus(self, piece: chess.Piece, square: chess.Square) -> int:
        """Fast positional bonus using piece-square tables."""
        # Mirror square for black pieces
        if piece.color == chess.BLACK:
            square = chess.square_mirror(square)
        
        if piece.piece_type == chess.PAWN:
            return self.pawn_table[square]
        elif piece.piece_type == chess.KNIGHT:
            return self.knight_table[square]
        elif piece.piece_type == chess.BISHOP:
            return self.bishop_table[square]
        elif piece.piece_type == chess.ROOK:
            # Rooks belong on open files
            file = chess.square_file(square)
            # Simple bonus for center files
            if file in [2, 3, 4, 5]:
                return 10
            return 0
        elif piece.piece_type == chess.QUEEN:
            # Queens belong in center
            file = chess.square_file(square)
            rank = chess.square_rank(square)
            center_distance = abs(3.5 - file) + abs(3.5 - rank)
            return int((8 - center_distance) * 5)
        
        return 0

    def evaluate_pawn_structure_simple(self, board: chess.Board) -> int:
        """Fast pawn structure evaluation."""
        score = 0
        pawns = board.pieces(chess.PAWN, chess.WHITE)
        
        for pawn in pawns:
            # Bonus for passed pawns
            file = chess.square_file(pawn)
            rank = chess.square_rank(pawn)
            
            # Check if pawn is passed
            is_passed = True
            for f in [max(0, file-1), file, min(7, file+1)]:
                for r in range(rank + 1, 8):
                    test_square = chess.square(f, r)
                    if board.piece_at(test_square) == chess.Piece(chess.PAWN, chess.BLACK):
                        is_passed = False
                        break
                if not is_passed:
                    break
            
            if is_passed:
                score += (rank * 10)  # Further advanced = better
        
        # Do the same for black pawns
        black_pawns = board.pieces(chess.PAWN, chess.BLACK)
        for pawn in black_pawns:
            file = chess.square_file(pawn)
            rank = chess.square_rank(pawn)
            
            is_passed = True
            for f in [max(0, file-1), file, min(7, file+1)]:
                for r in range(0, rank):
                    test_square = chess.square(f, r)
                    if board.piece_at(test_square) == chess.Piece(chess.PAWN, chess.WHITE):
                        is_passed = False
                        break
                if not is_passed:
                    break
            
            if is_passed:
                score -= ((7 - rank) * 10)  # Further advanced = better for black
        
        return score

    def order_moves_fast(self, board: chess.Board, moves: List[chess.Move]) -> List[chess.Move]:
        """Fast move ordering for alpha-beta pruning."""
        move_scores = []
        
        for move in moves:
            score = 0
            
            # MVV-LVA (Most Valuable Victim - Least Valuable Aggressor)
            if board.is_capture(move):
                victim = board.piece_at(move.to_square)
                aggressor = board.piece_at(move.from_square)
                
                if victim and aggressor:
                    victim_value = self.piece_values[victim.piece_type]
                    aggressor_value = self.piece_values[aggressor.piece_type]
                    score = victim_value - aggressor_value + 1000  # Captures get high priority
            
            # Promotion moves
            if move.promotion:
                score += 900  # Just below queen capture
            
            # Killer heuristic: moves that cause checks
            board.push(move)
            if board.is_check():
                score += 50
            board.pop()
            
            move_scores.append((score, move))
        
        # Sort by score (highest first)
        move_scores.sort(reverse=True, key=lambda x: x[0])
        return [move for _, move in move_scores]

    def minimax_alpha_beta(self, board: chess.Board, depth: int, alpha: float, 
                          beta: float, maximizing_player: bool) -> float:
        """Minimax with alpha-beta pruning (optimized)."""
        self.nodes_searched += 1
        
        # Return early conditions
        if depth == 0:
            return self.evaluate_board(board)
        
        if board.is_game_over():
            if board.is_checkmate():
                return -100000 if maximizing_player else 100000
            return 0
        
        # Get and order moves
        legal_moves = list(board.legal_moves)
        legal_moves = self.order_moves_fast(board, legal_moves)
        
        if maximizing_player:
            max_eval = float('-inf')
            for move in legal_moves:
                board.push(move)
                eval_score = self.minimax_alpha_beta(board, depth - 1, alpha, beta, False)
                board.pop()
                
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                
                # Alpha-beta pruning
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in legal_moves:
                board.push(move)
                eval_score = self.minimax_alpha_beta(board, depth - 1, alpha, beta, True)
                board.pop()
                
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                # Alpha-beta pruning
                if beta <= alpha:
                    break
            return min_eval

    def get_best_move_fast(self, board: chess.Board, time_limit: float = 2.0) -> Optional[chess.Move]:
        """Fast move selection with iterative deepening and time limit."""
        import time
        start_time = time.time()
        
        best_move = None
        legal_moves = list(board.legal_moves)
        
        if not legal_moves:
            return None
        
        # If only one move, return it immediately
        if len(legal_moves) == 1:
            return legal_moves[0]
        
        # Simple opening book
        opening_move = self.get_opening_move(board)
        if opening_move:
            return opening_move
        
        # Order moves once at the beginning
        legal_moves = self.order_moves_fast(board, legal_moves)
        
        # Try increasing depths until time runs out
        for depth in range(1, self.max_depth + 1):
            current_best = None
            current_best_value = float('-inf')
            
            # Reset node count for this depth
            self.nodes_searched = 0
            
            for move in legal_moves:
                # Check time limit
                if time.time() - start_time > time_limit:
                    return best_move if best_move else legal_moves[0]
                
                board.push(move)
                value = self.minimax_alpha_beta(board, depth - 1, float('-inf'), float('inf'), False)
                board.pop()
                
                if value > current_best_value:
                    current_best_value = value
                    current_best = move
            
            # Update overall best move
            if current_best:
                best_move = current_best
                best_value = current_best_value
            
            # If we found a winning move, return it immediately
            if current_best_value > 5000:  # Checkmate score
                return current_best
            
            # Break early if taking too long
            if time.time() - start_time > time_limit / 2:
                break
        
        return best_move if best_move else legal_moves[0]

    def get_opening_move(self, board: chess.Board) -> Optional[chess.Move]:
        """Simple opening book for common openings."""
        opening_moves = {
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1": [
                chess.Move.from_uci("e2e4"),  # King's pawn
                chess.Move.from_uci("d2d4"),  # Queen's pawn
                chess.Move.from_uci("g1f3"),  # King's knight
            ],
            "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1": [
                chess.Move.from_uci("e7e5"),  # Open game
                chess.Move.from_uci("c7c5"),  # Sicilian
                chess.Move.from_uci("e7e6"),  # French
            ]
        }
        
        fen = board.fen().split(' ')[0]  # Get position part of FEN
        if fen in opening_moves:
            moves = opening_moves[fen]
            for move in moves:
                if move in board.legal_moves:
                    return move
        
        return None

    def get_best_move(self, board: chess.Board) -> Optional[chess.Move]:
        """Main method to get best move (uses fast version)."""
        return self.get_best_move_fast(board, time_limit=1.5)  # Reduced time limit for responsiveness