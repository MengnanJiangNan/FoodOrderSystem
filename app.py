from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
from pathlib import Path
from datetime import datetime

app = Flask(__name__)

# 定义常量
USERS_EXCEL_FILE = Path('food_orders.xlsx')
MENU_EXCEL_FILE = Path('menu_data.xlsx')

def init_excel_files():
    """初始化Excel文件"""
    try:
        # 初始化菜单文件
        if not MENU_EXCEL_FILE.exists():
            menu_df = pd.DataFrame({
                'id': [1, 2],
                'name': ['汉堡', '薯条'],
                'price': [25.0, 12.0],
                'image': ['/static/burger.jpg', '/static/fries.jpg'],
                'description': ['美味牛肉汉堡，搭配新鲜蔬菜', '香脆金黄薯条，外酥里嫩']
            })
            menu_df.to_excel(MENU_EXCEL_FILE, index=False)
            print("✅ 菜单文件创建成功")
        
        # 初始化订单文件
        if not USERS_EXCEL_FILE.exists():
            orders_df = pd.DataFrame(columns=[
                'user_id', 'user_name', 'food_id', 'food_name', 
                'quantity', 'price', 'subtotal'
            ])
            users_df = pd.DataFrame(columns=['id', 'name'])
            
            with pd.ExcelWriter(USERS_EXCEL_FILE) as writer:
                orders_df.to_excel(writer, sheet_name='orders', index=False)
                users_df.to_excel(writer, sheet_name='users', index=False)
            print("✅ 订单文件创建成功")
    except Exception as e:
        print(f"❌ 初始化文件失败: {str(e)}")

def get_menu():
    """获取菜单数据"""
    try:
        if not MENU_EXCEL_FILE.exists():
            init_excel_files()
        df = pd.read_excel(MENU_EXCEL_FILE)
        return df.to_dict('records')
    except Exception as e:
        print(f"❌ 读取菜单数据失败: {str(e)}")
        return []

def get_orders():
    """获取订单数据"""
    try:
        if not USERS_EXCEL_FILE.exists():
            init_excel_files()
        df = pd.read_excel(USERS_EXCEL_FILE, sheet_name='orders')
        return df.to_dict('records')
    except Exception as e:
        print(f"❌ 读取订单数据失败: {str(e)}")
        return []

def get_users():
    """获取用户数据"""
    try:
        if not USERS_EXCEL_FILE.exists():
            init_excel_files()
        df = pd.read_excel(USERS_EXCEL_FILE, sheet_name='users')
        return df.to_dict('records')
    except Exception as e:
        print(f"❌ 读取用户数据失败: {str(e)}")
        return []

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/menu')
def menu():
    """获取菜单API"""
    return jsonify(get_menu())

@app.route('/api/menu-from-file')
def menu_from_file():
    """直接从文件获取菜单数据"""
    return jsonify(get_menu())

@app.route('/api/users')
def users():
    """获取用户列表API"""
    return jsonify({"users": get_users()})

@app.route('/api/orders')
def orders():
    """获取订单API"""
    return jsonify(get_orders())

@app.route('/api/user-orders/<int:user_id>')
def user_orders(user_id):
    """获取指定用户的订单"""
    try:
        orders_df = pd.read_excel(USERS_EXCEL_FILE, sheet_name='orders')
        user_orders = orders_df[orders_df['user_id'] == user_id]
        orders_list = user_orders.to_dict('records')
        total = sum(order['price'] * order['quantity'] for order in orders_list)
        return jsonify({
            'orders': orders_list,
            'total': total
        })
    except Exception as e:
        return jsonify({
            'error': f"获取用户订单失败: {str(e)}"
        }), 400

@app.route('/api/all-orders')
def all_orders():
    """获取所有订单，按用户分组"""
    try:
        orders_df = pd.read_excel(USERS_EXCEL_FILE, sheet_name='orders')
        users_df = pd.read_excel(USERS_EXCEL_FILE, sheet_name='users')
        
        # 按用户分组订单
        result = []
        for user_id in orders_df['user_id'].unique():
            user_orders = orders_df[orders_df['user_id'] == user_id]
            user_name = f"用户{user_id}"
            
            # 尝试从users表获取用户名
            user = users_df[users_df['id'] == user_id]
            if not user.empty:
                user_name = user.iloc[0]['name']
            
            orders_list = user_orders.to_dict('records')
            total = sum(order['price'] * order['quantity'] for order in orders_list)
            
            result.append({
                'user_id': int(user_id),
                'user_name': user_name,
                'items': orders_list,
                'total': total
            })
        
        return jsonify({"users": result})
    except Exception as e:
        return jsonify({
            'error': f"获取所有订单失败: {str(e)}"
        }), 400

