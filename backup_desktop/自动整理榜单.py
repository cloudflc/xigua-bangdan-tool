# -*- coding: utf-8 -*-
"""
自动整理榜单脚本
将完成奖学员姓名替换到完成奖.html
将优秀奖及创意奖学员姓名替换到优秀奖.html
"""

import pandas as pd
import re
import os
import sys
import io

if sys.platform == 'win32' and sys.stdout is not None and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 获取基础目录
def get_base_dir():
    if getattr(sys, 'frozen', False):
        # 打包后的EXE环境 - 优先使用临时目录中的资源
        if hasattr(sys, '_MEIPASS'):
            return sys._MEIPASS.replace('\\', '/')
        return os.path.dirname(sys.executable).replace('\\', '/')
    else:
        # 开发环境
        return os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')

BASE_DIR = get_base_dir()

# 文件路径配置
XIAOSHUTONG_FILE = os.path.join(BASE_DIR, '小书童_2026-01-29.csv')
MINGDAN_FILE = os.path.join(BASE_DIR, '名单.csv')
WANCHENGJIAO_HTML = os.path.join(BASE_DIR, '完成奖.html')
YOUXIUJIANG_HTML = os.path.join(BASE_DIR, '优秀奖-创意奖.html')
YOUXIUJIANG_ONLY_HTML = os.path.join(BASE_DIR, '优秀奖.html')
YOUXIUJIANG_BACKUP_HTML = os.path.join(BASE_DIR, '优秀奖-创意奖.html.backup')

# 内部员工名单（需要过滤掉的学员姓名）
# 在此列表中添加内部员工名称，程序会自动从榜单中删除
INTERNAL_EMPLOYEES = [
    # 示例格式：
    "凹凸",
    "凹凸曼",
    "Count",
    '​Chloe',
    'Isabella',
    '测试 账号',
    '--',
    'James',
    'Zoe'
]


def read_xiaoshutong(file_path=None):
    """读取小书童文件，获取学员名称（自动过滤内部员工）"""
    try:
        # Use the provided file path or the default one
        if file_path is None:
            file_path = XIAOSHUTONG_FILE
            
        df = pd.read_excel(file_path)
        # 去除空值和空白字符
        names = df['学员名称'].dropna().astype(str).str.strip().tolist()
        # 过滤掉空字符串、纯数字（如'1', '222'）和内部员工
        names = [name for name in names if name and not name.isdigit() and name not in INTERNAL_EMPLOYEES]

        # 如果过滤掉了内部员工，显示提示信息
        original_count = len(df['学员名称'].dropna())
        filtered_count = len(names)
        if filtered_count < original_count:
            print(f"  [过滤] 已移除 {original_count - filtered_count} 名内部员工")

        return names
    except Exception as e:
        print(f"读取小书童文件出错: {e}")
        return []


def read_mingdan(file_path=None):
    """读取名单.csv文件，获取完成奖、优秀奖、创意奖名单"""
    try:
        # Use the provided file path or the default one
        if file_path is None:
            file_path = MINGDAN_FILE
            
        df = pd.read_csv(file_path, sep='\t', header=None, names=['奖项', '姓名'])
        
        # 分类统计（去重）
        wanchengjiang = []
        youxiujiang = []
        chuangyijiang = []
        
        seen_wancheng = set()
        seen_youxiu = set()
        seen_chuangyi = set()
        
        for _, row in df.iterrows():
            award = str(row['奖项']).strip()
            name = str(row['姓名']).strip()
            
            if award == '完成奖' and name not in seen_wancheng:
                wanchengjiang.append(name)
                seen_wancheng.add(name)
            elif award == '优秀奖' and name not in seen_youxiu:
                youxiujiang.append(name)
                seen_youxiu.add(name)
            elif award == '创意奖' and name not in seen_chuangyi:
                chuangyijiang.append(name)
                seen_chuangyi.add(name)
        
        return wanchengjiang, youxiujiang, chuangyijiang
    except Exception as e:
        print(f"读取名单.csv文件出错: {e}")
        return [], [], []


