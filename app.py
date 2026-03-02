import pandas as pd
import re
import os
import base64
from flask import Flask, render_template, request, jsonify, send_file
import io
import tempfile

app = Flask(__name__)

INTERNAL_EMPLOYEES = [
    "凹凸", "凹凸曼", "Count", '​Chloe', 'Isabella', '测试 账号', '--', 'James', 'Zoe'
]

def get_template_dir():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

def read_xiaoshutong(file_storage):
    try:
        file_storage.seek(0)
        df = pd.read_excel(file_storage)
        names = df['学员名称'].dropna().astype(str).str.strip().tolist()
        names = [name for name in names if name and not name.isdigit() and name not in INTERNAL_EMPLOYEES]
        return names
    except Exception as e:
        print(f"读取小书童文件出错: {e}")
        return []

def read_mingdan(file_storage):
    try:
        file_storage.seek(0)
        df = pd.read_csv(file_storage, sep='\t', header=None, names=['奖项', '姓名'])
        
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
        print(f"读取名单文件出错: {e}")
        return [], [], []

def update_wanchengjiang_html(wanchengjiang_names, template_content):
    content = template_content
    
    names_str = ", ".join([f"'{name}'" for name in wanchengjiang_names])
    new_students = f"const students = [{names_str}];"
    pattern = r"const students\s*=\s*\[[^\]]*\];"
    content = re.sub(pattern, new_students, content)
    
    total_students = len(wanchengjiang_names)
    total_coins = total_students * 100
    
    stat_numbers = re.findall(r'<div class="stat-number">(\d+)</div>', content)
    new_stats = []
    for i, num in enumerate(stat_numbers):
        if i == 0:
            new_stats.append(str(total_students))
        elif i == 1:
            new_stats.append(str(total_coins))
        else:
            new_stats.append(num)
    
    for i, num in enumerate(stat_numbers):
        content = re.sub(
            f'<div class="stat-number">{num}</div>', 
            f'<div class="stat-number">{new_stats[i]}</div>', 
            content, 
            count=1
        )
    
    return content

def update_youxiujiang_html(youxiujiang_names, chuangyijiang_names, template_content):
    content = template_content
    
    if 'creativeWinners' not in content:
        awards_section_start = content.find('<section class="awards-section">')
        if awards_section_start != -1:
            insert_pos = content.find('\n', awards_section_start) + 1
            
            creative_section = '''            <div class="award-category creative">
                <div class="award-header">
                    <div>创意奖</div>
                    <div class="coins">400 <i class="fas fa-watermelon"></i> /人</div>
                </div>
                <div class="winners-list" id="creativeWinners">
                </div>
            </div>
'''
            content = content[:insert_pos] + creative_section + content[insert_pos:]
            
            old_clear = "document.getElementById('excellentWinners').innerHTML = '';"
            new_clear = "document.getElementById('creativeWinners').innerHTML = '';\n            document.getElementById('excellentWinners').innerHTML = '';"
            content = content.replace(old_clear, new_clear)
            
            old_render = "renderCategory(excellents, 'excellentWinners', '优秀奖');"
            new_render = """// 渲染创意奖
            const creatives = data.filter(item => item.award === '创意奖');
            document.getElementById('creativeCount').textContent = creatives.length;
            renderCategory(creatives, 'creativeWinners', '创意奖');

            renderCategory(excellents, 'excellentWinners', '优秀奖');"""
            content = content.replace(old_render, new_render)
    
    awards_items = []
    for name in chuangyijiang_names:
        awards_items.append(f'{{"award": "创意奖", "name": "{name}"}}')
    for name in youxiujiang_names:
        awards_items.append(f'{{"award": "优秀奖", "name": "{name}"}}')
    
    awards_str = ",\n".join(awards_items)
    awards_array = f"const awardsData = [{awards_str}];"
    
    idx = content.find("const awardsData = [")
    if idx != -1:
        end_idx = content.find("}];", idx)
        if end_idx != -1:
            content = content[:idx] + awards_array + content[end_idx + 3:]
    
    total_count = len(youxiujiang_names) + len(chuangyijiang_names)
    pattern = r'<span id="totalWinners">\d+</span>'
    content = re.sub(pattern, f'<span id="totalWinners">{total_count}</span>', content)
    
    if chuangyijiang_names:
        if '<span class="watermelon-coin">创意奖 <strong>400🍉</strong></span>' not in content:
            old_rewards = '<span class="watermelon-coin">优秀奖 <strong>200🍉</strong></span>'
            new_rewards = '<span class="watermelon-coin">创意奖 <strong>400🍉</strong></span>\n                <span class="watermelon-coin">优秀奖 <strong>200🍉</strong></span>'
            content = content.replace(old_rewards, new_rewards)
    
    return content

