# coding: utf-8

from fdfs_client.client import Fdfs_client
client = Fdfs_client('./client.conf')
# with open('./test.jpg', 'rb') as f:
#     content = f.read()
# result = client.upload_by_buffer(content)
result = client.upload_by_filename('./test.jpg')
print(result)
print(type(result))
