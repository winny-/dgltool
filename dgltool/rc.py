"""
Work with DGL-hosted nhrc and variant rc files.
"""

from requests_html import HTMLSession
import re
import os
from collections import deque
from pathlib import Path
from urllib.parse import urlparse


def backup_hardfought(account, directory=None):
    """Back up your hardfought userdata to a folder."""
    host = account['ssh']['host']
    dgluser = account['dgl']['user']
    if 'hardfought.org' not in host:
        raise ValueError(
            "Invalid account - ssh host does not contain hardfought.org."
        )
    url = f'https://{host}/userdata/{dgluser[:1]}/{dgluser}/'
    download_hf_folder(url, directory)


def download_hf_folder(root_url, directory=None):
    """
    Download all files rooted in a folder rooted in
    hardfought.org/userdata/x/xyz user folder.
    """
    root_path = urlparse(root_url).path
    if directory is None:
        directory = './'
    directory = Path(directory)
    session = HTMLSession()
    visited = []
    queue = deque([root_url])
    while queue:
        url = queue.popleft()
        path = directory / urlparse(url).path.replace(root_path, '', 1)
        r = session.get(url)
        if not url.endswith('/'):
            os.makedirs(path.parent, exist_ok=True)
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
