"""
数据导出工具：将清洗后的TXT文件数据导出为Excel表格
表格包含四列：时间、平台名称、平台性质、协议内容
"""

import os
import re
import pandas as pd
from pathlib import Path
from datetime import datetime

def extract_date_from_filename(filename):
    """
    从文件名中提取日期
    文件名格式: platform_agreement_YYYY-MM-DD.txt
    """
    pattern = r'.*_agreement_(\d{4}-\d{2}-\d{2})\.txt'
    match = re.match(pattern, filename)
    
    if match:
        return match.group(1)  # 返回YYYY-MM-DD格式的日期字符串
    return None

def read_platform_info(folder_path):
    """
    读取文件夹中的.desc文件，提取平台名称和平台性质
    """
    desc_file = os.path.join(folder_path, '.desc')
    platform_name = "未知平台"
    platform_type = "未知类型"
    
    if os.path.exists(desc_file):
        try:
            with open(desc_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if len(lines) >= 1:
                    platform_name = lines[0].strip()
                if len(lines) >= 2:
                    platform_type = lines[1].strip()
        except Exception as e:
            print(f"读取.desc文件时出错: {e}")
    else:
        print(f"警告: {folder_path} 中未找到.desc文件")
    
    return platform_name, platform_type

def export_data_to_excel(input_dir):
    """
    将清洗后的数据导出到Excel
    :param input_dir: 输入目录路径 (cleaned_data)
    """
    # 用于存储所有数据的列表
    data = []
    
    # 获取所有子文件夹
    subfolders = [f for f in os.listdir(input_dir) 
                 if os.path.isdir(os.path.join(input_dir, f))]
    
    print(f"开始处理 {len(subfolders)} 个平台文件夹...")
    
    # 遍历每个子文件夹
    for subfolder in subfolders:
        folder_path = os.path.join(input_dir, subfolder)
        
        # 获取平台信息
        platform_name, platform_type = read_platform_info(folder_path)
        print(f"处理平台: {platform_name} (类型: {platform_type})...")
        
        # 获取所有txt文件
        txt_files = list(Path(folder_path).glob('*.txt'))
        
        # 处理每个文件
        for file_path in txt_files:
            try:
                # 从文件名提取日期
                date_str = extract_date_from_filename(file_path.name)
                if not date_str:
                    print(f"警告: 无法从 {file_path.name} 提取日期，跳过")
                    continue
                
                # 读取文件内容
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                
                # 添加到数据列表
                data.append({
                    "时间": date_str,
                    "平台名称": platform_name,
                    "平台性质": platform_type,
                    "协议内容": content
                })
                
            except Exception as e:
                print(f"处理文件 {file_path.name} 时出错: {e}")
    
    # 如果有数据，创建DataFrame并保存为Excel
    if data:
        print(f"成功处理 {len(data)} 条协议记录，开始导出Excel...")
        
        # 创建DataFrame
        df = pd.DataFrame(data)
        
        # 按时间和平台名称排序
        df = df.sort_values(by=["时间", "平台名称"])
        
        # 保存为Excel
        output_file = os.path.join(input_dir, "协议数据汇总.xlsx")
        df.to_excel(output_file, index=False)
        
        print(f"Excel文件已保存至: {output_file}")
        return len(data)
    else:
        print("警告: 没有找到可处理的数据")
        return 0

if __name__ == "__main__":
    # 设置输入目录
    cleaned_data_dir = "./cleaned_data"  # 清洗后的数据文件夹路径
    
    if not os.path.exists(cleaned_data_dir):
        print(f"错误: 目录 '{cleaned_data_dir}' 不存在!")
    else:
        # 导出到Excel
        record_count = export_data_to_excel(cleaned_data_dir)
        
        if record_count > 0:
            print(f"===== 导出成功! 共导出 {record_count} 条记录 =====")
        else:
            print("===== 导出失败! 未找到有效数据 =====")