import sys
import asyncio
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QMenuBar, QStatusBar, QTreeWidget, 
                             QTreeWidgetItem, QStackedWidget, QLabel, QPushButton,
                             QTextEdit, QListWidget, QTableWidget, QTableWidgetItem,
                             QFrame, QSplitter, QAction, QMessageBox, QDialog,
                             QFormLayout, QLineEdit, QSpinBox, QDialogButtonBox,
                             QHeaderView, QAbstractItemView)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot, QTimer
from PyQt5.QtGui import QIcon, QFont
from supabase import create_client, Client
import json


# Supabase配置 - 请替换为您的实际配置
SUPABASE_URL = ''
SUPABASE_KEY = ''

class SupabaseClient:
    """Supabase数据库客户端"""
    def __init__(self):
        try:
            self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception as e:
            print(f"Supabase连接失败: {e}")
            self.supabase = None
    
    def get_users(self):
        """获取所有用户"""
        try:
            if not self.supabase:
                return []
            response = self.supabase.table('users').select("*").execute()
            return response.data
        except Exception as e:
            print(f"获取用户列表失败: {e}")
            return []
    
    def add_user(self, name, email, age):
        """添加用户"""
        try:
            if not self.supabase:
                return False, "数据库连接失败"
            data = {"name": name, "email": email, "age": age}
            response = self.supabase.table('users').insert(data).execute()
            return True, "用户添加成功"
        except Exception as e:
            return False, f"添加用户失败: {e}"
    
    def update_user(self, user_id, name, email, age):
        """更新用户"""
        try:
            if not self.supabase:
                return False, "数据库连接失败"
            data = {"name": name, "email": email, "age": age}
            response = self.supabase.table('users').update(data).eq('id', user_id).execute()
            return True, "用户更新成功"
        except Exception as e:
            return False, f"更新用户失败: {e}"
    
    def delete_user(self, user_id):
        """删除用户"""
        try:
            if not self.supabase:
                return False, "数据库连接失败"
            response = self.supabase.table('users').delete().eq('id', user_id).execute()
            return True, "用户删除成功"
        except Exception as e:
            return False, f"删除用户失败: {e}"


class UserDialog(QDialog):
    """用户添加/编辑对话框"""
    def __init__(self, parent=None, user_data=None):
        super().__init__(parent)
        self.user_data = user_data
        self.init_ui()
        
        if user_data:
            self.load_user_data()
    
    def init_ui(self):
        self.setWindowTitle("添加用户" if not self.user_data else "编辑用户")
        self.setModal(True)
        self.setFixedSize(400, 250)
        
        layout = QVBoxLayout()
        
        # 表单布局
        form_layout = QFormLayout()
        
        # 输入字段
        self.name_edit = QLineEdit()
        self.name_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        
        self.email_edit = QLineEdit()
        self.email_edit.setStyleSheet(self.name_edit.styleSheet())
        
        self.age_spin = QSpinBox()
        self.age_spin.setRange(1, 120)
        self.age_spin.setValue(25)
        self.age_spin.setStyleSheet("""
            QSpinBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                font-size: 14px;
            }
            QSpinBox:focus {
                border-color: #3498db;
            }
        """)
        
        form_layout.addRow("姓名:", self.name_edit)
        form_layout.addRow("邮箱:", self.email_edit)
        form_layout.addRow("年龄:", self.age_spin)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.setStyleSheet("""
            QDialogButtonBox QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QDialogButtonBox QPushButton:hover {
                background-color: #2980b9;
            }
            QDialogButtonBox QPushButton[text="Cancel"] {
                background-color: #95a5a6;
            }
            QDialogButtonBox QPushButton[text="Cancel"]:hover {
                background-color: #7f8c8d;
            }
        """)
        
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addLayout(form_layout)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def load_user_data(self):
        """加载用户数据到表单"""
        if self.user_data:
            self.name_edit.setText(str(self.user_data.get('name', '')))
            self.email_edit.setText(str(self.user_data.get('email', '')))
            self.age_spin.setValue(int(self.user_data.get('age', 25)))
    
    def get_user_data(self):
        """获取表单数据"""
        return {
            'name': self.name_edit.text().strip(),
            'email': self.email_edit.text().strip(),
            'age': self.age_spin.value()
        }
    
    def validate_data(self):
        """验证数据"""
        data = self.get_user_data()
        
        if not data['name']:
            QMessageBox.warning(self, "验证错误", "请输入姓名")
            return False
        
        if not data['email']:
            QMessageBox.warning(self, "验证错误", "请输入邮箱")
            return False
        
        if '@' not in data['email']:
            QMessageBox.warning(self, "验证错误", "请输入有效的邮箱地址")
            return False
        
        return True
    
    def accept(self):
        if self.validate_data():
            super().accept()


