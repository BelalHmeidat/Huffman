import Read_File
from graphviz import Graph, Digraph
from bitstring import BitArray

dot = None

class Node:
    def __init__(self, value, freq):
        self.left = None
        self.right = None
        self.freq = freq
        self.byte_value : bytes = value
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
            node.byte_value = b' '
            node.left = child1
            node.right = child2
            heap.insert(node)
    return child1


def visualize_huff_tree(root, compress=True):
    # should be called after the huff codes were given to each node
    # compress boolean to know if the tree being built during compression or decompression; in case of decompression the frequencies are unknown
    global dot
    dot = Digraph()
    if not compress:
        dot.node(f"{root.freq} {root.byte_value} {root.huff_code}", label=f"")
    else : dot.node(f"{root.freq} {root.byte_value} {root.huff_code}", label=f"{root.freq}")

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

    def add_nodes_edges_decompression(node):
        if node.left is not None:
            if node.left.is_leaf():  # if leaf show utf-8 encoding in addition to frequency
                dot.node(f"{node.left.freq} {node.left.byte_value} {node.left.huff_code}",
                         label=f"{node.left.byte_value}")
            else:  # if is not leaf the node doesn't hold a byte value
                dot.node(f"{node.left.freq} {node.left.byte_value} {node.left.huff_code}",
                         label=f"")
            dot.edge(f"{node.freq} {node.byte_value} {node.huff_code}",
                     f"{node.left.freq} {node.left.byte_value} {node.left.huff_code}", label="0")
            add_nodes_edges_decompression(node.left)
        if node.right is not None:
            if node.right.is_leaf():
                dot.node(f"{node.right.freq} {node.right.byte_value} {node.right.huff_code}",
                         label=f"{node.right.byte_value}")
            else:
                dot.node(f"{node.right.freq} {node.right.byte_value} {node.right.huff_code}",
                         label=f"")
            dot.edge(f"{node.freq} {node.byte_value} {node.huff_code}",
                     f"{node.right.freq} {node.right.byte_value} {node.right.huff_code}", label="1")
            add_nodes_edges_decompression(node.right)

    if not compress:
        add_nodes_edges_decompression(root)
    else:
        add_nodes_edges(root)

    dot.render('huffman_binary_tree', view=False, format='png')


def build_heap(bytes_freq_dict):
    heap = MaxHeap()
    # sorted_byte_freq = sorted(bytes_freq_dict.items(), key=lambda x: x[1])
    for byte, freq in bytes_freq_dict.items():
    # for byte, freq in sorted_byte_freq:
        node = Node(byte, freq)
        heap.insert(node)
    return heap


# test_parent: Node = build_huf_tree(build_heap(Read_File.char_feq))


# show_huff_tree(test_parent)


def build_huff_code_dict(tree):
    huff_code_dict = {}

    def assign_huff_codes_to_tree_nodes(parent: Node, huff_code):  # preorder traversal
        if parent is None:
            return
        parent.huff_code = f"{huff_code}"
        if parent.is_leaf():
            huff_code_dict[parent.byte_value] = parent.huff_code
            # print(type(parent.byte_value))
        if parent.left is not None:
            parent.left.huff_code = f"{parent.huff_code}0"
            huff_code = parent.left.huff_code
        assign_huff_codes_to_tree_nodes(parent.left, huff_code)
        if parent.right is not None:
            parent.right.huff_code = f"{parent.huff_code}1"
            huff_code = parent.right.huff_code
        assign_huff_codes_to_tree_nodes(parent.right, huff_code)

    assign_huff_codes_to_tree_nodes(tree, "")
    # print(huff_code_dict)
    return huff_code_dict