def update_wanchengjiang_html(wanchengjiang_names, html_path=None):
    """更新完成奖.html文件"""
    if html_path is None:
        html_path = WANCHENGJIAO_HTML
    
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 转换为JavaScript数组格式
        names_str = ", ".join([f"'{name}'" for name in wanchengjiang_names])
        new_students = f"const students = [{names_str}];"
        
        # 替换students数组 - 使用正则匹配整个数组定义
        pattern = r"const students\s*=\s*\[[^\]]*\];"
        content = re.sub(pattern, new_students, content)
        
        # 更新统计数据
        total_students = len(wanchengjiang_names)
        total_coins = total_students * 100
        
        # 查找所有stat-number标签
        stat_numbers = re.findall(r'<div class="stat-number">(\d+)</div>', content)
        
        # 第一个是获奖人数，第二个是总西瓜币，第三个保持不变（年份）
        new_stats = []
        for i, num in enumerate(stat_numbers):
            if i == 0:
                new_stats.append(str(total_students))
            elif i == 1:
                new_stats.append(str(total_coins))
            else:
                new_stats.append(num)
        
        # 替换统计数字
        for i, num in enumerate(stat_numbers):
            content = re.sub(
                f'<div class="stat-number">{num}</div>', 
                f'<div class="stat-number">{new_stats[i]}</div>', 
                content, 
                count=1
            )
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[OK] 完成奖.html 已更新，共 {total_students} 人")
        
    except Exception as e:
        print(f"更新完成奖.html出错: {e}")


def update_youxiujiang_html(youxiujiang_names, chuangyijiang_names, html_path=None):
    """更新优秀奖-创意奖.html文件"""
    if html_path is None:
        html_path = YOUXIUJIANG_HTML
    
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查并添加创意奖的HTML展示区域
        if 'creativeWinners' not in content:
            # 找到awards-section开始位置，在优秀奖之前插入创意奖
            awards_section_start = content.find('<section class="awards-section">')
            if awards_section_start != -1:
                # 找到section开始标签后面的换行位置
                insert_pos = content.find('\n', awards_section_start) + 1
                
                creative_section = '''            <div class="award-category creative">
                <div class="award-header">
                    <div>创意奖</div>
                    <div class="coins">400 <i class="fas fa-watermelon"></i> /人</div>
                </div>
                <div class="winners-list" id="creativeWinners">
                    <!-- 创意奖获奖者将在这里展示 -->
                </div>
            </div>
'''
                content = content[:insert_pos] + creative_section + content[insert_pos:]

            # 更新JavaScript中的renderAwards函数
            # 1. 添加清空creativeWinners
            old_clear = "document.getElementById('excellentWinners').innerHTML = '';"
            new_clear = "document.getElementById('creativeWinners').innerHTML = '';\n            document.getElementById('excellentWinners').innerHTML = '';"
            content = content.replace(old_clear, new_clear)

            # 2. 添加创意奖渲染代码（在优秀奖之前）
            old_render = "renderCategory(excellents, 'excellentWinners', '优秀奖');"
            new_render = """// 渲染创意奖
            const creatives = data.filter(item => item.award === '创意奖');
            document.getElementById('creativeCount').textContent = creatives.length;
            renderCategory(creatives, 'creativeWinners', '创意奖');

            renderCategory(excellents, 'excellentWinners', '优秀奖');"""
            content = content.replace(old_render, new_render)

        # 构建奖项数据
        awards_items = []

        # 添加创意奖数据（放在前面）
        for name in chuangyijiang_names:
            awards_items.append(f"{{\"award\": \"创意奖\", \"name\": \"{name}\"}}")

        # 添加优秀奖数据
        for name in youxiujiang_names:
            awards_items.append(f"{{\"award\": \"优秀奖\", \"name\": \"{name}\"}}")

        # 转换为JavaScript数组格式
        awards_str = ",\n".join(awards_items)
        awards_array = f"const awardsData = [{awards_str}];"

        # 替换awardsData数组
        idx = content.find("const awardsData = [")
        if idx != -1:
            end_idx = content.find("}];", idx)
            if end_idx != -1:
                content = content[:idx] + awards_array + content[end_idx + 3:]

        # 更新统计数据
        total_count = len(youxiujiang_names) + len(chuangyijiang_names)
        creative_count = len(chuangyijiang_names)
        excellent_count = len(youxiujiang_names)

        # 替换HTML中的统计数字
        pattern = r'<span id="totalWinners">\d+</span>'
        content = re.sub(pattern, f'<span id="totalWinners">{total_count}</span>', content)

        # 更新奖项奖励说明
        if chuangyijiang_names:
            # 有创意奖，检查是否已经包含创意奖的奖励说明
            if '<span class="watermelon-coin">创意奖 <strong>400🍉</strong></span>' not in content:
                # 没有创意奖奖励说明，将单个优秀奖的奖励替换为两个奖项的奖励
                old_rewards = '<span class="watermelon-coin">优秀奖 <strong>200🍉</strong></span>'
                new_rewards = '<span class="watermelon-coin">创意奖 <strong>400🍉</strong></span>\n                <span class="watermelon-coin">优秀奖 <strong>200🍉</strong></span>'
                content = content.replace(old_rewards, new_rewards)

        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"[OK] 优秀奖-创意奖.html 已更新")
        print(f"  - 优秀奖: {excellent_count} 人")
        print(f"  - 创意奖: {creative_count} 人")
        print(f"  - 总计: {total_count} 人")

    except Exception as e:
        print(f"更新优秀奖-创意奖.html出错: {e}")


