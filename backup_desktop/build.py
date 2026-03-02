import PyInstaller.__main__
import os
import platform

current_dir = os.path.dirname(os.path.abspath(__file__))

if platform.system() == "Windows":
    args = [
        '--onefile',
        '--windowed',
        '--name', '榜单制作工具',
        '--clean',
        '--noconfirm',
        '--add-data', os.path.join(current_dir, '完成奖.html') + ';.',
        '--add-data', os.path.join(current_dir, '优秀奖-创意奖.html') + ';.',
        '--add-data', os.path.join(current_dir, '优秀奖.html') + ';.',
        '--exclude-module', 'matplotlib',
        '--exclude-module', 'sklearn',
        '--exclude-module', 'scipy',
        '--exclude-module', 'cv2',
        '--exclude-module', 'PIL',
        '--exclude-module', 'sympy',
        '--exclude-module', 'openpyxl',
        '--exclude-module', 'xlrd',
        '--exclude-module', 'xlwt',
        '--hidden-import', 'pandas',
        '--hidden-import', 'tkinter',
        '--hidden-import', 'tkinter.ttk',
        os.path.join(current_dir, 'gui_app.py')
    ]
    print("开始打包 Windows 版本...")
elif platform.system() == "Darwin":
    args = [
        '--onefile',
        '--windowed',
        '--name', '榜单制作工具',
        '--clean',
        '--noconfirm',
        '--add-data', os.path.join(current_dir, '完成奖.html') + ':.',
        '--add-data', os.path.join(current_dir, '优秀奖-创意奖.html') + ':.',
        '--add-data', os.path.join(current_dir, '优秀奖.html') + ':.',
        '--exclude-module', 'matplotlib',
        '--exclude-module', 'sklearn',
        '--exclude-module', 'scipy',
        '--exclude-module', 'cv2',
        '--exclude-module', 'PIL',
        '--exclude-module', 'sympy',
        '--exclude-module', 'openpyxl',
        '--exclude-module', 'xlrd',
        '--exclude-module', 'xlwt',
        '--hidden-import', 'pandas',
        '--hidden-import', 'tkinter',
        '--hidden-import', 'tkinter.ttk',
        os.path.join(current_dir, 'gui_app.py')
    ]
    print("开始打包 Mac 版本...")
else:
    print("不支持的操作系统")
    exit(1)

print("这可能需要几分钟，请耐心等待...")

PyInstaller.__main__.run(args)

print("打包完成！")
print(f"EXE文件位置: dist/榜单制作工具")
