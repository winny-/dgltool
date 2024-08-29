"""dgltool's command line interface.  Written in click."""

from dataclasses import dataclass
import click
import shutil
import time
import os
import signal
import tomlkit
from . import util, rc, config, logger


class AliasParamType(click.ParamType):
    name = 'alias'

    def shell_complete(self, ctx, param, incomplete):
        # The aliases should be deduplicated, in lexicographical order.
        aliases = sorted(set(util.all_aliases(config.read(ctx.cfg_path))))
        return [
            click.shell_completion.CompletionItem(alias)
            for alias in aliases
            if alias.startswith(incomplete)
        ]


@dataclass
class Context:
    cfg: tomlkit.TOMLDocument | None
    cfg_path: str | None


@click.group()
@click.option('-c', '--config-path', type=click.Path())
@click.option('-v', '--verbose', count=True)
@click.pass_context
def main(ctx, config_path, verbose):
    """Dungeon Game Launcher tool

    Client ard player QoL thingy.
    """
    logger.configure(verbose)
    cfg = config.read(config_path)
    ctx.obj = Context(cfg=cfg, cfg_path=config_path)


@main.command()
@click.pass_context
def list(ctx):
    """List all configured accounts."""
    for a in ctx.obj.cfg['account']:
        click.echo(util.account_to_str(a))


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
    account = util.get_account(ctx.obj.cfg, alias)
    if account is None:
        click.echo(f"No account found matching alias \"{alias}\"")
        exit(1)
    ################################################################
    util.set_title(
        f"{util.account_to_str(account, use_aliases=False)} :: dgltool"
    )
    dgl_user = account['dgl']['user']
    dgl_password = account['dgl']['password']
    os.environ['DGLAUTH'] = f"{dgl_user}:{dgl_password}"
    os.execlp(
        "ssh",
        "ssh",
        "-oSendEnv=DGLAUTH",
        f"-p{account['ssh']['port']}",
        f"-l{account['ssh']['user']}",
        account['ssh']['host'],
    )


class Redraw(RuntimeError):
    pass


@main.command()
def dimensions():
    """Echo terminal dimensions until user issues an interrupt (^C)."""
    try:

        def handler(signum, frame):
            raise Redraw()

        if os.name == 'posix':
            signal.signal(signal.SIGWINCH, handler)
        while True:
            try:
                columns, lines = shutil.get_terminal_size()
                msg = f"{columns}x{lines}"
                util.set_title(f"{msg} :: dgltool")
                # https://stackoverflow.com/questions/1508490
                click.echo(f"\033[2K\r{msg}", nl=False)
                time.sleep(1)
            except Redraw:
                pass
    except KeyboardInterrupt:
        click.echo()


@main.group(name='rc')
def rc_group():
    """Manipulate nhrc files."""
    pass


@rc_group.command()
@click.argument('alias', type=AliasParamType())
@click.option('--directory', '-d', type=click.Path(), default='./')
@click.pass_context
def backup(ctx, alias, directory):
    """
    Back up DGL hosted player data to directory.

    Works with hardfought.org hosts.
    """
    rc.backup_userdata(util.get_account(ctx.obj.cfg, alias), directory)
