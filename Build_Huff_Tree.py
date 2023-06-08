import Read_File
from graphviz import Graph, Digraph
from bitstring import BitArray
from dsplot.tree import BinaryTree


class Node:
    def __init__(self, value, freq):
        self.left = None
        self.right = None
        self.freq = freq
        self.byte_value = value
        self.huff_code = ''

    def __ge__(self, other):
        return self.freq >= other.freq

    def __gt__(self, other):
        return self.freq > other.freq

    def __lt__(self, other):
        return self.freq < other.freq

    def __str__(self):
        return f"{self.freq}, {self.byte_value}, {self.huff_code}"

    def is_leaf(self):
        return self.left is None and self.right is None


class MaxHeap:
    def __init__(self):
        self.heap = []

    def __len__(self):
        return len(self.heap)

    def insert(self, node):
        self.heap.append(node)
        self.heapify()
        # self.makeMaxHeap()

    def heapify(self):
        i = len(self.heap) - 1
        self.heapify2(i)

    def heapify2(self, i):  # heapifying after insertion
        if i == 0:
            return
        parent = (i - 1) // 2
        if self.heap[parent] > self.heap[i]:
            self.heap[parent], self.heap[i] = self.heap[i], self.heap[parent]
        self.heapify2(parent)

    def remove_top(self):
        if len(self.heap) == 0:
            return None
        top = self.heap[0]
        self.heap[0] = self.heap[-1]
        self.heapify3(0)
        new_heap = self.heap[:-1]
        self.heap = new_heap
        return top

    def heapify3(self, i):  # heapifying after deletion
        largest = i
        l = len(self.heap)
        if i >= l - 1:
            return
        left = i * 2 + 1
        right = 2 * i + 2
        if left < l and self.heap[largest] > self.heap[left]:
            largest = left
        if right < l and self.heap[largest] > self.heap[right]:
            largest = right

        if i != largest:
            self.heap[i], self.heap[largest] = self.heap[largest], self.heap[i]
            self.heapify3(largest)

    def print(self):
        for node in self.heap:
            print(node)

    def view_heap_tree(self):
        g = Graph('G', filename='heap.gv', engine='sfdp', format='png')
        # g.attr('node', shape='circle')
        # g.graph_attr['bgcolor'] = 'white'
        # g.edge_attr['dir'] = 'forward'
        # g.node_attr['style'] = 'filled'
        g.graph_attr['rankdir'] = 'TB'
        i = 0
        current = self.heap[i]
        g.node(str(f"{current.freq}, {current.byte_value}"))
        while i < len(self.heap):
            current = self.heap[i]
            if i * 2 + 1 < len(self.heap):
                left = self.heap[i * 2 + 1]
                g.node(str(f"{left.freq}, {left.byte_value}"))
                g.edge(str(f"{current.freq}, {current.byte_value}"), str(f"{left.freq}, {left.byte_value}"))
                if i * 2 + 2 < len(self.heap):
                    right = self.heap[i * 2 + 2]
                    g.node(str(f"{right.freq}, {right.byte_value}"))
                    g.edge(str(f"{current.freq}, {current.byte_value}"), str(f"{right.freq}, {right.byte_value}"))
            i += 1
        g.view()


def build_huf_tree(heap):
    child1 = None
    while len(heap) > 0:
        child1 = heap.remove_top()
        node = None
        if len(heap) > 0:
            child2 = heap.remove_top()
            node = Node(0, child1.freq + child2.freq)
            node.byte_value = -1
            node.left = child1
            node.right = child2
            heap.insert(node)
    return child1


def visualize_huff_tree(root):
    dot = Digraph()
    dot.node(f"{root.freq} {root.byte_value} {root.huff_code}", label=f"{root.freq}")

    def add_nodes_edges(node):
        if node.left is not None:
            if node.left.is_leaf():  # if leaf show utf-8 encoding in addition to frequency
                dot.node(f"{node.left.freq} {node.left.byte_value} {node.left.huff_code}",
                         label=f"{node.left.freq}, {node.left.byte_value}")
            else:  # if is not leaf the node doesn't hold a byte value
                dot.node(f"{node.left.freq} {node.left.byte_value} {node.left.huff_code}", label=f"{node.left.freq}")
            dot.edge(f"{node.freq} {node.byte_value} {node.huff_code}",
                     f"{node.left.freq} {node.left.byte_value} {node.left.huff_code}", label="0")
            add_nodes_edges(node.left)
        if node.right is not None:
            if node.right.is_leaf():
                dot.node(f"{node.right.freq} {node.right.byte_value} {node.right.huff_code}",
                         label=f"{node.right.freq}, {node.right.byte_value}")
            else:
                dot.node(f"{node.right.freq} {node.right.byte_value} {node.right.huff_code}",
                         label=f"{node.right.freq}")
            dot.edge(f"{node.freq} {node.byte_value} {node.huff_code}",
                     f"{node.right.freq} {node.right.byte_value} {node.right.huff_code}", label="1")
            add_nodes_edges(node.right)

    add_nodes_edges(root)
    dot.render('huffman_binary_tree', view=True, format='png')


test_heap = MaxHeap()
for tuple in Read_File.char_feq:
    node = Node(tuple[0], tuple[1])
    test_heap.insert(node)
