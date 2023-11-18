import os
import random
from PIL import Image
from fpdf import FPDF
import argparse

MARGIN = 5

def scale_image(image_file, cell_width, cell_height, margin=3):
    image = Image.open(image_file)
    width, height = image.size
    original_aspect_ratio = width / height

    if width >= height:
        image_width = cell_width - margin
        image_height = image_width / original_aspect_ratio
    else:
        image_height = cell_height - margin
        image_width = image_height * original_aspect_ratio

    x_offset = (cell_width - image_width) // 2
    y_offset = (cell_height - image_height) // 2

    return image_width, image_height, x_offset, y_offset

def generate_bingo_card(image_files, output_file, card_size, n_pages=30):
    # Create a new PDF doc
    pdf = FPDF()

    for page in range(n_pages):
        add_bingo_page(card_size, image_files, pdf)

    # Save the PDF document
    pdf.output(output_file)


def add_bingo_page(card_size, image_files, pdf):
    # Add a page with 6 puzzles to the PDF. First find the locations of the top left corner of each puzzle:
    # Add a page to the PDF
    pdf.add_page()
    # Set the line width and color for table borders
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(1)

    # page_width, page_height = pdf.get_page_width(), pdf.get_page_height()
    page_width = 210  # Default page width in millimeters.
    page_height = 297  # Default page height in millimeters.

    # Create the start offsets for each table - we have MARGIN on the top and bottom, and also between tables.
    # So we want the overall height to be divided between 3 tables and 4 MARGINs.
    # Tables are square, so height is equal to width
    table_height = (page_height - 3*MARGIN) // 3
    table_width = table_height

    # Calculate image width and height based on card size
    image_width = int((table_width - MARGIN) / card_size)
    image_height = image_width

    for n_row in range(3):
        table_top_left_y = (MARGIN + table_height) * n_row + MARGIN
        for n_col in range(2):
            table_top_left_x = (MARGIN + table_width) * n_col + MARGIN

            # Shuffle the image files list
            random.shuffle(image_files)
            add_bingo_table(pdf, card_size, image_files, image_width, image_height, table_top_left_x, table_top_left_y)


def add_bingo_table(pdf, card_size, image_files, image_width, image_height, x_start, y_start):
    # Iterate through each cell of the bingo card
    for row in range(card_size):
        for col in range(card_size):
            # Get the image file for the current cell
            image_file = image_files[row * card_size + col]

            w, h, x_offset, y_offset = scale_image(image_file, image_width, image_height)

            # Insert the image into the PDF document
            x = col * image_width + x_start
            y = row * image_height + y_start
            pdf.image(image_file, x + x_offset, y + y_offset, w, h)

    # Draw table borders
    for row in range(card_size + 1):
        pdf.line(x_start, y_start + row * image_height, x_start + card_size * image_width,
                 y_start + row * image_height)
    for col in range(card_size + 1):
        pdf.line(x_start + col * image_width, y_start, x_start + col * image_width,
                 y_start + card_size * image_height)


if __name__ == "__main__":
    # Add command line arguments with argparse: -n for grid size, -d for directory with images, -o for output file:
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--grid_size", type=int, default=4, help="Grid size (n x n)")
    parser.add_argument("-d", "--directory", type=str, help="Directory with images")
    parser.add_argument("-p", "--pages", type=int, default=5, help="Number of pages")
    parser.add_argument("-o", "--output_file", type=str, default="bingo.pdf", help="Output file name")
    args = parser.parse_args()

    # Get the list of image files - list files in args,directory:
    image_files = [os.path.join(args.directory, file) for file in os.listdir(args.directory) if file.lower().endswith(".png")]

    # Get the output file name
    output_file = args.output_file

    # Generate the bingo card
    generate_bingo_card(image_files, output_file, args.grid_size, args.pages)
