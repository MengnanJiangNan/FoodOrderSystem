import gradio as gr
import pandas as pd
import os
from pathlib import Path
from datetime import datetime

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
        return df
    except Exception as e:
        print(f"❌ 读取菜单数据失败: {str(e)}")
        return pd.DataFrame()

def get_orders():
    """获取订单数据"""
    try:
        if not USERS_EXCEL_FILE.exists():
            init_excel_files()
        df = pd.read_excel(USERS_EXCEL_FILE, sheet_name='orders')
        return df
    except Exception as e:
        print(f"❌ 读取订单数据失败: {str(e)}")
        return pd.DataFrame()

def add_order(user_id: int, food_id: int, quantity: int):
    """添加新订单"""
    try:
        # 获取菜单数据
        menu_df = get_menu()
        food = menu_df[menu_df['id'] == food_id].iloc[0]
        
        # 准备新订单数据
        new_order = {
            'user_id': user_id,
            'user_name': f"用户{user_id}",
            'food_id': food_id,
            'food_name': food['name'],
            'quantity': quantity,
            'price': food['price'],
            'subtotal': food['price'] * quantity
        }
        
        # 读取现有订单
        orders_df = get_orders()
        
        # 添加新订单
        orders_df = pd.concat([orders_df, pd.DataFrame([new_order])], ignore_index=True)
        
        # 保存更新后的订单
        with pd.ExcelWriter(USERS_EXCEL_FILE, mode='a', if_sheet_exists='replace') as writer:
            orders_df.to_excel(writer, sheet_name='orders', index=False)
        
        return f"✅ 订单添加成功：{food['name']} x {quantity}"
    except Exception as e:
        return f"❌ 添加订单失败: {str(e)}"

def create_interface():
    """创建Gradio界面"""
    with gr.Blocks() as demo:
        gr.Markdown("# 点餐系统")
        
        with gr.Tab("菜单"):
            gr.Markdown("## 今日菜单")
            menu_df = get_menu()
            menu_display = gr.DataFrame(
                value=menu_df,
                headers=['ID', '名称', '价格', '图片', '描述'],
                datatype=['number', 'str', 'number', 'str', 'str'],
                row_count=(5, 'dynamic'),
                col_count=(5, 'fixed'),
                interactive=False
            )
            
            with gr.Row():
                user_id = gr.Number(label="用户ID", precision=0)
                food_id = gr.Number(label="食品ID", precision=0)
                quantity = gr.Number(label="数量", precision=0, value=1)
            
            order_btn = gr.Button("提交订单")
            result = gr.Textbox(label="订单结果")
            
            order_btn.click(
                fn=add_order,
                inputs=[user_id, food_id, quantity],
                outputs=result
            )
        
        with gr.Tab("订单"):
            gr.Markdown("## 订单管理")
            orders_df = get_orders()
            orders_display = gr.DataFrame(
                value=orders_df,
                headers=['用户ID', '用户名', '食品ID', '食品名', '数量', '单价', '小计'],
                datatype=['number', 'str', 'number', 'str', 'number', 'number', 'number'],
                row_count=(10, 'dynamic'),
                col_count=(7, 'fixed'),
                interactive=False
            )
            
            refresh_btn = gr.Button("刷新订单")
            refresh_btn.click(
                fn=get_orders,
                inputs=[],
                outputs=orders_display
            )
    
    return demo

# 初始化数据
init_excel_files()

# 创建并启动接口
demo = create_interface()

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)