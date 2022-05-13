import binascii


def standardize_ipv6_format(ipv6_address: str):
    segments_count = 8
    ipv6_address = ipv6_address.split("%")[0]
    zeros_index = ipv6_address.find("::")
    if zeros_index > 0:
        zero_segments_count = segments_count - (len(ipv6_address.split(":")) - ipv6_address.split(":").count(""))
        zeros = "0000"
        for i in range(1, zero_segments_count):
            zeros += ":0000"
        ipv6_address = ipv6_address[:zeros_index+1] + zeros + ipv6_address[zeros_index+1:]
    return ipv6_address


def calculate_checksum(ip_pseudo_header: bytes):
    checksum = 0

    for i in range(0, len(ip_pseudo_header), 2):
        byte1 = ip_pseudo_header[i]
        byte2 = ip_pseudo_header[i+1]
        byte1 = byte1 << 8
        checksum += byte1 + byte2

    checksum = (checksum >> 16) + (checksum & 0xFFFF)
    checksum = ~checksum & 0xFFFF

    print(hex(checksum).lstrip("0x").rstrip("L"))

    return binascii.unhexlify(hex(checksum).lstrip("0x").rstrip("L"))
