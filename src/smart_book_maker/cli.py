"""
Command Line Interface for Smart Book Maker

This module provides a command-line interface for generating puzzle books.
"""

import argparse
import sys
import os
from pathlib import Path

# Add the src directory to the path so we can import our modules
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from smart_book_maker.generators.sudoku import SudokuGenerator
from smart_book_maker.generators.maze import MazeGenerator
from smart_book_maker.pdf.sudoku_book import SudokuBookPDF
from smart_book_maker.pdf.maze_book import MazeBookPDF
from smart_book_maker.utils.file_management import ensure_output_directories, get_sudoku_filenames, get_maze_filenames


def generate_sudoku_puzzles(count: int = 160, output_dir: str = "output", levels: list = None, include_solutions: bool = True) -> None:
    """
    Generate Sudoku puzzles and save them as text and image files.

    Args:
        count: Number of puzzles to generate
        output_dir: Output directory for files
        levels: List of difficulty level names to use
        include_solutions: Whether to generate solution images
    """
    print(f"Generating {count} Sudoku puzzles...")

    # Ensure output directories exist
    ensure_output_directories(output_dir)

    generator = SudokuGenerator()

    for i in range(1, count + 1):
        print(f'Generating Sudoku {i}/{count}...')

        # Generate puzzle and solution
        puzzle, solution = generator.generate_puzzle(i, count, levels)

        # Get difficulty name
        difficulty_name = generator.get_difficulty_name(i, count, levels)
        
        # Get filenames
        filenames = get_sudoku_filenames(i, difficulty_name, output_dir)
        
        # Save files
        generator.save_puzzle_text(puzzle, solution, filenames["text"])
        generator.save_puzzle_image(puzzle, filenames["puzzle"])
        if include_solutions:
            generator.save_solution_image(solution, puzzle, filenames["solution"])
        
        print(f'Generated puzzle {i} (Difficulty: {difficulty_name})')
    
    print(f"Successfully generated {count} Sudoku puzzles!")


def generate_maze_puzzles(count: int = 160, output_dir: str = "output") -> None:
    """
    Generate Maze puzzles and save them as text and image files.
    
    Args:
        count: Number of puzzles to generate
        output_dir: Output directory for files
    """
    print(f"Generating {count} Maze puzzles...")
    
    # Ensure output directories exist
    ensure_output_directories(output_dir)
    
    generator = MazeGenerator()
    
    for i in range(1, count + 1):
        print(f'Generating Maze {i}/{count}...')
        
        # Generate maze
        maze, width, height, cell_size = generator.generate_puzzle(i, count)
        
        # Get filenames
        filenames = get_maze_filenames(i, width, height, output_dir)
        
        # Save files
        generator.save_maze_text(maze, filenames["text"])
        generator.save_maze_image(maze, filenames["image"], cell_size)
        
        print(f'Generated maze {i} ({width}x{height}, cell_size={cell_size})')
    
    print(f"Successfully generated {count} Maze puzzles!")


def create_sudoku_book(output_dir: str = "output", filename: str = None,
                       book_title: str = None, book_subtitle: str = None,
                       total_puzzles: int = 160, levels: list = None,
                       include_solutions: bool = True) -> None:
    """
    Create a Sudoku puzzle book PDF.

    Args:
        output_dir: Directory containing puzzle and solution images
        filename: Output PDF filename
        book_title: Custom book title
        book_subtitle: Custom book subtitle
        total_puzzles: Total number of puzzles in the book
        levels: List of difficulty level names to use
        include_solutions: Whether to include solution pages in the book
    """
    if filename is None:
        filename = f"{output_dir}/books/Complete_Sudoku_Puzzle_Book.pdf"
    
    if book_title is None:
        book_title = "Sudoku Journey"
    
    if book_subtitle is None:
        book_subtitle = "Brain-Busting Challenges to Sharpen Your Logic"
    
    print(f"Creating Sudoku puzzle book PDF with {total_puzzles} puzzles...")
    
    # Ensure the books directory exists
    os.makedirs(f"{output_dir}/books", exist_ok=True)
    
    # Create the book
    book = SudokuBookPDF(filename, book_title, book_subtitle, total_puzzles,
                         levels=levels, include_solutions=include_solutions)
    book.create_book(f"{output_dir}/puzzles", f"{output_dir}/solutions")


