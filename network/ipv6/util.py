import binascii


def standardize_ipv6_format(ipv6_address: str):
    """
    Function used to standardize IPv6 format by expanding the shortened form of address by filling it back with zeroes.

    Parameters:
        ipv6_address (str): IPv6 address in either full or shortened form
    Returns:
        string containing full form of IPv6 address given as parameter
    """
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
    """
    UDP checksum is calculated as 16-bit one's complement pf the one's complement sum of
    pseudo-header bytes (padded with zeroes at the end in order to make a multiple of two octets)

    Parameters:
        ip_pseudo_header (bytes): ipv6-pseudo-header in the form of a byte array
    Returns:
        UDP checksum as a 16-bit long byte array
    """
    checksum = 0

    for i in range(0, len(ip_pseudo_header), 2):
        byte1 = ip_pseudo_header[i]
        byte2 = ip_pseudo_header[i+1]
        byte1 = byte1 << 8
        checksum += byte1 + byte2

    checksum = (checksum >> 16) + (checksum & 0xFFFF)
    checksum = ~checksum & 0xFFFF

    hex_checksum = hex(checksum).lstrip("0x").rstrip("L")
    if len(hex_checksum) != 4:
        zeroes = "0" * (4 - len(hex_checksum))
        hex_checksum = zeroes + hex_checksum

    return binascii.unhexlify(hex_checksum)
