# colorize-photos
Colorize all the photos in a directory

## About
Uses the [Image Colorization API](https://deepai.org/machine-learning-model/colorizer) from DeepAi to colorize all the images in a directory. Downloads the results to a neighbouring directory, with the suffix 'colorised' appended to the directory.

## How to use
```
export DL_API_KEY=<your-deep-ai-key>
python3 main.py /path/to/images
```
