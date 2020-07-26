from moexclient.cmd import base


class SecuritiesBase(base.Lister):
    def get_parser(self, prog_name):
        parser = super(SecuritiesBase, self).get_parser(prog_name)
        parser.add_argument(
            '--market',
            required=True,
            help='Market to list securities from'
        )
        parser.add_argument(
            '--board',
            help='Board ID'
        )
        parser.add_argument(
            '--index',
            help='List securities only from index'
        )
        parser.add_argument(
            '--securities',
            help='Securities filter, up to 10'
        )
        return parser

    def _list_securities(self, parsed_args):
        return self.app.moex.securities.list(
            parsed_args.market, board=parsed_args.board,
            index=parsed_args.index,
            securities=parsed_args.securities,
        )


class SecurityFind(base.Lister):
    def _default_columns(self, parsed_args):
        return ['secid', 'shortname', 'name', 'group', 'primary_boardid']

    def get_parser(self, prog_name):
        parser = super(SecurityFind, self).get_parser(prog_name)
        parser.add_argument(
            'query',
            help='Market to list securities from'
        )
        parser.add_argument(
            '--all',
            action="store_true",
            help='Market to list securities from'
        )
        return parser

    def do_action(self, parsed_args):
        data = self.app.moex.securities.find(parsed_args.query, all=parsed_args.all)
        return data['securities']


class SecurityShow(base.ShowOne):
    def get_parser(self, prog_name):
        parser = super(SecurityShow, self).get_parser(prog_name)
        parser.add_argument(
            'security',
            help='Security ID to show'
        )
        return parser

    def do_action(self, parsed_args):
        data = self.app.moex.securities.get(parsed_args.security)

        res = {}
        for item in data['description']:
            res[item['name']] = item['value']

        return res


class SecurityList(SecuritiesBase):
    def _default_columns(self, parsed_args):
        if parsed_args.market == 'index':
            return ['SECID', 'BOARDID', 'SHORTNAME', 'ANNUALHIGH', 'ANNUALLOW',
                    'CURRENCYID']
        elif parsed_args.market == 'shares':
            return ['SECID', 'BOARDID', 'SHORTNAME', 'ISIN', 'PREVPRICE',
                    'PREVDATE']
        elif parsed_args.market == 'bonds':
            return ['SECID', 'BOARDID', 'SHORTNAME', 'YIELDATPREVWAPRICE', 'COUPONPERCENT',
                    'COUPONVALUE', 'COUPONPERIOD', 'MATDATE', 'OFFERDATE']

    def do_action(self, parsed_args):
        data = self._list_securities(parsed_args)
        return data['securities']


class MarketdataList(SecuritiesBase):
    def _default_columns(self, parsed_args):
        if parsed_args.market == 'shares':
            return ['SECID', 'BOARDID', 'OPEN', 'LOW', 'HIGH', 'LAST',
                    'VOLTODAY', 'VALTODAY_RUR', 'UPDATETIME']
        elif parsed_args.market == 'bonds':
            return ['SECID', 'BOARDID', 'OPEN', 'LOW', 'HIGH', 'LAST',
                    'VOLTODAY', 'VALTODAY_RUR', 'UPDATETIME']

    def do_action(self, parsed_args):
        data = self._list_securities(parsed_args)
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
