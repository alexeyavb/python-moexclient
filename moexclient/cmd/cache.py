import os

from moexclient.cmd import base


class BaseInit(base.Command):
    def take_action(self, parsed_args):
        markets = self.app.moex.markets.list()['markets']
        cache_dir = os.path.expanduser('~/.moex')
        if not os.path.exists(cache_dir):
            os.mkdir(cache_dir)

        columns = markets['columns']
        data = markets['data']

        for idx, key in enumerate(columns):
            if key.lower() == 'name':
                break
        else:
            raise Exception('Cannot find name key')

        names = []
        for market_data in data:
            names.append(market_data[idx])

        fname = os.path.join(cache_dir, 'markets')
        print(fname)
        with open(fname, 'w') as fd:
            fd.write('\n'.join(names))
