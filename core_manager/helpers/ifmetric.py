from helpers.commander import shell_command

def change_metric_in_line(line, metric):
    if line.find("metric") == -1:
        line += f" metric {metric}"
        return line
    
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
    local_network_routes = []
    dns_routes = []

    output = shell_command("ip route show")

    if output[2] != 0:
        raise RuntimeError('Error occured on "ip route list" command!')

    for line in output[0].splitlines():

        line = line.strip()
        
        if interface in line:
            if "default" in line:
                default_route_lines.append(line)
            elif "8.8.8.8" in line or "8.8.4.4" in line:
                dns_routes.append(line)
            else:
                local_network_routes.append(line)

    # Choose the correct line
    default_line = ""
    local_network_line = ""
    dns_line = ""
    
    if len(default_route_lines) == 1:
        default_line = default_route_lines[0]
    else:
        for line in default_route_lines:
            if "metric" in line:
                default_line = line
                break

    if len(local_network_routes) == 1:
        local_network_line = local_network_routes[0]
    else:
        for line in local_network_routes:
            if "metric" in line:
                local_network_line = line
                break
    
    if len(dns_routes) == 1:
        dns_line = dns_routes[0]
    else:
        for line in dns_routes:
            if interface in line:
                dns_line = line
                break
    
    # delete route first
    for line in local_network_routes:
        shell_command(f"sudo ip route del {line}")
        if output[2] != 0:
            raise RuntimeError(f'Error occured on "ip route del {line}" command!')
            
    for line in default_route_lines:
        output = shell_command(f"sudo ip route del {line}")
        if output[2] != 0:
            raise RuntimeError(f'Error occured on "ip route del {line}" command!')
        
    for line in dns_routes:
        output = shell_command(f"sudo ip route del {line}")
        if output[2] != 0:
            raise RuntimeError(f'Error occured on "ip route del {line}" command!')
        

    # Change the metrics
    default_line= change_metric_in_line(default_line, metric)
    local_network_line = change_metric_in_line(local_network_line, metric)

    # Add the routes back
    output = shell_command(f"sudo ip route add {local_network_line}")
    if output[2] != 0:
        raise RuntimeError(f'Error occured on "ip route add {local_network_line}" command!')


    output = shell_command(f"sudo ip route add {default_line}")
    if output[2] != 0:
        raise RuntimeError(f'Error occured on "ip route add {default_line}" command!')
    
    
    output = shell_command(f"sudo ip route add {dns_line}")
    if output[2] != 0:
        raise RuntimeError(f'Error occured on "ip route add {dns_line}" command!')


