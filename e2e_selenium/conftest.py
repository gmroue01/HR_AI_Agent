import subprocess
import sys
import time
import urllib.request

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from helpers import BASE_URL

_streamlit_process = None


def _is_streamlit_up() -> bool:
    try:
        urllib.request.urlopen(BASE_URL, timeout=1)
        return True
    except OSError:
        return False


@pytest.fixture(scope="session", autouse=True)
def streamlit_server():
    global _streamlit_process

    if _is_streamlit_up():
        yield
        return

    _streamlit_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "streamlit_app.py", "--server.headless", "true"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(60):
        if _is_streamlit_up():
            break
        time.sleep(1)
    else:
        _streamlit_process.terminate()
        raise RuntimeError("Streamlit server did not start within 60s")

    yield

    _streamlit_process.terminate()
    _streamlit_process.wait(timeout=10)


@pytest.fixture
def driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1280,960")
    chrome = webdriver.Chrome(options=options)
    yield chrome
    chrome.quit()
