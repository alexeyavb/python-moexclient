from cliff import command
from cliff import show
from cliff import lister


class Lister(lister.Lister):
    _default_columns = tuple()

    def get_parser(self, prog_name):
        parser = super(Lister, self).get_parser(prog_name)
        self.init_parser(parser)
        arg_group = parser.add_argument_group(
            title="additional arguments",
            description="additional vinfra arguments"
        )
        arg_group.add_argument(
            "--long",
            action="store_true",
            help="enable access and listing of all fields of objects."
        )
        return parser

    def init_parser(self, parser):
        pass

    def take_action(self, parsed_args):
        items = self.do_action(parsed_args)

        all_columns = items[0].keys() if items else []
        default_columns = list(self._default_columns)
        if not default_columns:
            default_columns = all_columns

        if parsed_args.long or parsed_args.columns or not default_columns:
            columns = all_columns
        else:
            columns = default_columns

        rows = []
        for item in items:
            row = []
            for column in columns:
                value = item[column]
                row.append(value)

            rows.append(row)
        return columns, rows


class ShowOne(show.ShowOne):
    def get_parser(self, prog_name):
        parser = super(ShowOne, self).get_parser(prog_name)
        self.init_parser(parser)
        return parser

    def init_parser(self, parser):
        pass

    def take_action(self, parsed_args):
        data = self.do_action(parsed_args)
        return self.dict2columns(data)
