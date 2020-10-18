from moexclient import exceptions
from moexclient.cmd import base
from moexclient.cmd import defaults


class BoardList(base.Lister):
    def init_parser(self, parser):
        parser.add_argument(
            '--engine',
            metavar='<engine>',
            default=defaults.engine,
            help=('Engine to list markets from [Env: MOEX_ENGINE].')
        )
        parser.add_argument(
            '--market',
            metavar='<market>',
            default=defaults.market,
            help=('Market to list boards from [Env: MOEX_MARKET].')
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Show all boards.',
        )

    def do_action(self, parsed_args):
        if not parsed_args.engine:
            raise exceptions.MoexValueError('Missing --engine value')
        if not parsed_args.market:
            raise exceptions.MoexValueError('Missing --market value')

        data = self.app.moex.boards.list(
            parsed_args.engine, parsed_args.market)
        data = data['boards']

        if not parsed_args.all:
            new_data = []
            for item in data:
                if int(item['is_traded']) == 1:
                    new_data.append(item)

            data = new_data

        return data
