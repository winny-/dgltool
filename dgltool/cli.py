from dataclasses import dataclass
import click
import tomlkit

# import xdg_base_dirs
import os
from pathlib import Path


def read_config(config_path=None):
    if config_path is None:
        config_dir = Path('~/.config/dgltool').expanduser()
        os.makedirs(config_dir, mode=0o700, exist_ok=True)
        config_path = config_dir / 'dgltool.toml'
    with open(config_path, 'r') as f:
        return tomlkit.load(f)


@dataclass
class Context:
    cfg: tomlkit.TOMLDocument | None
    cfg_path: str | None


@click.group()
@click.option('-c', '--config-path')
@click.pass_context
def main(ctx, config_path):
    cfg = read_config(config_path)
    ctx.obj = Context(cfg=cfg, cfg_path=config_path)


@main.command()
@click.pass_context
def list(ctx):
    for a in ctx.obj.cfg['account']:
        dgl_user = a['dgl']['user']
        ssh_user = a['ssh']['user']
        ssh_host = a['ssh']['host']
        ssh_port = a['ssh']['port']
        aliases = a['aliases']

        ssh_info = f'{ssh_user}@{ssh_host}'
        if ssh_port != 22:
            ssh_info += f':{ssh_port}'
        cleaned_aliases = ''
        if aliases:
            cleaned_aliases = ','.join(alias for alias in aliases)
        click.echo(f'{cleaned_aliases} :: {dgl_user} at {ssh_info}')


@main.command()
@click.argument('alias')
@click.pass_context
def ssh(ctx, alias):
    target = None
    for account in ctx.obj.cfg['account']:
        if alias in account['aliases']:
            target = account
            break
    if target is None:
        click.echo(f"No account found matching alias \"{alias}\"")
        exit(1)
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
