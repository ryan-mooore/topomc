def unstream(data, bits_per_value, int_size):
    """
    This function is a pythonic adaptation of Reddit user bxny5's unstream
    function for decoding minecraft chunkheightmap data, written in perl.
    https://www.reddit.com/r/Minecraft/comments/bxny75/fun_with_chunk_data_heightmap_edition/
    """

    bl = 0
    result = []
    value = 0

    for byte in data:
        for num in range(int_size): # int_size-1, to support 1.16+
            bit = (byte >> num) & 0x01
            value = (bit << bl) | value
            bl += 1
            if bl >= bits_per_value:
                result.append(value)
                value = 0
                bl = 0
        # or bl = 0   
    return result
