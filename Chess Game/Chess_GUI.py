import pygame
import chess
import time
import sys
import os
from typing import Optional, Tuple, List, Dict
import threading

# Try to import the bot
try:
    from Chess_Bot import ChessBot
except ImportError:
    # Create a simple fallback bot if import fails
    class ChessBot:
        def __init__(self, max_depth=2):
            self.max_depth = max_depth
        
        def get_best_move(self, board):
            import random
            legal_moves = list(board.legal_moves)
            return random.choice(legal_moves) if legal_moves else None

class GameState:
    """Encapsulates all game state to avoid global variables."""
    def __init__(self):
        self.board = chess.Board()
        self.bot = ChessBot(max_depth=3)  # Increased to 3 for better AI
        self.move_history: List[str] = []
        self.player_color = chess.WHITE
        
        # UI state
        self.selected_square: Optional[chess.Square] = None
        self.check_message_time: float = 0
        self.last_mover: Optional[str] = None
        
        # Animation
        self.animating = False
        
        # Bot thinking
        self.bot_thinking = False
        self.bot_move_result = None
        self.bot_thread = None
        
        # Endgame 5-move rule tracking (FIXED: Issue #1)
        self.endgame_mode: Optional[str] = None
        self.moves_left_white: Optional[int] = None
        self.moves_left_black: Optional[int] = None

