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
        self.free_priorities = list(range(self.priority, self.priority+10))

    def update_priority(self, priority):
        self.priority = priority
        self.child_int_table = {}
        self.free_priorities = list(range(self.priority, self.priority+10))

    def add_child_interface(self, name):
        try:
            self.child_int_table[name] = self.free_priorities.pop(0)
        except Exception as error:
            raise ValueError("No free priority number exist in free_priorities list!") from error
        else:
            return int(self.child_int_table[name])

    def remove_child_interface(self, name):
        value = self.child_int_table.get(name, None)
        if value:
            self.free_priorities.append(value)
            self.free_priorities.sort()
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
