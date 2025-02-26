import subprocess
import platform
import os
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json

class CommandManager:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("命令启动管理器")
        self.window.geometry("800x500")
        
        # 确保配置目录存在
        self.config_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'XmiCmd')
        self.config_file = os.path.join(self.config_dir, 'commands.json')
        os.makedirs(self.config_dir, exist_ok=True)
        
        # 存储命令列表
        self.commands = self.load_commands()
        
        # 创建界面
        self.create_widgets()
        
        # 主窗口居中
        self.center_window(self.window)
        
    def create_widgets(self):
        """创建GUI界面元素"""
        # 按钮框架
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="新增", command=self.show_add_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="删除", command=self.delete_command).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="全选", command=self.select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="启动选中", command=self.start_all).pack(side=tk.RIGHT, padx=5)
        
        # 命令列表框架
        list_frame = ttk.LabelFrame(self.window, text="命令列表", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建表格
        columns = ("选择", "标签名", "命令")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # 设置列标题和宽度
        self.tree.heading("选择", text="选择")
        self.tree.column("选择", width=80, anchor=tk.CENTER)
        self.tree.heading("标签名", text="名称")
        self.tree.column("标签名", width=150)
        self.tree.heading("命令", text="命令")
        self.tree.column("命令", width=520)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 放置表格和滚动条
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定事件
        self.tree.bind('<Button-1>', self.toggle_selection)
        self.tree.bind('<Double-1>', self.on_double_click)
        
        # 更新表格数据
        self.update_tree()

    def center_window(self, window):
        """将窗口居中显示"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')

    def show_add_dialog(self):
        """显示新增/编辑对话框"""
        dialog = tk.Toplevel(self.window)
        dialog.title("新增命令")
        dialog.geometry("500x200")
        dialog.transient(self.window)
        dialog.grab_set()
        
        # 对话框居中
        self.center_window(dialog)
        
        # 创建主框架并添加内边距
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建变量
        dir_var = tk.StringVar()
        cmd_var = tk.StringVar()
        name_var = tk.StringVar()
        
        # 目录选择框架
        dir_frame = ttk.Frame(main_frame)
        dir_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(dir_frame, text="目录:", width=8).pack(side=tk.LEFT)
        dir_entry = ttk.Entry(dir_frame, textvariable=dir_var)
        dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        ttk.Button(dir_frame, text="浏览", command=lambda: self.browse_directory(dir_var, dialog)).pack(side=tk.LEFT)
        
        # 命令输入框架
        cmd_frame = ttk.Frame(main_frame)
        cmd_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(cmd_frame, text="命令:", width=8).pack(side=tk.LEFT)
        ttk.Entry(cmd_frame, textvariable=cmd_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # 名称输入框架
        name_frame = ttk.Frame(main_frame)
        name_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(name_frame, text="名称:", width=8).pack(side=tk.LEFT)
        ttk.Entry(name_frame, textvariable=name_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        def save_command():
            dir_path = dir_var.get().strip()
            cmd = cmd_var.get().strip()
            name = name_var.get().strip()
            
            if dir_path and cmd and name:
                self.commands.append([dir_path, cmd, name])
                self.save_commands()
                self.update_tree()
                dialog.destroy()
            else:
                messagebox.showwarning("警告", "请填写所有字段", parent=dialog)
        
        ttk.Button(button_frame, text="保存", command=save_command).pack(side=tk.RIGHT)

    def browse_directory(self, dir_var, parent):
        directory = filedialog.askdirectory(parent=parent)
        if directory:
            dir_var.set(directory)
    
    def edit_command(self, event):
        """编辑命令"""
        item = self.tree.identify_row(event.y)
        if not item:
            return
            
        # 获取当前命令数据
        idx = self.tree.index(item)
        current_cmd = self.commands[idx]
        
        dialog = tk.Toplevel(self.window)
        dialog.title("编辑命令")
        dialog.geometry("500x200")
        dialog.transient(self.window)
        dialog.grab_set()
        
        # 对话框居中
        self.center_window(dialog)
        
        # 创建主框架并添加内边距
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建变量
        dir_var = tk.StringVar(value=current_cmd[0])
        cmd_var = tk.StringVar(value=current_cmd[1])
        name_var = tk.StringVar(value=current_cmd[2])
        
        # 目录选择框架
        dir_frame = ttk.Frame(main_frame)
        dir_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(dir_frame, text="目录:", width=8).pack(side=tk.LEFT)
        dir_entry = ttk.Entry(dir_frame, textvariable=dir_var)
        dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        ttk.Button(dir_frame, text="浏览", command=lambda: self.browse_directory(dir_var, dialog)).pack(side=tk.LEFT)
        
        # 命令输入框架
        cmd_frame = ttk.Frame(main_frame)
        cmd_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(cmd_frame, text="命令:", width=8).pack(side=tk.LEFT)
        ttk.Entry(cmd_frame, textvariable=cmd_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # 名称输入框架
        name_frame = ttk.Frame(main_frame)
        name_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(name_frame, text="名称:", width=8).pack(side=tk.LEFT)
        ttk.Entry(name_frame, textvariable=name_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        def update_command():
            dir_path = dir_var.get().strip()
            cmd = cmd_var.get().strip()
            name = name_var.get().strip()
            
            if dir_path and cmd and name:
                self.commands[idx] = [dir_path, cmd, name]
                self.save_commands()
                self.update_tree()
                dialog.destroy()
            else:
                messagebox.showwarning("警告", "请填写所有字段", parent=dialog)
        
        ttk.Button(button_frame, text="保存", command=update_command).pack(side=tk.RIGHT)

    def update_tree(self):
        """更新表格数据"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for cmd in self.commands:
            # 使用空白和勾选符号
            self.tree.insert("", tk.END, values=("　", cmd[2], f"[{cmd[0]}] {cmd[1]}"))
    
    def delete_command(self):
        """删除选中的命令"""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            idx = self.tree.index(selected[0])
            self.commands.pop(idx)
            self.save_commands()
            self.update_tree()
    
    def toggle_selection(self, event):
        """切换命令的选择状态"""
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            if column == "#1":  # 点击选择列
                item = self.tree.identify_row(event.y)
                if item:
                    values = list(self.tree.item(item)['values'])
                    # 使用空白和勾选符号
                    values[0] = "✓" if values[0] == "　" else "　"
                    self.tree.item(item, values=values)
    
    def select_all(self):
        """全选/取消全选"""
        # 检查是否所有项目都已选中
        all_selected = True
        for item in self.tree.get_children():
            if self.tree.item(item)['values'][0] == "　":
                all_selected = False
                break
        
        # 切换所有项目的选择状态
        for item in self.tree.get_children():
            values = list(self.tree.item(item)['values'])
            values[0] = "　" if all_selected else "✓"
            self.tree.item(item, values=values)
    
    def start_all(self):
        """启动选中的命令"""
        if not self.commands:
            messagebox.showinfo("提示", "没有可用的命令")
            return
        
        if platform.system() != "Windows":
            messagebox.showerror("错误", "此功能仅支持 Windows Terminal")
            return
        
        # 获取选中的命令
        selected_commands = []
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            if values[0] == "✓":  # 修改选中状态的判断
                selected_commands.append(self.commands[self.tree.index(item)])
        
        if not selected_commands:
            messagebox.showinfo("提示", "请选择要启动的命令")
            return
        
        try:
            # 启动第一个标签页
            first_dir, first_cmd, first_name = selected_commands[0]
            first_full_cmd = f'cd /d "{first_dir}" && {first_cmd}'
            subprocess.Popen(f'wt -p "Command Prompt" --title "{first_name}" cmd /k "{first_full_cmd}"', shell=True)
            time.sleep(1)
            
            # 在新标签页中启动其他命令
            for work_dir, cmd, name in selected_commands[1:]:
                full_cmd = f'cd /d "{work_dir}" && {cmd}'
                subprocess.Popen(f'wt -w 0 nt --title "{name}" cmd /k "{full_cmd}"', shell=True)
                time.sleep(0.5)
            
            messagebox.showinfo("成功", "选中的命令已启动")
        except Exception as e:
            messagebox.showerror("错误", f"启动失败: {str(e)}")
    
    def load_commands(self):
        """从文件加载命令配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_commands(self):
        """保存命令配置到文件"""
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.commands, f, ensure_ascii=False, indent=2)
    
    def on_double_click(self, event):
        """处理双击事件"""
        region = self.tree.identify_region(event.x, event.y)
        column = self.tree.identify_column(event.x)
        
        # 如果不是点击选择列，才打开编辑窗口
        if region == "cell" and column != "#1":
            self.edit_command(event)
    
    def run(self):
        """运行应用"""
        self.window.mainloop()

if __name__ == "__main__":
    app = CommandManager()
    app.run()
