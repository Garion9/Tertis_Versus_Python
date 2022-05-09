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
