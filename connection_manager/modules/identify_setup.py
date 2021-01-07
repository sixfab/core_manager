
import platform 
from helpers.serial import send_at_com
from helpers.config import read_config, save_system_id

def identify_setup():
    # Modem identification
    # -----------------------------------------
    modem_info = send_at_com("ATI", "OK")[0]
    modem_info = modem_info.replace("\n", " ")
    # IMEI
    raw_imei = send_at_com("AT+CGSN","OK")[0]
    imei_filter = filter(str.isdigit, raw_imei)
    imei = "".join(imei_filter)
    # CCID
    raw_ccid = send_at_com("AT+CCID","OK")[0]
    ccid_filter = filter(str.isdigit, raw_ccid)
    ccid = "".join(ccid_filter)
    # SW version
    sw_ver = send_at_com("AT+CGMR","OK")[0].split("\n")[1]

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
            "modem_info" : modem_info,
            "imei" : imei,
            "ccid" : ccid,
            "sw_version" : sw_ver,
        }
    )

    save_system_id(system_id)