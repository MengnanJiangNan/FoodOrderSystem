---
title: Order System
emoji: 🍽️
colorFrom: blue
colorTo: green
sdk: docker
sdk_version: "latest"
app_file: app.py
pinned: false
---

# 点餐系统

这是一个简单的点餐系统，使用 Flask 作为后端，提供以下功能：

- 显示菜单
- 添加订单
- 查看订单历史
- 修改订单

## API 接口

- `/api/menu` - 获取菜单
- `/api/users` - 获取用户列表
- `/api/orders` - 获取/添加订单
- `/api/user-orders/<user_id>` - 获取指定用户的订单
- `/api/all-orders` - 获取所有订单
- `/api/edit-orders` - 修改订单

## 部署说明

应用使用 Flask 作为 Web 框架，使用 pandas 处理数据，数据存储在 Excel 文件中。

环境要求：
- Python 3.9+
- Flask 3.0+
- pandas 2.0+
- gunicorn 20.1+

## 使用方法

访问应用首页即可开始使用点餐系统。系统会自动初始化必要的数据文件。

## 技术栈

- Python 3.9+
- Gradio 4.0+
- Pandas 2.0+
- OpenPyXL 3.0+

本项目已部署在Gradio Space上，可以直接访问使用。

如需本地运行：

1. 克隆仓库
2. 安装依赖：`pip install -r requirements.txt`
3. 运行应用：`python app.py`