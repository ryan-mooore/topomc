from nbt.nbt import TAG_Long_Array, TAG_Int  # type: ignore


def unstream(
    data: TAG_Long_Array, version_tag: TAG_Int, bits_per_value: int, int_size: int
) -> list[int]:
    """
    This function is a pythonic adaptation of Reddit user bxny5's unstream
    function for decoding minecraft chunkheightmap data, written in perl.
    https://www.reddit.com/r/Minecraft/comments/bxny75/fun_with_chunk_data_heightmap_edition/
    """
    legacy = True
    # 2230 == MC version 1.15.2 ( this is the cut off )
    if version_tag.value > 2230:
        legacy = False

    bl = 0
    result = []
    value = 0

    for byte in data:
        for num in range(int_size):
            bit = (byte >> num) & 0x01
            value = (bit << bl) | value
            bl += 1
            if bl >= bits_per_value:
                result.append(value)
                value = 0
                bl = 0
        if not legacy:
            bl = 0

    return result
