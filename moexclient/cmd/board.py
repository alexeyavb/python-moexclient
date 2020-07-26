import copy

from moexclient.cmd import base


class BoardList(base.Lister):
    def get_parser(self, prog_name):
        parser = super(BoardList, self).get_parser(prog_name)
        parser.add_argument(
            '--market',
            required=True,
            help='Market to list boards from.',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Show all boards, not only traded ones.',
        )
        return parser

    def do_action(self, parsed_args):
        data = self.app.moex.boards.list(parsed_args.market)
        data = data['boards']

        if not parsed_args.all:
            new_data = []
            for item in data:
                if int(item['is_traded']) == 1:
                    new_data.append(item)

            data = new_data

        return data