class ChessGUI:
    def __init__(self):
        pygame.init()
        
        # ==========================
        # WINDOW SETUP (From Previous)
        # ==========================
        self.WIDTH, self.HEIGHT = 900, 700
        self.BOARD_SIZE = 640
        self.SQUARE_SIZE = self.BOARD_SIZE // 8
        
        self.WINDOW = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Chess Game")
        
        # ==========================
        # COLORS & UI STYLE (From Previous)
        # ==========================
        self.WHITE = (240, 217, 181)
        self.BROWN = (181, 136, 99)
        self.HIGHLIGHT = (0, 255, 0, 120)
        self.SELECTED = (0, 150, 255, 120)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.PANEL_BG = (245, 245, 245)
        self.BOARD_OUTLINE = (60, 40, 20)
        self.GREEN = (0, 180, 0)
        self.OVERLAY = (0, 0, 0, 180)
        self.BLUE = (0, 100, 200)  # For player labels
        
        # ==========================
        # LOAD BACKGROUND TEXTURE (From Previous)
        # ==========================
        self.background = self.load_background()
        
        # ==========================
        # LOAD PIECES (From Previous)
        # ==========================
        self.pieces = self.load_pieces()
        self.PIECE_SCALE = 0.95
        
        # Game state
        self.state = GameState()
        self.last_move = None
        
        # Animation state
        self.animation_data = None
        self.animation_progress = 0
        self.animation_speed = 15  # Animation steps
        
        # Clock for FPS control
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Load fonts
        self.fonts = self.load_fonts()
    
    # ==========================
    # RESOURCE LOADING FUNCTIONS (From Previous)
    # ==========================
    def load_background(self):
        """Load background with fallback (From Previous)."""
        try:
            if os.path.exists("images/background.jpg"):
                img = pygame.image.load("images/background.jpg").convert()
                return pygame.transform.scale(img, (self.WIDTH, self.HEIGHT))
        except:
            pass
        
        # Create gradient background as fallback
        background = pygame.Surface((self.WIDTH, self.HEIGHT))
        for i in range(self.HEIGHT):
            color = (40 + i//10, 60 + i//8, 80 + i//6)
            pygame.draw.line(background, color, (0, i), (self.WIDTH, i))
        return background
    
    def load_pieces(self):
        """Load piece images exactly like previous code."""
        def load_piece(path):
            try:
                if os.path.exists(path):
                    img = pygame.image.load(path).convert_alpha()
                    # Get bounding rect and crop like previous code
                    rect = img.get_bounding_rect()
                    img = img.subsurface(rect).copy()
                    return img
                else:
                    raise FileNotFoundError
            except (pygame.error, FileNotFoundError):
                # Create fallback piece
                return self.create_fallback_piece(path)
        
        pieces = {}
        piece_files = {
            "P": "images/pawn-w.png",
            "R": "images/rook-w.png",
            "N": "images/knight-w.png",
            "B": "images/bishop-w.png",
            "Q": "images/queen-w.png",
            "K": "images/king-w.png",
            "p": "images/pawn-b.png",
            "r": "images/rook-b.png",
            "n": "images/knight-b.png",
            "b": "images/bishop-b.png",
            "q": "images/queen-b.png",
            "k": "images/king-b.png",
        }
        
        for symbol, path in piece_files.items():
            pieces[symbol] = load_piece(path)
        
        return pieces
    
    def create_fallback_piece(self, path):
        """Create fallback piece when image is missing."""
        # Determine piece color and type from filename
        if "w.png" in path:
            color = 'w'
            fill_color = (255, 255, 255, 230)
        else:
            color = 'b'
            fill_color = (30, 30, 30, 230)
        
        # Determine piece type from path
        if "pawn" in path:
            piece_type = 'P' if color == 'w' else 'p'
        elif "rook" in path:
            piece_type = 'R' if color == 'w' else 'r'
        elif "knight" in path:
            piece_type = 'N' if color == 'w' else 'n'
        elif "bishop" in path:
            piece_type = 'B' if color == 'w' else 'b'
        elif "queen" in path:
            piece_type = 'Q' if color == 'w' else 'q'
        elif "king" in path:
            piece_type = 'K' if color == 'w' else 'k'
        else:
            piece_type = '?'
        
        size = int(self.SQUARE_SIZE * self.PIECE_SCALE)
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        outline_color = (0, 0, 0, 255)
        
        # Draw circle piece
        pygame.draw.circle(surface, fill_color, (size//2, size//2), size//2 - 5)
        pygame.draw.circle(surface, outline_color, (size//2, size//2), size//2 - 5, 2)
        
        # Add piece letter
        piece_letters = {
            'P': '♙', 'p': '♟',
            'R': '♖', 'r': '♜',
            'N': '♘', 'n': '♞',
            'B': '♗', 'b': '♝',
            'Q': '♕', 'q': '♛',
            'K': '♔', 'k': '♚'
        }
        
        letter = piece_letters.get(piece_type, '?')
        try:
            font = pygame.font.SysFont('segoeuisymbol', size//2)
        except:
            font = pygame.font.SysFont('arial', size//2)
        
        text = font.render(letter, True, outline_color)
        text_rect = text.get_rect(center=(size//2, size//2))
        surface.blit(text, text_rect)
        
        return surface
    
    def load_fonts(self):
        """Load fonts with fallbacks."""
        fonts = {}
        try:
            # Try to load the exact fonts from previous code
            fonts['title'] = pygame.font.Font("freesansbold.ttf", 28)
            fonts['normal'] = pygame.font.Font("freesansbold.ttf", 26)
            fonts['small'] = pygame.font.Font(None, 20)
            fonts['large'] = pygame.font.Font("freesansbold.ttf", 34)
            fonts['button'] = pygame.font.Font("freesansbold.ttf", 30)
            fonts['small_bold'] = pygame.font.Font("freesansbold.ttf", 22)
        except:
            # Fallback to system fonts
            fonts['title'] = pygame.font.SysFont('arial', 28, bold=True)
            fonts['normal'] = pygame.font.SysFont('arial', 26, bold=True)
            fonts['small'] = pygame.font.SysFont('arial', 20)
            fonts['large'] = pygame.font.SysFont('arial', 34, bold=True)
            fonts['button'] = pygame.font.SysFont('arial', 30, bold=True)
            fonts['small_bold'] = pygame.font.SysFont('arial', 22, bold=True)
        
        return fonts
    
    def reset_game(self):
        """Reset the game to initial state (FIXED: Issue #6)."""
        # Create a completely new game state
        self.state = GameState()
        self.last_move = None
        self.animation_data = None
    
    # ==========================
    # DRAWING FUNCTIONS
    # ==========================
    def draw_background(self):
        """Draw the background exactly like previous code."""
        self.WINDOW.blit(self.background, (0, 0))
    
    def draw_board(self):
        """Draw the chess board exactly like previous code."""
        pygame.draw.rect(self.WINDOW, self.BOARD_OUTLINE, (0, 0, self.BOARD_SIZE, self.BOARD_SIZE), 6)
        for row in range(8):
            for col in range(8):
                color = self.WHITE if (row + col) % 2 == 0 else self.BROWN
                pygame.draw.rect(
                    self.WINDOW, color,
                    (col * self.SQUARE_SIZE, row * self.SQUARE_SIZE,
                     self.SQUARE_SIZE, self.SQUARE_SIZE)
                )
        
        # Highlight last move
        if self.last_move:
            from_sq, to_sq = self.last_move
            self.highlight_square(from_sq, (255, 255, 0, 80))
            self.highlight_square(to_sq, (255, 255, 0, 80))
    
    def draw_pieces(self, exclude_square: Optional[chess.Square] = None):
        """Draw all pieces on the board exactly like previous code."""
        for square in chess.SQUARES:
            # Skip the piece being animated
            if self.animation_data and square == self.animation_data['from_sq']:
                continue
                
            piece = self.state.board.piece_at(square)
            if piece:
                row = 7 - (square // 8)
                col = square % 8

                img = self.pieces[piece.symbol()]
                new_size = int(self.SQUARE_SIZE * self.PIECE_SCALE)
                scaled_img = pygame.transform.smoothscale(img, (new_size, new_size))

                center_x = col * self.SQUARE_SIZE + (self.SQUARE_SIZE // 2)
                center_y = row * self.SQUARE_SIZE + (self.SQUARE_SIZE // 2)

                draw_x = center_x - (new_size // 2)
                draw_y = center_y - (new_size // 2)

                self.WINDOW.blit(scaled_img, (draw_x, draw_y))
    
    def draw_animated_piece(self):
        """Draw the piece being animated."""
        if self.animation_data:
            t = self.animation_progress / self.animation_speed
            # Use easing for smoother animation
            eased_t = t * t * (3 - 2 * t)
            
            from_sq = self.animation_data['from_sq']
            to_sq = self.animation_data['to_sq']
            piece_symbol = self.animation_data['piece_symbol']
            
            from_row = 7 - (from_sq // 8)
            from_col = from_sq % 8
            to_row = 7 - (to_sq // 8)
            to_col = to_sq % 8
            
            start_x = from_col * self.SQUARE_SIZE
            start_y = from_row * self.SQUARE_SIZE
            end_x = to_col * self.SQUARE_SIZE
            end_y = to_row * self.SQUARE_SIZE
            
            x = start_x + (end_x - start_x) * eased_t
            y = start_y + (end_y - start_y) * eased_t
            
            img = self.pieces[piece_symbol]
            new_size = int(self.SQUARE_SIZE * self.PIECE_SCALE)
            scaled_img = pygame.transform.smoothscale(img, (new_size, new_size))
            
            self.WINDOW.blit(scaled_img, (x, y))
    
    def highlight_square(self, square: chess.Square, color: Tuple[int, int, int, int]):
        """Highlight a square on the board exactly like previous code."""
        row = 7 - (square // 8)
        col = square % 8
        s = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE), pygame.SRCALPHA)
        s.fill(color)
        self.WINDOW.blit(s, (col * self.SQUARE_SIZE, row * self.SQUARE_SIZE))
    
    def draw_labels(self):
        """Draw turn indicator (FIXED: Issue #5 - Add player labels)."""
        # Draw player labels on board
        human_label = self.fonts['small_bold'].render("HUMAN", True, self.BLUE)
        ai_label = self.fonts['small_bold'].render("AI", True, self.RED)
        
        # Draw HUMAN on left side (White pieces at bottom)
        self.WINDOW.blit(human_label, (10, self.BOARD_SIZE - 40))
        
        # Draw AI on right side (Black pieces at top)
        self.WINDOW.blit(ai_label, (self.BOARD_SIZE - 40, 10))
        
        # Draw turn indicator
        if self.state.bot_thinking:
            text = "AI THINKING..."
            color = self.GREEN
        else:
            if self.state.board.turn == self.state.player_color:
                text = "YOUR TURN (White)"
                color = self.BLACK
            else:
                text = "AI'S TURN (Black)"
                color = self.BLACK
        
        turn_label = self.fonts['normal'].render(text, True, color)
        self.WINDOW.blit(turn_label, (20, 650))
    
    def draw_game_status(self):
        """Draw check/checkmate status (FIXED: Issue #2 - Only show CHECK)."""
        # Only show "CHECK!" message, not "CHECKMATE!"
        if self.state.board.is_check() and not self.state.board.is_checkmate():
            text = "CHECK!"
            self.state.check_message_time = time.time()
        else:
            text = ""

        if text and time.time() - self.state.check_message_time < 2.5:
            label = self.fonts['large'].render(text, True, self.RED)
            self.WINDOW.blit(label, (300, 650))
    
    def draw_move_history(self):
        """Draw move history panel exactly like previous code."""
        pygame.draw.rect(self.WINDOW, self.PANEL_BG, (640, 0, 260, 700))
        title = self.fonts['title'].render("Move History", True, self.BLACK)
        self.WINDOW.blit(title, (660, 20))

        y_offset = 50
        for move in self.state.move_history[-20:]:
            text = self.fonts['small'].render(move, True, self.BLACK)
            self.WINDOW.blit(text, (660, y_offset))
            y_offset += 22
    
    def draw_endgame_rules(self) -> bool:
        """Draw endgame 5-move rule (FIXED: Issue #1)."""
        # Check for endgame conditions
        white_pieces = [p for p in self.state.board.piece_map().values() if p.color == chess.WHITE]
        black_pieces = [p for p in self.state.board.piece_map().values() if p.color == chess.BLACK]

        white_only_king = all(p.piece_type == chess.KING for p in white_pieces)
        black_only_king = all(p.piece_type == chess.KING for p in black_pieces)

        # === CASE 2: BOTH SIDES HAVE ONLY KINGS ===
        if white_only_king and black_only_king:
            if self.state.endgame_mode is None:
                self.state.endgame_mode = "two_kings"
                self.state.moves_left_white = 5
                self.state.moves_left_black = 5

            text = f"Only Kings Left — White: {self.state.moves_left_white} moves | Black: {self.state.moves_left_black} moves"
            label = self.fonts['small_bold'].render(text, True, self.RED)
            self.WINDOW.blit(label, (60, 610))

            if self.state.moves_left_white <= 0 and self.state.moves_left_black <= 0:
                # Game drawn
                self.show_draw_screen("Game drawn: both kings, no checkmate in 10 moves.")
                return True

        # === CASE 1: ONLY ONE SIDE HAS A KING ===
        elif white_only_king or black_only_king:
            if self.state.endgame_mode is None:
                self.state.endgame_mode = "one_king"

                if white_only_king:
                    self.state.moves_left_black = 5
                    self.state.moves_left_white = None
                else:
                    self.state.moves_left_white = 5
                    self.state.moves_left_black = None

            if white_only_king:
                text = f"Black has 5 moves to checkmate: {self.state.moves_left_black} left"
            else:
                text = f"White has 5 moves to checkmate: {self.state.moves_left_white} left"

            label = self.fonts['small_bold'].render(text, True, self.RED)
            self.WINDOW.blit(label, (100, 610))

            if (white_only_king and self.state.moves_left_black <= 0) or \
               (black_only_king and self.state.moves_left_white <= 0):
                # Game drawn
                self.show_draw_screen("Game drawn: one king side survived 5 moves.")
                return True
        
        return False
    
    def draw_highlights(self):
        """Draw highlighted squares for selected piece."""
        if self.state.selected_square is not None and not self.state.animating:
            # Highlight selected square
            self.highlight_square(self.state.selected_square, self.SELECTED)
            
            # Highlight legal moves
            for move in self.state.board.legal_moves:
                if move.from_square == self.state.selected_square:
                    self.highlight_square(move.to_square, self.HIGHLIGHT)
    
    def draw(self):
        """Main draw function."""
        self.draw_background()
        self.draw_board()
        self.draw_highlights()
        
        if not self.state.animating:
            # Draw all pieces normally
            self.draw_pieces()
        else:
            # Draw all pieces except the animated one
            self.draw_pieces(exclude_square=self.animation_data['from_sq'])
            # Draw the animated piece
            self.draw_animated_piece()
        
        self.draw_move_history()
        self.draw_labels()
        self.draw_game_status()
        # Draw endgame rules (returns True if game should end)
        if self.draw_endgame_rules():
            return True
        
        return False
    
    # ==========================
    # GAME LOGIC FUNCTIONS
    # ==========================
    def get_square_from_pos(self, pos: Tuple[int, int]) -> Optional[chess.Square]:
        """Convert screen position to chess square."""
        x, y = pos
        if y >= self.BOARD_SIZE:
            return None
        col = x // self.SQUARE_SIZE
        row = y // self.SQUARE_SIZE
        return chess.square(col, 7 - row)
    
    def add_move_to_history(self, move_san: str, player: str):
        """Add a move to the history."""
        self.state.move_history.append(f"{player}: {move_san}")
    
    def update_endgame_move_counters(self):
        """Update endgame move counters after a move."""
        if self.state.endgame_mode == "one_king":
            if self.state.moves_left_white is not None:
                self.state.moves_left_white -= 1
            if self.state.moves_left_black is not None:
                self.state.moves_left_black -= 1
        elif self.state.endgame_mode == "two_kings":
            if self.state.last_mover == "Human":
                self.state.moves_left_white -= 1
            else:  # AI moved
                self.state.moves_left_black -= 1
    
    def start_animation(self, from_sq: chess.Square, to_sq: chess.Square, piece_symbol: str):
        """Start animation for a move."""
        self.animation_data = {
            'from_sq': from_sq,
            'to_sq': to_sq,
            'piece_symbol': piece_symbol
        }
        self.animation_progress = 0
        self.state.animating = True
    
    def update_animation(self):
        """Update animation progress."""
        if self.state.animating and self.animation_data:
            self.animation_progress += 1
            
            if self.animation_progress >= self.animation_speed:
                # Animation complete
                self.state.animating = False
                self.animation_data = None
                return False  # Animation done
            
            return True  # Animation still running
        
        return False  # No animation
    
    def choose_promotion(self) -> chess.PieceType:
        """Show promotion menu exactly like previous code."""
        font = self.fonts['title']
        options = ["Queen", "Rook", "Bishop", "Knight"]

        self.WINDOW.blit(font.render("Choose Promotion:", True, self.BLACK), (200, 200))

        buttons = []
        x = 180
        for opt in options:
            rect = pygame.Rect(x, 260, 120, 50)
            pygame.draw.rect(self.WINDOW, self.WHITE, rect)
            pygame.draw.rect(self.WINDOW, self.BLACK, rect, 2)
            self.WINDOW.blit(font.render(opt, True, self.BLACK), (x + 10, 270))
            buttons.append((rect, opt))
            x += 140

        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for rect, opt in buttons:
                        if rect.collidepoint(event.pos):
                            return {
                                "Queen": chess.QUEEN,
                                "Rook": chess.ROOK,
                                "Bishop": chess.BISHOP,
                                "Knight": chess.KNIGHT
                            }[opt]
    
    def show_draw_screen(self, reason: str):
        """Show draw result screen."""
        font_big = self.fonts['large']
        font_small = self.fonts['normal']

        overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        overlay.fill(self.OVERLAY)
        self.WINDOW.blit(overlay, (0, 0))

        title = "GAME DRAWN"
        t1 = font_big.render(title, True, self.WHITE)
        t2 = font_small.render(reason, True, self.WHITE)
        t3 = font_small.render("Score: ½ - ½", True, self.WHITE)

        self.WINDOW.blit(t1, (320, 200))
        self.WINDOW.blit(t2, (200, 270))
        self.WINDOW.blit(t3, (350, 320))

        close_rect = pygame.Rect(250, 380, 180, 60)
        new_rect = pygame.Rect(470, 380, 180, 60)

        pygame.draw.rect(self.WINDOW, self.WHITE, close_rect)
        pygame.draw.rect(self.WINDOW, self.BLACK, close_rect, 2)
        pygame.draw.rect(self.WINDOW, self.WHITE, new_rect)
        pygame.draw.rect(self.WINDOW, self.BLACK, new_rect, 2)

        self.WINDOW.blit(font_small.render("CLOSE", True, self.BLACK), (300, 395))
        self.WINDOW.blit(font_small.render("NEW GAME", True, self.BLACK), (500, 395))

        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if close_rect.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()

                    if new_rect.collidepoint(event.pos):
                        self.reset_game()
                        return True
    
    def show_checkmate_screen(self, winner: str):
        """Show checkmate result screen exactly like previous code."""
        font_big = self.fonts['large']
        font_small = self.fonts['normal']

        overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        overlay.fill(self.OVERLAY)
        self.WINDOW.blit(overlay, (0, 0))

        if winner == "Human":
            title = "CHECKMATE — HUMAN WINS"
            score = "Human 1 : 0 AI"
        else:
            title = "CHECKMATE — AI WINS"
            score = "Human 0 : 1 AI"

        t1 = font_big.render(title, True, self.WHITE)
        t2 = font_small.render(score, True, self.WHITE)

        self.WINDOW.blit(t1, (250, 220))
        self.WINDOW.blit(t2, (320, 270))

        close_rect = pygame.Rect(250, 350, 180, 60)
        new_rect = pygame.Rect(470, 350, 180, 60)

        pygame.draw.rect(self.WINDOW, self.WHITE, close_rect)
        pygame.draw.rect(self.WINDOW, self.BLACK, close_rect, 2)
        pygame.draw.rect(self.WINDOW, self.WHITE, new_rect)
        pygame.draw.rect(self.WINDOW, self.BLACK, new_rect, 2)

        self.WINDOW.blit(font_small.render("CLOSE", True, self.BLACK), (300, 365))
        self.WINDOW.blit(font_small.render("NEW GAME", True, self.BLACK), (500, 365))

        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if close_rect.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()

                    if new_rect.collidepoint(event.pos):
                        self.reset_game()
                        return True
    
    def start_screen(self):
        """Show start screen exactly like previous code."""
        font = self.fonts['button']

        self.WINDOW.blit(self.background, (0, 0))
        text1 = font.render("White = HUMAN", True, self.BLACK)
        text2 = font.render("Black = AI", True, self.BLACK)
        self.WINDOW.blit(text1, (330, 220))
        self.WINDOW.blit(text2, (350, 260))

        play_rect = pygame.Rect(350, 350, 200, 70)
        pygame.draw.rect(self.WINDOW, self.WHITE, play_rect)
        pygame.draw.rect(self.WINDOW, self.BLACK, play_rect, 2)

        play_text = font.render("PLAY", True, self.BLACK)
        self.WINDOW.blit(play_text, (410, 365))
        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_rect.collidepoint(event.pos):
                        return
    
    def handle_human_move(self, pos: Tuple[int, int]) -> bool:
        """Handle human player move (FIXED: Issue #3, #4)."""
        # Lock input during animation or bot thinking (FIXED: Issue #4)
        if self.state.animating or self.state.bot_thinking:
            return False
            
        square = self.get_square_from_pos(pos)
        if square is None:
            self.state.selected_square = None
            return False
        
        if self.state.selected_square is None:
            # Select a piece
            piece = self.state.board.piece_at(square)
            if piece and piece.color == self.state.player_color:
                self.state.selected_square = square
                return False
        else:
            # Try to make a move
            from_square = self.state.selected_square
            piece = self.state.board.piece_at(from_square)
            
            if not piece:
                self.state.selected_square = None
                return False
            
            # Check if this is a pawn promotion (FIXED: Issue #3 - Check legality first)
            is_pawn = piece.piece_type == chess.PAWN
            to_rank = chess.square_rank(square)
            
            # First, try non-promotion move
            move = chess.Move(from_square, square)
            
            # If pawn is moving to last rank, check if promotion is a legal option
            if is_pawn and ((piece.color == chess.WHITE and to_rank == 7) or 
                           (piece.color == chess.BLACK and to_rank == 0)):
                # Check if promotion move is legal
                for promo_piece in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]:
                    promo_move = chess.Move(from_square, square, promotion=promo_piece)
                    if promo_move in self.state.board.legal_moves:
                        # Show promotion menu since at least one promotion is legal
                        promotion_piece = self.choose_promotion()
                        move = chess.Move(from_square, square, promotion=promotion_piece)
                        break
            
            # Check if move is legal
            if move in self.state.board.legal_moves:
                # Get SAN notation BEFORE pushing the move
                move_san = self.state.board.san(move)
                
                # Store piece symbol for animation
                piece_symbol = piece.symbol()
                
                # Start animation
                self.start_animation(from_square, square, piece_symbol)
                
                # Make move after animation
                self.state.board.push(move)
                
                # Add to history
                self.add_move_to_history(move_san, "You")
                self.state.last_mover = "Human"
                
                # Update last move for highlighting
                self.last_move = (from_square, square)
                
                # Update endgame move counters
                self.update_endgame_move_counters()
                
                self.state.selected_square = None
                return True
            
            # Invalid move, deselect
            self.state.selected_square = None
        
        return False
    
    def bot_think_thread(self):
        """Thread function for bot thinking."""
        self.state.bot_move_result = self.state.bot.get_best_move(self.state.board)
    
    def handle_bot_move(self):
        """Handle AI bot move (non-blocking)."""
        if not self.state.bot_thinking and self.state.board.turn != self.state.player_color:
            # Start bot thinking in a thread
            self.state.bot_thinking = True
            self.state.bot_thread = threading.Thread(target=self.bot_think_thread)
            self.state.bot_thread.daemon = True
            self.state.bot_thread.start()
        
        # Check if bot has finished thinking
        if self.state.bot_thinking and self.state.bot_move_result is not None:
            bot_move = self.state.bot_move_result
            
            if bot_move:
                # Check if promotion is needed
                piece = self.state.board.piece_at(bot_move.from_square)
                if piece and piece.piece_type == chess.PAWN:
                    to_rank = chess.square_rank(bot_move.to_square)
                    if (piece.color == chess.WHITE and to_rank == 7) or \
                       (piece.color == chess.BLACK and to_rank == 0):
                        # Add promotion to queen (bot always promotes to queen)
                        bot_move = chess.Move(
                            bot_move.from_square,
                            bot_move.to_square,
                            promotion=chess.QUEEN
                        )
                
                # Get SAN notation BEFORE pushing the move
                move_san = self.state.board.san(bot_move)
                
                # Start animation
                piece_symbol = self.state.board.piece_at(bot_move.from_square).symbol()
                self.start_animation(bot_move.from_square, bot_move.to_square, piece_symbol)
                
                # Make move
                self.state.board.push(bot_move)
                
                # Add to history
                self.add_move_to_history(move_san, "AI")
                self.state.last_mover = "AI"
                
                # Update last move for highlighting
                self.last_move = (bot_move.from_square, bot_move.to_square)
                
                # Update endgame move counters
                self.update_endgame_move_counters()
            
            # Reset bot state
            self.state.bot_thinking = False
            self.state.bot_move_result = None
            self.state.bot_thread = None
    
    def run(self):
        """Main game loop."""
        self.start_screen()
        
        running = True
        while running:
            self.clock.tick(self.fps)
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state.board.turn == self.state.player_color and not self.state.animating:
                        if self.handle_human_move(pygame.mouse.get_pos()):
                            # Check for checkmate after human move
                            if self.state.board.is_checkmate():
                                if self.show_checkmate_screen("Human"):
                                    # New game was requested (FIXED: Issue #6)
                                    self.start_screen()
                                else:
                                    running = False
                                continue
            
            # Update animation
            if self.state.animating:
                self.update_animation()
            
            # Handle bot move if it's bot's turn and not animating
            if not self.state.board.is_game_over() and not self.state.animating:
                self.handle_bot_move()
                
                # Check for checkmate after bot move
                if self.state.board.is_checkmate() and not self.state.animating:
                    if self.show_checkmate_screen("AI"):
                        # New game was requested (FIXED: Issue #6)
                        self.start_screen()
                    else:
                        running = False
            
            # Draw everything
            if self.draw():  # Returns True if draw screen should be shown
                if self.show_draw_screen("Endgame rule triggered"):
                    self.start_screen()
                else:
                    running = False
            
            pygame.display.update()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = ChessGUI()
    game.run()