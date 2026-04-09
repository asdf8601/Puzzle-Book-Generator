"""
Sudoku Generator Module

This module provides functionality to generate Sudoku puzzles and solutions
with various difficulty levels and save them as images and text files.
"""

import random
import os
import copy
from typing import List, Tuple, Optional, Dict
from PIL import Image, ImageDraw, ImageFont


class SudokuGenerator:
    """A class for generating Sudoku puzzles with configurable difficulty levels."""
    
    def __init__(self):
        """Initialize the Sudoku generator."""
        self.grid = [[0 for _ in range(9)] for _ in range(9)]
        
    def is_valid(self, grid: List[List[int]], row: int, col: int, num: int) -> bool:
        """
        Check if placing num at (row, col) is valid according to Sudoku rules.
        
        Args:
            grid: The current Sudoku grid
            row: Row index (0-8)
            col: Column index (0-8) 
            num: Number to place (1-9)
            
        Returns:
            True if the placement is valid, False otherwise
        """
        # Check row
        for x in range(9):
            if grid[row][x] == num:
                return False
        
        # Check column
        for x in range(9):
            if grid[x][col] == num:
                return False
        
        # Check 3x3 box
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if grid[i + start_row][j + start_col] == num:
                    return False
        
        return True
    
    def solve_sudoku(self, grid: List[List[int]]) -> bool:
        """
        Solve sudoku using backtracking algorithm.
        
        Args:
            grid: The Sudoku grid to solve
            
        Returns:
            True if solution found, False otherwise
        """
        for i in range(9):
            for j in range(9):
                if grid[i][j] == 0:
                    numbers = list(range(1, 10))
                    random.shuffle(numbers)
                    for num in numbers:
                        if self.is_valid(grid, i, j, num):
                            grid[i][j] = num
                            if self.solve_sudoku(grid):
                                return True
                            grid[i][j] = 0
                    return False
        return True
    
    def generate_complete_grid(self) -> List[List[int]]:
        """
        Generate a complete valid Sudoku grid.
        
        Returns:
            A 9x9 grid with a valid Sudoku solution
        """
        self.grid = [[0 for _ in range(9)] for _ in range(9)]
        self.solve_sudoku(self.grid)
        return copy.deepcopy(self.grid)
    
    def remove_numbers(self, grid: List[List[int]], difficulty: int, total_puzzles: int = 160, levels: Optional[List[str]] = None) -> List[List[int]]:
        """
        Remove numbers from complete grid based on difficulty level.

        Args:
            grid: Complete Sudoku solution
            difficulty: Difficulty level (1-total_puzzles)
            total_puzzles: Total number of puzzles to generate
            levels: List of difficulty level names to use

        Returns:
            Puzzle grid with appropriate numbers removed
        """
        # Calculate difficulty ranges based on total puzzles
        ranges = self.get_difficulty_ranges(total_puzzles, levels)
        
        # Determine which difficulty level this puzzle belongs to
        difficulty_level = self._get_difficulty_level(difficulty, ranges)
        
        # Set clue counts based on difficulty level
        clue_ranges = {
            "Very Easy": (45, 50),  # remove 31-36 numbers
            "Easy": (40, 45),       # remove 36-41 numbers
            "Medium": (32, 40),     # remove 41-49 numbers
            "Hard": (28, 32),       # remove 49-53 numbers
            "Expert": (22, 28)      # remove 53-59 numbers
        }
        
        min_clues, max_clues = clue_ranges[difficulty_level]
        target_clues = random.randint(min_clues, max_clues)
        remove_count = 81 - target_clues
        
        puzzle = copy.deepcopy(grid)
        positions = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(positions)
        
        # Remove numbers randomly (simplified approach for performance)
        for i in range(remove_count):
            if i < len(positions):
                row, col = positions[i]
                puzzle[row][col] = 0
        
        return puzzle

    def get_difficulty_ranges(self, total_puzzles: int, levels: Optional[List[str]] = None) -> Dict[str, Tuple[int, int]]:
        """
        Calculate difficulty ranges based on total number of puzzles.

        Args:
            total_puzzles: Total number of puzzles
            levels: List of difficulty level names to use

        Returns:
            Dictionary mapping difficulty names to (start, end) ranges
        """
        # Distribute puzzles across difficulty levels
        if levels is None:
            levels = ["Medium", "Hard", "Expert"]
        puzzles_per_level = total_puzzles // len(levels)
        remainder = total_puzzles % len(levels)
        
        ranges = {}
        current = 1
        
        for i, level in enumerate(levels):
            # Add extra puzzles to later levels if there's a remainder
            count = puzzles_per_level + (1 if i >= (len(levels) - remainder) else 0)
            ranges[level] = (current, current + count - 1)
            current += count
            
        return ranges
    
    def _get_difficulty_level(self, puzzle_num: int, ranges: Dict[str, Tuple[int, int]]) -> str:
        """
        Determine difficulty level for a given puzzle number.
        
        Args:
            puzzle_num: Puzzle number
            ranges: Difficulty ranges
            
        Returns:
            Difficulty level name
        """
        for level, (start, end) in ranges.items():
            if start <= puzzle_num <= end:
                return level
        return "Expert"  # fallback
    
    def generate_puzzle(self, difficulty: int, total_puzzles: int = 160, levels: Optional[List[str]] = None) -> Tuple[List[List[int]], List[List[int]]]:
        """
        Generate a complete puzzle and solution pair.

        Args:
            difficulty: Difficulty level (1-total_puzzles)
            total_puzzles: Total number of puzzles to generate
            levels: List of difficulty level names to use

        Returns:
            Tuple of (puzzle, solution) grids
        """
        solution = self.generate_complete_grid()
        puzzle = self.remove_numbers(solution, difficulty, total_puzzles, levels)
        return puzzle, solution

    def save_puzzle_text(self, puzzle: List[List[int]], solution: List[List[int]], 
                        filename: str) -> None:
        """
        Save sudoku puzzle and solution to text file.
        
        Args:
            puzzle: The puzzle grid
            solution: The solution grid
            filename: Output filename
        """
        with open(filename, 'w') as f:
            f.write("PUZZLE:\n")
            for row in puzzle:
                f.write(' '.join('.' if x == 0 else str(x) for x in row) + '\n')
            f.write("\nSOLUTION:\n")
            for row in solution:
                f.write(' '.join(str(x) for x in row) + '\n')

    def save_puzzle_image(self, puzzle: List[List[int]], filename: str, 
                         cell_size: int = 180) -> None:
        """
        Save sudoku puzzle as an image without labels.
        
        Args:
            puzzle: The puzzle grid
            filename: Output filename
            cell_size: Size of each cell in pixels
        """
        margin = 20
        grid_size = 9 * cell_size
        total_width = grid_size + 2 * margin
        total_height = grid_size + 2 * margin
        
        # Create image
        img = Image.new('RGB', (total_width, total_height), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        try:
            import os
            # Try to find a good TrueType font
            font_paths = [
                "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf",
                "C:\\Windows\\Fonts\\arialbd.ttf",
                "arialbd.ttf"
            ]
            bold_font = None
            for p in font_paths:
                if os.path.exists(p) or p == "arialbd.ttf":
                    try:
                        bold_font = ImageFont.truetype(p, int(cell_size * 0.65))
                        break
                    except:
                        pass
            if bold_font is None:
                bold_font = ImageFont.load_default()
        except:
            # Fallback to default font
            bold_font = ImageFont.load_default()
        
        # Draw grid lines
        for i in range(10):
            line_width = 5 if i % 3 == 0 else 2
            # Vertical lines
            x = margin + i * cell_size
            draw.line([(x, margin), (x, margin + grid_size)], 
                     fill=(0, 0, 0), width=line_width)
            # Horizontal lines
            y = margin + i * cell_size
            draw.line([(margin, y), (margin + grid_size, y)], 
                     fill=(0, 0, 0), width=line_width)
        
        # Fill numbers
        for i in range(9):
            for j in range(9):
                if puzzle[i][j] != 0:
                    x = margin + j * cell_size + cell_size // 2
                    y = margin + i * cell_size + cell_size // 2
                    
                    # Center the text
                    text = str(puzzle[i][j])
                    bbox = draw.textbbox((0, 0), text, font=bold_font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    
                    draw.text((x - text_width // 2, y - text_height // 2), 
                             text, fill=(0, 0, 0), font=bold_font)
        
        img.save(filename)

    def save_solution_image(self, solution: List[List[int]], puzzle: List[List[int]], 
                           filename: str, cell_size: int = 180) -> None:
        """
        Save sudoku solution as an image with given numbers in black and solved numbers in blue.
        
        Args:
            solution: The complete solution grid
            puzzle: The original puzzle grid
            filename: Output filename
            cell_size: Size of each cell in pixels
        """
        margin = 20
        grid_size = 9 * cell_size
        total_width = grid_size + 2 * margin
        total_height = grid_size + 2 * margin
        
        # Create image
        img = Image.new('RGB', (total_width, total_height), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        try:
            import os
            font_paths_reg = [
                "/System/Library/Fonts/Supplemental/Arial.ttf",
                "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf",
                "C:\\Windows\\Fonts\\arial.ttf",
                "arial.ttf"
            ]
            font_paths_bold = [
                "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf",
                "C:\\Windows\\Fonts\\arialbd.ttf",
                "arialbd.ttf"
            ]
            
            font = None
            for p in font_paths_reg:
                if os.path.exists(p) or p == "arial.ttf":
                    try:
                        font = ImageFont.truetype(p, int(cell_size * 0.65))
                        break
                    except:
                        pass
                        
            bold_font = None
            for p in font_paths_bold:
                if os.path.exists(p) or p == "arialbd.ttf":
                    try:
                        bold_font = ImageFont.truetype(p, int(cell_size * 0.65))
                        break
                    except:
                        pass
                        
            if font is None:
                font = ImageFont.load_default()
            if bold_font is None:
                bold_font = font
        except:
            # Fallback to default font
            font = ImageFont.load_default()
            bold_font = font
        
        # Draw grid lines
        for i in range(10):
            line_width = 5 if i % 3 == 0 else 2
            # Vertical lines
            x = margin + i * cell_size
            draw.line([(x, margin), (x, margin + grid_size)], 
                     fill=(0, 0, 0), width=line_width)
            # Horizontal lines
            y = margin + i * cell_size
            draw.line([(margin, y), (margin + grid_size, y)], 
                     fill=(0, 0, 0), width=line_width)
        
        # Fill numbers with different colors based on whether they were given or solved
        for i in range(9):
            for j in range(9):
                if solution[i][j] != 0:
                    x = margin + j * cell_size + cell_size // 2
                    y = margin + i * cell_size + cell_size // 2
                    
                    # Determine color based on whether this was a given clue or solved number
                    if puzzle[i][j] != 0:
                        # This was a given clue - use black and bold font
                        color = (0, 0, 0)
                        current_font = bold_font
                    else:
                        # This was solved by the player - use blue and regular font
                        color = (0, 0, 255)
                        current_font = font
                    
                    # Center the text
                    text = str(solution[i][j])
                    bbox = draw.textbbox((0, 0), text, font=current_font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    
                    draw.text((x - text_width // 2, y - text_height // 2), 
                             text, fill=color, font=current_font)
        
        img.save(filename)

    def get_difficulty_name(self, level: int, total_puzzles: int = 160, levels: Optional[List[str]] = None) -> str:
        """
        Get difficulty name based on level and total puzzles.

        Args:
            level: Puzzle number (1-total_puzzles)
            total_puzzles: Total number of puzzles
            levels: List of difficulty level names to use

        Returns:
            Difficulty level name
        """
        ranges = self.get_difficulty_ranges(total_puzzles, levels)
        return self._get_difficulty_level(level, ranges)