@app.route('/api/orders', methods=['POST'])
def add_order():
    """添加订单API"""
    try:
        data = request.json
        user_id = int(data['user_id'])
        items = data['items']

        # 读取现有订单
        orders_df = pd.read_excel(USERS_EXCEL_FILE, sheet_name='orders')
        
        # 处理每个订单项
        for item in items:
            new_order = {
                'user_id': user_id,
                'user_name': f"用户{user_id}",
                'food_id': item['food_id'],
                'food_name': item['food_name'],
                'quantity': item['quantity'],
                'price': float(item['price']),
                'subtotal': float(item['price']) * item['quantity']
            }
            orders_df = pd.concat([orders_df, pd.DataFrame([new_order])], ignore_index=True)
        
        # 保存更新后的订单
        with pd.ExcelWriter(USERS_EXCEL_FILE, mode='a', if_sheet_exists='replace') as writer:
            orders_df.to_excel(writer, sheet_name='orders', index=False)
        
        return jsonify({
            'status': 'success',
            'message': f"✅ 订单添加成功"
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f"❌ 添加订单失败: {str(e)}"
        }), 400

@app.route('/api/edit-orders', methods=['POST'])
def edit_orders():
    """修改订单API"""
    try:
        data = request.json
        user_id = int(data['user_id'])
        items = data['items']

        # 读取现有订单
        orders_df = pd.read_excel(USERS_EXCEL_FILE, sheet_name='orders')
        
        # 删除该用户的所有订单
        orders_df = orders_df[orders_df['user_id'] != user_id]
        
        # 添加新的订单项
        for item in items:
            if item['quantity'] > 0:  # 只添加数量大于0的订单
                new_order = {
                    'user_id': user_id,
                    'user_name': f"用户{user_id}",
                    'food_id': item['food_id'],
                    'food_name': item['food_name'],
                    'quantity': item['quantity'],
                    'price': float(item['price']),
                    'subtotal': float(item['price']) * item['quantity']
                }
                orders_df = pd.concat([orders_df, pd.DataFrame([new_order])], ignore_index=True)
        
        # 保存更新后的订单
        with pd.ExcelWriter(USERS_EXCEL_FILE, mode='a', if_sheet_exists='replace') as writer:
            orders_df.to_excel(writer, sheet_name='orders', index=False)
        
        return jsonify({
            'status': 'success',
            'message': f"✅ 订单修改成功"
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f"❌ 修改订单失败: {str(e)}"
        }), 400

@app.route('/api/add-user', methods=['POST'])
def add_user():
    """添加新用户API"""
    try:
        data = request.json
        new_user_name = data['name']

        # 读取现有用户
        users_df = pd.read_excel(USERS_EXCEL_FILE, sheet_name='users')
        
        # 生成新用户ID (确保转换为Python原生整数)
        new_user_id = 1 if users_df.empty else int(users_df['id'].max() + 1)
        
        # 添加新用户
        new_user = {
            'id': new_user_id,
            'name': new_user_name
        }
        users_df = pd.concat([users_df, pd.DataFrame([new_user])], ignore_index=True)
        
        # 保存更新后的用户列表
        with pd.ExcelWriter(USERS_EXCEL_FILE, mode='a', if_sheet_exists='replace') as writer:
            users_df.to_excel(writer, sheet_name='users', index=False)
            # 保持orders sheet不变
            orders_df = pd.read_excel(USERS_EXCEL_FILE, sheet_name='orders')
            orders_df.to_excel(writer, sheet_name='orders', index=False)
        
        return jsonify({
            'status': 'success',
            'message': 'Benutzer erfolgreich hinzugefügt',
            'user': {
                'id': int(new_user_id),  # 确保ID是Python原生整数
                'name': new_user_name
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f"Fehler beim Hinzufügen des Benutzers: {str(e)}"
        }), 400

# 初始化数据
init_excel_files()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)