from cliff import command
from cliff import show
from cliff import lister


class Lister(lister.Lister):
    def _default_columns(self, parsed_args):
        return []

    def get_parser(self, prog_name):
        parser = super(Lister, self).get_parser(prog_name)
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

    def take_action(self, parsed_args):
        items = self.do_action(parsed_args)

        all_columns = items[0].keys() if items else []
        default_columns = self._default_columns(parsed_args)
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
                value_formatter = getattr(self, '_%s_formatter' % column.lower(), None)
                if value_formatter:
                    value = value_formatter(parsed_args.formatter, value)
                row.append(value)

            rows.append(row)
        return columns, rows


class ShowOne(show.ShowOne):
    def take_action(self, parsed_args):
        data = self.do_action(parsed_args)
        return self.dict2columns(data)


class Command(command.Command):
    def take_action(self, parsed_args):
        return self.do_action(parsed_args)
