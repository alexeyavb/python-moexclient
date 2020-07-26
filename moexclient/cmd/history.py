from moexclient.cmd import base


class CacheBase(base.ShowOne):
    market = None

    def get_parser(self, prog_name):
        parser = super(CacheBase, self).get_parser(prog_name)
        parser.add_argument('--board', required=True)
        return parser

    def take_action(self, parsed_args):
        return self.app.moex.histoty.get(market=self.market, board=parsed_args.board)


class CacheShares(CacheBase):
    market = 'shares'


class CacheBonds(CacheBase):
    market = 'bonds'


def factory(market):
    class_mapping = {
        'shares': CacheShares,
        'bonds': CacheBonds,
    }
    cls = class_mapping.get(market)
    if not cls:
        raise exceptions.CliException(
            "Cannot init command with market %r" % market)
    return cls
