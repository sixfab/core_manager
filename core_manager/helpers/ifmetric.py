import time
from helpers.commander import shell_command

def change_metric_in_line(line, metric):
    list_of_data = line.split(" ")

    for value in list_of_data:
        if value == "":
            list_of_data.remove(value)

    metric_index = list_of_data.index("metric")
    metric_value_index = metric_index + 1
    list_of_data[metric_value_index] = str(metric)

    new_line = ""

    for index, word in enumerate(list_of_data):
        if index == len(list_of_data) - 1:
            new_line += word
        else:
            new_line += f"{word} "
    
    return new_line
        

def set_metric(interface, metric):

    default_route_lines = []
    dev_lines = []

    output = shell_command("ip route show")

    if output[2] != 0:
        raise RuntimeError('Error occured on "ip route list" command!')

    for line in output[0].splitlines():

        line = line.strip()
        
        if interface in line:
            if "default" in line:
                default_route_lines.append(line)
            else:
                dev_lines.append(line)

    # Choose the correct line
    default_line = ""
    dev_line = ""

    for line in default_route_lines:
        if "metric" in line:
            default_line = line
            break
    
    for line in dev_lines:
        if "metric" in line:
            dev_line = line
            break

    # delete route first
    for line in dev_lines:
        shell_command(f"sudo ip route del {line}")
        if output[2] != 0:
            raise RuntimeError(f'Error occured on "ip route del {line}" command!')
            
    for line in default_route_lines:
        output = shell_command(f"sudo ip route del {line}")
        if output[2] != 0:
            raise RuntimeError(f'Error occured on "ip route del {line}" command!')
        

    # Change the metrics
    default_line= change_metric_in_line(default_line, metric)
    dev_line = change_metric_in_line(dev_line, metric)

    # Add the routes back
    dev_is_ok = False
    for _ in range(3):
        if not dev_is_ok:
            output = shell_command(f"sudo ip route add {dev_line}")
            if output[2] != 0:
                dev_is_ok = False
                time.sleep(1)
            else:
                dev_is_ok = True
    
    default_is_ok = False
    for _ in range(3):
        if not default_is_ok:
            output = shell_command(f"sudo ip route add {default_line}")
            if output[2] != 0:
                default_is_ok = False
                time.sleep(1)
            else:
                default_is_ok = True
        
    if not dev_is_ok or not default_is_ok:
        raise RuntimeError(f'Error occured on "ip route add" command!')
