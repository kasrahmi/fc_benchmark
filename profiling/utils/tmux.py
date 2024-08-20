import subprocess


class Tmux:
    def __init__(self) -> None:
        pass

    def create_session(session_name: str) -> None:
        subprocess.run(f'tmux new-session -d -s {session_name}', shell=True)
    
    def kill_session(session_name: str) -> None:
        subprocess.run(f'tmux kill-session -t {session_name}', shell=True)
    
    def run_command_in_session(session_name: str, command: str) -> None:
        subprocess.run(f'tmux send-keys -t {session_name} "{command}" Enter', shell=True)

    def capture_last_stdout_line(session_name: str) -> str:
        command = f'tmux capture-pane -t {session_name} -p'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')
        if lines:
            number = lines[-1]
        else:
            raise ValueError("No output captured")
        
        return number