import sys
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QTableWidget, QTableWidgetItem, 
                           QPushButton, QLineEdit, QComboBox, QLabel, 
                           QMessageBox, QDialog, QFormLayout, QDialogButtonBox,
                           QHeaderView, QAbstractItemView, QMenuBar, QMenu,
                           QAction, QStatusBar, QGroupBox, QGridLayout)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon

class DatabaseManager:
    """数据库管理类"""
    
    def __init__(self, db_name="data_management.db"):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """初始化数据库，创建表"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # 创建数据表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS data_list (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active',
                    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 插入一些示例数据
            cursor.execute('SELECT COUNT(*) FROM data_list')
            if cursor.fetchone()[0] == 0:
                sample_data = [
                    ('项目Alpha', 'active'),
                    ('项目Beta', 'inactive'),
                    ('项目Gamma', 'active'),
                    ('项目Delta', 'inactive'),
                    ('项目Epsilon', 'active')
                ]
                cursor.executemany(
                    'INSERT INTO data_list (name, status) VALUES (?, ?)', 
                    sample_data
                )
            
            conn.commit()
            conn.close()
            print("数据库初始化成功")
        except Exception as e:
            print(f"数据库初始化失败: {e}")
    
    def get_all_data(self):
        """获取所有数据"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, status, createdAt FROM data_list ORDER BY id DESC')
            data = cursor.fetchall()
            conn.close()
            return data
        except Exception as e:
            print(f"获取数据失败: {e}")
            return []
    
    def add_data(self, name, status):
        """添加数据"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO data_list (name, status) VALUES (?, ?)',
                (name, status)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"添加数据失败: {e}")
            return False
    
    def update_data(self, id, name, status):
        """更新数据"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE data_list SET name = ?, status = ? WHERE id = ?',
                (name, status, id)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"更新数据失败: {e}")
            return False
    
    def delete_data(self, id):
        """删除数据"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM data_list WHERE id = ?', (id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"删除数据失败: {e}")
            return False
    
    def search_data(self, keyword):
        """搜索数据"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id, name, status, createdAt FROM data_list WHERE name LIKE ? ORDER BY id DESC',
                (f'%{keyword}%',)
            )
            data = cursor.fetchall()
            conn.close()
            return data
        except Exception as e:
            print(f"搜索数据失败: {e}")
            return []

class DataEditDialog(QDialog):
    """数据编辑对话框"""
    
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.data = data
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("编辑数据" if self.data else "添加数据")
        self.setFixedSize(400, 200)
        
        layout = QFormLayout()
        
        # 名称输入
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("请输入名称")
        layout.addRow("名称:", self.name_edit)
        
        # 状态选择
        self.status_combo = QComboBox()
        self.status_combo.addItems(["active", "inactive"])
        layout.addRow("状态:", self.status_combo)
        
        # 如果是编辑模式，填充现有数据
        if self.data:
            self.name_edit.setText(self.data[1])
            self.status_combo.setCurrentText(self.data[2])
        
        # 按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        layout.addRow(buttons)
        self.setLayout(layout)
    
    def get_data(self):
        """获取表单数据"""
        return self.name_edit.text(), self.status_combo.currentText()

