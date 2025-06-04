import os
import pandas as pd

# 设置目标文件夹路径
folder_path = "C:/Users/zya/Desktop/bilibili_User_Agreements"
output_path = "C:/Users/zya/Desktop/bilibili_User_Agreements/bilibili_User_Agreements_cleaned.csv"

# 获取所有 .txt 文件
files = sorted([f for f in os.listdir(folder_path) if f.endswith(".txt")])

# 初始化结果列表
valid_data = []

# 遍历每个文件
for file in files:
    if not file.startswith("bilibili_agreement_") or not file.endswith(".txt"):
        continue  # 跳过不符合命名规范的文件

    file_path = os.path.join(folder_path, file)
    with open(file_path, 'r', encoding='utf-8',errors="replace") as f:
        content = f.read().strip()

    # 检查是否为空文件
    if not content:
        print(f"⚠️ 文件为空：{file}，跳过")
        continue

    # 提取文件信息
    date = file.replace("bilibili_agreement_", "").replace(".txt", "")
    word_count = len(content)
    line_count = content.count("\n") + 1

    # 存储有效数据
    valid_data.append({
        "date": date,
        "word_count": word_count,
        "line_count": line_count,
        "text": content
    })

# 如果有有效数据，生成 DataFrame 并保存为 CSV
if valid_data:
    df_valid = pd.DataFrame(valid_data).sort_values("date").reset_index(drop=True)
    print(f"🎉 有效协议条目：{len(df_valid)}")

    df_valid.to_csv(output_path, index=False, encoding='utf-8')

    print(f"✅ 数据已保存为 CSV 文件：{output_path}")
else:
    print("⚠️ 没有有效数据，请检查文件内容。")