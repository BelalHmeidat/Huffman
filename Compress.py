from typing import Tuple

from bitstring import BitArray

import Build_Huff_Tree


def read_file(pathname) -> tuple[bytes, int]:
    file = open(pathname, "rb")
    file_content = file.read()
    file_content_len = len(file_content)
    file.close()
    # print(file_content)
    return file_content, file_content_len


def get_frequency(file_content) -> dict:
    byte_freq = {}
    for byte in file_content:
        real_byte = byte.to_bytes()
        if real_byte in byte_freq:
            byte_freq[real_byte] += 1
        else:
            byte_freq[real_byte] = 1
    return byte_freq


def make_compressed_file(original_filename, header, header_bits_len, huff_code_dict, uncompressed_file_content,
                         uncompressed_file_length, dir_path):
    compressed_string_bytes = b''
    compressed_string_bits = ""
    for byte in uncompressed_file_content:
        real_byte = byte.to_bytes()  # the reader reads chars not bytes
        compressed_string_bits += huff_code_dict[real_byte]
        while len(compressed_string_bits) >= 8:
            compressed_string_bytes += BitArray(bin=compressed_string_bits[:8]).bytes
            compressed_string_bits = compressed_string_bits[8:]
    num_of_bits_left = len(compressed_string_bits)
    # print(num_of_bits_left)
    num_of_bits_to_add = 8 - num_of_bits_left
    if num_of_bits_to_add == 8: num_of_bits_to_add = 0
    for i in range(num_of_bits_to_add):
        compressed_string_bits += "0"
    # print(compressed_string_bits)
    compressed_string_bytes += BitArray(bin=compressed_string_bits).bytes
    num_prefix = BitArray(int=num_of_bits_to_add, length=8).bytes
    compressed_file = open(f"{dir_path}/{original_filename}.huff", "wb")
    header_bits_len_bytes = header_bits_len.to_bytes(4, "big")
    uncompressed_file_length_bytes = uncompressed_file_length.to_bytes(4, "big")
    header_and_compressed_data: bytes = header_bits_len_bytes + header + uncompressed_file_length_bytes + num_prefix + compressed_string_bytes
    # print(header_bits_len_bytes)
    # print(header)
    # print(uncompressed_file_length_bytes)
    # print(num_prefix)
    # print(compressed_string_bytes)
    compressed_file.write(header_and_compressed_data)
    # compressed_file.write(num_prefix + compressed_string_bytes)
    compressed_file.close()

    return len(header_and_compressed_data)


def make_header(huff_tree_root):
    big_header = b''

    def post_traverse_and_add_bits_to_header(root_node):
        if root_node is None:
            return
        post_traverse_and_add_bits_to_header(root_node.left)
        post_traverse_and_add_bits_to_header(root_node.right)
        nonlocal big_header
        if root_node.is_leaf():
            big_header += b'1'
            big_header += root_node.byte_value
            # big_header_nodes_only += root_node.byte_value
        else:
            big_header += b'0'

    post_traverse_and_add_bits_to_header(huff_tree_root)
    big_header += b'0'  # marks the end of the header
    header_len_bits = 0
    # print(big_header)
    compact_header = b''
    header_bits = ""
    skip_flag = False
    for i in range(len(big_header)):
        if skip_flag:
            skip_flag = False
            continue
        if big_header[i] == 49:
            bits_string = format(big_header[i + 1], "08b")
            header_len_bits += 9
            bits_string = f"1{bits_string}"
            header_bits += bits_string
            # if big_header[i + 1] == 49 or big_header[i + 1] == 48:
            skip_flag = True
        elif big_header[i] == 48:
            header_bits += "0"
            header_len_bits += 1
        if len(header_bits) >= 8:
            compact_header += BitArray(bin=header_bits[:8]).bytes
            header_bits = header_bits[8:]
    num_of_bits_to_byte = 8 - len(header_bits)
    for i in range(num_of_bits_to_byte):
        header_bits += '0'
    compact_header += BitArray(bin=header_bits).bytes
    # print([i for i in compact_header])
    # print(compact_header)
    # print(test_full_bits[:header_len_bits])
    return compact_header, header_len_bits




def run(in_filepath, output_dir):
    filename = in_filepath.split("/")[-1]
    file_content, file_content_len = read_file(in_filepath)
    byte_freq = get_frequency(file_content)
    freq_heap = Build_Huff_Tree.build_heap(byte_freq)
    huff_tree = Build_Huff_Tree.build_huf_tree(freq_heap)
    huff_codes_dict = Build_Huff_Tree.build_huff_code_dict(huff_tree)
    Build_Huff_Tree.visualize_huff_tree(huff_tree)
    header, header_len_bits = make_header(huff_tree)
    compressed_file_length = make_compressed_file(filename, header, header_len_bits, huff_codes_dict, file_content,
                                                  file_content_len, output_dir)

    # test_internal_decompress(in_filepath, huff_tree)
    # test_tree(huff_tree)

    return len(header), header, file_content_len, compressed_file_length
