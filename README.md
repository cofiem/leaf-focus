# leaf-focus

Extract text from pdf files.

Some steps use [Tensorflow](https://www.tensorflow.org).

Tensorflow can, be run more efficiently using one or more GPUs, but this is not required.
Running tensorflow has some [requirements](https://www.tensorflow.org/install/source_windows#gpu).

## Steps

### Download pdfs, create images and extract text (download)

- Input: list of urls
  - `--cache-dir`: absolute path to cache directory
  - `--items-dir`: absolute path to items output directory
  - `--pdf-to-text-file`: absolute path to pdftotext.exe
  - `--pdf-to-image-file`: absolute path to pdftopng.exe
- Output: csv entries, pdf files, images of each pdf page, text from each pdf
- Notes: Implemented using [Scrapy](https://docs.scrapy.org/en/latest/index.html).

### Optical Character Recognition (ocr)

- Input: images of each pdf page
  - `--cache-dir`: absolute path to cache directory
  - `--items-dir`: absolute path to items output directory
- Output: recognised text from each line of each pdf page
- Notes: Implemented using [keras-ocr](https://github.com/faustomorales/keras-ocr).

### Handwriting recognition (handwriting)

- Input: images of parts of each pdf page
  - `--cache-dir`: absolute path to cache directory
  - `--items-dir`: absolute path to items output directory
- Output: recognised handwriting from parts of each pdf page
- Notes: Implemented using [Simple Handwritten Text Recognition](https://github.com/githubharald/SimpleHTR).

### Report generation (report)

- Input: 
  - text from each pdf, 
  - recognised text from each line of each pdf page,
  - recognised handwriting from parts of each pdf page
  - `--cache-dir`: absolute path to cache directory
  - `--items-dir`: absolute path to items output directory
  - `--output-file`: absolute path to the report csv file
- Output: csv file where each column is a data item, and each row is either the initial form, or a later update
- Notes: later updates sometimes are just a paragraph of text with no indication of which section the updates are belong
