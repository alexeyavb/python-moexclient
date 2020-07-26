from moexclient.cmd import base


class MarketList(base.Lister):
    def _default_columns(self, parsed_args):
        return ['NAME', 'title']

    def do_action(self, parsed_args):
        return self.app.moex.markets.list()['markets']
