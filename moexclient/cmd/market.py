from moexclient import exceptions
from moexclient.cmd import base
from moexclient.cmd import defaults


class MarketList(base.Lister):
    _default_columns = (
        'NAME',
        'title'
    )

    def init_parser(self, parser):
        parser.add_argument(
            '--engine',
            metavar='<engine>',
            default=defaults.engine,
            help=('Engine to list markets from [Env: MOEX_ENGINE].')
        )

    def do_action(self, parsed_args):
        if not parsed_args.engine:
            raise exceptions.MoexValueError('Missing --engine value')
        return self.app.moex.markets.list(parsed_args.engine)['markets']
