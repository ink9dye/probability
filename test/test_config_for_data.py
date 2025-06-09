import os
from config.settings import CSV_FILE

print("CSV_FILE 路径:", CSV_FILE)
print("父目录存在吗？", os.path.exists(os.path.dirname(CSV_FILE)))
print("文件本身存在吗？", os.path.exists(CSV_FILE))