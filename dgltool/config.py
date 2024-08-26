import tomlkit
import os
from pathlib import Path


def read(config_path=None):
    """Read TOML config.

    config_path defaults to ~/.config/dgltool/dgltool.toml
    """
    if config_path is None:
        config_dir = Path('~/.config/dgltool').expanduser()
        os.makedirs(config_dir, mode=0o700, exist_ok=True)
        config_path = config_dir / 'dgltool.toml'
    Path(config_path).touch()  # Ensure it exists.
    with open(config_path, 'r') as f:
        return clean(tomlkit.load(f))


def clean(cfg):
    """Clean the TOML document.

    Ensure default field values are initialized.  Look for schema errors.
    """

    def validate_keys(what, D, required=None, optional=None):
        if required is None:
            required = frozenset()
        if optional is None:
            optional = frozenset()
        if unknown := D.keys() - (required | optional):
            raise ValueError(f'{what}: Unknown key(s): {", ".join(unknown)}')
        if wanted := required - D.keys():
            raise ValueError(f'{what}: Need key(s): {", ".join(wanted)}')

    def validate_type(what, v, type_):
        if not isinstance(v, type_):
            raise ValueError(
                f'{what}: expected type {type_} but got {type(v)}'
            )

    validate_keys('top level', cfg, optional={'default', 'account'})
    default_user = None
    if 'default' in cfg:
        default = cfg['default']
        if 'dgl' in default:
            dgl = default['dgl']
            if 'user' in dgl:
                default_user = dgl['user']
                validate_type('[default] dgl.user', default_user, str)
    for account in cfg.get('account', {}):
        validate_keys(
            '[[account]]', account, required={'aliases', 'dgl', 'ssh'}
        )
        dgl = account['dgl']
        validate_keys(
            '[[account]] dgl',
            dgl,
            required={'password'}
            | (frozenset() if default_user else {'user'}),
            optional={'user'} if default_user else frozenset(),
        )
        if 'user' not in dgl:
            if default_user:
                dgl['user'] = default_user
            else:
                raise ValueError(
                    '[[account]]: missing dgl.user (OR [default] dgl.user)'
                )
        else:
            validate_type('[[account]] dgl.user', dgl['user'], str)
        validate_type('[[account]] dgl.password', dgl['password'], str)
        ssh = account['ssh']
        validate_keys(
            '[[account]] ssh',
            ssh,
            required={'host'},
            optional={'user', 'port'},
        )
        if 'user' not in ssh:
            ssh['user'] = 'nethack'
        else:
            validate_type('[[account]] ssh.user', ssh['user'], str)
        validate_type('[[account]] ssh.host', ssh['host'], str)
        if 'port' not in ssh:
            ssh['port'] = 22
        else:
            validate_type('[[account]] ssh.port', ssh['port'], int)
    return cfg
