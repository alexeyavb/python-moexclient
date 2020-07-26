from moexclient.cmd import base


class IndexList(base.Lister):
    def take_action(self, parsed_args):
        data = self.app.moex.indices.list()
        return data['indices']['columns'], data['indices']['data']
