import logging
import os
import platform
import shutil
import subprocess
import tempfile
import zipfile

import requests
from tqdm import tqdm


def hello_page():
    print(
        """
                                                  _________________
                                   ._ o o        | X-CON INSTALLER |
                                   \_`-)|_       |_________________|
                                ,""       \       /
                              ,"  ## |   0 0.    /
                            ," ##   ,-\__    `. /
                          ,"       /     `--._;)
                        ,"     ## /
                      ,"   ##    /
                """
    )


def prepare_parrent_dir(path):
    parrent_directory = os.path.abspath(os.path.join(path, os.pardir))
    if not os.path.exists(parrent_directory):
        logging.debug(f"Created directory for file {parrent_directory}.")
        os.mkdir(parrent_directory)


def create_temporary_directory(filename):
    dirpath = tempfile.mkdtemp()
    path = delimeter.join([dirpath, filename])
    logging.debug(f"Created temporary directory and file: {path}.")
    return path


def prepare_place_for_download(path_to_download, url):
    if path_to_download is None:
        filename = url.split("/")[-1]
        path_to_download = create_temporary_directory(filename)
    elif isinstance(path_to_download, str):
        prepare_parrent_dir(path_to_download)
    return path_to_download


def download_file(url, progress_bar_description="", path_to_download=None):
    logging.debug(f"Got url with description: {url} / {progress_bar_description}.")
    path_to_download = prepare_place_for_download(path_to_download, url)
    logging.debug(f"Downloaded file will store here: {path_to_download}.")
    with requests.get(url, stream=True) as r:
        total = int(r.headers.get("content-length", 0))
        logging.debug(f"Downloaded file will take next disk storage: {total} bytes.")
        block_size = 2048
        with open(path_to_download, "wb") as f, tqdm(
            desc=progress_bar_description, total=total, unit="B", unit_scale=True
        ) as bar:
            for data in r.iter_content(block_size):
                bar.update(len(data))
                f.write(data)
    logging.debug(f"Downloading complete. File save to {path_to_download}.")
    return path_to_download


