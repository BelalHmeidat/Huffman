from math import floor

from bitstring import BitArray

import Build_Huff_Tree


def read_file_to_decode(file_path):
    file = open(file_path, "rb")
    file_content: bytes = file.read()
    file.close()
    return file_content


def uncompress_to_original_file(huff_tree_root, compressed_file_content, dest):
    len_of_tail_bits: int = compressed_file_content[0]
    original_bytes = b''
    current_node = huff_tree_root
    found_size = 0
    for byte in compressed_file_content[1:-1]:
        for i in reversed(range(8)):
            if byte & 1 << i == 0:
                current_node = current_node.left
            else:
                current_node = current_node.right
            if current_node.is_leaf():
                original_bytes += current_node.byte_value
                current_node = huff_tree_root
                found_size += 1
                # print(found_size)
    last_byte = compressed_file_content[-1]
    for i in reversed(range(len_of_tail_bits, 8)):
        if last_byte & 1 << i == 0:
            current_node = current_node.left
        else:
            current_node = current_node.right
        if current_node.is_leaf():
            original_bytes += current_node.byte_value
            current_node = huff_tree_root
            found_size += 1
    uncompressed_file = open(dest, "wb")
    uncompressed_file.write(original_bytes)
    uncompressed_file.close()
    return found_size


def get_original_header_bits(initial_header, header_bits_len):
    header_bits = ""
    for byte in initial_header:
        header_bits += format(byte, "08b")
    header_bits = header_bits[:header_bits_len]
    # print(header_bits)
    return header_bits


def process_header_bits(header_bits):
    header_stack = []
    i = 0
    node_freq = 0
    final_parent = None
    while i < len(header_bits) - 1:
        if header_bits[i] == '1':
            i += 1
            node_byte = BitArray(bin=header_bits[i:i + 8]).bytes
            # print(node_byte)
            header_stack.append(Build_Huff_Tree.Node(node_byte, node_freq.to_bytes(8, "big")))
            i += 8
        else:
            right_node = header_stack.pop()
            left_node = header_stack.pop()
            parent = Build_Huff_Tree.Node(b'', node_freq)
            final_parent = parent
            parent.left = left_node
            parent.right = right_node
            header_stack.append(parent)
            i += 1
        node_freq += 1
    return final_parent


def run(huff_file, output_dir):
    file_content = read_file_to_decode(huff_file)
    compressed_file_size = len(file_content)
    header_bits_len = int.from_bytes(file_content[:4], 'big')
    header_len = floor(header_bits_len / 8.0)
    initial_header = file_content[4:4 + header_len + 1]
    original_file_size = int.from_bytes(file_content[5 + header_len: header_len + 9], "big")
    compressed_data = file_content[header_len + 9:]
    reduced_header_bits = get_original_header_bits(initial_header, header_bits_len)  # without the tail of last byte
    restored_huff_tree = process_header_bits(reduced_header_bits)
    Build_Huff_Tree.visualize_huff_tree(restored_huff_tree, compress=False)
    # huff_dict = Build_Huff_Tree.build_huff_code_dict(restored_huff_tree)
    out_file_path = f'{output_dir}/{huff_file.split("/")[-1][:-5]}'
    found_size = uncompress_to_original_file(restored_huff_tree, compressed_data, out_file_path)

    # test_tree(restored_huff_tree)

    return header_len, initial_header, original_file_size, compressed_file_size
