"""
Sudoku Book PDF Generator

This module provides functionality to create professional PDF books
containing Sudoku puzzles with proper formatting and organization.
"""

import os
from typing import List, Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from PIL import Image
import uuid


class SudokuBookPDF:
    """A class for creating professional Sudoku puzzle books in PDF format."""
    
    def __init__(self, output_filename: str = "Complete_Sudoku_Puzzle_Book.pdf", 
                 book_title: str = "Sudoku Journey", 
                 book_subtitle: str = "Brain-Busting Challenges to Sharpen Your Logic",
                 total_puzzles: int = 160):
        """
        Initialize the Sudoku book PDF generator.
        
        Args:
            output_filename: Name of the output PDF file
            book_title: Main title of the book
            book_subtitle: Subtitle of the book
            total_puzzles: Total number of puzzles in the book
        """
        self.output_filename = output_filename
        self.book_title = book_title
        self.book_subtitle = book_subtitle
        self.total_puzzles = total_puzzles
        self.page_width, self.page_height = 8.5 * inch, 11 * inch
        self.bleed = 0.125 * inch
        self.content_width = self.page_width - 2 * self.bleed
        self.content_height = self.page_height - 2 * self.bleed
        self.page_count = 1
        
    def get_difficulty_info(self) -> List[Dict[str, Any]]:
        """
        Get information about difficulty levels based on total puzzles.
        
        Returns:
            List of dictionaries containing difficulty information
        """
        levels = ["Medium", "Hard", "Expert"]
        puzzles_per_level = self.total_puzzles // len(levels)
        remainder = self.total_puzzles % len(levels)
        
        difficulty_info = []
        current = 1
        
        for i, level in enumerate(levels):
            # Add extra puzzles to later levels if there's a remainder
            count = puzzles_per_level + (1 if i >= (len(levels) - remainder) else 0)
            end = current + count - 1
            
            difficulty_info.append({
                "name": level,
                "range": f"{current}-{end}",
                "start": current,
                "end": end
            })
            current += count
            
        return difficulty_info
    
    def add_image(self, c: canvas.Canvas, img_path: str, x: float, y: float, 
                  w: float, h: float) -> None:
        """
        Add an image to the PDF canvas.
        
        Args:
            c: ReportLab canvas object
            img_path: Path to the image file
            x, y: Position coordinates
            w, h: Width and height dimensions
        """
        if not os.path.exists(img_path):
            print(f"Warning: Image not found: {img_path}")
            return
            
        img = Image.open(img_path)
        img = img.convert('RGB')
        img = img.resize((int(w), int(h)), Image.LANCZOS)
        temp_path = f'temp_img_{uuid.uuid4().hex}.jpg'
        img.save(temp_path)
        img.close()
        c.drawImage(temp_path, x, y, width=w, height=h)
        os.remove(temp_path)
    
    def add_page_number(self, c: canvas.Canvas, page_num: int) -> None:
        """
        Add page number at the bottom of the page.
        
        Args:
            c: ReportLab canvas object
            page_num: Page number to display
        """
        c.setFont('Helvetica', 10)
        c.drawCentredString(self.page_width / 2, 0.5 * inch, str(page_num))
    
    def create_title_page(self, c: canvas.Canvas) -> None:
        """Create the title page of the book."""
        c.setFont('Helvetica-Bold', 28)
        c.drawCentredString(self.page_width / 2, self.page_height / 2 + 80, 
                           self.book_title)
        c.setFont('Helvetica-Bold', 22)
        c.drawCentredString(self.page_width / 2, self.page_height / 2 + 40, 
                           self.book_subtitle)
        c.setFont('Helvetica', 18)
        c.drawCentredString(self.page_width / 2, self.page_height / 2, 
                           f'{self.total_puzzles} Puzzles - All Difficulty Levels')
        c.setFont('Helvetica', 16)
        c.drawCentredString(self.page_width / 2, self.page_height / 2 - 40, 
                           'By Smart Book Maker')
        
        # Footer
        c.setFont('Helvetica', 10)
        footer = ('Copyright © 2025 Smart Book Maker Contributors\\n'
                 'All rights reserved. No part of this book may be reproduced without permission.\\n\\n'
                 'Published by Smart Book Maker\\n'
                 'Open Source Project on GitHub')
        footer_offset = 0.25 * inch
        for i, line in enumerate(footer.split('\\n')):
            c.drawCentredString(self.page_width / 2, 0.7 * inch + footer_offset - i * 12, line)
        
        c.showPage()
        self.page_count += 1
    
    def create_table_of_contents(self, c: canvas.Canvas) -> None:
        """Create the table of contents page."""
        c.setFont('Helvetica-Bold', 24)
        c.drawCentredString(self.page_width / 2, self.page_height - 1.5 * inch, 
                           'Table of Contents')
        
        difficulty_info = self.get_difficulty_info()
        
        # Calculate page numbers for each section
        current_page = 4  # After title, TOC, and how-to-play pages
        toc_entries = []
        
        for diff in difficulty_info:
            puzzle_count = diff['end'] - diff['start'] + 1
            section_start = current_page
            toc_entries.append({
                'name': diff['name'],
                'range': diff['range'],
                'page': section_start
            })
            current_page += 1 + puzzle_count  # +1 for divider page
        
        # Solutions section
        solutions_start = current_page
        toc_entries.append({
            'name': 'Solutions',
            'range': 'All Levels',
            'page': solutions_start
        })
        
        # Draw TOC entries
        c.setFont('Helvetica', 14)
        start_y = self.page_height - 2.5 * inch
        
        # Instructions entry
        c.drawString(self.bleed + 0.5 * inch, start_y, 'How to Play Sudoku')
        c.drawString(self.page_width - self.bleed - 1 * inch, start_y, '3')
        start_y -= 0.3 * inch
        
        c.drawString(self.bleed + 0.5 * inch, start_y, '')
        start_y -= 0.3 * inch
        
        c.setFont('Helvetica-Bold', 16)
        c.drawString(self.bleed + 0.5 * inch, start_y, 'Puzzles by Difficulty:')
        start_y -= 0.4 * inch
        
        c.setFont('Helvetica', 14)
        for entry in toc_entries:
            if entry['name'] == 'Solutions':
                start_y -= 0.2 * inch
                c.setFont('Helvetica-Bold', 16)
                c.drawString(self.bleed + 0.5 * inch, start_y, 
                           f"{entry['name']} ({entry['range']})")
                c.drawString(self.page_width - self.bleed - 1 * inch, start_y, 
                           str(entry['page']))
            else:
                c.drawString(self.bleed + 0.8 * inch, start_y, 
                           f"{entry['name']} - Puzzles {entry['range']}")
                c.drawString(self.page_width - self.bleed - 1 * inch, start_y, 
                           str(entry['page']))
            start_y -= 0.3 * inch
        
        self.add_page_number(c, self.page_count)
        c.showPage()
        self.page_count += 1
    
    def create_instructions_page(self, c: canvas.Canvas) -> None:
        """Create the how-to-play instructions page."""
        c.setFont('Helvetica-Bold', 22)
        c.drawCentredString(self.page_width / 2, self.page_height - 1.5 * inch, 
                           'How to Play Sudoku')
        
        c.setFont('Helvetica', 14)
        instructions = [
            'The goal is to fill the 9×9 grid with digits 1-9, following these rules:',
            '',
            '• Each row must contain all digits from 1 to 9 (no repeats)',
            '• Each column must contain all digits from 1 to 9 (no repeats)',
            '• Each 3×3 box must contain all digits from 1 to 9 (no repeats)',
            '',
            'Some numbers are already given as clues to get you started.',
            '',
            'Difficulty Levels:',
            '• Medium: Test your skills',
            '• Hard: Challenge yourself',
            '• Expert: Master level puzzles',
            '',
            'Tips:',
            '• Start with rows, columns, or boxes with the most given numbers',
            '• Look for numbers that can only go in one place',
            '• Use pencil marks to track possibilities',
            '• Check the solutions section at the back if you get stuck',
            '',
            'Good luck and have fun solving!'
        ]
        
        start_y = self.page_height - 2 * inch
        for i, line in enumerate(instructions):
            if line.startswith('•'):
                c.drawString(self.bleed + 0.5 * inch, start_y - i * 18, line)
            else:
                c.drawCentredString(self.page_width / 2, start_y - i * 18, line)
        
        self.add_page_number(c, self.page_count)
        c.showPage()
        self.page_count += 1
    
    def create_puzzle_pages(self, c: canvas.Canvas, puzzle_dir: str = "output/puzzles") -> None:
        """
        Create pages for all puzzles organized by difficulty.
        
        Args:
            c: ReportLab canvas object
            puzzle_dir: Directory containing puzzle images
        """
        if not os.path.exists(puzzle_dir):
            print(f"Error: {puzzle_dir} directory not found. Please generate puzzles first.")
            return
        
        difficulty_info = self.get_difficulty_info()
        
        for diff in difficulty_info:
            # Add difficulty divider page
            c.setFont('Helvetica-Bold', 32)
            c.drawCentredString(self.page_width / 2, self.page_height / 2 + 40, 
                               diff['name'])
            c.setFont('Helvetica-Bold', 20)
            c.drawCentredString(self.page_width / 2, self.page_height / 2, 
                               f"Puzzles {diff['range']}")
            c.setFont('Helvetica', 16)
            puzzle_count = diff['end'] - diff['start'] + 1
            c.drawCentredString(self.page_width / 2, self.page_height / 2 - 40, 
                               f"{puzzle_count} Puzzles")
            
            self.add_page_number(c, self.page_count)
            c.showPage()
            self.page_count += 1
            
            # Add puzzles for this difficulty
            for puzzle_num in range(diff['start'], diff['end'] + 1):
                diff_name_file = diff['name'].replace(" ", "_").lower()
                puzzle_file = f'puzzle_{puzzle_num:03d}_{diff_name_file}.png'
                puzzle_path = os.path.join(puzzle_dir, puzzle_file)
                
                if os.path.exists(puzzle_path):
                    # Title
                    c.setFont('Helvetica-Bold', 18)
                    title_y = self.page_height - 0.8 * inch
                    c.drawCentredString(self.page_width / 2, title_y, f'Puzzle {puzzle_num}')
                    
                    # Puzzle image - centered on page
                    img_size = 6 * inch
                    img_x = (self.page_width - img_size) / 2
                    img_y = (self.page_height - img_size) / 2 - 0.2 * inch
                    
                    self.add_image(c, puzzle_path, img_x, img_y, img_size, img_size)
                    
                    self.add_page_number(c, self.page_count)
                    c.showPage()
                    self.page_count += 1
                    print(f'Added puzzle {puzzle_num} to PDF')
                else:
                    print(f'Warning: Puzzle file not found: {puzzle_path}')
    
    def create_solution_pages(self, c: canvas.Canvas, solution_dir: str = "output/solutions") -> None:
        """
        Create pages for all solutions.
        
        Args:
            c: ReportLab canvas object
            solution_dir: Directory containing solution images
        """
        # Solutions section divider
        c.setFont('Helvetica-Bold', 32)
        c.drawCentredString(self.page_width / 2, self.page_height / 2 + 40, 'Solutions')
        c.setFont('Helvetica', 18)
        c.drawCentredString(self.page_width / 2, self.page_height / 2, 'All Puzzle Solutions')
        c.setFont('Helvetica', 14)
        c.drawCentredString(self.page_width / 2, self.page_height / 2 - 40, 
                           'Organized by Puzzle Number')
        
        self.add_page_number(c, self.page_count)
        c.showPage()
        self.page_count += 1
        
        if not os.path.exists(solution_dir):
            print(f"Error: {solution_dir} directory not found. Please generate solutions first.")
            return
        
        difficulty_info = self.get_difficulty_info()
        
        for diff in difficulty_info:
            for puzzle_num in range(diff['start'], diff['end'] + 1):
                diff_name_file = diff['name'].replace(" ", "_").lower()
                solution_file = f'solution_{puzzle_num:03d}_{diff_name_file}.png'
                solution_path = os.path.join(solution_dir, solution_file)
                
                if os.path.exists(solution_path):
                    # Title
                    c.setFont('Helvetica-Bold', 18)
                    title_y = self.page_height - 0.8 * inch
                    c.drawCentredString(self.page_width / 2, title_y, f'Solution {puzzle_num}')
                    
                    # Solution image - centered on page
                    img_size = 6 * inch
                    img_x = (self.page_width - img_size) / 2
                    img_y = (self.page_height - img_size) / 2 - 0.2 * inch
                    
                    self.add_image(c, solution_path, img_x, img_y, img_size, img_size)
                    
                    self.add_page_number(c, self.page_count)
                    c.showPage()
                    self.page_count += 1
                    print(f'Added solution {puzzle_num} to PDF')
                else:
                    print(f'Warning: Solution file not found: {solution_path}')
    
    def create_closing_page(self, c: canvas.Canvas) -> None:
        """Create the closing thank you page."""
        c.setFont('Helvetica-Bold', 20)
        c.drawCentredString(self.page_width / 2, self.page_height - 2 * inch, 
                           'Thank You for Solving!')
        
        c.setFont('Helvetica', 12)
        closing_messages = [
            '',
            'Congratulations on completing these Sudoku puzzles!',
            'We hope you enjoyed the mental challenge and had fun along the way.',
            '',
            'If you enjoyed these puzzles, please consider giving us a star on GitHub —',
            'it really helps support this open source project!',
            '',
            'Share your puzzle-solving achievements with the community!',
            'Visit us at github.com/TheUnknown550/Smart-Book-Maker',
            '',
            'Keep challenging your mind and happy puzzling!',
            '',
            '— The Smart Book Maker Contributors'
        ]
        
        start_y = self.page_height - 3 * inch
        for i, line in enumerate(closing_messages):
            if line == '— The Smart Book Maker Contributors':
                c.setFont('Helvetica', 11)
            c.drawCentredString(self.page_width / 2, start_y - i * 20, line)
        
        # Add decorative border
        border_margin = 1 * inch
        c.setStrokeGray(0.7)
        c.setLineWidth(2)
        c.rect(border_margin, border_margin,
               self.page_width - 2 * border_margin, self.page_height - 2 * border_margin)
        
        self.add_page_number(c, self.page_count)
        c.showPage()
        self.page_count += 1
    
    def create_book(self, puzzle_dir: str = "output/puzzles", 
                   solution_dir: str = "output/solutions") -> None:
        """
        Create the complete Sudoku puzzle book PDF.
        
        Args:
            puzzle_dir: Directory containing puzzle images
            solution_dir: Directory containing solution images
        """
        c = canvas.Canvas(self.output_filename, pagesize=(self.page_width, self.page_height))
        
        # Create all sections
        self.create_title_page(c)
        self.create_table_of_contents(c)
        self.create_instructions_page(c)
        self.create_puzzle_pages(c, puzzle_dir)
        self.create_solution_pages(c, solution_dir)
        self.create_closing_page(c)
        
        c.save()
        print(f'Complete Sudoku Puzzle Book PDF created successfully with {self.page_count} pages!')
        print(f'Saved as: {self.output_filename}')