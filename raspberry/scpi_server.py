import sys


class ScpiCommand(object):
    def write(self, args):
        return ""

    def read(self, args):
        return ""


class ScpiCommandInline(ScpiCommand):
    def __init__(self, read=None, write=None):
        super().__init__()
        self.readc = read
        self.writec = write

    def write(self, args):
        return self.writec(args) if self.writec else "ERR: Read only"

    def read(self, args):
        return self.readc(args) if self.readc else "ERR: Write only"


class ScpiCommandFunctor(ScpiCommand):
    SCPI_READ = 1
    SCPI_WRITE = 2

    def __init__(self, func):
        super().__init__()
        self.func = func

    def write(self, args):
        return self.func(self.SCPI_WRITE, args)

    def read(self, args):
        return self.func(self.SCPI_READ, args)


class ScpiServer(object):
    def __init__(self, cmds, idn="SCPI_SERVER"):
        self.cmds = cmds
        self.idn = idn

    def register(self, cmd):
        pass

    def match(self, cmd, ref):
        pass

    def execute_command(self, cmd, parent=""):
        scmd = cmd.split()[0]
        read = False
        # check for read/write
        if scmd[-1] == '?':
            read = True
            scmd = scmd[:-1]
        # print("%s %s %s"%(cmd, scmd, read))
        # reset parent id if begins commands with :
        if scmd[0] == ':':
            scmd = scmd[1:]
            parent = "".join(scmd.split(":")[:-1])
        elif parent:
            scmd = parent + ":" + scmd

        # print(scmd)
        scmdc = scmd.split(":")
        for ref in self.cmds:
            refc = ref.split(":")
            if compare_chain(scmdc, refc):
                if read:
                    return self.cmds[ref].read(cmd.split()[1:]), parent
                else:
                    return self.cmds[ref].write(cmd.split()[1:]), parent
        #print("No such command")
        return "<<No such command", parent

    def execute(self, cmd):
        commands = [str.strip() for str in (":" + cmd).split(";") if str]
        parent = ""
        finalresponse = ""

        for s in commands:
            # print(s)
            if s[0] == '*':
                response, parent = self.execute_command(s, "")
            else:
                response, parent = self.execute_command(s, parent)
            #print(response)
            finalresponse += response + "\r\n"
        return finalresponse


    def idn(self):
        return self.idn


def compare(s, ref):
    # print("<< %s %s" % (s, ref))
    s = s.lower()
    if len(s) > len(ref):
        return False
    for i in range(0, len(ref)):
        # print("< %s %s" % (s[i], ref[i]))
        if ref[i].isupper() or ref[i] in '*':
            if i >= len(s) or ref[i].lower() != s[i]:
                return False
        else:
            if i >= len(s):
                break
            if ref[i].lower() != s[i]:
                return False
    return True


def compare_chain(sc, refc):
    if len(sc) != len(refc):
        return False
    for i in range(0, len(refc)):
        # print("%s = %s : %s" % (sc[i], refc[i], compare(sc[i], refc[i])))
        if not compare(sc[i], refc[i]):
            return False
    return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: %s <command>" % sys.argv[0])
        exit(0)
    cmd = (sys.argv[1] + "\r\n").strip()
    cmds = {
        "NAVigate:STATus": ScpiCommandInline(write=lambda args: "WRITE %s" % args, read=lambda args: "READ %s" % args),
        "NAVigate:PICKup": ScpiCommandInline(write=lambda args: "WRITE %s" % args, read=lambda args: "READ %s" % args),
        "NAVigate:DROPoff": ScpiCommandInline(write=lambda args: "WRITE %s" % args, read=lambda args: "READ %s" % args),
        "*IDN": ScpiCommandInline(write=lambda args: None, read=lambda args: "SCPI stuff")
    }
    server = ScpiServer(cmds)
    server.execute(cmd)
