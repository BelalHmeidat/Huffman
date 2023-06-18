# file_path = "sample"
#
# # readign a file to store frequency of characters
# file = open(file_path, 'rb')
# file_content = file.read()
# file.close()
# print("File content: ", file_content)
# for byte in file_content:
#     print(byte.to_bytes())
#
#
# # storing frequency of characters in a dictionary
# char_feq = {}
# for char in file_content:
#     byte = char.to_bytes()
#     if byte in char_feq:
#         char_feq[byte] += 1
#     else:
#         char_feq[byte] = 1
#
# # sort dictionary by value ascending
# # char_feq = sorted(char_feq.items(), key=lambda x: x[1])
# # char_feq = char_feq.items()
# # # convert list of tupples to dictionary
# # char_feq = dict(char_feq)
#
# print("Character frequency: ", char_feq)