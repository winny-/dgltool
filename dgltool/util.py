import itertools
import click


def set_title(s: str) -> None:
    """Set terminal title to s."""
    click.echo(f'\33]0;{s}\a', nl=False)


def all_aliases(cfg):
    """Get an iterable of all account aliases."""
    accounts = cfg.get('account', [])
    aliases = (account['aliases'] for account in accounts)
    return itertools.chain.from_iterable(aliases)