def update_youxiujiang_only_html(youxiujiang_names, template_content):
    content = template_content
    
    awards_items = []
    for name in youxiujiang_names:
        awards_items.append(f'{{"award": "优秀奖", "name": "{name}"}}')
    
    awards_str = ",\n".join(awards_items)
    awards_array = f"const awardsData = [{awards_str}];"
    
    pattern = r"const awardsData\s*=\s*\[[^\]]*\]\s*;"
    content = re.sub(pattern, awards_array, content)
    
    total_count = len(youxiujiang_names)
    pattern = r'<span id="totalWinners">\d+</span>'
    content = re.sub(pattern, f'<span id="totalWinners">{total_count}</span>', content)
    
    return content

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        mingdan_file = request.files.get('mingdan')
        xiaoshutong_file = request.files.get('xiaoshutong')
        
        if not mingdan_file:
            return jsonify({'error': '请上传名单.csv文件'}), 400
        
        wanchengjiang, youxiujiang, chuangyijiang = read_mingdan(mingdan_file)
        
        xiaoshutong_names = []
        if xiaoshutong_file:
            xiaoshutong_names = read_xiaoshutong(xiaoshutong_file)
        
        wanchengjiang_list = list(set(xiaoshutong_names + wanchengjiang))
        wanchengjiang_list.sort()
        youxiujiang.sort()
        chuangyijiang.sort()
        
        template_dir = get_template_dir()
        
        wancheng_template = os.path.join(template_dir, '完成奖.html')
        youxiujiang_template = os.path.join(template_dir, '优秀奖-创意奖.html')
        youxiujiang_only_template = os.path.join(template_dir, '优秀奖.html')
        
        files = {}
        
        with open(wancheng_template, 'r', encoding='utf-8') as f:
            wancheng_content = update_wanchengjiang_html(wanchengjiang_list, f.read())
        
        wancheng_base64 = base64.b64encode(wancheng_content.encode('utf-8')).decode('utf-8')
        files['完成奖.html'] = wancheng_base64
        
        if chuangyijiang:
            with open(youxiujiang_template, 'r', encoding='utf-8') as f:
                youxiujiang_content = update_youxiujiang_html(youxiujiang, chuangyijiang, f.read())
            
            youxiujiang_base64 = base64.b64encode(youxiujiang_content.encode('utf-8')).decode('utf-8')
            files['优秀奖-创意奖.html'] = youxiujiang_base64
        else:
            with open(youxiujiang_only_template, 'r', encoding='utf-8') as f:
                youxiujiang_content = update_youxiujiang_only_html(youxiujiang, f.read())
            
            youxiujiang_base64 = base64.b64encode(youxiujiang_content.encode('utf-8')).decode('utf-8')
            files['优秀奖.html'] = youxiujiang_base64
        
        return jsonify({
            'success': True,
            'wanchengjiang': len(wanchengjiang_list),
            'youxiujiang': len(youxiujiang),
            'chuangyijiang': len(chuangyijiang),
            'files': files
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
