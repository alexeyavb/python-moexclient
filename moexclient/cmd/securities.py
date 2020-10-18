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
        return self.app.moex.securities.list(
            engine, market,
            board=parsed_args.board,
            index=parsed_args.index,
            securities=parsed_args.securities,
        )


class SecurityFindBase(base.Lister):
    _default_columns = ('secid', 'isin', 'shortname', 'name', 'group', 'primary_boardid')

    def init_parser(self, parser):
        parser.add_argument(
            'query',
            help='Find a security query'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Find non tranding securities'
        )
        return parser

    def _find(self, engine, market, parsed_args):
        data = self.app.moex.securities.find(parsed_args.query,
                                             engine=engine,
                                             market=market)
        # Somehow iss return deplicated objects in find API
        securities = data['securities']
        securities_set = set(tuple(sec.items()) for sec in securities)
        return [dict(sec) for sec in securities_set]


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


class SecurityFind(SecurityFindBase):
    def init_parser(self, parser):
        parser.add_argument(
            '--engine',
            help='Engine to list securities from'
        )
        parser.add_argument(
            '--market',
            help='Market to list securities from'
        )
        super(SecurityFind, self).init_parser(parser)

    def do_action(self, parsed_args):
        return self._find(parsed_args.engine, parsed_args.market, parsed_args)


class SecurityShow(base.ShowOne):
    def init_parser(self, parser):
        parser.add_argument(
            'security',
            help='Security ID to show'
        )

    def do_action(self, parsed_args):
        data = self.app.moex.securities.get(parsed_args.security)
        res = {}
        for item in data['description']:
            res[item['name']] = item['value']

        return res


class SecurityBoardList(base.Lister):
    _default_columns = (
        'secid',
        'boardid',
        'title',
        'is_primary',
        'engine',
        'market'
    )

    def init_parser(self, parser):
        parser.add_argument(
            'security',
            help='Security ID to show'
        )

    def do_action(self, parsed_args):
        data = self.app.moex.securities.get(parsed_args.security)
        return data['boards']
        res = {}
        print(data['boards'])
        for item in data['boards']:
            res[item['name']] = item['value']

        return res


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


class StockSharesFind(SecurityFindBase):
    def do_action(self, parsed_args):
        return self._find('stock', 'shares', parsed_args)


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


class StockBondsFind(SecurityFindBase):
    def do_action(self, parsed_args):
        return self._find('stock', 'bonds', parsed_args)


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


class StockIndexFind(SecurityFindBase):
    def do_action(self, parsed_args):
        return self._find('stock', 'index', parsed_args)


class MarketdataList(SecurityListBase):
    def _default_columns(self, parsed_args):
        if parsed_args.market == 'shares':
            return ['SECID', 'BOARDID', 'OPEN', 'LOW', 'HIGH', 'LAST',
                    'VOLTODAY', 'VALTODAY_RUR', 'UPDATETIME']
        elif parsed_args.market == 'bonds':
            return ['SECID', 'BOARDID', 'OPEN', 'LOW', 'HIGH', 'LAST',
                    'VOLTODAY', 'VALTODAY_RUR', 'UPDATETIME']

    def do_action(self, parsed_args):
        data = self._list(parsed_args)
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
