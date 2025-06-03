import socket

from rich import print
from ssh2.session import Session


class SSH:
    def __init__(self, host="hp-ml350egen8-01.rhts.eng.bos.redhat.com", auth=("root", "dog8code")):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, 22))
        self.session = Session()
        self.session.handshake(sock)
        self.session.userauth_password(*auth)

    def run(self, command):
        """run a command on the host and return the results"""
        print(f"[bold blue]Executing command:[/] {command}")
        channel = self.session.open_session()
        channel.execute(command)
        size, data = channel.read()
        results = ""
        while size > 0:
            results += data.decode("utf-8")
            size, data = channel.read()
        channel.close()
        return {"results": results, "status": channel.get_exit_status()}


class OptionException(BaseException):
    def __init__(self, bad_options=None):
        super().__init__(f"Received unexpected option(s): {bad_options}")


class Hammer:
    def __init__(self):
        self._command = "hammer"
        self._options = [
            "autocomplete",
            "csv",
            "csv_separator",
            "fetch_ca_cert",
            "interactive",
            "no_headers",
        ]
        self.connection = SSH()

    def _in_options(self, options=None, attributes=None):
        options = self._options if not options else options + self._options
        errs = [arg for arg in attributes if arg not in options]
        if errs:
            raise OptionException(errs)
        return True

    def _add_attributes(self, attributes):
        for name, value in attributes.items():
            self.__dict__[name] = value

    def _execute(self, sub_command, options):
        cmd_string = " ".join(
            [self._command, sub_command] + [f"--{name} {value}" for name, value in options.items()]
        )
        self._result = self.connection.run(cmd_string)
        if int(self._result["status"]) == 0:
            self._add_attributes(options)


class ActivationKey(Hammer):
    def __init__(self, **kwargs):
        self._command = "hammer activation-key"
        self._options = [
            "id",
            "name",
            "organization",
            "organization_id",
            "organization_label",
        ]
        self.subscription = self.Subscription()

    def copy(self, **kwargs):
        _options = ["new_name"]
        if self._in_options(_options, kwargs):
            self._execute("copy", kwargs)

    class Subscription(Hammer):
        def __init__(self, **kwargs):
            self._command = "hammer activation-key subscription"
            self._options = [
                "id",
                "name",
                "organization",
                "organization_id",
                "organization_label",
            ]

        def add(self, **kwargs):
            _options = ["subscription_id"]
            if self._in_options(_options, kwargs):
                self._execute("copy", kwargs)
