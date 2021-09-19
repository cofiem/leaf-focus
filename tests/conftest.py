from pathlib import Path

import pytest

from tests.base_test import BaseTest


def pytest_addoption(parser):
    parser.addoption(
        "--exe-pdf-info",
        action="store",
        default=None,
        help="path to xpdf pdfinfo exe",
    )
    parser.addoption(
        "--exe-pdf-text",
        action="store",
        default=None,
        help="path to xpdf pdftotext exe",
    )
    parser.addoption(
        "--exe-pdf-image",
        action="store",
        default=None,
        help="path to xpdf pdftopng exe",
    )


@pytest.fixture
def exe_pdf_info(request):
    file = request.config.getoption("--exe-pdf-info")
    if file:
        return Path(file)
    return None


@pytest.fixture
def exe_pdf_text(request):
    file = request.config.getoption("--exe-pdf-text")
    if file:
        return Path(file)
    return None


@pytest.fixture
def exe_pdf_image(request):
    file = request.config.getoption("--exe-pdf-image")
    if file:
        return Path(file)
    return None


@pytest.fixture
def example1_pdf_hash_dir():
    b = BaseTest()
    return b.example1_hash_dir(".pdf")


@pytest.fixture
def example1_pdf_hash():
    b = BaseTest()
    return b.example1_hash(".pdf")