def create_maze_book(output_dir: str = "output", filename: str = None) -> None:
    """
    Create a Maze puzzle book PDF.
    
    Args:
        output_dir: Directory containing maze images
        filename: Output PDF filename
    """
    if filename is None:
        filename = f"{output_dir}/books/Complete_Maze_Puzzle_Book.pdf"
    
    print("Creating Maze puzzle book PDF...")
    
    # Ensure the books directory exists
    os.makedirs(f"{output_dir}/books", exist_ok=True)
    
    # Create the book
    book = MazeBookPDF(filename)
    book.create_book(f"{output_dir}/mazes_png")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Smart Book Maker - Generate puzzle books",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s generate sudoku --count 160
  %(prog)s generate maze --count 100
  %(prog)s create sudoku-book --output-dir ./output
  %(prog)s create maze-book --output-dir ./output
  %(prog)s all sudoku --count 160 --output-dir ./my_puzzles
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate puzzles')
    generate_subparsers = generate_parser.add_subparsers(dest='puzzle_type', help='Puzzle type')
    
    # Generate Sudoku
    sudoku_gen_parser = generate_subparsers.add_parser('sudoku', help='Generate Sudoku puzzles')
    sudoku_gen_parser.add_argument('--count', type=int, default=160, help='Number of puzzles to generate')
    sudoku_gen_parser.add_argument('--output-dir', default='output', help='Output directory')
    sudoku_gen_parser.add_argument('--levels', default='Medium,Hard,Expert', help='Comma-separated difficulty levels (e.g. Easy,Medium,Hard,Expert)')
    sudoku_gen_parser.add_argument('--no-solutions', action='store_true', help='Omit solution images')
    
    # Generate Maze
    maze_gen_parser = generate_subparsers.add_parser('maze', help='Generate Maze puzzles')
    maze_gen_parser.add_argument('--count', type=int, default=160, help='Number of puzzles to generate')
    maze_gen_parser.add_argument('--output-dir', default='output', help='Output directory')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create puzzle books')
    create_subparsers = create_parser.add_subparsers(dest='book_type', help='Book type')
    
    # Create Sudoku book
    sudoku_book_parser = create_subparsers.add_parser('sudoku-book', help='Create Sudoku book PDF')
    sudoku_book_parser.add_argument('--output-dir', default='output', help='Directory containing puzzles')
    sudoku_book_parser.add_argument('--filename', help='Output PDF filename')
    sudoku_book_parser.add_argument('--title', help='Custom book title')
    sudoku_book_parser.add_argument('--subtitle', help='Custom book subtitle')
    sudoku_book_parser.add_argument('--total-puzzles', type=int, default=160, help='Total number of puzzles')
    sudoku_book_parser.add_argument('--levels', default='Medium,Hard,Expert', help='Comma-separated difficulty levels (e.g. Easy,Medium,Hard,Expert)')
    sudoku_book_parser.add_argument('--no-solutions', action='store_true', help='Omit solution pages from the book')
    
    # Create Maze book
    maze_book_parser = create_subparsers.add_parser('maze-book', help='Create Maze book PDF')
    maze_book_parser.add_argument('--output-dir', default='output', help='Directory containing mazes')
    maze_book_parser.add_argument('--filename', help='Output PDF filename')
    
    # All-in-one commands
    all_parser = subparsers.add_parser('all', help='Generate puzzles and create book')
    all_subparsers = all_parser.add_subparsers(dest='all_type', help='Type of complete workflow')
    
    # All Sudoku
    all_sudoku_parser = all_subparsers.add_parser('sudoku', help='Generate Sudoku puzzles and create book')
    all_sudoku_parser.add_argument('--count', type=int, default=160, help='Number of puzzles to generate')
    all_sudoku_parser.add_argument('--output-dir', default='output', help='Output directory')
    all_sudoku_parser.add_argument('--filename', help='Output PDF filename')
    all_sudoku_parser.add_argument('--title', help='Custom book title')
    all_sudoku_parser.add_argument('--subtitle', help='Custom book subtitle')
    all_sudoku_parser.add_argument('--levels', default='Medium,Hard,Expert', help='Comma-separated difficulty levels (e.g. Easy,Medium,Hard,Expert)')
    all_sudoku_parser.add_argument('--no-solutions', action='store_true', help='Omit solution pages from the book')
    
    # All Maze
    all_maze_parser = all_subparsers.add_parser('maze', help='Generate Maze puzzles and create book')
    all_maze_parser.add_argument('--count', type=int, default=160, help='Number of puzzles to generate')
    all_maze_parser.add_argument('--output-dir', default='output', help='Output directory')
    all_maze_parser.add_argument('--filename', help='Output PDF filename')
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    try:
        if args.command == 'generate':
            if args.puzzle_type == 'sudoku':
                levels = [l.strip() for l in args.levels.split(',')]
                generate_sudoku_puzzles(args.count, args.output_dir, levels,
                                       include_solutions=not args.no_solutions)
            elif args.puzzle_type == 'maze':
                generate_maze_puzzles(args.count, args.output_dir)
            else:
                generate_parser.print_help()
        
        elif args.command == 'create':
            if args.book_type == 'sudoku-book':
                levels = [l.strip() for l in args.levels.split(',')]
                create_sudoku_book(args.output_dir, args.filename,
                                 getattr(args, 'title', None),
                                 getattr(args, 'subtitle', None),
                                 getattr(args, 'total_puzzles', 160),
                                 levels=levels,
                                 include_solutions=not args.no_solutions)
            elif args.book_type == 'maze-book':
                create_maze_book(args.output_dir, args.filename)
            else:
                create_parser.print_help()
        
        elif args.command == 'all':
            if args.all_type == 'sudoku':
                levels = [l.strip() for l in args.levels.split(',')]
                generate_sudoku_puzzles(args.count, args.output_dir, levels,
                                       include_solutions=not args.no_solutions)
                create_sudoku_book(args.output_dir, args.filename,
                                 getattr(args, 'title', None),
                                 getattr(args, 'subtitle', None),
                                 args.count,
                                 levels=levels,
                                 include_solutions=not args.no_solutions)
            elif args.all_type == 'maze':
                generate_maze_puzzles(args.count, args.output_dir)
                create_maze_book(args.output_dir, args.filename)
            else:
                all_parser.print_help()
        
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()