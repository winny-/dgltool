from dataclasses import dataclass
import click
import tomlkit
import shutil
import time
import os
from . import util
from pathlib import Path


class AliasParamType(click.ParamType):
    name = 'alias'

    def shell_complete(self, ctx, param, incomplete):
        # The aliases should be deduplicated, in lexicographical order.
        aliases = sorted(set(util.all_aliases(read_config())))
        return [
            click.shell_completion.CompletionItem(alias)
            for alias in aliases
            if alias.startswith(incomplete)
        ]


def read_config(config_path=None):
    """Read TOML config.

    config_path defaults to ~/.config/dgltool/dgltool.toml
    """
    if config_path is None:
        config_dir = Path('~/.config/dgltool').expanduser()
        os.makedirs(config_dir, mode=0o700, exist_ok=True)
        config_path = config_dir / 'dgltool.toml'
    Path(config_path).touch()  # Ensure it exists.
    with open(config_path, 'r') as f:
        return tomlkit.load(f)


@dataclass
class Context:
    cfg: tomlkit.TOMLDocument | None
    cfg_path: str | None


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


@click.group()
@click.option('-c', '--config-path', type=click.Path())
@click.pass_context
def main(ctx, config_path):
    """Dungeon Game Launcher tool

    Client ard player QoL thingy.
    """
    cfg = read_config(config_path)
    ctx.obj = Context(cfg=cfg, cfg_path=config_path)


@main.command()
@click.pass_context
def list(ctx):
    """List all configured accounts."""
    for a in ctx.obj.cfg['account']:
        click.echo(account_to_str(a))


@main.command()
@click.pass_context
def help(ctx):
    """Show program help."""
    click.echo(ctx.find_root().get_help())
    ctx.exit()


@main.command()
@click.argument('alias', type=AliasParamType())
@click.pass_context
def ssh(ctx, alias):
    """Connect to an account using its ALIAS."""
    target = None
    for account in ctx.obj.cfg['account']:
        if alias in account['aliases']:
            target = account
            break
    if target is None:
        click.echo(f"No account found matching alias \"{alias}\"")
        exit(1)
    ################################################################
    util.set_title(f"{account_to_str(account, use_aliases=False)} :: dgltool")
    dgl_user = account['dgl']['user']
    dgl_password = account['dgl']['password']
    os.environ['DGLAUTH'] = f"{dgl_user}:{dgl_password}"
    os.execlp(
        "ssh",
        "ssh",
        "-oSendEnv=DGLAUTH",
        f"-p{account['ssh'].get('port', 22)}",
        f"-l{account['ssh']['user']}",
        account['ssh']['host'],
    )


@main.command()
def dimensions():
    """Echo terminal dimensions until user issues an interrupt (^C)."""
    while True:
        columns, lines = shutil.get_terminal_size()
        msg = f"{columns}x{lines}"
        util.set_title(f"{msg} :: dgltool")
        click.echo(f"\r{msg}", nl=False)
        time.sleep(1)