class DataManagementWidget(QWidget):
    """数据管理主界面"""
    
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("数据管理 - 数据列表")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 搜索和操作区域
        control_group = QGroupBox("操作面板")
        control_layout = QGridLayout()
        
        # 搜索框
        search_label = QLabel("搜索:")
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入名称进行搜索...")
        self.search_edit.textChanged.connect(self.search_data)
        
        # 操作按钮
        self.add_btn = QPushButton("添加数据")
        self.edit_btn = QPushButton("编辑数据")
        self.delete_btn = QPushButton("删除数据")
        self.refresh_btn = QPushButton("刷新列表")
        
        # 设置按钮样式
        buttons = [self.add_btn, self.edit_btn, self.delete_btn, self.refresh_btn]
        for btn in buttons:
            btn.setMinimumHeight(35)
            btn.setFont(QFont("Arial", 10))
        
        # 按钮颜色样式
        self.add_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; border-radius: 5px; }")
        self.edit_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; border-radius: 5px; }")
        self.delete_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; border-radius: 5px; }")
        self.refresh_btn.setStyleSheet("QPushButton { background-color: #FF9800; color: white; border-radius: 5px; }")
        
        # 布局
        control_layout.addWidget(search_label, 0, 0)
        control_layout.addWidget(self.search_edit, 0, 1, 1, 2)
        control_layout.addWidget(self.add_btn, 1, 0)
        control_layout.addWidget(self.edit_btn, 1, 1)
        control_layout.addWidget(self.delete_btn, 1, 2)
        control_layout.addWidget(self.refresh_btn, 1, 3)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # 数据表格
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "名称", "状态", "创建时间"])
        
        # 表格样式设置
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        
        # 设置列宽
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.table)
        
        # 状态栏信息
        self.status_label = QLabel("就绪")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # 连接信号
        self.add_btn.clicked.connect(self.add_data)
        self.edit_btn.clicked.connect(self.edit_data)
        self.delete_btn.clicked.connect(self.delete_data)
        self.refresh_btn.clicked.connect(self.load_data)
        self.table.doubleClicked.connect(self.edit_data)
    
    def load_data(self):
        """加载数据到表格"""
        data = self.db_manager.get_all_data()
        self.populate_table(data)
        self.status_label.setText(f"共加载 {len(data)} 条数据")
    
    def populate_table(self, data):
        """填充表格数据"""
        self.table.setRowCount(len(data))
        
        for row, item in enumerate(data):
            # ID
            self.table.setItem(row, 0, QTableWidgetItem(str(item[0])))
            
            # 名称
            self.table.setItem(row, 1, QTableWidgetItem(item[1]))
            
            # 状态 - 带颜色标识
            status_item = QTableWidgetItem(item[2])
            if item[2] == 'active':
                status_item.setBackground(Qt.green)
            else:
                status_item.setBackground(Qt.red)
            self.table.setItem(row, 2, status_item)
            
            # 创建时间
            created_at = item[3] if item[3] else ""
            if created_at:
                # 格式化时间显示
                try:
                    dt = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
                    formatted_time = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    formatted_time = created_at
            else:
                formatted_time = ""
            
            self.table.setItem(row, 3, QTableWidgetItem(formatted_time))
    
    def search_data(self):
        """搜索数据"""
        keyword = self.search_edit.text().strip()
        if keyword:
            data = self.db_manager.search_data(keyword)
            self.populate_table(data)
            self.status_label.setText(f"搜索到 {len(data)} 条数据")
        else:
            self.load_data()
    
    def add_data(self):
        """添加数据"""
        dialog = DataEditDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            name, status = dialog.get_data()
            if name.strip():
                if self.db_manager.add_data(name.strip(), status):
                    QMessageBox.information(self, "成功", "数据添加成功！")
                    self.load_data()
                else:
                    QMessageBox.critical(self, "错误", "数据添加失败！")
            else:
                QMessageBox.warning(self, "警告", "名称不能为空！")
    
    def edit_data(self):
        """编辑数据"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            # 获取当前行数据
            id_item = self.table.item(current_row, 0)
            name_item = self.table.item(current_row, 1)
            status_item = self.table.item(current_row, 2)
            created_item = self.table.item(current_row, 3)
            
            if id_item and name_item and status_item:
                data = (
                    int(id_item.text()),
                    name_item.text(),
                    status_item.text(),
                    created_item.text() if created_item else ""
                )
                
                dialog = DataEditDialog(self, data)
                if dialog.exec_() == QDialog.Accepted:
                    name, status = dialog.get_data()
                    if name.strip():
                        if self.db_manager.update_data(data[0], name.strip(), status):
                            QMessageBox.information(self, "成功", "数据更新成功！")
                            self.load_data()
                        else:
                            QMessageBox.critical(self, "错误", "数据更新失败！")
                    else:
                        QMessageBox.warning(self, "警告", "名称不能为空！")
        else:
            QMessageBox.warning(self, "警告", "请选择要编辑的行！")
    
    def delete_data(self):
        """删除数据"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            id_item = self.table.item(current_row, 0)
            name_item = self.table.item(current_row, 1)
            
            if id_item and name_item:
                reply = QMessageBox.question(
                    self, "确认删除", 
                    f"确定要删除 '{name_item.text()}' 吗？",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    if self.db_manager.delete_data(int(id_item.text())):
                        QMessageBox.information(self, "成功", "数据删除成功！")
                        self.load_data()
                    else:
                        QMessageBox.critical(self, "错误", "数据删除失败！")
        else:
            QMessageBox.warning(self, "警告", "请选择要删除的行！")

class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """初始化主界面"""
        self.setWindowTitle("数据管理系统")
        self.setGeometry(100, 100, 900, 600)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建状态栏
        self.statusBar().showMessage("数据管理系统已就绪")
        
        # 设置中心组件
        self.data_widget = DataManagementWidget()
        self.setCentralWidget(self.data_widget)
        
        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QMenuBar {
                background-color: #2c3e50;
                color: white;
                font-size: 12px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 16px;
            }
            QMenuBar::item:selected {
                background-color: #34495e;
            }
            QStatusBar {
                background-color: #2c3e50;
                color: white;
            }
        """)
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 数据管理菜单
        data_menu = menubar.addMenu("数据管理")
        
        # 数据列表菜单项
        data_list_action = QAction("数据列表", self)
        data_list_action.setStatusTip("查看和管理数据列表")
        data_list_action.triggered.connect(self.show_data_list)
        data_menu.addAction(data_list_action)
        
        data_menu.addSeparator()
        
        # 退出菜单项
        exit_action = QAction("退出", self)
        exit_action.setStatusTip("退出应用程序")
        exit_action.triggered.connect(self.close)
        data_menu.addAction(exit_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def show_data_list(self):
        """显示数据列表"""
        self.statusBar().showMessage("正在显示数据列表...")
        # 这里可以添加切换到数据列表界面的逻辑
        # 目前主界面就是数据列表，所以只刷新数据
        self.data_widget.load_data()
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self, "关于", 
            "数据管理系统 v1.0\n\n"
            "基于PyQt5开发的SQLite数据库管理工具\n"
            "支持数据的增删查改操作"
        )

def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setApplicationName("数据管理系统")
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()