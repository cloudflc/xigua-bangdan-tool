import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import sys
import shutil

# Add the current directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir:
    sys.path.append(current_dir)

# Import the main functions from the original script
from 自动整理榜单 import read_mingdan, read_xiaoshutong, update_wanchengjiang_html, update_youxiujiang_html, update_youxiujiang_only_html

class AwardListApp:
    def __init__(self, root):
        self.root = root
        self.root.title("榜单制作工具")
        self.root.geometry("600x400")
        
        # Variables
        self.mingdan_file = tk.StringVar()
        self.xiaoshutong_file = tk.StringVar()
        self.output_path = tk.StringVar()
        
        # Create GUI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 1. 名单.csv file selection
        ttk.Label(main_frame, text="名单.csv 文件:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.mingdan_file, width=50).grid(row=0, column=1, pady=5)
        ttk.Button(main_frame, text="浏览", command=self.browse_mingdan).grid(row=0, column=2, pady=5)
        
        # 2. 小书童文件 selection (optional)
        ttk.Label(main_frame, text="小书童文件 (可选):").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.xiaoshutong_file, width=50).grid(row=1, column=1, pady=5)
        ttk.Button(main_frame, text="浏览", command=self.browse_xiaoshutong).grid(row=1, column=2, pady=5)
        
        # 3. Output path selection
        ttk.Label(main_frame, text="输出路径:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_path, width=50).grid(row=2, column=1, pady=5)
        ttk.Button(main_frame, text="浏览", command=self.browse_output_path).grid(row=2, column=2, pady=5)
        
        # 4. Create button
        create_btn = ttk.Button(main_frame, text="制作榜单", command=self.create_awards)
        create_btn.grid(row=3, column=1, pady=20)
        
        # 5. Progress bar
        self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.progress.grid(row=4, column=0, columnspan=3, pady=10)
        
        # 6. Status text
        self.status_text = tk.Text(main_frame, height=10, width=70)
        self.status_text.grid(row=5, column=0, columnspan=3, pady=10)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
    def browse_mingdan(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.mingdan_file.set(file_path)
            
    def browse_xiaoshutong(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel and CSV Files", "*.xlsx *.csv"), ("Excel Files", "*.xlsx"), ("CSV Files", "*.csv"), ("All Files", "*.*")])
        if file_path:
            self.xiaoshutong_file.set(file_path)
            
    def browse_output_path(self):
        path = filedialog.askdirectory()
        if path:
            self.output_path.set(path)
            
    def create_awards(self):
        # Validate inputs
        if not self.mingdan_file.get():
            messagebox.showerror("错误", "请选择名单.csv 文件")
            return
            
        if not self.output_path.get():
            messagebox.showerror("错误", "请选择输出路径")
            return
            
        # Clear status text
        self.status_text.delete(1.0, tk.END)
        
        # Update progress
        self.progress['value'] = 0
        self.root.update_idletasks()
        
        original_dir = None
        
        try:
            # 1. Read mingdan file
            self.status_text.insert(tk.END, "读取名单.csv 文件...\n")
            self.root.update_idletasks()
            self.progress['value'] = 20
            
            # Read mingdan file
            wancheng_from_mingdan, youxiujiang, chuangyijiang = read_mingdan(self.mingdan_file.get())
            
            # 2. Read xiaoshutong file if provided
            self.status_text.insert(tk.END, f"名单中的完成奖: {len(wancheng_from_mingdan)} 人\n")
            self.status_text.insert(tk.END, f"名单中的优秀奖: {len(youxiujiang)} 人\n")
            self.status_text.insert(tk.END, f"名单中的创意奖: {len(chuangyijiang)} 人\n")
            self.root.update_idletasks()
            self.progress['value'] = 40
            
            xiaoshutong_names = []
            if self.xiaoshutong_file.get():
                self.status_text.insert(tk.END, "读取小书童文件...\n")
                xiaoshutong_names = read_xiaoshutong(self.xiaoshutong_file.get())
                self.status_text.insert(tk.END, f"小书童文件中的学员: {len(xiaoshutong_names)} 人\n")
                
            # 3. Merge wanchengjiang list
            self.status_text.insert(tk.END, "合并完成奖名单...\n")
            wanchengjiang_list = list(set(xiaoshutong_names + wancheng_from_mingdan))
            wanchengjiang_list.sort()
            self.status_text.insert(tk.END, f"完成奖总计: {len(wanchengjiang_list)} 人\n")
            self.root.update_idletasks()
            self.progress['value'] = 60
            
            # 4. Copy HTML templates to output path
            self.status_text.insert(tk.END, "复制 HTML 模板到输出路径...\n")
            
            # Normalize the output path to fix path separator issues
            output_dir = self.output_path.get().replace('\\', '/')
            script_dir = self.get_script_dir()
            
            # 只复制需要的HTML模板文件
            if chuangyijiang:
                # 有创意奖，只复制优秀奖-创意奖.html
                template_files = ["完成奖.html", "优秀奖-创意奖.html"]
            else:
                # 没有创意奖，只复制优秀奖.html
                template_files = ["完成奖.html", "优秀奖.html"]
            
            for template_file in template_files:
                src_path = f"{script_dir}/{template_file}"
                if os.path.exists(src_path):
                    dst_path = f"{output_dir}/{template_file}"
                    shutil.copy2(src_path, dst_path)
            
            # 5. Update HTML files (in output path, not in script directory)
            self.status_text.insert(tk.END, "更新 HTML 文件...\n")
            self.root.update_idletasks()
            self.progress['value'] = 80
            
            # Update wanchengjiang HTML - use output path
            wancheng_html_path = f"{output_dir}/完成奖.html"
            update_wanchengjiang_html(wanchengjiang_list, wancheng_html_path)
            
            # Update youxiujiang HTML - only generate needed file
            if chuangyijiang:
                youxiujiang_html_path = f"{output_dir}/优秀奖-创意奖.html"
                update_youxiujiang_html(youxiujiang, chuangyijiang, youxiujiang_html_path)
            else:
                youxiujiang_only_html_path = f"{output_dir}/优秀奖.html"
                update_youxiujiang_only_html(youxiujiang, youxiujiang_only_html_path)
            
            # Update progress
            self.progress['value'] = 100
            self.status_text.insert(tk.END, "榜单制作完成！\n")
            messagebox.showinfo("成功", "榜单制作完成！")
            
        except Exception as e:
            messagebox.showerror("错误", f"制作过程中出现错误: {str(e)}")
            self.status_text.insert(tk.END, f"错误: {str(e)}\n")
            
        finally:
            # Restore original directory
            if original_dir:
                os.chdir(original_dir)
                
    def get_script_dir(self):
        if getattr(sys, 'frozen', False):
            # 打包后的EXE环境 - 优先使用临时目录中的资源
            if hasattr(sys, '_MEIPASS'):
                return sys._MEIPASS
            return os.path.dirname(sys.executable)
        else:
            return os.path.dirname(os.path.abspath(__file__))
                
    def copy_html_templates(self):
        script_dir = self.get_script_dir()
        output_dir = self.output_path.get().replace('\\', '/')
        
        # Copy HTML templates to output path
        template_files = ["完成奖.html", "优秀奖-创意奖.html", "优秀奖.html"]
        
        for template_file in template_files:
            src_path = f"{script_dir}/{template_file}"
            if os.path.exists(src_path):
                dst_path = f"{output_dir}/{template_file}"
                shutil.copy2(src_path, dst_path)
                
    def move_html_files(self):
        script_dir = self.get_script_dir()
        
        # Move updated HTML files to output path
        html_files = ["完成奖.html", "优秀奖-创意奖.html", "优秀奖.html"]
        
        for html_file in html_files:
            src_path = os.path.join(script_dir, html_file)
            if os.path.exists(src_path):
                dst_path = os.path.join(self.output_path.get(), html_file)
                shutil.move(src_path, dst_path)
                
if __name__ == "__main__":
    root = tk.Tk()
    app = AwardListApp(root)
    root.mainloop()
