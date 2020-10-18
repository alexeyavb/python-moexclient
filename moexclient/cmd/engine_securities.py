import abc

from moexclient.cmd import base


class SecurityListBase(base.Lister):
    def init_parser(self, parser):
        parser.add_argument(
            '--index',
            help='List securities from the index'
        )
        parser.add_argument(
            '--board',
            help='List securities from the board'
        )
        parser.add_argument(
            '--securities',
            help='Securities filter, up to 10'
        )
        return parser

    def _list(self, engine, market, parsed_args):
        return self.app.moex.engine_securities.list(
            engine, market,
            board=parsed_args.board,
            index=parsed_args.index,
            securities=parsed_args.securities,
        )


class SecurityList(SecurityListBase):
    _default_columns = ('SECID', 'BOARDID', 'SHORTNAME')

    def init_parser(self, parser):
        parser.add_argument(
            '--engine',
            required=True,
            help='Engine to list securities from'
        )
        parser.add_argument(
            '--market',
            required=True,
            help='Market to list securities from'
        )
        super(SecurityList, self).init_parser(parser)

    def do_action(self, parsed_args):
        data = self._list(parsed_args.engine, parsed_args.market, parsed_args)
        return data['securities']


class SecurityShow(base.ShowOne):
    def init_parser(self, parser):
        parser.add_argument(
            'security',
            help='Security ID to show'
        )
        parser.add_argument(
            '--board',
            help='Board to list securities from'
        )

    def do_action(self, parsed_args):
        if not parsed_args.board:
            sec = self.app.moex.securities.get(parsed_args.security)
            primary_board = None
            for b in sec['boards']:
                if b['is_primary']:
                    parsed_args.board = b['name']
                    break
            else:
                raise Exception('No primary board')

        data = self.app.moex.engine_securities.get(
            'stock', 'shares', parsed_args.security, board=parsed_args.board)
        return data['securities'][0]


# Shares
class StockSharesList(SecurityListBase):
    _default_columns = (
        'SECID',
        'BOARDID',
        'SHORTNAME',
        'ISIN',
        'PREVPRICE',
        'PREVDATE'
    )

    def do_action(self, parsed_args):
        data = self._list('stock', 'shares', parsed_args)
        return data['securities']


class StockSharesShow(base.ShowOne):
    def init_parser(self, parser):
        parser.add_argument(
            'security',
            help='Security ID to show'
        )
        parser.add_argument(
            '--board',
            help='Board to show securities from'
        )

    def do_action(self, parsed_args):
        if not parsed_args.board:
            sec = self.app.moex.securities.get(parsed_args.security)
            primary_board = None
            for board in sec['boards']:
                if board['is_primary']:
                    parsed_args.board = board['boardid']
                    break
            else:
                raise Exception('Cannot find a primary board')

        data = self.app.moex.engine_securities.get(
            'stock', 'shares', parsed_args.security, board=parsed_args.board)
        if not data['securities']:
            return None
        return data['securities'][0]



# Bonds
class StockBondsList(SecurityListBase):
    _default_columns = (
        'SECID',
        'BOARDID',
        'SHORTNAME',
        'YIELDATPREVWAPRICE',
        'COUPONPERCENT',
        'COUPONVALUE',
        'COUPONPERIOD',
        'MATDATE',
        'OFFERDATE'
    )

    def do_action(self, parsed_args):
        data = self._list('stock', 'bonds', parsed_args)
        return data['securities']


class StockBoardShow(base.ShowOne):
    def init_parser(self, parser):
        parser.add_argument(
            'security',
            help='Security ID to show'
        )
        parser.add_argument(
            '--board',
            help='Board to show securities from'
        )

    def do_action(self, parsed_args):
        if not parsed_args.board:
            sec = self.app.moex.securities.get(parsed_args.security)
            primary_board = None
            for board in sec['boards']:
                if board['is_primary']:
                    parsed_args.board = board['boardid']
                    break
            else:
                raise Exception('Cannot find a primary board')

        data = self.app.moex.engine_securities.get(
            'stock', 'bonds', parsed_args.security, board=parsed_args.board)
        if not data['securities']:
            return None
        return data['securities'][0]


# Index
class StockIndexList(SecurityListBase):
    _default_columns = (
        'SECID',
        'BOARDID',
        'SHORTNAME',
        'ANNUALHIGH',
        'ANNUALLOW',
        'CURRENCYID'
    )

    def do_action(self, parsed_args):
        data = self._list('stock', 'index', parsed_args)
        return data['securities']


class MarketdataList(SecurityListBase):
    def init_parser(self, parser):
        parser.add_argument(
            '--engine',
            help='Engine to list securities from'
        )
        parser.add_argument(
            '--market',
            help='Market to list securities from'
        )
        super(MarketdataList, self).init_parser(parser)

    #def _default_columns(self, parsed_args):
    #    if parsed_args.market == 'shares':
    #        return ['SECID', 'BOARDID', 'OPEN', 'LOW', 'HIGH', 'LAST',
    #                'VOLTODAY', 'VALTODAY_RUR', 'UPDATETIME']
    #    elif parsed_args.market == 'bonds':
    #        return ['SECID', 'BOARDID', 'OPEN', 'LOW', 'HIGH', 'LAST',
    #                'VOLTODAY', 'VALTODAY_RUR', 'UPDATETIME']

    def do_action(self, parsed_args):
        data = self._list(parsed_args.engine, parsed_args.market, parsed_args)
        return data['marketdata']


class MarketdataShow(base.ShowOne):
    def get_parser(self, prog_name):
        parser = super(MarketdataShow, self).get_parser(prog_name)
        parser.add_argument(
            'security',
            help='Security ID to show'
        )
        parser.add_argument(
            '--board',
            help=''
        )
        return parser

    def do_action(self, parsed_args):
        data = self.app.moex.securities.get(parsed_args.security)

        group = None
        for item in data['description']:
            if item['name'] == 'GROUP':
                group = item['value']
                break
        if not group:
            raise Exception('No group')

        engine, market = group.split('_')
        data = self.app.moex.securities.get_by_market(parsed_args.security, engine, market, board=parsed_args.board)
        if len(data['marketdata']) > 1:
            boards = [m['BOARDID'] for m in data['marketdata']]
            raise Exception('More then one board for %s was found. '
                            'Use "list" command or specify the --borad: %s'
                            % (parsed_args.security, ', '.join(boards)))

        return data['marketdata'][0]