test_heap.print()

test_parent: Node = build_huf_tree(test_heap)
# show_huff_tree(test_parent)
huff_code_dict = {}


def assign_bits_to_huff_tree(parent: Node, huff_code):  # preorder traversal
    if parent is None:
        return
    parent.huff_code = f"{huff_code}"
    if parent.is_leaf():
        huff_code_dict[parent.byte_value] = parent.huff_code
        # print(parent)
    if parent.left is not None:
        parent.left.huff_code = f"{parent.huff_code}0"
        huff_code = parent.left.huff_code
    assign_bits_to_huff_tree(parent.left, huff_code)
    if parent.right is not None:
        parent.right.huff_code = f"{parent.huff_code}1"
        huff_code = parent.right.huff_code
    assign_bits_to_huff_tree(parent.right, huff_code)


assign_bits_to_huff_tree(test_parent, '')
visualize_huff_tree(test_parent)


# print(huff_code_dict)


def compress_file():
    compressed_string_bytes = b''
    compressed_string_bits = ""
    for byte in Read_File.file_content:
        real_byte = byte.to_bytes()  # the reader reads chars not bytes
        compressed_string_bits += huff_code_dict[real_byte]
        while len(compressed_string_bits) >= 8:
            compressed_string_bytes += BitArray(bin=compressed_string_bits[:8]).bytes
            compressed_string_bits = compressed_string_bits[8:]
    num_of_bits_left = len(compressed_string_bits)
    print(num_of_bits_left)
    num_of_bits_to_add = 8 - num_of_bits_left
    if num_of_bits_to_add == 8: num_of_bits_to_add = 0
    for i in range(num_of_bits_to_add):
        compressed_string_bits += "0"
    print(compressed_string_bits)
    compressed_string_bytes += BitArray(bin=compressed_string_bits).bytes
    num_prefix = BitArray(int=num_of_bits_to_add, length=8).bytes
    compressed_file = open("output.huff", "wb")
    compressed_file.write(num_prefix + compressed_string_bytes)
    compressed_file.close()


compress_file()


def uncompress_file(huff_tree_root, source, dest):
    compressed_file = open(source, "rb")
    compressed_file_content = compressed_file.read()
    compressed_file.close()
    len_of_tail_bits: int = compressed_file_content[0]
    original_bytes = b''
    current_node = huff_tree_root
    for byte in compressed_file_content[1:-1]:
        for i in reversed(range(8)):
            if byte & 1 << i == 0:
                current_node = current_node.left
            else:
                current_node = current_node.right
            if current_node.is_leaf():
                original_bytes += current_node.byte_value
                current_node = huff_tree_root
    last_byte = compressed_file_content[-1]
    for i in reversed(range(len_of_tail_bits, 8)):
        if last_byte & 1 << i == 0:
            current_node = current_node.left
        else:
            current_node = current_node.right
        if current_node.is_leaf():
            original_bytes += current_node.byte_value
            current_node = huff_tree_root
    uncompressed_file = open(dest, "wb")
    uncompressed_file.write(original_bytes)
    uncompressed_file.close()
    return original_bytes


og_bytes = uncompress_file(test_parent, "output.huff", "uncompressed")

# print(og_bytes)


big_header = b''
big_header_nodes_only = b''
big_header2 = b""


def post_traverse_and_add_bits(root_node):
    if root_node is None:
        return
    post_traverse_and_add_bits(root_node.left)
    post_traverse_and_add_bits(root_node.right)
    global big_header, big_header_nodes_only
    if root_node.is_leaf():
        big_header += b'1'
        big_header += root_node.byte_value
        big_header_nodes_only += root_node.byte_value
    else:
        big_header += b'0'
        pass


excess_bits = ""


def post_traverse_and_add_bits2(root_node):
    if root_node is None:
        return
    post_traverse_and_add_bits2(root_node.left)
    post_traverse_and_add_bits2(root_node.right)
    global big_header2
    global excess_bits
    while len(excess_bits) >= 8:
        byte = BitArray(bin=excess_bits[:8]).bytes
        big_header2 += byte
        excess_bits = excess_bits[8:]
    if root_node.is_leaf():
        excess_bits += "1"
        to_be_excess_bits = ""
        int_byte = int.from_bytes(root_node.byte_value)
        for i in range(len(excess_bits)):
            if int_byte & 1 << i == 0:
                to_be_excess_bits += "0"
            else:
                to_be_excess_bits += "1"
            if excess_bits[i] == '1':
                int_byte = int_byte | 1 << (8 + i)
            else:
                int_byte = int_byte & 0 << (8 + i)
        int_byte = int_byte >> len(excess_bits)
        big_header2 += bytes([int_byte])
        excess_bits = to_be_excess_bits
        to_be_excess_bits = ""
    else:
        excess_bits += '0'


def make_header(huff_tree):
    # post_traverse_and_add_bits2(huff_tree)
    post_traverse_and_add_bits(huff_tree)
    # print(raw_header.decode("utf-8"))
    global big_header
    big_header += b'0'  # marks the end of the header
    header_len_bits = 0
    print(big_header)
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
    print([i for i in compact_header])
    print(header_len_bits)
    return compact_header, header_len_bits


# make_header(test_parent)
