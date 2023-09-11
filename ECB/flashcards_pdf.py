import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Image, PageBreak, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import Spacer
from ECB.scan_cards import FlashCards


def create_pdf(images, titles, output_pdf):
    doc = SimpleDocTemplate(output_pdf, pagesize=A4)  # Set page size to A4
    story = []

    styles = getSampleStyleSheet()

    # Adjust title font size (you can change the value as needed)
    title_style = styles["Title"]
    title_style.fontName = 'Helvetica-Bold'
    title_style.fontSize = 26  # Increase font size

    for image_path, title in zip(images, titles):
        img = Image(image_path)
        img.width = int(A4[0] * 0.8)  # Set image width to match A4 page width
        img.height = int(A4[1] * 0.8)  # Set image height to match A4 page height

        # Add title as a Paragraph
        title_paragraph = Paragraph(title, title_style)
        story.extend([title_paragraph, Spacer(1, 12), img, Spacer(1, 12), PageBreak()])

    doc.build(story)

if __name__ == "__main__":
    #Scan for the flahcards and get a dataframe with the cards:
    add_titles = False
    names_by_page = []

    # Read the groups from the CSV:
    df = pd.read_csv('/Users/talsegalov/Downloads/Sarit/FlashCards/fc_content.csv')
    df['page'] = df.File.str.extract(r'page(.*?)_')

    fc = FlashCards('/Users/talsegalov/Downloads/Sarit/4610/content/activities/images')
    fc.scan_files()
    fc_df = fc.files[fc.files.is_fc & (~fc.files.is_th)]

    for grp in sorted(df.Save.unique()):
        # List of image files to include in the PDF
        fc_part = fc_df[fc_df.page.isin(df.page[df.Save==grp].unique().astype(int))].sort_values('page')
        image_files = fc_part.path

        # List of titles corresponding to each image
        if add_titles:
            titles = fc_part.img_name
        else:
            titles = [''] * len(image_files)

        # Output PDF file name
        output_pdf = f'/Users/talsegalov/Downloads/Sarit/FlashCards/fc_unit_{grp}.pdf'

        names_by_page.append({'File': output_pdf.rsplit('/',1)[1],
                              'Names': ",".join(fc_part.img_name)})

        create_pdf(image_files, titles, output_pdf)
        print(f'PDF created: {output_pdf}')
    df = pd.DataFrame(names_by_page)
    df.to_csv('/Users/talsegalov/Downloads/Sarit/FlashCards/fc_content2.csv', index=False)
