import subprocess

def send_at_com(command, desired):
    try:
        cp = subprocess.run(["atcom", command, "--find", desired], universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return (cp.stdout, cp.stderr, cp.returncode)
    except Exception as e:
        print(e)
        return False