class UserListPage(QWidget):
    """用户列表页面"""
    def __init__(self):
        super().__init__()
        self.title = "用户列表"
        self.db_client = SupabaseClient()
        print('db_client_: ', self.db_client )
        self.init_ui()
        self.load_users()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 标题和操作按钮
        header_layout = QHBoxLayout()
        title_label = QLabel("用户管理")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        
        # 操作按钮
        self.add_btn = QPushButton("➕ 添加用户")
        self.edit_btn = QPushButton("✏️ 编辑用户")
        self.delete_btn = QPushButton("🗑️ 删除用户")
        self.refresh_btn = QPushButton("🔄 刷新")
        
        # 设置按钮样式
        button_style = """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """
        
        for btn in [self.add_btn, self.edit_btn, self.delete_btn, self.refresh_btn]:
            btn.setStyleSheet(button_style)
        
        # 删除按钮特殊样式
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        
        # 编辑和删除按钮默认禁用
        self.edit_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        
        # 连接按钮事件
        self.add_btn.clicked.connect(self.add_user)
        self.edit_btn.clicked.connect(self.edit_user)
        self.delete_btn.clicked.connect(self.delete_user)
        self.refresh_btn.clicked.connect(self.load_users)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.add_btn)
        header_layout.addWidget(self.edit_btn)
        header_layout.addWidget(self.delete_btn)
        header_layout.addWidget(self.refresh_btn)
        
        # 用户表格
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(4)
        self.user_table.setHorizontalHeaderLabels(["ID", "姓名", "邮箱", "年龄"])
        
        # 设置表格属性
        self.user_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.user_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.user_table.setAlternatingRowColors(True)
        
        # 设置列宽
        header = self.user_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID列
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # 姓名列
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # 邮箱列
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 年龄列
        
        # 表格样式
        self.user_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #ddd;
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 12px 8px;
                border: none;
                font-weight: bold;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        
        # 连接选择变化事件
        self.user_table.selectionModel().selectionChanged.connect(self.on_selection_changed)
        
        # 状态标签
        self.status_label = QLabel("正在加载用户数据...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-style: italic;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 4px;
            }
        """)
        
        layout.addLayout(header_layout)
        layout.addWidget(self.user_table)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
    
    def load_users(self):
        """加载用户数据"""
        self.status_label.setText("正在加载用户数据...")
        
        # 模拟加载延迟（在实际应用中，这里应该使用QThread来避免界面冻结）
        QTimer.singleShot(100, self._load_users_data)
    
    def _load_users_data(self):
        """实际加载用户数据"""
        try:
            users = self.db_client.get_users()
            
            if not users:
                self.user_table.setRowCount(0)
                self.status_label.setText("暂无用户数据")
                return
            
            # 设置表格行数
            self.user_table.setRowCount(len(users))
            
            # 填充数据
            for row, user in enumerate(users):
                self.user_table.setItem(row, 0, QTableWidgetItem(str(user.get('id', ''))))
                self.user_table.setItem(row, 1, QTableWidgetItem(str(user.get('name', ''))))
                self.user_table.setItem(row, 2, QTableWidgetItem(str(user.get('email', ''))))
                self.user_table.setItem(row, 3, QTableWidgetItem(str(user.get('age', ''))))
            
            self.status_label.setText(f"共找到 {len(users)} 位用户")
            
        except Exception as e:
            self.status_label.setText(f"加载失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"加载用户数据失败:\n{str(e)}")
    
    def on_selection_changed(self):
        """选择变化事件"""
        has_selection = bool(self.user_table.selectionModel().selectedRows())
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
    
    def get_selected_user(self):
        """获取选中的用户数据"""
        selected_rows = self.user_table.selectionModel().selectedRows()
        if not selected_rows:
            return None
        
        row = selected_rows[0].row()
        return {
            'id': self.user_table.item(row, 0).text(),
            'name': self.user_table.item(row, 1).text(),
            'email': self.user_table.item(row, 2).text(),
            'age': int(self.user_table.item(row, 3).text())
        }
    
    def add_user(self):
        """添加用户"""
        dialog = UserDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_user_data()
            
            # 添加到数据库
            success, message = self.db_client.add_user(data['name'], data['email'], data['age'])
            
            if success:
                QMessageBox.information(self, "成功", message)
                self.load_users()  # 重新加载数据
            else:
                QMessageBox.critical(self, "错误", message)
    
    def edit_user(self):
        """编辑用户"""
        user_data = self.get_selected_user()
        if not user_data:
            QMessageBox.warning(self, "警告", "请选择要编辑的用户")
            return
        
        dialog = UserDialog(self, user_data)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_user_data()
            
            # 更新数据库
            success, message = self.db_client.update_user(
                user_data['id'], data['name'], data['email'], data['age']
            )
            
            if success:
                QMessageBox.information(self, "成功", message)
                self.load_users()  # 重新加载数据
            else:
                QMessageBox.critical(self, "错误", message)
    
    def delete_user(self):
        """删除用户"""
        user_data = self.get_selected_user()
        if not user_data:
            QMessageBox.warning(self, "警告", "请选择要删除的用户")
            return
        
        # 确认删除
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除用户 '{user_data['name']}' 吗？\n此操作无法撤销。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 从数据库删除
            success, message = self.db_client.delete_user(user_data['id'])
            
            if success:
                QMessageBox.information(self, "成功", message)
                self.load_users()  # 重新加载数据
            else:
                QMessageBox.critical(self, "错误", message)
    """内容页面基类"""
    def __init__(self, title="默认页面"):
        super().__init__()
        self.title = title
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 页面标题
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; margin: 10px 0;")
        
        # 页面内容
        content_label = QLabel(f"这是{self.title}的内容区域")
        content_label.setStyleSheet("color: #34495e; font-size: 14px;")
        content_label.setAlignment(Qt.AlignCenter)
        content_label.setMinimumHeight(200)
        
        layout.addWidget(title_label)
        layout.addWidget(content_label)
        layout.addStretch()
        
        self.setLayout(layout)

class ContentPage(QWidget):
    """内容页面基类"""
    def __init__(self, title="默认页面"):
        super().__init__()
        self.title = title
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 页面标题
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; margin: 10px 0;")
        
        # 页面内容
        content_label = QLabel(f"这是{self.title}的内容区域")
        content_label.setStyleSheet("color: #34495e; font-size: 14px;")
        content_label.setAlignment(Qt.AlignCenter)
        content_label.setMinimumHeight(200)
        
        layout.addWidget(title_label)
        layout.addWidget(content_label)
        layout.addStretch()
        
        self.setLayout(layout)

class DashboardPage(ContentPage):
    """仪表板页面"""
    def __init__(self):
        super().__init__("仪表板")
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("系统仪表板")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; margin: 10px 0;")
        
        # 统计卡片区域
        cards_layout = QHBoxLayout()
        
        for i, (title, value, color) in enumerate([
            ("总用户数", "1,234", "#e74c3c"),
            ("活跃用户", "856", "#27ae60"),
            ("今日访问", "2,458", "#3498db"),
            ("系统状态", "正常", "#f39c12")
        ]):
            card = QFrame()
            card.setFrameStyle(QFrame.Box)
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: white;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 15px;
                }}
            """)
            
            card_layout = QVBoxLayout()
            value_label = QLabel(value)
            value_label.setFont(QFont("Arial", 20, QFont.Bold))
            value_label.setStyleSheet(f"color: {color};")
            value_label.setAlignment(Qt.AlignCenter)
            
            title_label_card = QLabel(title)
            title_label_card.setAlignment(Qt.AlignCenter)
            title_label_card.setStyleSheet("color: #7f8c8d; font-size: 12px;")
            
            card_layout.addWidget(value_label)
            card_layout.addWidget(title_label_card)
            card.setLayout(card_layout)
            cards_layout.addWidget(card)
        
        # 图表区域
        chart_area = QFrame()
        chart_area.setFrameStyle(QFrame.Box)
        chart_area.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                margin: 10px 0;
            }
        """)
        chart_layout = QVBoxLayout()
        chart_title = QLabel("数据趋势图")
        chart_title.setFont(QFont("Arial", 14, QFont.Bold))
        chart_title.setStyleSheet("color: #2c3e50; margin: 10px;")
        
        chart_placeholder = QLabel("📈 图表内容区域")
        chart_placeholder.setAlignment(Qt.AlignCenter)
        chart_placeholder.setMinimumHeight(200)
        chart_placeholder.setStyleSheet("color: #95a5a6; font-size: 16px;")
        
        chart_layout.addWidget(chart_title)
        chart_layout.addWidget(chart_placeholder)
        chart_area.setLayout(chart_layout)
        
        layout.addWidget(title_label)
        layout.addLayout(cards_layout)
        layout.addWidget(chart_area)
        layout.addStretch()
        
        self.setLayout(layout)


class DataManagePage(ContentPage):
    """数据管理页面"""
    def __init__(self):
        super().__init__("数据管理")
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 标题和操作按钮
        header_layout = QHBoxLayout()
        title_label = QLabel("数据管理")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        
        add_btn = QPushButton("新增数据")
        edit_btn = QPushButton("编辑")
        delete_btn = QPushButton("删除")
        
        for btn in [add_btn, edit_btn, delete_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(add_btn)
        header_layout.addWidget(edit_btn)
        header_layout.addWidget(delete_btn)
        
        # 数据表格
        table = QTableWidget(5, 4)
        table.setHorizontalHeaderLabels(["ID", "名称", "创建时间", "状态"])
        
        # 添加示例数据
        sample_data = [
            ["001", "项目A", "2024-01-15", "活跃"],
            ["002", "项目B", "2024-01-16", "暂停"],
            ["003", "项目C", "2024-01-17", "活跃"],
            ["004", "项目D", "2024-01-18", "完成"],
            ["005", "项目E", "2024-01-19", "活跃"]
        ]
        
        for row, data in enumerate(sample_data):
            for col, value in enumerate(data):
                table.setItem(row, col, QTableWidgetItem(value))
        
        table.setStyleSheet("""
            QTableWidget {
                gridline-color: #ddd;
                background-color: white;
                alternate-background-color: #f8f9fa;
            }
            QHeaderView::section {
                background-color: #ecf0f1;
                padding: 8px;
                border: 1px solid #bdc3c7;
                font-weight: bold;
            }
        """)
        
        layout.addLayout(header_layout)
        layout.addWidget(table)
        
        self.setLayout(layout)


class SettingsPage(ContentPage):
    """设置页面"""
    def __init__(self):
        super().__init__("系统设置")
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        title_label = QLabel("系统设置")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        
        # 设置选项
        settings_frame = QFrame()
        settings_frame.setFrameStyle(QFrame.Box)
        settings_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        
        settings_layout = QVBoxLayout()
        
        # 设置项
        for setting in ["主题设置", "语言设置", "通知设置", "安全设置", "备份设置"]:
            setting_item = QHBoxLayout()
            setting_label = QLabel(setting)
            setting_label.setStyleSheet("font-size: 14px; color: #34495e;")
            
            config_btn = QPushButton("配置")
            config_btn.setStyleSheet("""
                QPushButton {
                    background-color: #95a5a6;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #7f8c8d;
                }
            """)
            
            setting_item.addWidget(setting_label)
            setting_item.addStretch()
            setting_item.addWidget(config_btn)
            
            settings_layout.addLayout(setting_item)
        
        settings_frame.setLayout(settings_layout)
        
        layout.addWidget(title_label)
        layout.addWidget(settings_frame)
        layout.addStretch()
        
        self.setLayout(layout)


class LeftMenuWidget(QTreeWidget):
    """左侧菜单组件"""
    menu_clicked = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_menu()
    
    def init_ui(self):
        self.setHeaderHidden(True)
        self.setRootIsDecorated(True)
        self.setIndentation(20)
        self.setMinimumWidth(200)
        self.setMaximumWidth(250)
        
        # 设置样式
        self.setStyleSheet("""
            QTreeWidget {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: none;
                font-size: 14px;
                outline: none;
            }
            QTreeWidget::item {
                padding: 8px;
                border-bottom: 1px solid #34495e;
            }
            QTreeWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QTreeWidget::item:hover {
                background-color: #34495e;
            }
            QTreeWidget::branch:has-children:closed {
                image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAkAAAAJCAYAAADgkQYQAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAAdgAAAHYBTnsmCAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAFJSURBVBiVY/z//z8DKYCJgUTABKW5uLg4Hz58+B8XJ8g5OTk5);
            }
            QTreeWidget::branch:has-children:open {
                image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAkAAAAJCAYAAADgkQYQAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAAdgAAAHYBTnsmCAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAFJSURBVBiVY/z//z8DKYCJgUTABKW5uLg4Hz58+B8XJ8g5OTk5);
            }
        """)
    
    def setup_menu(self):
        # 主要菜单项
        dashboard = QTreeWidgetItem(self, ["📊 仪表板"])
        dashboard.setData(0, Qt.UserRole, "dashboard")
        
        # 数据管理
        data_mgmt = QTreeWidgetItem(self, ["📁 数据管理"])
        data_item1 = QTreeWidgetItem(data_mgmt, ["📄 数据列表"])
        data_item1.setData(0, Qt.UserRole, "data_list")
        data_item2 = QTreeWidgetItem(data_mgmt, ["📈 数据分析"])
        data_item2.setData(0, Qt.UserRole, "data_analysis")
        data_item3 = QTreeWidgetItem(data_mgmt, ["📊 数据报表"])
        data_item3.setData(0, Qt.UserRole, "data_report")
        
        # 用户管理
        user_mgmt = QTreeWidgetItem(self, ["👥 用户管理"])
        user_item1 = QTreeWidgetItem(user_mgmt, ["👤 用户列表"])
        user_item1.setData(0, Qt.UserRole, "user_list")
        user_item2 = QTreeWidgetItem(user_mgmt, ["🔒 权限管理"])
        user_item2.setData(0, Qt.UserRole, "permission")
        
        # 系统设置
        settings = QTreeWidgetItem(self, ["⚙️ 系统设置"])
        settings.setData(0, Qt.UserRole, "settings")
        setting_item1 = QTreeWidgetItem(settings, ["🎨 界面设置"])
        setting_item1.setData(0, Qt.UserRole, "ui_settings")
        setting_item2 = QTreeWidgetItem(settings, ["🔧 系统配置"])
        setting_item2.setData(0, Qt.UserRole, "system_config")
        
        # 帮助
        help_item = QTreeWidgetItem(self, ["❓ 帮助"])
        help_item.setData(0, Qt.UserRole, "help")
        
        # 展开主要节点
        self.expandItem(data_mgmt)
        self.expandItem(user_mgmt)
        
        # 连接点击事件
        self.itemClicked.connect(self.on_item_clicked)
    
    def on_item_clicked(self, item, column):
        item_key = item.data(0, Qt.UserRole)
        if item_key:
            self.menu_clicked.emit(item_key)


class MainWindow(QMainWindow):
    """主窗口"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_menu_bar()
        self.setup_status_bar()
        self.setup_central_widget()
        
    def init_ui(self):
        self.setWindowTitle("PyQt5 桌面软件")
        self.setGeometry(100, 100, 1200, 800)
        
        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ecf0f1;
            }
        """)
    
    def setup_menu_bar(self):
        """设置菜单栏"""
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #34495e;
                color: #ecf0f1;
                border-bottom: 1px solid #2c3e50;
                padding: 4px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 12px;
            }
            QMenuBar::item:selected {
                background-color: #3498db;
                border-radius: 4px;
            }
            QMenu {
                background-color: #34495e;
                color: #ecf0f1;
                border: 1px solid #2c3e50;
            }
            QMenu::item {
                padding: 8px 20px;
            }
            QMenu::item:selected {
                background-color: #3498db;
            }
        """)
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        
        new_action = QAction('新建', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(lambda: self.show_message('新建文件'))
        file_menu.addAction(new_action)
        
        open_action = QAction('打开', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(lambda: self.show_message('打开文件'))
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('退出', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = menubar.addMenu('编辑')
        
        copy_action = QAction('复制', self)
        copy_action.setShortcut('Ctrl+C')
        copy_action.triggered.connect(lambda: self.show_message('复制'))
        edit_menu.addAction(copy_action)
        
        paste_action = QAction('粘贴', self)
        paste_action.setShortcut('Ctrl+V')
        paste_action.triggered.connect(lambda: self.show_message('粘贴'))
        edit_menu.addAction(paste_action)
        
        # 视图菜单
        view_menu = menubar.addMenu('视图')
        
        fullscreen_action = QAction('全屏', self)
        fullscreen_action.setShortcut('F11')
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助')
        
        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_status_bar(self):
        """设置状态栏"""
        statusbar = self.statusBar()
        statusbar.setStyleSheet("""
            QStatusBar {
                background-color: #34495e;
                color: #ecf0f1;
                border-top: 1px solid #2c3e50;
                padding: 2px;
            }
        """)
        
        # 添加状态信息
        statusbar.showMessage("就绪")
        
        # 添加永久显示的状态信息
        status_label = QLabel("系统状态：正常运行")
        status_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
        statusbar.addPermanentWidget(status_label)
        
        time_label = QLabel("用户：管理员")
        time_label.setStyleSheet("color: #ecf0f1; margin-left: 20px;")
        statusbar.addPermanentWidget(time_label)
    
    def setup_central_widget(self):
        """设置中央窗口部件"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧菜单
        self.left_menu = LeftMenuWidget()
        self.left_menu.menu_clicked.connect(self.switch_page)
        
        # 右侧内容区域
        self.content_area = QStackedWidget()
        self.content_area.setStyleSheet("""
            QStackedWidget {
                background-color: #ecf0f1;
                border: none;
            }
        """)
        
        # 创建内容页面
        self.pages = {
            "dashboard": DashboardPage(),
            "data_list": DataManagePage(),
            "data_analysis": ContentPage("数据分析"),
            "data_report": ContentPage("数据报表"),
            "user_list": UserListPage('ulist12131'),  # 使用新的用户管理页面
            "permission": ContentPage("权限管理"),
            "settings": SettingsPage(),
            "ui_settings": ContentPage("界面设置"),
            "system_config": ContentPage("系统配置"),
            "help": ContentPage("帮助文档")
        }
        
        # 添加页面到堆栈窗口
        for page in self.pages.values():
            self.content_area.addWidget(page)
        
        # 设置默认页面
        self.content_area.setCurrentWidget(self.pages["dashboard"])
        
        # 添加到分割器
        splitter.addWidget(self.left_menu)
        splitter.addWidget(self.content_area)
        splitter.setSizes([250, 950])  # 设置初始分割比例
        
        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)
    
    def switch_page(self, page_key):
        """切换页面"""
        if page_key in self.pages:
            self.content_area.setCurrentWidget(self.pages[page_key])
            self.statusBar().showMessage(f"当前页面：{self.pages[page_key].title}")
        else:
            self.show_message(f"页面 {page_key} 功能开发中...")
    
    def show_message(self, message):
        """显示消息"""
        self.statusBar().showMessage(message, 3000)  # 显示3秒
    
    def toggle_fullscreen(self):
        """切换全屏模式"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于", 
                         "PyQt5 桌面软件演示\n\n"
                         "版本：1.0.0\n"
                         "基于 Python 3.8 + PyQt5\n\n"
                         "功能特点：\n"
                         "• 现代化界面设计\n"
                         "• 响应式布局\n"
                         "• 多页面管理\n"
                         "• 完整的菜单系统")


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 检查Supabase配置
    if SUPABASE_URL == "your-supabase-url" or SUPABASE_KEY == "your-supabase-anon-key":
        QMessageBox.warning(
            window, 
            "配置提醒", 
            "请在代码中配置您的Supabase URL和API密钥\n\n"
            "需要修改以下变量:\n"
            "• SUPABASE_URL\n"
            "• SUPABASE_KEY\n\n"
            "同时确保已安装supabase库:\n"
            "pip install supabase"
        )
    
    # 运行应用程序
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()