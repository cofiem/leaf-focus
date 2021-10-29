# leaf-focus

Extract structured text from pdf files.

Dealing with pdf files that are scans of pages or don't contain machine-readable text can be difficult.

This package is a command line program that helps to extract text from these kinds of pdf files.

It is a best-effort approach, so be aware that any text extracted may be incorrect.

There are four stages:

- download pdfs
- extract pdf information
- run optical character recognition (OCR) on the pdf pages
- generate a report in csv format


[![Build and Test](https://github.com/cofiem/leaf-focus/actions/workflows/build-test.yml/badge.svg)](https://github.com/cofiem/leaf-focus/actions/workflows/build-test.yml)


## Command line

```
$ leaf-focus
Usage: leaf-focus [OPTIONS] COMMAND [ARGS]...

  Extract structured text from pdf files.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  download   Find and download pdfs.
  ocr        Run Optical Character Recognition.
  pdf        Extract information and text from pdf files.
  report     Create a report.
  visualise  Visualise all the stages that are run using a pipeline.
```

Add `--help` to any command to see the help for that command.

For example, `leaf-focus download --help`.


## Overview

To begin, run the four stages in order: `download`, `pdf`, `ocr`, `report`.

The inputs are pdf files, urls, and xpdf program.

The outputs are the extracted pdf information, text form the pdfs, and csv report files.

Each stage can work with partial results from the previous stage.
This helps with checking the output and processing, so changes can be made without waiting for all the stages
to complete.

- The downloading stage makes the pdf files available to the pdf processing stage.
- The pdf processing stage tries to extract information and metadata about the pdfs.
- The ocr stage extracts the text from pdf page images to characters in a plain text file.
- The report stage makes use of the text extracted from the pdf file to build a report specific to the 
  format of the pdf content.


## Install

Download and install [Python 3.9](https://www.python.org/downloads/).

Create a folder to store this program, the pdf files, images, and report.

For example, `C:\Users\myname\leaf-focus`.

Create a virtual environment: 

```bash
python -m venv "C:\Users\myname\leaf-focus\venv"
```

Install this program:

```bash
"C:\Users\myname\leaf-focus\venv\Scripts\python.exe" -m pip install -U pip
"C:\Users\myname\leaf-focus\venv\Scripts\pip.exe" install -U setuptools wheel
"C:\Users\myname\leaf-focus\venv\Scripts\pip.exe" install -U leaf-focus
```

Run commands using the virtual environment:

```bash
"C:\Users\myname\leaf-focus\venv\Scripts\leaf-focus.exe" --help
```

Download the [xpdf tools](https://www.xpdfreader.com/download.html).

Put the files into a folder in the folder you created earlier.

For example, `C:\Users\myname\leaf-focus\xpdf`.


## Configure

Create a configuration file to let the program know where to find the folders
and xpdf tools.

For example, `C:\Users\myname\leaf-focus\config.yml`.

An example partial config file is available in this git repository at `leaf_focus\resources\example.yml`.
This example contains `allowed_domains` and `urls`.
Copy these to your file and fill in the remaining configuration.

```yaml
directories:
  feed: 'C:\Users\myname\leaf-focus\feed'
  cache: 'C:\Users\myname\leaf-focus\cache'
  processing: 'C:\Users\myname\leaf-focus\processing'
  report: 'C:\Users\myname\leaf-focus\report'
xpdf:
  info: 'C:\Users\myname\leaf-focus\xpdf\bin64\pdfinfo.exe'
  text: 'C:\Users\myname\leaf-focus\xpdf\bin64\pdftotext.exe'
  image: 'C:\Users\myname\leaf-focus\xpdf\bin64\pdftopng.exe'
settings:
  imagethreshold: 190
allowed_domains:
  - "<domain>"
urls:
  - category: "members"
    url: "<url to page containing links to pdfs>"
    comment: ""
  - category: "senators"
    url: "<url to page containing links to pdfs>"
    comment: ""
```


## Find and download pdfs.

Run the command to find and download the pdf files.

This stage might take a while.

For example, using the example config file:

- 3 to 4 hours for an initial run with no cache
- about an hour with an existing cache

```bash
leaf-focus download --config-file "C:\Users\myname\leaf-focus\config.yml"
```


## Extract information and text from pdf files.

Run the command to extract information and text from pdf files.

This stage can be run using a collection of pdf files or a single pdf file.

For example, using the same directories from the download stage:

```bash
leaf-focus pdf all --config-file "C:\Users\myname\leaf-focus\config.yml"

```


## Run Optical Character Recognition.

Run the commands to prepare the images for OCR, and then run the OCR.

```bash
leaf-focus ocr prepare-many --config-file "C:\Users\myname\leaf-focus\config.yml"
leaf-focus ocr recognise-many --config-file "C:\Users\myname\leaf-focus\config.yml"
```


## Create a report.

(todo)


## Dependencies

- [xpdf](https://www.xpdfreader.com/download.html)
- [Scrapy](https://docs.scrapy.org/en/latest/index.html)
- [keras-ocr](https://github.com/faustomorales/keras-ocr)
- [Simple Handwritten Text Recognition](https://github.com/githubharald/SimpleHTR)
- [Tensorflow](https://www.tensorflow.org) (can optionally be run more efficiently [using one or more GPUs](https://www.tensorflow.org/install/source_windows#gpu))
- [Pillow](https://python-pillow.org/)
- [Prefect](https://docs.prefect.io/)
