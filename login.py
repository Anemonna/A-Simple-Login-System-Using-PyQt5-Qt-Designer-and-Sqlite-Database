import email
import sys
import webbrowser
import time
import sqlite3
import ctypes

from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem,QAbstractItemView,QHeaderView
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon,QColor

import resource_rc
import resource_main_rc


class LoginWindow(QMainWindow):
    # 类属性，用于存储当前登录用户信息
    current_username = ""
    current_password = ""
    
    def __init__(self):
        super().__init__()
        # 加载 .ui 文件
        self.ui = uic.loadUi('./loginUI.ui', self)
        self.setWindowIcon(QIcon('icon.png'))  # 路径指向你的图标文件
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 设置默认显示登录页面
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.stackedWidget_2.setCurrentIndex(2)
        #设置界面login跳转
        self.ui.pushButton_login.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        self.ui.pushButton_register.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))

        #登录按钮点击事件
        self.ui.pushButton_l_sure.clicked.connect(self.login)

        #注册按钮点击事件(还没写)
        self.ui.pushButton_r_sure.clicked.connect(self.register)



        # 用于拖动窗口的变量
        self.oldPos = None

    def login(self):
        username = self.ui.lineEdit_l_account.text()
        password = self.ui.lineEdit_l_password.text()
        username_list = []
        password_list = []
        conn = sqlite3.connect(database='MyData.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        rows = cursor.fetchall()
        for item in rows:
            username_list.append(item[1])
            password_list.append(item[2])
        conn.close()

        for i in range(len(username_list)):
            self.ui.stackedWidget_2.setCurrentIndex(3)
            if username == '' or password == '':
                self.ui.stackedWidget_2.setCurrentIndex(0) # 账号或密码不能为空!
                return
            elif username == username_list[i] and password == password_list[i]:
                # 设置类属性
                LoginWindow.current_username = username
                LoginWindow.current_password = password

                self.win = MainWindow()
                self.win.show()
                self.close()
                return
            else:
                self.ui.stackedWidget_2.setCurrentIndex(1) # 账号或密码错误!

    def register(self):
        new_username = self.ui.lineEdit_r_account.text()
        new_password = self.ui.lineEdit_r_password.text()
        confirm_password = self.ui.lineEdit_r_sure.text()

        conn = sqlite3.connect(database='MyData.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')  # 添加查询语句
        rows = cursor.fetchall()
        username_list = []
        for item in rows:
            username_list.append(item[1])

        if new_username == '' or new_password == '' or confirm_password == '':
            self.ui.stackedWidget_2.setCurrentIndex(0)
            return
        elif new_password != confirm_password:
            self.ui.stackedWidget_2.setCurrentIndex(3) # 两次密码不一致!
            return
        elif new_username in username_list:
            self.ui.stackedWidget_2.setCurrentIndex(4) # 账号已存在!
            return
        else:
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?);', (new_username, new_password))
            conn.commit()
            self.ui.stackedWidget_2.setCurrentIndex(5) # 注册成功，请登录!
            return
    
    # 使得窗口可以拖动-1
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPos()

    # 使得窗口可以拖动-2
    def mouseMoveEvent(self, event):
        if self.oldPos:
            delta = event.globalPos() - self.oldPos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()
    # 使得窗口可以拖动-3
    def mouseReleaseEvent(self, event):
        self.oldPos = None




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 加载 .ui 文件
        self.ui = uic.loadUi('./mainwindow.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.label_current_user.setText('用户：'+ LoginWindow.current_username)

        #左侧选择栏点击事件
        self.ui.pushButton_firstpage.clicked.connect(self.firstpage)
        self.ui.pushButton_web.clicked.connect(self.web)
        self.ui.pushButton_myinfo.clicked.connect(self.myinfo)

        # 数据查看按钮点击事件
        self.ui.pushButton_seedata.clicked.connect(self.seedata)

        #登出按钮点击事件
        self.ui.pushButton_logout.clicked.connect(self.logout)



        self.oldPos = None

    def firstpage(self):
        self.ui.stackedWidget.setCurrentIndex(0)

    def web(self):
        self.ui.stackedWidget.setCurrentIndex(1)
        self.ui.pushButton_bilibili.clicked.connect(lambda: webbrowser.open('https://www.bilibili.com/'))
        self.ui.pushButton_github.clicked.connect(lambda: webbrowser.open('https://github.com/'))
        self.ui.pushButton_CSDN.clicked.connect(lambda: webbrowser.open('https://www.csdn.net/'))
        self.ui.pushButton_apple.clicked.connect(lambda: webbrowser.open('https://www.apple.com/'))

    # 用户数据查看按钮点击事件
    def seedata(self):
        if LoginWindow.current_username == 'admin':
            self.ui.stackedWidget.setCurrentIndex(2)
            self.ui.stackedWidget_3.setCurrentIndex(0)

            #查看用户数据按钮点击事件
            self.ui.pushButton_reg_user.clicked.connect(self.register_user)
            self.ui.pushButton_stu_info.clicked.connect(self.student_info)
        else: return

    def register_user(self):
        self.ui.stackedWidget_3.setCurrentIndex(1)
        
        # 切换到正确页面后再清空和设置消息
        self.ui.label_log_user_info.setText("")

        # 存储用户数据，包括ID
        self.user_data = []
        
        conn = sqlite3.connect(database='MyData.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        rows = cursor.fetchall()
        
        for item in rows:
            self.user_data.append({
                'id': item[0],
                'username': item[1],
                'password': item[2],
                'nation': item[3],
                'telephone': item[4]
            })
        conn.close()

        # --- 关键修改：先阻塞信号再填充数据 ---
        self.ui.tableWidget_reg_users.blockSignals(True)

        self.ui.tableWidget_reg_users.setRowCount(len(self.user_data))
        self.ui.tableWidget_reg_users.setColumnCount(4) # 设置列数为4
        self.ui.tableWidget_reg_users.setHorizontalHeaderLabels(['用户名', '密码', '国家区号','电话'])
        
        
        for i, user in enumerate(self.user_data):
            self.ui.tableWidget_reg_users.setItem(i, 0, QTableWidgetItem(user['username']))
            self.ui.tableWidget_reg_users.setItem(i, 1, QTableWidgetItem(user['password']))
            self.ui.tableWidget_reg_users.setItem(i, 2, QTableWidgetItem(str(user['nation'])))
            self.ui.tableWidget_reg_users.setItem(i, 3, QTableWidgetItem(user['telephone']))


        self.ui.tableWidget_reg_users.blockSignals(False) 
        # --- 信号恢复 ---

        self.ui.tableWidget_reg_users.setEditTriggers(QAbstractItemView.DoubleClicked)

        # 确保信号只连接一次（安全做法）
        try:
            self.ui.tableWidget_reg_users.itemChanged.disconnect()
        except:
            pass

        self.ui.tableWidget_reg_users.itemChanged.connect(self.save_changes)
        self.ui.pushButton_add.clicked.connect(self.add_user)
        self.ui.pushButton_delete.clicked.connect(self.delete_user)


    def save_changes(self, item):
        row = item.row()
        column = item.column()
        new_value = item.text()
        
        # 检查是否有存储的用户数据
        if not hasattr(self, 'user_data') or row >= len(self.user_data):
            return
        
        # 获取用户ID
        user_username = self.user_data[row]['username']
        print(user_username)
        
        conn = sqlite3.connect(database='MyData.db')
        cursor = conn.cursor()
        
        # 根据列索引更新对应字段（列索引从0开始）
        if column == 1:  # 密码列
            cursor.execute("UPDATE users SET password = ? WHERE username = ?", (new_value, user_username))
            self.user_data[row]['password'] = new_value
        elif column == 2:  # 国家区号列
            try:
                cursor.execute("UPDATE users SET nation = ? WHERE username = ?", (int(new_value), user_username))
                self.user_data[row]['nation'] = int(new_value)
            except ValueError:
                self.ui.label_log_user_info.setText("国家区号必须是数字!")
                conn.close()
                return
        elif column == 3:  # 电话列
            cursor.execute("UPDATE users SET telephone = ? WHERE username = ?", (new_value, user_username))
            self.user_data[row]['telephone'] = new_value
        
        conn.commit()
        conn.close()
        self.ui.label_log_user_info.setText(f"用户 {user_username} 的数据已更新!")

    def add_user(self):
        username = self.ui.lineEdit_username.text()
        password = self.ui.lineEdit_password.text()
        nation = self.ui.lineEdit_nation.text()
        telephone = self.ui.lineEdit_telephone.text()
        
        if not username or not password or not nation or not telephone:
            self.ui.label_log_user_info.setText("请填写完整信息!")
            return
        elif username in [user['username'] for user in self.user_data]:
            self.ui.label_log_user_info.setText("用户名已存在!")
            return
        else:
            conn = sqlite3.connect(database='MyData.db')
            cursor = conn.cursor()
            # 获取当前最大ID并加1作为新ID
            cursor.execute("SELECT MAX(id) FROM users")
            result = cursor.fetchone()
            new_id = result[0] + 1 if result[0] else 1
            
            cursor.execute("INSERT INTO users (id, username, password, nation, telephone) VALUES (?, ?, ?, ?, ?)", (new_id, username, password, int(nation), telephone))
            conn.commit()
            conn.close()
            self.ui.label_log_user_info.setText(f"用户 {username} 已成功添加!")
            self.register_user() #刷新数据

            #清空文本框
            self.ui.lineEdit_username.setText('')
            self.ui.lineEdit_password.setText('')
            self.ui.lineEdit_nation.setText('')
            self.ui.lineEdit_telephone.setText('')

    def delete_user(self):
        # 获取当前选中的行
        current_row = self.ui.tableWidget_reg_users.currentRow()
        if current_row < 0:
            self.ui.label_log_user_info.setText("请先选择要删除的用户!")
            return
        else:
            # 获取用户名
            username = self.ui.tableWidget_reg_users.item(current_row, 0).text()
            
            # 删除用户
            conn = sqlite3.connect(database='MyData.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = ?", (username,))
            conn.commit()
            conn.close()
            
            self.ui.label_log_user_info.setText(f"用户 {username} 已成功删除!")
            self.register_user() #刷新数据


    def student_info(self):
        self.ui.stackedWidget_3.setCurrentIndex(2)

        # 存储用户数据，包括ID
        self.stu_data = []
        
        conn = sqlite3.connect(database='MyData.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Students')
        rows = cursor.fetchall()
        
        for item in rows:
            self.stu_data.append({
                'id': item[0],
                'name': item[1],
                'age': item[2],
                'gender': item[3],
                'city': item[4],
                'email': item[5],
                'education': item[6],
                'birthday': item[7],
                'phone': item[8]
            })
        conn.close()

        # 初始化排序状态
        self.sort_states = [None] * 8  # 存储每列的排序状态：None(未排序), 'asc'(升序), 'desc'(降序)
        
        # --- 关键修改：先阻塞信号再填充数据 ---
        self.ui.tableWidget_stu_info.blockSignals(True)

        self.ui.tableWidget_stu_info.setRowCount(len(self.stu_data))
        self.ui.tableWidget_stu_info.setColumnCount(8) # 设置列数为8
        
        # 设置带排序按钮的表头
        header = self.ui.tableWidget_stu_info.horizontalHeader()
        header.setSectionsClickable(True)
        header.sectionClicked.connect(self.sort_table)
        
        # 设置表头标签
        self.ui.tableWidget_stu_info.setHorizontalHeaderLabels(['姓名▲▼', '年龄▲▼', '性别▲▼', '城市▲▼', '邮箱▲▼', '学历▲▼', '出生日期▲▼', '电话▲▼'])
        
        # 填充表格数据
        self.refresh_student_table()

        self.ui.tableWidget_stu_info.blockSignals(False)
        
        # 连接搜索功能
        self.ui.pushButton_search.clicked.connect(self.search_student_data)

    def refresh_student_table(self):
        """刷新学生表格数据"""
        from PyQt5.QtGui import QColor
        
        self.ui.tableWidget_stu_info.setRowCount(len(self.stu_data))
        
        # 先填充数据
        for i, user in enumerate(self.stu_data):
            for j in range(8):  # 8个列
                item_text = ''
                if j == 0:
                    item_text = user['name']
                elif j == 1:
                    item_text = str(user['age'])
                elif j == 2:
                    item_text = user['gender']
                elif j == 3:
                    item_text = user['city']
                elif j == 4:
                    item_text = user['email']
                elif j == 5:
                    item_text = user['education']
                elif j == 6:
                    item_text = user['birthday']
                elif j == 7:
                    item_text = user['phone']
                
                item = QTableWidgetItem(item_text)
                self.ui.tableWidget_stu_info.setItem(i, j, item)
        
        # 再设置样式
        for i in range(self.ui.tableWidget_stu_info.rowCount()):
            # 设置行背景色：白灰相间（基于显示行索引）
            row_color = QColor(255, 255, 255) if i % 2 == 0 else QColor(240, 240, 240)  # 白色和浅灰色
            
            for j in range(self.ui.tableWidget_stu_info.columnCount()):
                item = self.ui.tableWidget_stu_info.item(i, j)
                if item:
                    # 设置列字色：紫色浅蓝相间
                    if j % 2 == 0:
                        item.setForeground(QColor(130, 0, 200))  # 紫色
                    else:
                        item.setForeground(QColor(0, 150, 220))  # 浅蓝色
                    
                    # 设置行背景色
                    item.setBackground(row_color)

    def sort_table(self, column):
        """根据列索引排序表格数据"""
        if not hasattr(self, 'stu_data') or not self.stu_data:
            return
        
        # 获取当前列的排序状态
        current_state = self.sort_states[column]
        
        # 切换排序状态：None -> asc -> desc -> None
        if current_state is None:
            new_state = 'asc'
        elif current_state == 'asc':
            new_state = 'desc'
        else:
            new_state = None
        
        # 更新排序状态
        self.sort_states = [None] * 8  # 重置所有列状态
        self.sort_states[column] = new_state
        
        # 根据排序状态排序数据
        if new_state == 'asc':
            # 升序排序
            if column == 0:  # 姓名
                self.stu_data.sort(key=lambda x: x['name'])
            elif column == 1:  # 年龄
                self.stu_data.sort(key=lambda x: int(x['age']))
            elif column == 2:  # 性别
                self.stu_data.sort(key=lambda x: x['gender'])
            elif column == 3:  # 城市
                self.stu_data.sort(key=lambda x: x['city'])
            elif column == 4:  # 邮箱
                self.stu_data.sort(key=lambda x: x['email'])
            elif column == 5:  # 学历
                self.stu_data.sort(key=lambda x: x['education'])
            elif column == 6:  # 出生日期
                self.stu_data.sort(key=lambda x: x['birthday'])
            elif column == 7:  # 电话
                self.stu_data.sort(key=lambda x: x['phone'])
        elif new_state == 'desc':
            # 降序排序
            if column == 0:  # 姓名
                self.stu_data.sort(key=lambda x: x['name'], reverse=True)
            elif column == 1:  # 年龄
                self.stu_data.sort(key=lambda x: int(x['age']), reverse=True)
            elif column == 2:  # 性别
                self.stu_data.sort(key=lambda x: x['gender'], reverse=True)
            elif column == 3:  # 城市
                self.stu_data.sort(key=lambda x: x['city'], reverse=True)
            elif column == 4:  # 邮箱
                self.stu_data.sort(key=lambda x: x['email'], reverse=True)
            elif column == 5:  # 学历
                self.stu_data.sort(key=lambda x: x['education'], reverse=True)
            elif column == 6:  # 出生日期
                self.stu_data.sort(key=lambda x: x['birthday'], reverse=True)
            elif column == 7:  # 电话
                self.stu_data.sort(key=lambda x: x['phone'], reverse=True)
        else:
            # 恢复原始顺序（按ID排序）
            self.stu_data.sort(key=lambda x: x['id'])
        
        # 更新表头显示
        self.update_header_labels(column, new_state)
        
        # 刷新表格显示
        self.refresh_student_table()

    def update_header_labels(self, sorted_column, state):
        """更新表头标签，显示排序状态"""
        labels = ['姓名', '年龄', '性别', '城市', '邮箱', '学历', '出生日期', '电话']
        
        for i in range(len(labels)):
            if i == sorted_column:
                if state == 'asc':
                    labels[i] += ' ▲'
                elif state == 'desc':
                    labels[i] += ' ▼'
                else:
                    labels[i] += ' ▲▼'
            else:
                labels[i] += ' ▲▼'
        
        self.ui.tableWidget_stu_info.setHorizontalHeaderLabels(labels)    

    def search_student_data(self):
        """搜索学生数据并高亮显示匹配的行"""
        # 获取搜索内容和搜索列
        search_text = self.ui.lineEdit_search.text().strip()
        selected_column = self.ui.comboBox_search.currentText()
        
        if not search_text:
            # 如果搜索内容为空，恢复所有行的正常显示
            self.clear_search_highlight()
            return
        
        # 存储匹配的行索引
        matched_rows = set()
        
        # 根据下拉框选择决定搜索范围
        if selected_column == "*":
            # 在所有列中搜索
            for row in range(self.ui.tableWidget_stu_info.rowCount()):
                for column in range(self.ui.tableWidget_stu_info.columnCount()):
                    item = self.ui.tableWidget_stu_info.item(row, column)
                    if item and search_text.lower() in item.text().lower():
                        matched_rows.add(row)
        else:
            # 在指定列中搜索
            # 映射列名到列索引
            column_map = {
                "姓名": 0,
                "年龄": 1,
                "性别": 2,
                "城市": 3,
                "邮箱": 4,
                "学历": 5,
                "出生日期": 6,
                "电话": 7
            }
            
            if selected_column in column_map:
                column_index = column_map[selected_column]
                for row in range(self.ui.tableWidget_stu_info.rowCount()):
                    item = self.ui.tableWidget_stu_info.item(row, column_index)
                    if item and search_text.lower() in item.text().lower():
                        matched_rows.add(row)
        
        # 高亮显示匹配的行
        self.highlight_matched_rows(matched_rows)
    
    def clear_search_highlight(self):
        """清除搜索高亮，恢复原始样式"""
        for row in range(self.ui.tableWidget_stu_info.rowCount()):
            # 恢复行背景色：白灰相间
            row_color = QColor(255, 255, 255) if row % 2 == 0 else QColor(240, 240, 240)
            
            for column in range(self.ui.tableWidget_stu_info.columnCount()):
                item = self.ui.tableWidget_stu_info.item(row, column)
                if item:
                    # 恢复行背景色
                    item.setBackground(row_color)
                    
                    # 恢复列字色：紫色浅蓝相间
                    if column % 2 == 0:
                        item.setForeground(QColor(130, 0, 200))  # 紫色
                    else:
                        item.setForeground(QColor(0, 150, 220))  # 浅蓝色
    
    def highlight_matched_rows(self, matched_rows):
        """高亮显示匹配的行"""
        
        # 先清除所有高亮
        self.clear_search_highlight()
        
        # 高亮匹配的行
        highlight_color = QColor(255, 255, 0)  # 黄色高亮
        
        for row in matched_rows:
            for column in range(self.ui.tableWidget_stu_info.columnCount()):
                item = self.ui.tableWidget_stu_info.item(row, column)
                if item:
                    item.setBackground(highlight_color)
    
    def myinfo(self):
        self.ui.stackedWidget.setCurrentIndex(3)
        #重设密码按钮点击事件
        self.ui.pushButton_change_sure.clicked.connect(self.reset_password)

    def reset_password(self):
        old_password = self.ui.lineEdit_oldpassword.text()
        new_password = self.ui.lineEdit_newpassword1.text()
        confirm_password = self.ui.lineEdit_newpassword2.text()
        
        conn = sqlite3.connect(database='MyData.db')
        cursor = conn.cursor()

        self.ui.stackedWidget_2.setCurrentIndex(3) #empty
        if old_password != LoginWindow.current_password:
            self.ui.stackedWidget_2.setCurrentIndex(0) #旧密码错误！
            return
        elif new_password != confirm_password or new_password == '' or confirm_password == '':
            self.ui.stackedWidget_2.setCurrentIndex(1) #新密码不一致或错误！
            return
        elif old_password == new_password:
            time.sleep(0.5)
            self.ui.stackedWidget_2.setCurrentIndex(2) #新密码不能与旧密码相同！
            return
        else:
            # 使用参数化查询防止SQL注入
            cursor.execute("UPDATE users SET password = ? WHERE username = ?", 
                         (new_password, LoginWindow.current_username))
            # 更新类属性中的密码
            LoginWindow.current_password = new_password
            self.ui.stackedWidget_2.setCurrentIndex(4) #密码重置成功，请重新登录！
            self.logout()

        conn.commit()
        conn.close()


    def logout(self):
        self.win = LoginWindow()
        self.win.show()
        self.close()
    
    # 使得窗口可以拖动-1
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPos()

    # 使得窗口可以拖动-2
    def mouseMoveEvent(self, event):
        if self.oldPos:
            delta = event.globalPos() - self.oldPos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()
    # 使得窗口可以拖动-3
    def mouseReleaseEvent(self, event):
        self.oldPos = None

    


if __name__ == "__main__":
    my_app_id = 'my_company.my_student_system.1.0' # 这里的字符串可以自定义
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)

    app = QApplication(sys.argv)
    win = LoginWindow()
    win.show()
    sys.exit(app.exec_())