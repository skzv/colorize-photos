import sys
import requests
import os
import shutil
from pathlib import Path

# This script colorizes all the photos in the specified directory, using the deepAI colorizer machine learned API.
#
# To use, you must set the DL_API_KEY env variable to your deepAI API key.
#
# Example usage (on UNIX):
# `export DL_API_KEY=<your-deep-ai-key> \ python3 main.py /path/to/images`

home = str(Path.home())
api_key = os.environ.get('DL_API_KEY')


# Returns the directory passed to script as a string
def get_directory():

    if len(sys.argv) != 2:
        raise ValueError('Please provide one directory as an argument.')

    # argv[0] is the script name, argv[1] is the first argument
    image_dir = sys.argv[1]

    # replace `~` with the path of the user's home directory to get the full path if necessary
    image_dir = image_dir.replace('~', home)

    print(f'Directory: {image_dir}')

    return image_dir


# Returns the URL of the colorized photo. Takes in a path to a local file.
def colorize_photo_local(path_to_file):

    r = requests.post(
        "https://api.deepai.org/api/colorizer",
        files={
            'image': open(path_to_file, 'rb'),
        },
        headers={'api-key': api_key}
    )

    return parse_request(r)


# Returns the URL of the colorized photo. Takes in a URL to a black and white photo.
def colorize_photo_url(url):
    r = requests.post(
        "https://api.deepai.org/api/colorizer",
        data={
            'image': url,
        },
        headers={'api-key': api_key}
    )

    return parse_request(r)


# Returns the URL of the colorized photo from the returned request.
def parse_request(r):
    # Check that the image was colorized successfully
    if r.status_code != 200:
        raise Exception(f'Couldnt colorize photo! Status: {r.status_code} Json: {r.json()}')

    print('Successfully colorized.')
    return r.json()['output_url']


# Downloads a photo from the specified URL. Saves it to the specified filepath.
def download_photo_from_url(url, output_filepath):
    r = requests.get(url, stream=True)

    # Check if the image was retrieved successfully
    if r.status_code == 200:
        # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
        r.raw.decode_content = True

        # Open a local file with wb ( write binary ) permission.
        with open(output_filepath, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

        print('Image sucessfully Downloaded: ', output_filepath)
    else:
        raise Exception('Image Couldn\'t be retreived')


#  Indicates whether the filename is an image based on its extension.
def has_image_extension(filename):
    return filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.tiff', '.bmp', '.gif'))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Get the input directory argument
    input_dir = get_directory()

    # Construct the output directory
    output_dir = f'{input_dir}-colorized'
    print(f'Outputting results to {output_dir}')

    if os.path.exists(output_dir) and not os.path.isdir(output_dir):
        raise Exception(f'Output path {output_dir} exists, and it is not a directory!')

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
        print(f'Created output dir {output_dir}')

    # Loop over all files in the input directory
    i = 0
    for root, directories, files in os.walk(input_dir):
        num_files = len(files)

        for name in files:
            if has_image_extension(name):
                # Construct the full path to the image to colorize
                input_file = os.path.join(root, name)
                print(f'Processing {input_file} {i}/{num_files} : {i/num_files * 100:.2f}%')

                # Construct the full path to where the colorized image will be downloaded
                output_to = f'{output_dir}/{name.split(".")[0]}.jpg'
                print(f'Output to {output_to}')

                # Check if the colorized image path exists. If it does, we've already colorized this image. So we
                # skip it.
                if os.path.exists(output_to):
                    print('File already exists. Skipping...')
                    i = i + 1
                    continue

                try:
                    output_url = colorize_photo_local(input_file)
                    download_photo_from_url(output_url, output_to)
                except Exception as err:
                    print('Error!', err)
                    print('Skipping file...')

            i = i + 1
