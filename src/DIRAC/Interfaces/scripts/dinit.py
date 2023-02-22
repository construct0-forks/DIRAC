#!/usr/bin/env python

"""
initialize DCommands/Shorthand Commands session
"""
import os

import DIRAC
from DIRAC import gLogger, S_OK, S_ERROR
from DIRAC.Interfaces.Utilities.DCommands import DSession
from DIRAC.Interfaces.Utilities.DCommands import sessionFromProxy
from DIRAC.Interfaces.Utilities.DConfigCache import ConfigCache
from DIRAC.Core.Base.Script import Script
import DIRAC.Core.Security.ProxyInfo as ProxyInfo


class Params:
    def __init__(self):
        self.fromProxy = False
        self.destroy = False

    def setFromProxy(self, arg):
        self.fromProxy = True

    def getFromProxy(self):
        return self.fromProxy

    def setDestroy(self, arg):
        self.destroy = True

    def getDestroy(self):
        return self.destroy


@Script()
def main():
    params = Params()
    Script.registerArgument("profile name: existing profile section in DCommands config", mandatory=False)
    Script.registerSwitch("p", "fromProxy", "build session from existing proxy", params.setFromProxy)
    Script.registerSwitch("D", "destroy", "destroy session information", params.setDestroy)

    Script.disableCS()

    Script.parseCommandLine(ignoreErrors=True)
    profile = Script.getPositionalArgs(group=True)

    if params.destroy:
        session = DSession()
        os.unlink(session.configPath)
        DIRAC.exit(0)

    session = None
    if params.fromProxy:
        retVal = Script.enableCS()
        ConfigCache(forceRefresh=True).cacheConfig()

        if not retVal["OK"]:
            gLogger.error("Error:", retVal["Message"])
            DIRAC.exit(-1)
        session = sessionFromProxy()
    else:
        session = DSession(profile)

    if not session:
        gLogger.error("Error: Session couldn't be initialized")
        DIRAC.exit(-1)

    session.write()

    try:
        session.checkProxyOrInit()
    except Exception as e:
        gLogger.error("Error:", e)
        DIRAC.exit(-1)

    retVal = session.proxyInfo()
    if not retVal["OK"]:
        gLogger.error(retVal["Message"])
        DIRAC.exit(-1)

    gLogger.notice(ProxyInfo.formatProxyInfoAsString(retVal["Value"]))


if __name__ == "__main__":
    main()