def update_youxiujiang_only_html(youxiujiang_names, html_path=None):
    """更新优秀奖.html文件（只有优秀奖）"""
    if html_path is None:
        html_path = YOUXIUJIANG_ONLY_HTML
    try:
        # 检查文件是否存在
        if not os.path.exists(html_path):
            # 如果使用默认路径，检查备份文件
            if os.path.exists(YOUXIUJIANG_BACKUP_HTML):
                # 从备份文件复制
                with open(YOUXIUJIANG_BACKUP_HTML, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查备份文件中是否有创意奖区域
                if '<div class="award-category creative">' in content:
                    # 使用正则表达式移除创意奖区域
                    pattern = r'<div class="award-category creative">.*?<\/div>\s*<\/div>'
                    content = re.sub(pattern, '', content, flags=re.DOTALL)
                    # 移除创意奖人数统计
                    pattern = r'<div class="stat-item">\s*<div class="stat-value creative-count" id="creativeCount">\d+<\/div>\s*<div class="stat-label">创意奖人数<\/div>\s*<\/div>'
                    content = re.sub(pattern, '', content, flags=re.DOTALL)
                    
                    # 移除创意奖奖励说明
                    old_rewards = '<span class="watermelon-coin">创意奖 <strong>400🍉</strong></span>\n                <span class="watermelon-coin">优秀奖 <strong>200🍉</strong></span>'
                    new_rewards = '<span class="watermelon-coin">优秀奖 <strong>200🍉</strong></span>'
                    content = content.replace(old_rewards, new_rewards)
                
                # 移除创意奖相关的JavaScript代码
                old_clear = "document.getElementById('excellentWinners').innerHTML = '';\n            document.getElementById('creativeWinners').innerHTML = '';"
                new_clear = "document.getElementById('excellentWinners').innerHTML = '';"
                content = content.replace(old_clear, new_clear)
                
                old_render = "renderCategory(excellents, 'excellentWinners', '优秀奖');\n\n            // 渲染创意奖\n            const creatives = data.filter(item => item.award === '创意奖');\n            document.getElementById('creativeCount').textContent = creatives.length;\n            renderCategory(creatives, 'creativeWinners', '创意奖');"
                new_render = "renderCategory(excellents, 'excellentWinners', '优秀奖');"
                content = content.replace(old_render, new_render)
                
                # 移除creativeCount元素（如果存在）
                content = re.sub(r'<span id="creativeCount">\d+<\/span>', '', content)
                
                # 保存为新文件
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            else:
                print("[错误] HTML模板文件不存在，无法创建优秀奖.html")
                return
        
        # 读取文件
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 构建奖项数据（只包含优秀奖）
        awards_items = []
        for name in youxiujiang_names:
            awards_items.append(f"{{\"award\": \"优秀奖\", \"name\": \"{name}\"}}")
        
        # 转换为JavaScript数组格式
        awards_str = ",\n".join(awards_items)
        awards_array = f"const awardsData = [{awards_str}];"
        
        # 替换awardsData数组
        pattern = r"const awardsData\s*=\s*\[[^\]]*\]\s*;"
        content = re.sub(pattern, awards_array, content)
        
        # 更新统计数据
        total_count = len(youxiujiang_names)
        
        # 替换HTML中的统计数字
        pattern = r'<span id="totalWinners">\d+</span>'
        content = re.sub(pattern, f'<span id="totalWinners">{total_count}</span>', content)
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[OK] 优秀奖.html 已更新")
        print(f"  - 优秀奖: {total_count} 人")
        
    except Exception as e:
        print(f"更新优秀奖.html出错: {e}")


def main():
    """主函数"""
    print("=" * 50)
    print("开始自动整理榜单...")
    print("=" * 50)
    
    # 1. 读取小书童文件获取完成奖名单
    print("\n读取小书童文件...")
    xiaoshutong_names = read_xiaoshutong()
    print(f"小书童文件中的学员: {len(xiaoshutong_names)} 人")
    
    # 2. 读取名单.csv
    print("\n读取名单.csv...")
    wancheng_from_mingdan, youxiujiang, chuangyijiang = read_mingdan()
    print(f"名单中的完成奖: {len(wancheng_from_mingdan)} 人")
    print(f"名单中的优秀奖: {len(youxiujiang)} 人")
    print(f"名单中的创意奖: {len(chuangyijiang)} 人")
    
    # 3. 合并完成奖名单（小书童 + 名单中的完成奖）
    print("\n合并完成奖名单...")
    wanchengjiang_list = list(set(xiaoshutong_names + wancheng_from_mingdan))
    wanchengjiang_list.sort()  # 排序
    print(f"完成奖总计: {len(wanchengjiang_list)} 人")
    
    # 4. 更新完成奖.html
    print("\n更新完成奖.html...")
    update_wanchengjiang_html(wanchengjiang_list)
    
    # 5. 更新优秀奖相关HTML文件
    print("\n更新优秀奖相关文件...")
    # 优秀奖和创意奖也需要排序
    youxiujiang.sort()
    chuangyijiang.sort()
    
    if chuangyijiang:
        # 有创意奖，更新优秀奖-创意奖.html
        update_youxiujiang_html(youxiujiang, chuangyijiang)
        # 如果存在优秀奖.html，删除它
        # if os.path.exists(YOUXIUJIANG_ONLY_HTML):
        #     os.remove(YOUXIUJIANG_ONLY_HTML)
        #     print(f"[OK] 已删除优秀奖.html（因为存在创意奖）")
    else:
        # 没有创意奖，更新优秀奖.html
        update_youxiujiang_only_html(youxiujiang)
        # 如果存在优秀奖-创意奖.html，删除它
        # if os.path.exists(YOUXIUJIANG_HTML):
        #     os.remove(YOUXIUJIANG_HTML)
        #     print(f"[OK] 已删除优秀奖-创意奖.html（因为不存在创意奖）")
    
    print("\n" + "=" * 50)
    print("榜单整理完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()
