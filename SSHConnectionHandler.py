# SSH handler to run ssh commands at remote machine.
# Wrapper over paramiko's ssh to allow clean ssh commands handling.

# Global imports.
import paramiko
import argparse
import os, sys


# Local imports.
from Logger import SetUpLogger
from paramiko_expect import SSHClientInteraction

class SSHConn2Machine:
    """
    Creates an SSH Connection to Remote Machine.
    """
    def __init__(self, ServerIPAddress, userName, password):
        self.ServerIPAddress = ServerIPAddress
        self.userName = userName
        self.password = password

        self.logger = SetUpLogger(loggerName='SSH Connection',)

        # SSH Connection object provided by paramiko.
        self.sshClient = None

        # IO Streams to the server.
        self.stdin = None
        self.stdout = None
        self.stderr = None

        # Decrease this if you trust that your server is faster and no command
        # will take more that 2min to process.
        self.sshCommandsTimeout = 120

        # Hold command's output as string with newline chars.
        self.output = ""
        self.exitStatus = None
        self.error = ""

        # Interactive SSH.
        self.interact = None

    def RefreshRecords(self):
        """
        Refresh the connection details locally.
        """
        self.stdin = None
        self.stdout = None
        self.stderr = None

        self.output = ""
        self.exitStatus = None
        self.error = ""

    def SSHConnect(self):
        """
        Create SSH Connection to remote client.
        :return: Create connection object.
        """
        self.logger.info("Creating SSH Connection :{}@{}: with password :{}:".\
                            format(self.userName, self.ServerIPAddress, self.password))

        try:
            # Create a new SSHClient.
            self.sshClient = paramiko.SSHClient()

            # Load host keys from a system (read-only) file.
            self.sshClient.load_system_host_keys()

            # Trust the remote machine and don't reject the connection.
            self.sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect to an SSH server and authenticate to it.
            self.sshClient.connect( self.ServerIPAddress,
                                    username=self.userName,
                                    password=self.password,
                                    timeout=60)

            self.logger.info("SSH Connection established to {}".\
                                    format(self.ServerIPAddress))

        except Exception as error:
            self.logger.error("SSHConnect raised : {} while connecting to {}".\
                              format(error, self.ServerIPAddress))
            raise error


    def RunCommands(self, command):
        """
        Run param command on ssh client at server.
        Wait for the command to complete or fail.
        return "success" / "fail" in respective cases.
        :param command: ssh command to be run at server.
        :return: command result
        """
        # Clear older command's output and status code.
        self.logger.info("Running CMD > {}".format(command))
        self.RefreshRecords()

        if not self.sshClient:
            self.logger.error("SSH connection is needed before running commands at server")
            raise Exception ("SSH connection not present to server")

        try:
            self.stdin, self.stdout, self.stderr = self.sshClient.exec_command(
                                                        command,
                                                        timeout=self.sshCommandsTimeout)
        except Exception as error:
            self.logger.error("Failed while running ssh command {} at server {} with error {}".
                              format(command, self.ServerIPAddress, error))
            return "fail"

        # ** Immediately check for the exit status of command. ** #

        # Get the SSH transport channel ( follows socket data behaviour ).
        channel = self.stdout.channel

        # Ensure the channel is not closed before going ahead.
        if channel.closed:
            self.logger.error("SSH Channel was closed abruptly after sending cmd")
            return "fail"

        # Reading some stdout data to prevent read block hang.
        stdoutChunks = []
        stdoutChunks.append(channel.recv(1024))

        # Wait until the channel is closed because of transport conn error.
        # Or till there is something to read on recv port, indicating command returned.
        # Or read is available on stderr indicating presence of internal error.

        # Note : Don't use recv_exit_status, it may hold in case read operations are
        #           not run and
        while not channel.closed or channel.recv_ready() or channel.recv_stderr_ready():
            # Read present on stdout from command.
            if channel.recv_ready():
                stdoutChunks.append(channel.recv(1024))

            # Read present from stderr, indicating command failed.
            elif channel.recv_stderr_ready():
                self.error = self.stderr.channel.recv_stderr(1024)
                self.logger.error(" Received error {} while running command {}".\
                                    format(self.error, command))

                self.exitStatus = channel.recv_exit_status()
                return "fail"

            # There was nothing to read, probably command execution complete,
            # Let's check exit_status_ready to know if command execution is over.
            elif channel.exit_status_ready():
                self.logger.info("Command execution completed")
                break

        # Just confirm that command has nothing pending.
        self.exitStatus = channel.recv_exit_status()

        self.logger.info("Command exit status {}".format(self.exitStatus))
        if not channel.closed:
            # Close the channel.
            channel.close()

        self.logger.info("Output > {}".format(str(stdoutChunks)))

        # get command output in string format.
        for line in stdoutChunks:
            self.output += line

        return "success"

    def GetCmdOutput(self):
        """
        Return command's output.
        :return:
        """
        return self.output

    def GetExitStatus(self):
        """
        Get exit status of commmand.
        :return:
        """
        return self.exitStatus

    def GetError(self):
        """
        Get Error from command execution.
        :return:
        """
        return self.error

    def Close(self):
        """
        Close SSH connection to server.
        """
        self.logger.info("Closed the SSH Client")
        self.sshClient.close()

    def GetInteractiveSSh(self):
        """
        Get an interactive object for running commands.
        """
        try:
            self.interact = SSHClientInteraction(self.sshClient,
                                                 timeout = 10,
                                                 encoding='utf-8',
                                                 display = True,
                                                 buffer_size=100000)

        except Exception as error:
            self.logger.error("Couldnt get a SSHClientInteraction session to server")
            raise error

    def expect(self, prompt):
        self.interact.expect(prompt)

    def send(self, command):
        self.interact.send(command)

# Test code, run from command line.
def main(ServerIPAddress, userName, password):
    # Create a SSH connection object.
    SSHObj = SSHConn2Machine(ServerIPAddress, userName, password)
    SSHObj.SSHConnect()

    SSHObj.RunCommands("ls")
    print SSHObj.GetCmdOutput()

    SSHObj.RunCommands("cd Nitin")
    print SSHObj.GetCmdOutput()

    SSHObj.GetInteractiveSSh()
    SSHObj.expect('.*:~.*\$.*')

    SSHObj.send("ls")
    SSHObj.expect('.*:~.*\$.*')

# Unit testing.
if __name__ == "__main__":
    # Create a argument parser object.
    parser = argparse.ArgumentParser( description = __doc__,
                                      prog = "SSH Handler",
                                      formatter_class = argparse.RawDescriptionHelpFormatter,
                                      usage = "%(prog)s ,Arguments :: " + \
                                              "<HOST> <USER NAME> <PASSWORD>" )

    # Add arguments to the parser.
    parser.add_argument('host', help="Help for this command")
    parser.add_argument('username', help="Username for login")
    parser.add_argument('password', help="Password for login")

    args = parser.parse_args()
    main(args.host, args.username, args.password)
