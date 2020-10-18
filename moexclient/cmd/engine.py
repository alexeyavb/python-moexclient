from moexclient.cmd import base


class EngineList(base.Lister):
    _default_columns = (
        'name',
        'title'
    )

    def do_action(self, parsed_args):
        return self.app.moex.engines.list()['engines']
