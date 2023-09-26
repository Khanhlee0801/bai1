# Viet code Python quet thong tin thiet bi OLT ALU NOKIA
# MENU : suy hao quang, luu luong PON (traffic), UP/DOWN LINK, BER cua PON
# Gui thong bao (gui den group Telegram)

from pysnmp.hlapi import *
import telegram
import random
import requests

# Thông tin OLT
olt_ip = "172.16.1.1"
olt_community = "public"

# Hàm gửi thông tin qua telegram
def send_test_message():
  try :
    random_number = random.randint(0, 1000)
    telegram_notify = telegram.Bot("[TOKEN]")
    message = "random {}".format(random_number)
    telegram_notify.send_message(chat_id="[CHAT_ID]",text=message, parse_mode="Markdown")
    except Exception as ex:
      print(ex)
send_test_message()

# Mã truy cập của bot và chat_id group chat
bot_token = "YOUR_BOT_TOKEN"
chat_id = "RECIPIENT_CHAT_ID"
message = "Hello, this is a notification from your bot!"
response = send_telegram_notification(bot_token, chat_id, message)
print(response) # phan hoi

# Hàm trích xuất SNMP
def extract_snmp_value(snmp_object):
    errorIndication, errorStatus, errorIndex, varBinds = next(snmp_object)
    if errorIndication:
        return None
    elif errorStatus:
        return None
    else:
        return varBinds[0][1].prettyPrint()

# Trạng thái OLT
def get_olt_status():
    oid = "" # OID mô tả hệ thống SNMP
    error_indication, error_status, error_index, var_binds = next(
        getCmd(SnmpEngine(),
               CommunityData(olt_community),
               UdpTransportTarget((olt_ip, 161)),
               ContextData(),
               ObjectType(ObjectIdentity(oid)))
    )
    if error_indication or error_status:
        return None
    else:
        return var_binds[0][1].prettyPrint()

# kiem tra tinh trang UP/DOWN
def get_up_down_time():
    oid = "" # OID up time
    snmp_object = getCmd(SnmpEngine(),
               CommunityData(olt_community),
               UdpTransportTarget((olt_ip, 161)),
               ContextData(),
               ObjectType(ObjectIdentity(oid)))
    up_time = extract_snmp_value(snmp_object)

    oid = "" # OID down time
    snmp_object = getCmd(SnmpEngine(),
               CommunityData(olt_community),
               UdpTransportTarget((olt_ip, 161)),
               ContextData(),
               ObjectType(ObjectIdentity(oid)))
    down_time = extract_snmp_value(snmp_object)
    if up_time and down_time:
        return f"UP: {up_time} / DOWN: {down_time}"
    else:
        return None

# lưu lượng PON
def get_pon_traffic():
    oid = "" # OID traffic của PON
    snmp_object = getCmd(SnmpEngine(),
               CommunityData(olt_community),
               UdpTransportTarget((olt_ip, 161)),
               ContextData(),
               ObjectType(ObjectIdentity(oid)))
    pon_traffic = extract_snmp_value(snmp_object)
    if pon_traffic:
        return f"Traffic: {pon_traffic}"
    else:
        return None

# suy hao quang PON
def get_pon_optic_loss():
    oid = "" # OID suy hao quang của PON
    snmp_object = next(
        walk(SnmpEngine(),
             CommunityData(olt_community),
             UdpTransportTarget((olt_ip, 161)),
             ContextData(),
             ObjectType(ObjectIdentity(oid)))
    )
    optical_loss_list = [float(varBind[1].prettyPrint()) / 10 for varBind in snmp_object]
    loss_values = ",".join([f"{i+1}: {optical_loss_list[i]} dBm" for i in range(len(optical_loss_list))])
    return f"Optic Loss: {loss_values}"

# BER (bit error rate / ti le loi bit) PON
def get_pon_ber():
    oid = "" # OID BER của PON
    snmp_object = getCmd(SnmpEngine(),
               CommunityData(olt_community),
               UdpTransportTarget((olt_ip, 161)),
               ContextData(),
               ObjectType(ObjectIdentity(oid)))
    ber = extract_snmp_value(snmp_object)
    if ber:
        return f"BER: {ber}"
    else:
        return None

# main
def main():
    # Trạng thái OLT / gửi cảnh báo nếu down lau 5 phut // 300s
    olt_status = get_olt_status()
    if olt_status is None:
        print("OLT DOWN")
    # Thời gian UP/DOWN / gửi cảnh báo khi DOWN lâu
    up_down_time = get_up_down_time()
    if up_down_time is None:
        print("Khong the tinh duoc thoi gian up/down")
    else:
        up_time = int(up_down_time.split(":")[1].strip())
        if down_time > 300:
            print(f"OLT DOWN 5 phut")

    # Lưu lượng PON / gửi cảnh báo nếu lưu lượng vượt ngưỡng 5M
    pon_traffic = get_pon_traffic()
    if pon_traffic is None: #neu khong du du lieu tinh toan
        print("Khong the tinh duoc luu luong PON")
    else:
        traffic = int(pon_traffic.split(":")[1].strip())
        if traffic > 5000000:
            print(f"Luu luong PON vuot nguong khi so sanh voi 5M : ({traffic} > 5M)")

    # Suy hao quang / gửi cảnh báo nếu suy hao quá lâu
    pon_optic_loss = get_pon_optic_loss()
    if pon_optic_loss is None:
        print("Khong the tinh duoc suy hao quang")
    else:
        optical_loss_list = [float(val.split(":")[1].strip()) for val in pon_optic_loss.split(",")[0:-1]]
        for i in range(len(optical_loss_list)):
            if optical_loss_list[i] > 3.0:
                print(f"PON{i+1} suy hao quang cao ({optical_loss_list[i]} dBm)")

    # BER PON / Ti le loi Bit // gửi cảnh báo nếu BER cao // vượt ngưỡng cho trước
    pon_ber = get_pon_ber()
    if pon_ber is None:
        print("Khong the tinh duoc BER (ti le loi Bit) của PON")
    else:
        ber = int(pon_ber.split(":")[1].strip())
        if ber > 10:
            print(f"Canh bao BER (ti le loi Bit) cua PON cao ({ber})")

if _name_ == "_main_":
    main()