#!/usr/bin/env python3
"""
Chess Game - Single File Entry Point
Combines Chess_Bot.py and Chess_GUI.py functionality
Run: python app.py
"""

import sys
import os

# Add current directory to path to ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main entry point for the chess game."""
    try:
        # Try to import the GUI module
        from Chess_GUI import ChessGUI
        
        print("=" * 50)
        print("CHESS GAME")
        print("=" * 50)
        print("Starting the game...")
        print("White = HUMAN")
        print("Black = AI")
        print("=" * 50)
        
        # Create and run the game
        game = ChessGUI()
        game.run()
        
    except ImportError as e:
        print(f"Error: Could not import required modules. Make sure all files are in the same directory.")
        print(f"Details: {e}")
        print("\nRequired files in the same directory:")
        print("1. Chess_Game.py  - AI logic")
        print("2. Chess_GUI.py   - GUI interface")
        print("3. app.py         - This file (entry point)")
        print("\nDirectory structure should be:")
        print("chess_game/")
        print("├── app.py")
        print("├── Chess_Game.py")
        print("├── Chess_GUI.py")
        print("└── images/")
        print("    ├── background.jpg")
        print("    ├── pawn-w.png")
        print("    └── ... (other piece images)")
        
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()