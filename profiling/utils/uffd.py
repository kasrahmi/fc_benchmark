import subprocess


class Uffd:
    def __init__(self) -> None:
        pass

    def get_uffd_pages(self) -> int:
        result = subprocess.run(f"tmux capture-pane -t uffd_handler -p", shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            return -1
        lines = result.stdout.strip().split('\n')
        if lines:
            last_line = lines[-1]
            return int(last_line.split()[-1])

        else:
            raise ValueError("No output captured")