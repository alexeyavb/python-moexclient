from moexclient import exceptions
from moexclient.cmd import base


def get_primary_board(security_manager, secid):
    security = security_manager.get(secid)
    primary_board = None
    for board in security['boards']:
        if board['is_primary']:
            return board['boardid']
    msg = 'Cannot find a primary board: secid=%s' % secid
    raise exceptions.MoexCommandError(msg)


# NOTE: this command doesn't work well because iss returns duplicated objects,
# and 'start' parameter confuses.
class SecurityList(base.Lister):
    _default_columns = ('secid', 'isin', 'shortname', 'name', 'group', 'primary_boardid')

    def init_parser(self, parser):
        parser.add_argument(
            '--query',
            help='Filter securities by query'
        )
        parser.add_argument(
            '--engine',
            help='Filter securities by engine'
        )
        parser.add_argument(
            '--market',
            help='Filter securities by market. If engine is not specified, '
                 '"stock" engine is used.'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Do not apply is_trading filtering'
        )
        parser.add_argument(
            '--start',
            type=int,
            help='Start index'
        )
        super(SpecList, self).init_parser(parser)

    def do_action(self, parsed_args):
        is_trading = None
        if not parsed_args.all:
            is_trading = 1
        data = self.app.moex.securities.list(query=parsed_args.query,
                                             engine=parsed_args.engine,
                                             market=parsed_args.market,
                                             is_trading=is_trading,
                                             start=parsed_args.start)

        # Somehow iss can return deplicated objects. Remove duplicates:
        securities = data['securities']
        securities_set = set(tuple(sec.items()) for sec in securities)
        return [dict(sec) for sec in securities_set]


class SecurityFind(base.Lister):
    _default_columns = ('secid', 'isin', 'shortname', 'name', 'group', 'primary_boardid')

    def init_parser(self, parser):
        parser.add_argument(
            'query',
            help='Filter securities by query'
        )
        parser.add_argument(
            '--engine',
            help='Filter securities by engine'
        )
        parser.add_argument(
            '--market',
            help='Filter securities by market. If engine is not specified, '
                 '"stock" engine is used.'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Do not apply is_trading filtering'
        )
        parser.add_argument(
            '--start',
            type=int,
            help='Start index'
        )
        super(SecurityFind, self).init_parser(parser)

    def do_action(self, parsed_args):
        is_trading = None
        if not parsed_args.all:
            is_trading = 1
        data = self.app.moex.securities.list(query=parsed_args.query,
                                             engine=parsed_args.engine,
                                             market=parsed_args.market,
                                             is_trading=is_trading,
                                             start=parsed_args.start)

        # Somehow iss can return deplicated objects. Remove duplicates:
        securities = data['securities']
        securities_set = set(tuple(sec.items()) for sec in securities)
        return [dict(sec) for sec in securities_set]


class SecurityInfo(base.ShowOne):
    def init_parser(self, parser):
        parser.add_argument(
            'security',
            help='Security ID to show'
        )
        super(SecurityInfo, self).init_parser(parser)

    def do_action(self, parsed_args):
        data = self.app.moex.securities.get(parsed_args.security)
        res = {}
        for item in data['description']:
            res[item['name']] = item['value']
        return res


class SecurityInfoBoards(base.Lister):
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
        parser.add_argument(
            '--all',
            action='store_true',
            help='List not trading boards'
        )
        super(SecurityInfoBoards, self).init_parser(parser)

    def do_action(self, parsed_args):
        is_traded = None
        if not parsed_args.all:
            is_traded = 1
        data = self.app.moex.securities.get(parsed_args.security)
        boards = data['boards']
        if not parsed_args.all:
            boards = filter(lambda item: item['is_traded'] == 1, boards)
        return boards


class SecurityMixin(object):
    @staticmethod
    def _check_single_security(secid, securities):
        if not securities:
            raise exceptions.MoexCommandError(
                'No engine securities found for secid=%s' % secid)
        if len(securities) > 1:
            # this shouldn't happen in practice.
            raise exceptions.MoexCommandError(
                'More then one securities found for secid=%s' % secid)
        return securities[0]


class SecurityShow(base.ShowOne, SecurityMixin):
    def init_parser(self, parser):
        parser.add_argument(
            'security',
            help='Security ID to show'
        )
        parser.add_argument(
            '--board',
            help='Security board ID'
        )
        super(SecurityShow, self).init_parser(parser)

    def do_action(self, parsed_args):
        secid = parsed_args.security
        data = self.app.moex.get_securities(secid, boardid=parsed_args.board)
        return self._check_single_security(secid, data['securities'])


class SecurityMarketData(base.ShowOne, SecurityMixin):
    def init_parser(self, parser):
        parser.add_argument(
            'security',
            help='Security ID to show'
        )
        parser.add_argument(
            '--board',
            help='Security board ID'
        )
        super(SecurityMarketData, self).init_parser(parser)

    def do_action(self, parsed_args):
        secid = parsed_args.security
        data = self.app.moex.get_securities(secid, boardid=parsed_args.board)
        return self._check_single_security(secid, data['marketdata'])
