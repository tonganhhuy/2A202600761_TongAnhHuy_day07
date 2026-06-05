import os
from pathlib import Path
from src.chunking import ChunkingStrategyComparator

# Danh sách file thực tế của bạn
file_paths = [
    "data/data_new/Day1.md",
    "data/data_new/day2.md",
    "data/data_new/day3.md",
    "data/data_new/Day4.md",
    "data/data_new/Day5.md",
    "data/data_new/Day6.md",
    "data/data_new/day7.md",
]

def main():
    print("="*50)
    print("BẢNG 1: DATA INVENTORY (SỐ KÝ TỰ THỰC TẾ)")
    print("="*50)
    print("| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán (Gợi ý) |")
    print("|---|--------------|-------|----------|-----------------|")
    
    comparator = ChunkingStrategyComparator()
    chunking_results = []
    
    for i, path_str in enumerate(file_paths, 1):
        path = Path(path_str)
        if not path.exists():
            print(f"Không tìm thấy file: {path_str}")
            continue
            
        content = path.read_text(encoding="utf-8")
        char_count = len(content)
        
        # Gợi ý metadata theo ngày để bạn dễ filter
        day_num = path.stem.lower().replace("day", "").strip()
        metadata_hint = f'`day: "{day_num}"`, `source: "{path.name}"`'
        
        print(f"| {i} | {path.name} | {path_str} | {char_count} | {metadata_hint} |")
        
        # Lấy 3 file đầu tiên để chạy so sánh Chunking (theo yêu cầu báo cáo)
        if i <= 3:
            stats = comparator.compare(content)
            for strategy, stat in stats.items():
                count = stat.get('count', 0)
                avg_len = stat.get('average_length', 0)
                chunking_results.append(f"| {path.name} | {strategy} | {count} | {avg_len:.2f} | (Tự đánh giá) |")

    print("\n" + "="*50)
    print("BẢNG 2: BASELINE ANALYSIS (KẾT QUẢ CẮT CHUNK THỰC TẾ)")
    print("="*50)
    print("| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |")
    print("|-----------|----------|-------------|------------|-------------------|")
    for r in chunking_results:
        print(r)

if __name__ == "__main__":
    main()