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
