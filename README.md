# leaf-focus

Extract text from pdf files.

```
$ leaf-focus --help
Usage: leaf-focus [OPTIONS] COMMAND [ARGS]...

  Extract text from pdf files.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  download  Find and download pdfs.
  ocr       Run Optical Character Recogition.
  pdf       Extract information from pdf files.
  pipeline  Run a pipeline of tasks.
  report    Create a report.
```

[![Build and Test](https://github.com/cofiem/leaf-focus/actions/workflows/build-test.yml/badge.svg)](https://github.com/cofiem/leaf-focus/actions/workflows/build-test.yml)
[![Coverage](coverage.svg)](https://github.com/cofiem/leaf-focus/actions/workflows/build-test.yml)

## Overview

Dealing with pdf files that are scans of pages or don't contain machine-readable text can be tough.
This package is a command line program that helps to extract text from these kinds of pdf files.

It is a best-effort approach, so be aware that any text extracted may be incorrect.

There are three main stages - downloading, pdf processing, and producing a report.

- The downloading stage makes the pdf files available to the pdf processing stage.
- The pdf processing stage tries to extract text from the pdfs.
  It has sub-steps that can be run as a pipeline or separately.
- The report stage makes use of the text extracted from the pdf file to build a report specific to the 
  format of the pdf content.

Each stage can work with partial results from the previous stage.
This helps with checking the output and processing, so changes can be made without waiting for all the stages 
to complete.

The essential inputs are pdf files and a definition of the pdf content,
to be able to extract data that can be used to build a report.

## Install

(todo)

## Find and download pdfs.

(todo)

## Extract information from pdf files.

(todo)

## Run Optical Character Recogition.

(todo)

## Run a pipeline of tasks.

(todo)

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
