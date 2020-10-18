#!/usr/bin/env python

import logging
import os
import signal
import sys

from cliff import app as cliff_app
from cliff import commandmanager as cliff_commandmanager

from moexclient.client import base
from moexclient.cmd import board
from moexclient.cmd import engine
from moexclient.cmd import index
from moexclient.cmd import market
from moexclient.cmd import securities

LOG = logging.getLogger(__name__)

COMMANDS_MAP = {
    'engine_list': engine.EngineList,
    'market_list': market.MarketList,
    'board_list': board.BoardList,

    'security_list': securities.SecurityList,
    'security_find': securities.SecurityFind,
    'security_show': securities.SecurityShow,
    'security_board-list': securities.SecurityBoardList,

    'stock_bonds_list': securities.StockBondsList,
    'stock_bonds_find': securities.StockBondsFind,

    'stock_shares_list': securities.StockSharesList,
    'stock_shares_find': securities.StockSharesFind,

    'stock_index_list': securities.StockIndexList,
    'stock_index_find': securities.StockIndexFind,
    # 'marketdata_list': securities.MarketdataList,
    # 'marketdata_show': securities.MarketdataShow,
    # 'index_list': index.IndexList,
}


class MoexApp(cliff_app.App):
    def __init__(self):
        super(MoexApp, self).__init__(
            description='Command line client for MOEX stock market',
            version='0.0.1',
            command_manager=cliff_commandmanager.CommandManager(None),
            deferred_help=True,
        )
        self._init_commands()
        self.moex = base.MoexClient()

        for name in ('requests.packages.urllib3.connectionpool',
                     'urllib3.connectionpool',
                     'stevedore.extension'):
            logging.getLogger(name).setLevel(logging.WARNING)

    def _init_commands(self):
        for cmd_name, cmd_class in COMMANDS_MAP.items():
            self.command_manager.add_command(cmd_name.replace('_', ' '), cmd_class)

    def run_subcommand(self, argv):
        if argv[0] == 'help':
            # WA cliff to unable print help with optional command args
            for arg in list(argv):
                if arg.startswith('-'):
                    argv.remove(arg)
        return super(MoexApp, self).run_subcommand(argv)

    def print_message(self, message):
        self.stderr.write(message + '/n')


def sigint_handler(signalnum, frame):
    LOG.debug("Command interrupted by SIGINT")
    sys.exit(1)


def main():
    signal.signal(signal.SIGINT, sigint_handler)
    ret = MoexApp().run(sys.argv[1:])

    # flush stdout to avoid interpretator fail on stdout descriptor closing
    try:
        sys.stdout.flush()
    except IOError:
        pass

    return ret


if __name__ == '__main__':
    sys.exit(main())
