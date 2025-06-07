# 数据清洗：去重 + 去空行 - 多文件夹批处理版本
import os
import hashlib
import shutil
import re
from pathlib import Path
from datetime import datetime

def clean_and_deduplicate(input_dir, output_dir):
    """
    对指定目录下的所有TXT文件进行内容去重，保留最早日期版本
    :param input_dir: 输入目录路径
    :param output_dir: 输出目录路径
    :return: 去重统计信息
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 用于存储文件内容哈希值及其对应的最早日期文件
    # 格式: {content_hash: (date, filename, content)}
    content_hashes = {}
    
    # 统计信息
    total_files = 0
    duplicate_files = 0
    empty_files = 0
    processed_files = 0
    
    # 获取所有txt文件并按文件名排序
    txt_files = sorted(list(Path(input_dir).glob('*.txt')))
    total_files = len(txt_files)
    
    print(f"开始处理 {input_dir} 中的 {total_files} 个TXT文件...")
    
    # 处理每个文件
    for file_path in txt_files:
        try:
            file_name = file_path.name
            
            # 从文件名中提取日期 - 假设格式为 xxx_agreement_YYYY-MM-DD.txt
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', file_name)
            if date_match:
                file_date = datetime.strptime(date_match.group(1), '%Y-%m-%d')
            else:
                # 如果无法提取日期，使用文件的修改时间
                file_date = datetime.fromtimestamp(os.path.getmtime(file_path))
                print(f"警告：文件 {file_name} 无法从名称提取日期，使用修改时间")
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # 去除空行和首尾空白
            cleaned_content = '\n'.join(line.strip() for line in content.splitlines() if line.strip())
            
            # 跳过空文件
            if not cleaned_content:
                empty_files += 1
                print(f"跳过空文件: {file_name}")
                continue
            
            # 计算内容哈希值
            content_hash = hashlib.md5(cleaned_content.encode('utf-8')).hexdigest()
            
            # 检查是否已存在相同内容
            if content_hash in content_hashes:
                stored_date, stored_file, _ = content_hashes[content_hash]
                
                # 判断哪个文件日期更早
                if file_date < stored_date:
                    # 当前文件日期更早，替换之前的记录
                    print(f"发现重复但日期更早: {file_name} ({file_date.date()}) 替换 {stored_file} ({stored_date.date()})")
                    content_hashes[content_hash] = (file_date, file_name, cleaned_content)
                else:
                    # 当前文件日期相同或更晚，标记为重复
                    duplicate_files += 1
                    print(f"发现重复且日期较晚: {file_name} ({file_date.date()}) 与 {stored_file} ({stored_date.date()})")
                    continue
            else:
                # 记录这个新内容的哈希值、文件名和内容
                content_hashes[content_hash] = (file_date, file_name, cleaned_content)
            
            processed_files += 1
            
        except Exception as e:
            print(f"处理文件 {file_path.name} 时出错: {e}")
    
    # 将保留的内容写入输出目录
    for content_hash, (_, file_name, content) in content_hashes.items():
        output_path = Path(output_dir) / file_name
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    # 返回处理统计
    stats = {
        "总文件数": total_files,
        "有效文件数": len(content_hashes),
        "重复文件数": duplicate_files,
        "空文件数": empty_files
    }
    
    return stats

def process_all_subfolders(base_input_dir, base_output_dir,new_dir=None,all=True):
    """
    处理基础目录下的所有子文件夹
    :param base_input_dir: 基础输入目录
    :param base_output_dir: 基础输出目录
    :return: 总体统计信息
    """
    # 确保基础输出目录存在
    os.makedirs(base_output_dir, exist_ok=True)

    if all == False:
        if new_dir is None:
            print("错误: 当 all=False 时，必须提供 new_dir 参数!")
            return
        new_dir = new_dir + "_User_Agreements/"
        base_input_dir = os.path.join(base_input_dir, new_dir)
        base_output_dir = os.path.join(base_output_dir, new_dir)
        print(f"\n开始处理文件夹: {base_input_dir}")
        # 处理该子文件夹
        stats = clean_and_deduplicate(base_input_dir, base_output_dir)
        return stats

    
    # 获取所有子文件夹
    subfolders = [f for f in os.listdir(base_input_dir) 
                 if os.path.isdir(os.path.join(base_input_dir, f))]
    
    print(f"发现 {len(subfolders)} 个子文件夹需要处理。")
    
    # 统计总信息
    all_stats = {
        "总文件数": 0,
        "有效文件数": 0,
        "重复文件数": 0,
        "空文件数": 0,
        "处理文件夹数": 0
    }
    
    # 处理每个子文件夹
    for subfolder in subfolders:
        input_path = os.path.join(base_input_dir, subfolder)
        output_path = os.path.join(base_output_dir, subfolder)
        
        print(f"\n开始处理文件夹: {subfolder}")
        
        # 处理该子文件夹
        stats = clean_and_deduplicate(input_path, output_path)
        
        # 累加统计信息
        for key in ["总文件数", "有效文件数", "重复文件数", "空文件数"]:
            all_stats[key] += stats[key]
        
        all_stats["处理文件夹数"] += 1
        
        # 显示子文件夹处理结果
        print(f"文件夹 {subfolder} 处理完成")
        print(f"  - 总文件数: {stats['总文件数']}")
        print(f"  - 有效文件数: {stats['有效文件数']}")
        print(f"  - 重复文件数: {stats['重复文件数']}")
        print(f"  - 空文件数: {stats['空文件数']}")
    
    return all_stats

if __name__ == "__main__":
    # 设置输入和输出目录
    base_input_directory = "./data/"  # data文件夹路径
    base_output_directory = "./cleaned_data/"  # 输出的根目录

    new_dir = input("请输入需要处理的子文件夹名称（留空则处理所有子文件夹）: ").strip()
    
    if not os.path.exists(base_input_directory):
        print(f"错误: 目录 '{base_input_directory}' 不存在!")
    else:
        # 处理所有子文件夹
        if new_dir:
            all = False
        else:
            all = True
        all_results = process_all_subfolders(base_input_directory, base_output_directory,new_dir,all)
        
        # 显示总体处理结果
        print("\n===== 全部处理完成! =====")