def is_installed_python(version):
    for python in ["python", "python3"]:
        try:
            process = subprocess.Popen(
                [python, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        except FileNotFoundError:
            continue
        stdout, stderr = process.communicate()
        if version in str(stdout):
            return True
    return False


def is_exists_path(path):
    return os.path.exists(path)


def install_python(version):
    if is_installed_python(version):
        logging.info(f"Python {version} already installed.")
        return
    logging.info(f"Staring to download python{version}..")
    if architecture == "64bit":
        python_exe_path = download_file(
            f"https://www.python.org/ftp/python/{version}/python-{version}-amd64.exe",
            "Downloading python3",
        )
    elif architecture == "32bit":
        python_exe_path = download_file(
            f"https://www.python.org/ftp/python/{version}/python-{version}.exe",
            "Downloading python3",
        )
    else:
        raise Exception(f"Undefiend architecture: {platform.architecture()}")

    logging.info(f"Downloading complete.")
    logging.info(f"Starting installing..")
    process = subprocess.Popen(
        [
            python_exe_path,
            "/quiet",
            "PrependPath=1",
            "Include_test=0",
            "CompileAll=1",
            "Include_tcltk=0",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()
    logging.info(f"Installing python{version} complete.")


def install_dependencies(path_pip):
    logging.info(f"Staring to install python requirements from path: {path_pip} ..")

    process = subprocess.Popen(
        ["python", "-m", "pip", "install", "-r", path_pip],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    stdout, stderr = process.communicate()
    logging.info(f"Complete installing python requirements.")


def install_touchdesigner(version):
    default_touchdesiger_exe_path = (
        "C:\\Program Files\\Derivative\\TouchDesigner\\bin\\TouchDesigner.exe"
    )
    if is_exists_path(default_touchdesiger_exe_path):
        logging.info(f"TouchDesigner already installed.")
        return

    logging.info(f"Staring to downloading TouchDesigner..")
    touchdesiger_exe_path = download_file(
        f"https://download.derivative.ca/TouchDesigner.{version}.exe",
        "Downloading TouchDesigner",
    )
    logging.info(f"Complete to downloading TouchDesigner.")
    logging.info(f"Staring to install TouchDesigner..")
    process = subprocess.Popen(
        [touchdesiger_exe_path, "/VERYSILENT"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()
    logging.info(f"Complete installing TouchDesigner.")


def download_file_from_yandex_disk(
    url, progress_bar_description="", path_to_download=None
):
    base_url = "https://cloud-api.yandex.net/v1/disk/public/resources/download"

    response = requests.get(base_url, params={"public_key": url})
    download_url = response.json().get("href")
    return download_file(download_url, progress_bar_description, path_to_download)


def install_ndi_tools(yandex_disk_url):
    default_ndi_tools_exe_path = "C:\\Program Files\\NDI.tv\\NDI 4 Tools"
    if is_exists_path(default_ndi_tools_exe_path):
        logging.info("NDI Tools already installed.")
        return

    logging.info("Staring to downloading NDI Tools..")
    ndi_tools_exe_path = download_file_from_yandex_disk(
        yandex_disk_url, "Installing NDI Tools"
    )
    logging.info("Complete to downloading NDI Tools")

    os.rename(ndi_tools_exe_path, f"{ndi_tools_exe_path}.exe")
    logging.info("Staring to install NDI Tools..")
    process = subprocess.Popen(
        [
            f"{ndi_tools_exe_path}.exe",
            "/VERYSILENT",
            "/NORESTART",
            "/TYPE=all_tools",
            "/SP-",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()
    logging.info("Complete installing NDI Tools.")


def obs_ndi(url):

    default_obs_directory_path = "C:\\Program Files\\OBS\\"

    # if is_exists_path(default_obs_directory_path):
    #     logging.info(f"OBS NDI plugins already installed.")
    #     return

    logging.info("Staring to downloading OBS NDI..")
    obs_dni_exe_path = download_file(url, "Downloading OBS NDI")
    logging.info("Complete to downloading OBS NDI.")

    logging.info("Staring to extract OBS NDI..")
    os.rename(obs_dni_exe_path, f"{obs_dni_exe_path}.zip")
    fantasy_zip = zipfile.ZipFile(f"{obs_dni_exe_path}.zip")
    fantasy_zip.extractall(default_obs_directory_path)
    fantasy_zip.close()

    # After install setup installing ndi-tools, which already installed
    # process = subprocess.Popen(
    #     [obs_dni_exe_path, "/SILENT", "/NORESTART", "/NOCANCEL"],
    #     stdout=subprocess.PIPE,
    #     stderr=subprocess.PIPE,
    # )
    # stdout, stderr = process.communicate()
    logging.info(f"Complete extracting OBS NDI.")


def download_media_files(yandex_disk_url):
    # default_media_files_path = "C:\\Program Files\\"

    # if is_exists_path(default_media_files_path):
    #     logging.info("Media files already extracted.")
    #     return

    logging.info("Starting to downloading media files..")
    media_files = download_file_from_yandex_disk(
        yandex_disk_url, "Downloading media files"
    )
    logging.info("Complete to downloading media files..")

    os.rename(media_files, f"{media_files}.zip")
    fantasy_zip = zipfile.ZipFile(f"{media_files}.zip")
    fantasy_zip.extractall(default_path)
    fantasy_zip.close()
    logging.info("Complete to extract media files.")


def download_project_toe(yandex_disk_url):
    path_to_download = delimeter.join([default_path, "Awesome-Project.toe"])

    if is_exists_path(path_to_download):
        logging.info("Project files already exists.")
        return

    logging.info("Starting to download TouchDesigner project.")
    download_file_from_yandex_disk(
        yandex_disk_url, "Downloading TouchDesigner projects", path_to_download
    )
    logging.info("Complete to download TouchDesigner project.")


if __name__ == "__main__":
    LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper().strip()
    logging.basicConfig(level=LOGLEVEL)

    hello_page()
    logging.debug("Starting to install tools..")

    architecture = platform.architecture()[0]
    logging.debug(f"Defined next architecture: {architecture}.")

    default_path = "C:\\Program Files (x86)\\X-CON"
    logging.debug(f"Defined default to extract path: {default_path}.")

    delimeter = {"Windows": "\\", "Darwin": "/", "Linux": "/"}.get(platform.system())
    logging.debug(f"Defined path delimeter for OS: {delimeter}.")

    install_python(version="3.9.6")
    install_touchdesigner(version="2021.14360")
    install_ndi_tools("https://disk.yandex.by/d/5qylbuELKWb98A")
    # obs_ndi(
    #     "https://github.com/Palakis/obs-ndi/releases/download/4.9.1/obs-ndi-4.9.0-Windows.zip"
    # )
    download_media_files("https://disk.yandex.by/d/2Q1R9kcYKl9Q-Q")
    install_dependencies(delimeter.join([default_path, "requirements.txt"]))
    download_project_toe("https://disk.yandex.by/d/fngADNHpJVLcuA")