class DefaultVendor:
    """
    Default class for modem vendors
    """

    vendor_name = "default"
    vid = "ffff"

    interface_name = ""
    mode_status_command = ""
    ecm_mode_response = ""
    ecm_mode_setter_command = ""
    reboot_command = ""
    pdp_activate_command = ""
    pdp_status_command = ""
    ccid_command = ""


class DefaultModule(DefaultVendor):
    """
    Default module class that contains default parameters
    """

    product_name = "default"
    pid = "ffff"

    def __init__(self, module_name="default", pid="ffff", vendor_object=DefaultVendor()):
        self.module_name = module_name
        self.pid = pid
        self.vendor_name = vendor_object.vendor_name
        self.vid = vendor_object.vid
        self.interface_name = vendor_object.interface_name
        self.mode_status_command = vendor_object.mode_status_command
        self.ecm_mode_setter_command = vendor_object.ecm_mode_setter_command
        self.ecm_mode_response = vendor_object.ecm_mode_response
        self.reboot_command = vendor_object.reboot_command
        self.pdp_activate_command = vendor_object.pdp_activate_command
        self.pdp_status_command = vendor_object.pdp_status_command
        self.ccid_command = vendor_object.ccid_command
