
# 🚀 Windows 快速启动指南

## ❌ 您遇到的问题

从您的错误信息来看，有两个问题：

### 问题1：乱码
原因：Windows命令提示符编码问题。

### 问题2：目录结构不对
看起来解压后的目录可能多了一层 `project_package` 文件夹。

---

## ✅ 第一步：确认目录结构

### 正确的目录结构应该是：
```
F:\ai\zhipin_future_project\
├── 03_项目代码\
├── 04_数据文件\
├── requirements.txt
└── start_simple.bat (新的启动脚本)
```

**如果您看到的是：**
```
F:\ai\zhipin_future_project\project_package\...
```

**请把 `project_package` 里面的所有文件移出来，放到 `F:\ai\zhipin_future_project\` 下面。**

---

## ✅ 第二步：手动启动（推荐，更简单）

### 方法1：手动启动（推荐）

打开 **命令提示符**（按 Win+R，输入 `cmd`，回车），然后依次运行：

```cmd
# 1. 进入项目目录
cd /d F:\ai\zhipin_future_project

# 2. 安装依赖
pip install -r requirements.txt

# 3. 初始化测试数据
cd 03_项目代码
py add_test_data.py
cd ..

# 4. 启动应用
streamlit run 03_项目代码/pages/main/chat_main.py
```

然后浏览器会自动打开 http://localhost:8501

---

### 方法2：使用新的启动脚本

1. 下载我新创建的 `start_simple.bat` 放到您的项目根目录
2. 双击运行

---

## 📋 检查是否安装正确

在命令提示符运行：

```cmd
py --version
```

您应该看到：
```
Python 3.13.6
```

---

## 🌐 启动后访问

| 页面 | 地址 |
|-------|------|
| 主应用 | http://localhost:8501 |
| HR后台 | http://localhost:8503 |

---

## ❓ 如果还有问题

### 问题：提示找不到模块
运行：
```cmd
pip install streamlit pandas pymysql requests openpyxl PyPDF2 python-dotenv
```

### 问题：端口被占用
关闭其他正在运行的程序，或者换端口：
```cmd
streamlit run 03_项目代码/pages/main/chat_main.py --server.port 8502
```

---

## 📞 需要帮助？

1. 确认目录结构正确
2. 确认Python 3.8+ 已安装
3. 手动一步步运行命令看是哪一步出错
4. 把错误信息发给我

