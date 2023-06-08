import Build_Huff_Tree


def read_header(header, header_bits_length):
    header_stack = []
    header_bits = ""
    first_byte = format(header[0], "08b")
    first_byte = first_byte[1:]
    left = 1
    for i in range(1, len(header)):
        current_byte = format(header[i], "08b")
        first_byte += current_byte[:left]
        header_stack.append(first_byte)
        first_byte = current_byte[left:]
        if first_byte[0] == 0:
            node = 0
            node = header_stack.pop()


        left = 8 - len(current_byte)

        byte_bits = format(header[i], "08b")
        cut_indx = 8 - len(current_byte)
        current_byte += byte_bits[:cut_indx]
        byte_bits = byte_bits[cut_indx:]

    print(header_bits)
    # for bit in header_bits:
    #     if bit == "1":


header_to_read, len_of_header = Build_Huff_Tree.make_header(Build_Huff_Tree.test_parent)

read_header(header_to_read, len_of_header)
