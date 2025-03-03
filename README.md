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

这是一个简单的点餐系统，使用Gradio构建的Web界面。

## 功能特点

- 查看菜单
- 提交订单
- 查看订单历史
- 实时更新订单状态

## 使用方法

1. 在"菜单"标签页查看可用的菜品
2. 输入用户ID、食品ID和数量来提交订单
3. 在"订单"标签页查看所有订单历史

## 技术栈

- Python 3.9+
- Gradio 4.0+
- Pandas 2.0+
- OpenPyXL 3.0+

## 部署说明

本项目已部署在Gradio Space上，可以直接访问使用。

如需本地运行：

1. 克隆仓库
2. 安装依赖：`pip install -r requirements.txt`
3. 运行应用：`python app.py`