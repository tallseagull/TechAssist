from PIL import Image
import os
import pandas as pd

# Scan the files in content/activities/images/*.jpg to identify the file sizes. We want to keep only the larger
# files, these are the flash cards. Then for each group (defined by page number in the file name) we build a PDF with
# the images to print as flashcards.

class FlashCards:
    def __init__(self, directory="content/activities/images/"):
        """
        Init the flash cards
        :param directory: The root for the flash cards - typically content/activities/images/
        """
        self.directory = directory
        self.files = None

    def scan_files(self):
        """
        Scan the files. Saves the result to a dataframe self.files. Has fields:
        * path - full path of the file
        * page - extracted from file name
        * is_fc - is it a flashcard? (inferred from the file name - flashcards seem to have _fc_ in the name)
        * activity - from the file name
        * is_th - is thumbnail?
        * img_name - from the file name (e.g. boy for file with _boy in the end)
        * height
        * width
        :return:
        """
        # Iterate over files in the directory
        res = []
        for filename in os.listdir(self.directory):
            if filename.endswith('.jpg') or filename.endswith('.jpeg'):
                file_path = os.path.join(self.directory, filename)
                # Get file size in bytes
                file_size = os.path.getsize(file_path)

                img_dict = {'path': file_path,
                            'file_size': file_size}

                # Open the image using PIL
                try:
                    with Image.open(file_path) as img:
                        # Get image dimensions (width x height)
                        image_width, image_height = img.size
                        img_dict['width'] = image_width
                        img_dict['height'] = image_height
                except Exception as e:
                    print(f"Error processing {filename}: {e}")

                # Now extract the parts from the file name:
                filename_base = filename.rsplit('.',1)[0]

                # Split the filename by _ (to its parts)
                # An example file name: jt1_pg8_fc_cat_th.jpg
                name_parts = filename_base.split('_')

                # We can ignore name_parts[0] - it is all jt1

                # name_parts[1] is the page number - e.g. pg8:
                if name_parts[1].startswith('pg'):
                    page_num = int(name_parts[1][2:])
                else:
                    print(f"Warning: Unrecognized name_parts[1]: {name_parts[1]}")
                    page_num = None

                # name_parts[2] can be 'fc' for flashcard, or an activity number if starts with 'act'
                if name_parts[2] == 'fc':
                    act_num = None
                    is_fc = True
                    # For a flashcard, the name is next and then there may be a 'th' for thumbnail:
                    if name_parts[-1]=='th':
                        img_name = " ".join(name_parts[3:-1]).title()
                    else:
                        img_name = " ".join(name_parts[3:]).title()
                elif name_parts[2].startswith('act'):
                    act_num = int(name_parts[2][3:])
                    is_fc = False
                    img_name = '_'.join(name_parts[3:])
                else:
                    print(f"Warning: Unrecognized name_parts[2]: {name_parts[2]} in file {filename}")
                    act_num = None
                    is_fc = False
                    img_name = None

                # Check if thumbnail and remove the _th ending:
                is_th = (name_parts[-1] == 'th')

                img_dict['is_th'] = is_th
                img_dict['is_fc'] = is_fc
                img_dict['page'] = page_num
                img_dict['activity'] = act_num
                img_dict['img_name'] = img_name
                res.append(img_dict)

        self.files = pd.DataFrame(res)


if __name__ == '__main__':
    fc = FlashCards('/Users/talsegalov/Downloads/Sarit/4610/content/activities/images')
    fc.scan_files()
    print(f"We found {fc.files.is_th.sum()} thumbnails!")
    print(f"Thumbnails are in {fc.files[fc.files.is_fc & (~fc.files.is_th)].page.nunique()} pages")
    print(fc.files[fc.files.is_fc & (~fc.files.is_th)])

