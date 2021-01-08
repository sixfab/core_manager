
import platform 
from helpers.serial import send_at_com
from helpers.config import read_config, save_system_id

def identify_setup():
    # Modem identification
    # -----------------------------------------
    output = send_at_com("ATI", "OK")
    modem_info = output[0].replace("\n", " ") if output[2] == 0 else ""
    # IMEI
    output = send_at_com("AT+CGSN","OK")
    raw_imei = output[0] if output[2] == 0 else ""
    imei_filter = filter(str.isdigit, raw_imei)
    imei = "".join(imei_filter)
    # CCID
    output = send_at_com("AT+CCID","OK")
    raw_ccid = output[0] if output[2] == 0 else ""
    ccid_filter = filter(str.isdigit, raw_ccid)
    ccid = "".join(ccid_filter)
    # SW version
    output = send_at_com("AT+CGMR","OK")
    sw_ver = output[0].split("\n")[1] if output[2] == 0 else ""

    # OS identification
    # -----------------------------------------
    architecture = str(platform.architecture()[0])
    machine = str(platform.machine())
    kernel_release = str(platform.release())
    version = str(platform.version())
    system_name = str(platform.system())
    host_name = str(platform.node())
    os_platform = str(platform.platform())

    system_id = {}
    system_id.update(
        {
            "arc" : architecture,
            "machine" : machine,
            "kernel" : kernel_release,
            "version" : version,
            "system_name" : system_name,
            "host_name" : host_name,
            "platform" : os_platform,
        }
    )

    save_system_id(system_id, True)

    modem_id = {}
    modem_id.update(
        {
            "modem_info" : modem_info,
            "imei" : imei,
            "ccid" : ccid,
            "sw_version" : sw_ver,
        }
    )

    save_system_id(modem_id)