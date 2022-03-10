class NetInterface:
    name = None
    actual_metric = None
    desired_metric = None
    metric_factor = None
    status = None
    connection_status = None
    if_type = None
    priority = None


class InterfaceTypes:
    CELLULAR="TYPE_C"
    WIFI="TYPE_W"
    ETHERNET="TYPE_E"
    UNKNOWN="TYPE_X"


class InterfaceType:
    def __init__(self, name, priority):
        self.name = name
        self.priority = priority
        self.child_int_table = {}

    def update_priority(self, priority):
        self.priority = priority

    def add_child_interface(self, name):
        dict_len = len(self.child_int_table)
        dict_len %= 10
        self.child_int_table[name] = self.priority + dict_len
        return int(self.child_int_table[name])

    def remove_child_interface(self, name):
        self.child_int_table.pop(name)

ethernet = InterfaceType(InterfaceTypes.ETHERNET, 10)
wifi = InterfaceType(InterfaceTypes.WIFI, 30)
cellular = InterfaceType(InterfaceTypes.CELLULAR, 50)
unknown = InterfaceType(InterfaceTypes.UNKNOWN, 70)

interface_types = {
    ethernet.name: ethernet,
    wifi.name: wifi,
    cellular.name: cellular,
    unknown.name: unknown
}
