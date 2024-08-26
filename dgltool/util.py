"""
Uncategorized support code.
"""

import itertools
import click
from .exceptions import NoSuchAccountError


def set_title(s: str) -> None:
    """Set terminal title to s."""
    click.echo(f'\33]0;{s}\a', nl=False)


def all_aliases(cfg):
    """Get an iterable of all account aliases."""
    accounts = cfg.get('account', [])
    aliases = (account['aliases'] for account in accounts)
    return itertools.chain.from_iterable(aliases)


def get_account(cfg, alias):
    """Get the account by alias.

    raises NoSuchAccountError, a subclass of ValueError."""
    for account in cfg['account']:
        if alias in account['aliases']:
            return account
    raise NoSuchAccountError(alias)


def account_to_str(account, use_aliases=True):
    """Pretty string representing an account dictionary."""
    dgl_user = account['dgl']['user']
    ssh_user = account['ssh']['user']
    ssh_host = account['ssh']['host']
    ssh_port = account['ssh']['port']
    aliases = account['aliases']

    ssh_info = f'{ssh_user}@{ssh_host}'
    if ssh_port != 22:
        ssh_info += f':{ssh_port}'
    cleaned_aliases = ''
    s = ''
    if use_aliases:
        cleaned_aliases = ','.join(alias for alias in aliases)
        s = f'{cleaned_aliases} :: '
    return f'{s}{dgl_user} at {ssh_info}'
