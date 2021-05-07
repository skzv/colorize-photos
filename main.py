import sys
import requests
import os
import shutil
from pathlib import Path


home = str(Path.home())
api_key = os.environ.get('DL_API_KEY')

def get_directory():

    if len(sys.argv) != 2:
        raise ValueError('Please provide one directory as an argument.')

    image_dir = sys.argv[1]

    image_dir = image_dir.replace('~', home)

    print(f'Directory: {image_dir}')
    return image_dir


def colorize_photo_local(path_to_file):

    r = requests.post(
        "https://api.deepai.org/api/colorizer",
        files={
            'image': open(path_to_file, 'rb'),
        },
        headers={'api-key': api_key}
    )

    return parse_request(r)


def colorize_photo_url(url):
    r = requests.post(
        "https://api.deepai.org/api/colorizer",
        data={
            'image': url,
        },
        headers={'api-key': api_key}
    )

    return parse_request(r)


def parse_request(r):
    # print(r)
    # print(r.status_code)
    # print(r.json())
    if r.status_code != 200:
        raise Exception(f'Couldnt colorize photo! Status: {r.status_code} Json: {r.json()}')

    print('Successfully colorized.')
    return r.json()['output_url']


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
        print('Image Couldn\'t be retreived')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    input_dir = get_directory()
    output_dir = f'{input_dir}-colorized'
    print(f'Outputting results to {output_dir}')

    if os.path.exists(output_dir) and not os.path.isdir(output_dir):
        raise Exception(f'Output path {output_dir} exists, and it is not a directory!')

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
        print(f'Created output dir {output_dir}')

    i = 0
    for root, directories, files in os.walk(input_dir):
        num_files = len(files)

        for name in files:
            if name.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.tiff', '.bmp', '.gif')):
                input_file = os.path.join(root, name)
                print(f'Processing {input_file} {i}/{num_files} : {i/num_files * 100}%')
                output_to = f'{output_dir}/{name}'
                print(f'Output to {output_to}')

                try:
                    output_url = colorize_photo_local(input_file)
                    download_photo_from_url(output_url, output_to)
                except Exception as err:
                    print('Error!', err)
                    print('Skipping file...')

                i = i + 1
