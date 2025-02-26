# 命令启动管理器 (Command Launcher Manager)

一个简单的Windows命令启动管理工具，可以保存并一键启动多个Windows Terminal命令。

## 功能特点

- 保存常用命令及其工作目录
- 支持批量选择并启动命令
- 使用Windows Terminal多标签页方式启动命令
- 支持编辑和删除已保存的命令
- 配置数据自动保存

## 系统要求

- Windows 10/11
- Python 3.6+
- Windows Terminal

## 安装步骤

1. 克隆或下载本项目
2. 安装所需依赖： 
bash
pip install -r requirements.txt

## 运行方式

直接运行源码：
bash
python xmi.py

## 打包步骤

1. 安装PyInstaller（如果尚未安装）：

pip install pyinstaller

2. 创建spec文件（如果尚未创建）：
bash
pyi-makespec xmi.py --name CommandManager --noconsole --onefile

3. 执行打包：
bash
python -m PyInstaller CommandManager.spec --clean


4. 打包完成后，可执行文件将在 `dist` 目录中

## 使用说明

1. 点击"新增"按钮添加新命令
2. 在弹出窗口中填写：
   - 目录：命令执行的工作目录
   - 命令：要执行的具体命令
   - 名称：命令的显示名称
3. 在主界面选择要执行的命令
4. 点击"启动选中"按钮执行所选命令

## 配置文件位置

配置文件保存在：`%LOCALAPPDATA%\XmiCmd\commands.json`

## 注意事项

- 本工具依赖Windows Terminal，请确保系统已安装
- 确保命令和目录路径正确
- 建议使用绝对路径

## 许可证

MIT License
