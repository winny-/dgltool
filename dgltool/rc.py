"""
Work with DGL-hosted nhrc and variant rc files.
"""

import requests_html
import re
import os
from collections import deque
from pathlib import Path
from urllib.parse import urlparse
import click
import time
from . import logger


def backup_userdata(account, directory=None):
    """Back up your userdata to a folder"""
    host = account['ssh']['host']
    dgluser = account['dgl']['user']
    prefix = None
    if 'hardfought.org' in host:
        prefix = f'https://{host}'
    elif host.endswith('alt.org'):
        prefix = 'https://alt.org/nethack'
    else:
        raise ValueError('Do not know how to back up account on host {host}')
    url = f'{prefix}/userdata/{dgluser[:1]}/{dgluser}/'
    download_userdata_to_folder(url, directory)


def download_userdata_to_folder(root_url, directory=None):
    """
    Download all files rooted in a folder rooted in
     user folder.
    """
    root_path = urlparse(root_url).path
    if directory is None:
        directory = './'
    directory = Path(directory)
    requests_html.DEFAULT_USER_AGENT = 'https://github.com/winny-/dgltool'
    session = requests_html.HTMLSession()
    logger.debug(f'User-Agent: {session.headers["User-Agent"]}')
    visited = []
    logger.info(f'Downloading userdata at {root_url} into {directory}/ ...')
    start = time.time()
    queue = deque([root_url])
    first = True
    while queue:
        if first:
            first = False
        else:
            time.sleep(.33)  # Pause for 1/3 of a second after each request.
        url = queue.popleft()
        logger.debug(f'GET {url}')
        path = directory / urlparse(url).path.replace(root_path, '', 1)
        r = session.get(url)
        if not url.endswith('/'):
            os.makedirs(path.parent, exist_ok=True)
            logger.debug(f'Save {path}')
            with open(path, 'xb') as f:
                f.write(r.content)
        if r.headers.get('content-type', '').startswith('text/html'):
            candidates = {
                li
                for li in r.html.absolute_links
                if re.match(re.escape(url) + '[^?#]', li)
            }
            for candidate in candidates:
                if candidate not in visited and candidate not in queue:
                    queue.append(candidate)
    logger.info(f'Downloaded userdata after {time.time() - start:.1f} seconds.')
