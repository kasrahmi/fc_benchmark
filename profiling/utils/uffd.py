import tmux
import profiling.utils.constants as constants

class Uffd:
    def __init__(self, session_name: str) -> None:
        self.session_name = session_name + "_uffd"
        self.tmux_client = tmux.Tmux

    def create_uffd_session(self) -> None:
        self.tmux_client.kill_session(self.session_name)
        self.tmux_client.create_session(self.session_name)
        self.tmux_client.run_command_in_session(self.session_name, f"sudo {constants.FC_UFFD_PATH} {constants.UFFD_SOCKET} {constants.SNAPSHOT_PATH}/mem_file")

    def get_uffd_pages(self) -> int:
        last_line = self.tmux_client.capture_last_stdout_line(self.session_name)
        # print(f"Last line captured: '{last_line}'")  # Debugging output
        try:
            return int(last_line.split()[-1])
        except (IndexError, ValueError):
            raise ValueError(f"Failed to parse the number of uffd pages from the last line: '{last_line}'")