from flask import Flask, render_template, request, jsonify
import pandas as pd
from pathlib import Path
import os
from datetime import datetime

app = Flask(__name__)
USERS_EXCEL_FILE = Path('food_orders.xlsx')
MENU_EXCEL_FILE = Path('menu_data.xlsx')

def init_excel():
    try:
        # 检查文件是否已存在
        if os.path.exists('food_orders.xlsx'):
            app.logger.info("food_orders.xlsx existiert bereits, Initialisierung wird übersprungen")
            return

        # 创建订单表（空表）
        orders_df = pd.DataFrame(columns=[
            'user_id', 'user_name', 'food_id', 'food_name', 'quantity', 'price', 'subtotal'
        ])
        
        # 创建用户表（空表）
        users_df = pd.DataFrame(columns=['id', 'name'])
        
        # 保存到Excel文件
        with pd.ExcelWriter('food_orders.xlsx') as writer:
            orders_df.to_excel(writer, sheet_name='orders', index=False)
            users_df.to_excel(writer, sheet_name='users', index=False)
            
        app.logger.info("Excel-Datei erfolgreich initialisiert")
    except Exception as e:
        app.logger.error(f"Excel-Initialisierung fehlgeschlagen: {str(e)}")

def init_users_excel():
    try:
        if not USERS_EXCEL_FILE.exists():
            print("⏳ Excel-Benutzerdatei wird erstellt...")
            USERS_EXCEL_FILE.parent.mkdir(parents=True, exist_ok=True)
            
            with pd.ExcelWriter(USERS_EXCEL_FILE, engine='openpyxl') as writer:
                # 创建空的用户表结构
                pd.DataFrame(columns=['id', 'name']).to_excel(
                    writer, 
                    sheet_name='users', 
                    index=False
                )
                print("✅ Benutzerstruktur erstellt")
                
                # 初始化订单表
                orders_df = pd.DataFrame(columns=['user_id', 'user_name', 'food_id', 'quantity', 'order_time'])
                orders_df.to_excel(writer, sheet_name='orders', index=False)
                print("✅ Bestelltabelle erfolgreich initialisiert")
                
            print(f"🎉 Benutzerdatendatei wurde erstellt: {USERS_EXCEL_FILE}")
            return True
        else:
            print(f"ℹ️ Benutzerdatendatei existiert bereits: {USERS_EXCEL_FILE}")
            return False
    except Exception as e:
        print(f"❌ Fehler bei der Initialisierung der Benutzerdatendatei: {str(e)}")
        if USERS_EXCEL_FILE.exists():
            USERS_EXCEL_FILE.unlink()
        return False

def init_menu_excel():
    try:
        if not MENU_EXCEL_FILE.exists():
            print("⏳ Menü-Excel-Datei wird erstellt...")
            MENU_EXCEL_FILE.parent.mkdir(parents=True, exist_ok=True)
            
            # 创建示例菜单数据（仅作为模板）
            sample_menu = [
                # {'id': 1, 'name': '汉堡', 'price': 25.0, 'image': '/static/burger.jpg', 'description': '美味牛肉汉堡，搭配新鲜蔬菜'},
                # {'id': 2, 'name': '薯条', 'price': 12.0, 'image': '/static/fries.jpg', 'description': '香脆金黄薯条，外酥里嫩'}
            ]
            
            menu_df = pd.DataFrame(sample_menu)
            menu_df.to_excel(MENU_EXCEL_FILE, index=False)
            print(f"✅ Erfolgreich Menüdatendatei mit {len(sample_menu)} Beispielgerichten erstellt")
            
            print(f"🎉 Menüdatendatei wurde erstellt: {MENU_EXCEL_FILE}")
            print("⚠️ Bitte bearbeiten Sie die Menüdaten und starten Sie die Anwendung neu")
            return True
        else:
            print(f"ℹ️ Menüdatendatei existiert bereits: {MENU_EXCEL_FILE}")
            return False
    except Exception as e:
        print(f"❌ Fehler bei der Initialisierung der Menüdatendatei: {str(e)}")
        if MENU_EXCEL_FILE.exists():
            MENU_EXCEL_FILE.unlink()
        return False

def read_users_excel(sheet_name):
    try:
        if not USERS_EXCEL_FILE.exists():
            init_users_excel()
            
        df = pd.read_excel(USERS_EXCEL_FILE, sheet_name=sheet_name, engine='openpyxl')
        
        if df.empty:
            print(f"⚠️ {sheet_name}表为空")
            
        return df
    except Exception as e:
        print(f"❌ 读取{sheet_name}表失败: {str(e)}")
        return pd.DataFrame()

def read_menu_excel():
    try:
        if not MENU_EXCEL_FILE.exists():
            init_menu_excel()
            
        df = pd.read_excel(MENU_EXCEL_FILE, engine='openpyxl')
        
        # 检查必要字段
        required_columns = ['id', 'name', 'price', 'image']
        if not all(col in df.columns for col in required_columns):
            print("⚠️ 菜单数据不完整，缺少必要字段")
            return pd.DataFrame()
            
        # 添加缺失的description字段
        if 'description' not in df.columns:
            df['description'] = ''
            
        return df
    except Exception as e:
        print(f"❌ 读取菜单数据失败: {str(e)}")
        return pd.DataFrame()

def write_users_excel(sheet_name, df):
    try:
        with pd.ExcelWriter(USERS_EXCEL_FILE, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        return True
    except Exception as e:
        print(f"❌ 写入{sheet_name}表失败: {str(e)}")
        return False

@app.route('/')
def index():
    return render_template('index.html',
                         currentUser=None,
                         user={"name": "", "id": 0})

@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        app.logger.info("获取所有用户信息")
        
        # 尝试从Excel文件读取用户数据
        if os.path.exists('food_orders.xlsx'):
            try:
                users_df = pd.read_excel('food_orders.xlsx', sheet_name='users')
                app.logger.info(f"成功读取用户数据，共{len(users_df)}条记录")
                
                # 确保id列是整数
                users_df['id'] = pd.to_numeric(users_df['id'], errors='coerce').fillna(0).astype(int)
                
                # 转换为JSON格式
                users = []
                for _, row in users_df.iterrows():
                    if row['id'] > 0:  # 跳过无效用户ID
                        users.append({
                            'id': int(row['id']),
                            'name': str(row['name'])
                        })
                
                return jsonify({'users': users})
            except Exception as e:
                app.logger.error(f"读取Excel用户数据失败: {str(e)}")
                # 如果读取失败，返回空列表
                return jsonify({'users': []})
        else:
            app.logger.warning("Excel文件不存在")
            return jsonify({'users': []})
        
    except Exception as e:
        app.logger.error(f"获取用户列表失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/foods')
def get_foods():
    try:
        df = read_menu_excel()
        
        if df.empty:
            print("⚠️ 菜单数据为空")
            return jsonify([])
            
        # 类型转换
        df['id'] = pd.to_numeric(df['id'], errors='coerce').fillna(0).astype(int)
        
        print(f"✅ 成功加载菜单数据: {len(df)}条")
        return jsonify(df.to_dict('records'))
    except Exception as e:
        print(f"❌ 获取菜单数据失败: {str(e)}")
        return jsonify([])

@app.route('/api/menu-from-file')
def get_menu_from_file():
    """直接从Excel文件加载菜单数据，不进行任何数据转换，保持原始格式"""
    try:
        app.logger.info("Menüdaten direkt aus Excel-Datei laden")
        if not os.path.exists(MENU_EXCEL_FILE):
            app.logger.error("Menüdatei nicht gefunden")
            return jsonify({"error": "Menüdatei nicht gefunden"}), 404
            
        df = pd.read_excel(MENU_EXCEL_FILE, engine='openpyxl')
        
        # 检查必要字段
        required_columns = ['id', 'name', 'price', 'image']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            error_msg = f"Menüdaten unvollständig, fehlende Spalten: {', '.join(missing_columns)}"
            app.logger.warning(error_msg)
            return jsonify({"error": error_msg}), 500
            
        # 添加缺失的description字段
        if 'description' not in df.columns:
            app.logger.info("Spalte 'description' fehlt in menu_data.xlsx. Es wird eine leere Spalte hinzugefügt.")
            df['description'] = ''
            # 保存回Excel文件以更新结构
            df.to_excel(MENU_EXCEL_FILE, index=False)
        
        # 保持原始格式，不做类型转换
        menu_data = df.to_dict('records')
        app.logger.info(f"Erfolgreich {len(menu_data)} Menüeinträge aus Excel geladen")
        
        # 确保每个菜单项都有必要的字段（即使为空）
        for item in menu_data:
            item['id'] = item.get('id', 0)
            item['name'] = item.get('name', '')
            item['price'] = item.get('price', 0)
            item['image'] = item.get('image', '')
            item['description'] = item.get('description', '')
        
        return jsonify(menu_data)
    except Exception as e:
        import traceback
        app.logger.error(f"Fehler beim Laden der Menüdaten aus Excel: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/api/orders', methods=['POST'])
def save_order():
    try:
        app.logger.info("Neue Bestellungsanfrage erhalten")
        
        # 先尝试修复Excel文件结构
        fix_excel_structure()
        
        data = request.json
        user_id = data.get('user_id')
        items = data.get('items', [])
        
        app.logger.info(f"Bestellungsdetails: user_id={user_id}, items={items}")
        
        if not user_id or not items:
            app.logger.warning("Notwendige Parameter fehlen")
            return jsonify({"error": "Notwendige Parameter fehlen"}), 400
        
        # 确保用户ID是整数
        try:
            user_id = int(user_id)
        except ValueError:
            app.logger.error(f"Benutzer-ID ist keine gültige Ganzzahl: {user_id}")
            return jsonify({"error": "Ungültige Benutzer-ID"}), 400
        
        # 读取用户名
        user_name = get_user_name_by_id(user_id)
        app.logger.info(f"Benutzer gefunden: {user_name}")
        
        # 读取现有订单和工作表
        sheet_dict = {}
        try:
            if os.path.exists('food_orders.xlsx'):
                with pd.ExcelFile('food_orders.xlsx') as xls:
                    sheet_names = xls.sheet_names
                    for sheet in xls.sheet_names:
                        sheet_dict[sheet] = pd.read_excel(xls, sheet_name=sheet)
                    app.logger.info(f"成功读取Excel文件，工作表: {sheet_names}")
            else:
                app.logger.warning("Excel文件不存在，将创建新文件")
        except Exception as e:
            app.logger.error(f"读取Excel文件失败: {str(e)}")
            app.logger.info("将创建新的工作表")
        
        # 确保orders表存在
        if 'orders' not in sheet_dict:
            sheet_dict['orders'] = pd.DataFrame(
                columns=['user_id', 'user_name', 'food_id', 'food_name', 'quantity', 'price', 'subtotal']
            )
            app.logger.info("创建新的orders表")
        
        # 确保users表存在
        if 'users' not in sheet_dict:
            sheet_dict['users'] = pd.DataFrame(columns=['id', 'name'])
            app.logger.info("创建新的users表")
            
            # 确保用户存在于users表中
            users_df = sheet_dict['users']
            if not any(users_df['id'] == user_id):
                new_user = pd.DataFrame([{'id': user_id, 'name': user_name}])
                sheet_dict['users'] = pd.concat([users_df, new_user], ignore_index=True)
                app.logger.info(f"添加新用户到users表: id={user_id}, name={user_name}")
        
        orders_df = sheet_dict['orders']
        
        # 确保数据类型正确
        for col in ['user_id', 'food_id', 'quantity']:
            if col in orders_df.columns:
                orders_df[col] = pd.to_numeric(orders_df[col], errors='coerce').fillna(0).astype(int)
        
        for col in ['price', 'subtotal']:
            if col in orders_df.columns:
                orders_df[col] = pd.to_numeric(orders_df[col], errors='coerce').fillna(0).astype(float)
        
        # 过滤掉无效记录（food_id为0的记录）
        orders_df = orders_df[orders_df['food_id'] > 0]
        app.logger.info(f"过滤无效记录后订单表记录数: {len(orders_df)}")
        
        # 处理每个订单项
        total_price = 0
        has_updates = False
        
        app.logger.info(f"开始处理{len(items)}个订单项")
        for item in items:
            try:
                food_id = int(item.get('food_id'))
                quantity = int(item.get('quantity'))
                # 直接使用前端传来的food_name和price，不再重新查询菜单
                food_name = item.get('food_name', '未知菜品')
                price = clean_price(item.get('price', 0))
                
                app.logger.info(f"处理订单项: food_id={food_id}, food_name={food_name}, price={price}, quantity={quantity}")
                
                if not food_id or quantity <= 0:
                    app.logger.warning(f"跳过无效订单项: food_id={food_id}, quantity={quantity}")
                    continue
                
                subtotal = price * quantity
                total_price += subtotal
                
                # 检查是否已存在该用户的该食物订单
                existing_mask = (orders_df['user_id'] == user_id) & (orders_df['food_id'] == food_id)
                if any(existing_mask):
                    # 更新现有订单的数量和小计
                    existing_idx = orders_df[existing_mask].index[0]
                    old_quantity = orders_df.at[existing_idx, 'quantity']
                    new_quantity = old_quantity + quantity
                    new_subtotal = price * new_quantity
                    
                    orders_df.at[existing_idx, 'quantity'] = new_quantity
                    orders_df.at[existing_idx, 'subtotal'] = new_subtotal
                    # 确保food_name和price是最新的
                    orders_df.at[existing_idx, 'food_name'] = food_name
                    orders_df.at[existing_idx, 'price'] = price
                    
                    app.logger.info(f"更新现有订单: user_id={user_id}, food_id={food_id}, food_name={food_name}, 原数量={old_quantity}, 新增数量={quantity}, 更新后数量={new_quantity}")
                else:
                    # 添加新订单
                    new_order = {
                        'user_id': user_id,
                        'user_name': user_name,
                        'food_id': food_id,
                        'food_name': food_name,
                        'quantity': quantity,
                        'price': price,
                        'subtotal': subtotal
                    }
                    orders_df = pd.concat([orders_df, pd.DataFrame([new_order])], ignore_index=True)
                    app.logger.info(f"添加新订单: user_id={user_id}, food_id={food_id}, food_name={food_name}, quantity={quantity}")
                
                has_updates = True
            except (TypeError, ValueError) as e:
                app.logger.error(f"处理订单项时出错: {str(e)}")
                continue
        
        if has_updates:
            sheet_dict['orders'] = orders_df
            
            # 保存所有工作表
            try:
                with pd.ExcelWriter('food_orders.xlsx') as writer:
                    for sheet_name, df in sheet_dict.items():
                        app.logger.info(f"保存工作表 {sheet_name}, 记录数: {len(df)}")
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                app.logger.info("成功保存订单数据到Excel文件")
                
                # 确保Excel文件结构正确
                fix_excel_structure()
                
                return jsonify({"status": "success", "total_price": total_price})
            except Exception as e:
                import traceback
                app.logger.error(f"保存Excel文件失败: {str(e)}")
                app.logger.error(traceback.format_exc())
                return jsonify({"error": f"保存订单失败: {str(e)}"}), 500
        else:
            app.logger.warning("没有有效的订单项可保存")
            return jsonify({"error": "无有效订单项"}), 400
            
    except Exception as e:
        import traceback
        app.logger.error(f"保存订单失败: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/api/all-orders', methods=['GET'])
def get_all_orders():
    try:
        app.logger.info("获取所有订单信息")
        
        # 读取Excel文件中的订单数据
        try:
            users_df = pd.read_excel('food_orders.xlsx', sheet_name='users')
            orders_df = pd.read_excel('food_orders.xlsx', sheet_name='orders')
            app.logger.info(f"成功读取订单数据，列名：{orders_df.columns.tolist()}")
        except Exception as e:
            app.logger.error(f"读取Excel数据失败: {str(e)}")
            return jsonify({"error": "无法读取订单数据"}), 500
        
        # 如果没有订单，返回空列表
        if orders_df.empty:
            app.logger.info("没有订单数据")
            return jsonify({"users": []})
        
        # 检查并修复可能缺失的列
        required_columns = ['user_id', 'food_id', 'quantity', 'food_name', 'price', 'subtotal', 'user_name']
        for col in required_columns:
            if col not in orders_df.columns:
                app.logger.warning(f"订单数据中缺少列 '{col}'，添加默认值")
                if col in ['user_id', 'food_id', 'quantity']:
                    orders_df[col] = 0
                elif col in ['price', 'subtotal']:
                    orders_df[col] = 0.0
                elif col == 'user_name':
                    # 为每个user_id添加相应的user_name
                    orders_df['user_name'] = orders_df['user_id'].apply(get_user_name_by_id)
                    app.logger.info("添加了user_name列并填充用户名")
                else:
                    orders_df[col] = '未知'
        
        # 确保数值列是数值类型
        orders_df['user_id'] = pd.to_numeric(orders_df['user_id'], errors='coerce').fillna(0).astype(int)
        orders_df['food_id'] = pd.to_numeric(orders_df['food_id'], errors='coerce').fillna(0).astype(int)
        orders_df['quantity'] = pd.to_numeric(orders_df['quantity'], errors='coerce').fillna(0).astype(int)
        orders_df['price'] = pd.to_numeric(orders_df['price'], errors='coerce').fillna(0).astype(float)
        orders_df['subtotal'] = pd.to_numeric(orders_df['subtotal'], errors='coerce').fillna(0).astype(float)

        # 计算缺失的subtotal
        mask = (orders_df['subtotal'] == 0) & (orders_df['price'] > 0) & (orders_df['quantity'] > 0)
        orders_df.loc[mask, 'subtotal'] = orders_df.loc[mask, 'price'] * orders_df.loc[mask, 'quantity']
        
        # 按用户分组订单
        result = []
        for user_id, group in orders_df.groupby('user_id'):
            if user_id == 0:  # 跳过无效用户ID
                continue
            
            # 优先使用订单表中的user_name，如果为空再查询用户表
            user_name = None
            if 'user_name' in group.columns and not pd.isna(group['user_name'].iloc[0]):
                user_name = group['user_name'].iloc[0]
            
            # 如果订单表中没有user_name或为空，尝试从用户表获取
            if not user_name or user_name == f"用户{user_id}":
                user_row = users_df[users_df['id'] == user_id]
                if not user_row.empty:
                    user_name = user_row.iloc[0]['name']
                else:
                    user_name = f"用户{user_id}"
            
            app.logger.info(f"处理用户[{user_id}]的订单，用户名：{user_name}")
            
            orders_list = []
            for _, order in group.iterrows():
                # 读取菜品名称（如果缺失）
                food_name = order['food_name']
                if pd.isna(food_name) or food_name == '未知':
                    try:
                        menu_df = pd.read_excel('menu_data.xlsx')
                        food_row = menu_df[menu_df['id'] == order['food_id']]
                        if not food_row.empty:
                            food_name = food_row.iloc[0]['name']
                    except:
                        food_name = f"菜品{order['food_id']}"
                
                orders_list.append({
                    "food_id": int(order['food_id']),
                    "food_name": food_name,
                    "price": float(order['price']),
                    "quantity": int(order['quantity']),
                    "subtotal": float(order['subtotal'])
                })
            
            # 计算该用户的总价
            total_amount = sum(item["subtotal"] for item in orders_list)
            
            result.append({
                "user_id": int(user_id),
                "user_name": user_name,
                "items": orders_list,
                "total": total_amount
            })
        
        app.logger.info(f"获取到{len(result)}个用户的订单数据")
        
        return jsonify({"users": result})
        
    except Exception as e:
        import traceback
        app.logger.error(f"获取所有订单失败: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/api/user-orders/<int:user_id>', methods=['GET'])
def get_user_orders(user_id):
    try:
        app.logger.info(f"获取用户(id={user_id})的订单信息")
        
        # 读取用户和订单数据
        try:
            users_df = pd.read_excel('food_orders.xlsx', sheet_name='users')
            orders_df = pd.read_excel('food_orders.xlsx', sheet_name='orders')
            app.logger.info(f"成功读取用户订单数据，列名：{orders_df.columns.tolist()}")
        except Exception as e:
            app.logger.error(f"读取Excel数据失败: {str(e)}")
            return jsonify({"error": "无法读取订单数据"}), 500
        
        # 检查并修复可能缺失的列
        required_columns = ['user_id', 'food_id', 'quantity', 'food_name', 'price', 'subtotal', 'user_name']
        for col in required_columns:
            if col not in orders_df.columns:
                app.logger.warning(f"订单数据中缺少列 '{col}'，添加默认值")
                if col in ['user_id', 'food_id', 'quantity']:
                    orders_df[col] = 0
                elif col in ['price', 'subtotal']:
                    orders_df[col] = 0.0
                elif col == 'user_name':
                    # 为每个user_id添加相应的user_name
                    orders_df['user_name'] = orders_df['user_id'].apply(get_user_name_by_id)
                    app.logger.info("添加了user_name列并填充用户名")
                else:
                    orders_df[col] = '未知'
        
        # 确保数值列是数值类型
        orders_df['user_id'] = pd.to_numeric(orders_df['user_id'], errors='coerce').fillna(0).astype(int)
        orders_df['food_id'] = pd.to_numeric(orders_df['food_id'], errors='coerce').fillna(0).astype(int)
        orders_df['quantity'] = pd.to_numeric(orders_df['quantity'], errors='coerce').fillna(0).astype(int)
        orders_df['price'] = pd.to_numeric(orders_df['price'], errors='coerce').fillna(0).astype(float)
        orders_df['subtotal'] = pd.to_numeric(orders_df['subtotal'], errors='coerce').fillna(0).astype(float)

        # 计算缺失的subtotal
        mask = (orders_df['subtotal'] == 0) & (orders_df['price'] > 0) & (orders_df['quantity'] > 0)
        orders_df.loc[mask, 'subtotal'] = orders_df.loc[mask, 'price'] * orders_df.loc[mask, 'quantity']
        
        # 过滤当前用户的订单
        user_orders = orders_df[orders_df['user_id'] == user_id]
        
        if user_orders.empty:
            app.logger.info(f"用户(id={user_id})没有订单")
            return jsonify({"orders": [], "total": 0.0})
        
        # 格式化订单数据
        orders_list = []
        for _, order in user_orders.iterrows():
            # 读取菜品名称（如果缺失）
            food_name = order['food_name']
            if pd.isna(food_name) or food_name == '未知':
                try:
                    menu_df = pd.read_excel('menu_data.xlsx')
                    food_row = menu_df[menu_df['id'] == order['food_id']]
                    if not food_row.empty:
                        food_name = food_row.iloc[0]['name']
                except:
                    food_name = f"菜品{order['food_id']}"
            
            orders_list.append({
                "food_id": int(order['food_id']),
                "food_name": food_name,
                "price": float(order['price']),
                "quantity": int(order['quantity']),
                "subtotal": float(order['subtotal'])
            })
        
        # 计算总价
        total_amount = sum(item["subtotal"] for item in orders_list)
        
        app.logger.info(f"获取到{len(orders_list)}个订单项，总价: {total_amount}")
        
        return jsonify({
            "orders": orders_list,
            "total": total_amount
        })
        
    except Exception as e:
        import traceback
        app.logger.error(f"获取用户订单失败: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/api/update-orders', methods=['POST'])
def update_orders():
    try:
        app.logger.info("收到订单更新请求")
        # 先尝试修复Excel文件结构
        fix_excel_structure()
        
        data = request.json
        changes = data.get('changes', [])
        
        app.logger.info(f"要更新的订单: {changes}")
        
        if not changes:
            return jsonify({"status": "success", "message": "No changes"})
        
        # 读取现有订单
        try:
            orders_df = pd.read_excel('food_orders.xlsx', sheet_name='orders')
            app.logger.info(f"读取到{len(orders_df)}条订单记录")
        except Exception as e:
            app.logger.error(f"读取订单表失败: {str(e)}")
            return jsonify({"status": "error", "message": "无法读取订单数据"}), 500
        
        # 处理每个更改
        for change in changes:
            # 在处理变更之前，确保类型正确
            user_id = int(change.get('user_id'))
            food_id = int(change.get('food_id'))
            quantity = int(change.get('quantity'))
            
            app.logger.info(f"处理变更: user_id={user_id}, food_id={food_id}, quantity={quantity}")
            
            # 确保orders_df中的列类型正确
            orders_df['user_id'] = orders_df['user_id'].astype(int)
            orders_df['food_id'] = orders_df['food_id'].astype(int)
            
            # 找到匹配的订单行
            mask = (
                (orders_df['user_id'] == user_id) & 
                (orders_df['food_id'] == food_id)
            )
            matching_rows = orders_df[mask]
            
            app.logger.info(f"找到{len(matching_rows)}条匹配记录")
            
            # 执行操作
            if quantity <= 0:
                app.logger.info("执行删除操作")
                # 删除所有匹配的行
                orders_df = orders_df[~mask]
            else:
                app.logger.info("执行更新操作")
                if not matching_rows.empty:
                    # 删除所有匹配的行
                    orders_df = orders_df[~mask]
                    
                    # 只添加一个新行，数量为修改后的总数量
                    user_name = matching_rows['user_name'].iloc[0] if 'user_name' in matching_rows.columns else f"用户{user_id}"
                    order_time = matching_rows['order_time'].iloc[0] if 'order_time' in matching_rows.columns else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    new_row = {
                        'user_id': user_id,
                        'user_name': user_name,
                        'food_id': food_id,
                        'quantity': quantity,
                        'order_time': order_time
                    }
                    app.logger.info(f"添加新行: {new_row}")
                    orders_df = pd.concat([orders_df, pd.DataFrame([new_row])], ignore_index=True)
        
        # 保存回Excel文件，保留所有工作表
        try:
            with pd.ExcelFile('food_orders.xlsx') as xls:
                sheet_dict = {}
                for sheet in xls.sheet_names:
                    if sheet == 'orders':
                        sheet_dict[sheet] = orders_df
                    else:
                        sheet_dict[sheet] = pd.read_excel(xls, sheet_name=sheet)
            
            app.logger.info(f"保存更新后的订单记录: {len(orders_df)}条")
            
            with pd.ExcelWriter('food_orders.xlsx') as writer:
                for sheet_name, df in sheet_dict.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            app.logger.info("成功保存订单更新")
            return jsonify({"status": "success", "updated_rows": len(orders_df)})
        except Exception as e:
            app.logger.error(f"保存更新后的订单失败: {str(e)}")
            return jsonify({"status": "error", "message": f"保存更新失败: {str(e)}"}), 500
        
    except Exception as e:
        import traceback
        app.logger.error(f"更新订单失败: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/batch-update-orders', methods=['POST'])
def batch_update_orders():
    try:
        data = request.json
        user_id = data.get('user_id')
        changes = data.get('changes', [])
        
        if not changes:
            return jsonify({"status": "success", "message": "没有要更新的订单"})
        
        # 加载当前订单数据
        orders_df = pd.read_excel(USERS_EXCEL_FILE, sheet_name='orders')
        
        # 处理每个更改
        for change in changes:
            food_id = change.get('food_id')
            quantity = change.get('quantity', 0)
            change_type = change.get('type')
            
            # 找到要更新的订单项
            mask = (orders_df['user_id'] == user_id) & (orders_df['food_id'] == food_id)
            
            if change_type == 'delete' or quantity <= 0:
                # 删除订单项
                orders_df = orders_df[~mask]
            else:
                # 更新订单数量
                if any(mask):
                    orders_df.loc[mask, 'quantity'] = quantity
        
        # 保存更新后的订单到Excel
        write_users_excel('orders', orders_df)
        
        return jsonify({"status": "success"})
        
    except Exception as e:
        app.logger.error(f"批量更新订单失败: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/edit-orders', methods=['POST'])
def edit_orders():
    try:
        app.logger.info("收到修改订单请求")
        data = request.json
        user_id = data.get('user_id')
        modified_items = data.get('items', [])
        
        app.logger.info(f"要修改的订单: user_id={user_id}, 项目数={len(modified_items)}")
        
        if not user_id or not modified_items:
            app.logger.warning("缺少必要参数")
            return jsonify({"status": "error", "message": "缺少必要参数"}), 400
        
        # 确保用户ID是整数
        try:
            user_id = int(user_id)
        except ValueError:
            app.logger.error(f"用户ID不是有效整数: {user_id}")
            return jsonify({"status": "error", "message": "用户ID无效"}), 400
        
        # 读取现有订单
        try:
            if not os.path.exists('food_orders.xlsx'):
                app.logger.error("订单文件不存在")
                return jsonify({"status": "error", "message": "订单文件不存在"}), 404
                
            orders_df = pd.read_excel('food_orders.xlsx', sheet_name='orders')
            users_df = pd.read_excel('food_orders.xlsx', sheet_name='users')
            app.logger.info(f"读取到{len(orders_df)}条订单记录")
        except Exception as e:
            app.logger.error(f"读取订单数据失败: {str(e)}")
            return jsonify({"status": "error", "message": "无法读取订单数据"}), 500
        
        # 确保数据类型正确
        for col in ['user_id', 'food_id', 'quantity']:
            if col in orders_df.columns:
                orders_df[col] = pd.to_numeric(orders_df[col], errors='coerce').fillna(0).astype(int)
        
        # 过滤该用户的订单
        user_orders_mask = orders_df['user_id'] == user_id
        if not any(user_orders_mask):
            app.logger.warning(f"未找到用户{user_id}的订单")
            return jsonify({"status": "error", "message": "未找到该用户的订单"}), 404
        
        # 处理每个修改项
        has_updates = False
        for item in modified_items:
            try:
                food_id = int(item.get('food_id'))
                new_quantity = int(item.get('quantity', 0))
                # 直接使用前端传递的food_name和price
                food_name = item.get('food_name', '')
                price = clean_price(item.get('price', 0))
                
                app.logger.info(f"处理修改: food_id={food_id}, food_name={food_name}, 新数量={new_quantity}, price={price}")
                
                # 找到对应的订单行
                item_mask = (orders_df['user_id'] == user_id) & (orders_df['food_id'] == food_id)
                
                if any(item_mask):
                    if new_quantity <= 0:
                        # 如果数量为0或负数，删除该订单项
                        app.logger.info(f"删除订单项: user_id={user_id}, food_id={food_id}")
                        orders_df = orders_df[~item_mask]
                    else:
                        # 更新数量和小计
                        idx = orders_df[item_mask].index[0]
                        
                        # 更新订单
                        orders_df.at[idx, 'quantity'] = new_quantity
                        orders_df.at[idx, 'subtotal'] = price * new_quantity
                        # 确保food_name和price是正确的
                        orders_df.at[idx, 'food_name'] = food_name
                        orders_df.at[idx, 'price'] = price
                        
                        app.logger.info(f"更新订单项: user_id={user_id}, food_id={food_id}, food_name={food_name}, 新数量={new_quantity}, 小计={price * new_quantity}")
                    
                    has_updates = True
                else:
                    app.logger.warning(f"未找到要修改的订单项: user_id={user_id}, food_id={food_id}")
            except (ValueError, TypeError) as e:
                app.logger.error(f"处理修改项时出错: {str(e)}")
                continue
        
        if not has_updates:
            app.logger.info("没有实际的订单修改")
            return jsonify({"status": "info", "message": "没有实际修改"})
        
        # 保存更新后的订单
        try:
            with pd.ExcelWriter('food_orders.xlsx') as writer:
                orders_df.to_excel(writer, sheet_name='orders', index=False)
                users_df.to_excel(writer, sheet_name='users', index=False)
            
            app.logger.info("成功保存修改后的订单")
            
            # 运行结构修复以确保数据一致性
            fix_excel_structure()
            
            return jsonify({"status": "success", "message": "订单已更新"})
        except Exception as e:
            app.logger.error(f"保存修改后的订单失败: {str(e)}")
            return jsonify({"status": "error", "message": f"保存修改失败: {str(e)}"}), 500
            
    except Exception as e:
        import traceback
        app.logger.error(f"修改订单失败: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500

# 添加一个初始化/修复Excel文件结构的函数
def fix_excel_structure():
    try:
        app.logger.info("尝试修复Excel文件结构")
        
        # 如果文件不存在，创建一个新的空结构
        if not os.path.exists('food_orders.xlsx'):
            app.logger.info("创建新的Excel文件")
            # 创建订单表
            orders_df = pd.DataFrame(columns=[
                'user_id', 'user_name', 'food_id', 'food_name', 'quantity', 'price', 'subtotal'
            ])
            
            # 创建空的用户表
            users_df = pd.DataFrame(columns=['id', 'name'])
            
            # 保存Excel文件
            with pd.ExcelWriter('food_orders.xlsx', engine='openpyxl') as writer:
                orders_df.to_excel(writer, sheet_name='orders', index=False)
                users_df.to_excel(writer, sheet_name='users', index=False)
            
            app.logger.info("创建了新的Excel文件结构")
            return
        
        # 读取现有文件
        sheet_dict = {}
        try:
            with pd.ExcelFile('food_orders.xlsx') as xls:
                sheet_names = xls.sheet_names
                for sheet in xls.sheet_names:
                    sheet_dict[sheet] = pd.read_excel(xls, sheet_name=sheet)
                app.logger.info(f"读取到现有工作表: {sheet_names}")
        except Exception as e:
            app.logger.error(f"读取Excel文件失败: {str(e)}")
            # 备份可能损坏的文件
            if os.path.exists('food_orders.xlsx'):
                os.rename('food_orders.xlsx', 'food_orders_corrupted.xlsx')
                app.logger.info("将可能损坏的文件重命名为food_orders_corrupted.xlsx")
            
            # 创建一个新的
            orders_df = pd.DataFrame(columns=[
                'user_id', 'user_name', 'food_id', 'food_name', 'quantity', 'price', 'subtotal'
            ])
            users_df = pd.DataFrame(columns=['id', 'name'])
            
            with pd.ExcelWriter('food_orders.xlsx', engine='openpyxl') as writer:
                orders_df.to_excel(writer, sheet_name='orders', index=False)
                users_df.to_excel(writer, sheet_name='users', index=False)
                
            app.logger.info("创建了新的Excel文件结构")
            return
        
        # 确保users表存在
        if 'users' not in sheet_dict:
            sheet_dict['users'] = pd.DataFrame(columns=['id', 'name'])
            app.logger.info("添加了空的users表")
        else:
            # 确保users表的列类型正确
            users_df = sheet_dict['users']
            if 'id' in users_df.columns:
                users_df['id'] = pd.to_numeric(users_df['id'], errors='coerce').fillna(0).astype(int)
            app.logger.info("修正了users表的数据类型")
        
        # 确保orders表存在且格式正确
        if 'orders' not in sheet_dict:
            sheet_dict['orders'] = pd.DataFrame(columns=[
                'user_id', 'user_name', 'food_id', 'food_name', 'quantity', 'price', 'subtotal'
            ])
            app.logger.info("添加了缺失的orders表")
        else:
            # 检查orders表是否有所有必要的列
            orders_df = sheet_dict['orders']
            required_columns = [
                'user_id', 'user_name', 'food_id', 'food_name', 'quantity', 'price', 'subtotal'
            ]
            
            # 检查并添加缺失的列
            missing_columns = [col for col in required_columns if col not in orders_df.columns]
            if missing_columns:
                app.logger.info(f"添加缺失的列: {missing_columns}")
                for col in missing_columns:
                    if col in ['user_id', 'food_id', 'quantity']:
                        orders_df[col] = 0
                    elif col in ['price', 'subtotal']:
                        orders_df[col] = 0.0
                    else:
                        orders_df[col] = ''
            
            # 移除旧的列（如order_time）
            if 'order_time' in orders_df.columns:
                orders_df = orders_df.drop(columns=['order_time'])
                app.logger.info("移除了不需要的order_time列")
            
            # 确保数据类型正确
            for col in ['user_id', 'food_id', 'quantity']:
                if col in orders_df.columns:
                    orders_df[col] = pd.to_numeric(orders_df[col], errors='coerce').fillna(0).astype(int)
            
            for col in ['price', 'subtotal']:
                if col in orders_df.columns:
                    orders_df[col] = pd.to_numeric(orders_df[col], errors='coerce').fillna(0).astype(float)
            
            app.logger.info("修正了orders表的数据类型")
            
            # 过滤掉无效记录（food_id为0的记录）
            invalid_count = len(orders_df[orders_df['food_id'] == 0])
            if invalid_count > 0:
                orders_df = orders_df[orders_df['food_id'] > 0]
                app.logger.info(f"移除了{invalid_count}条无效记录")
            
            # 更新user_name字段，确保每条记录都有正确的用户名
            if 'user_name' in orders_df.columns and 'user_id' in orders_df.columns:
                # 加载用户表，创建ID到名称的映射
                users_df = sheet_dict.get('users', pd.DataFrame())
                user_name_map = {}
                if not users_df.empty and 'id' in users_df.columns and 'name' in users_df.columns:
                    for _, row in users_df.iterrows():
                        if not pd.isna(row['id']) and not pd.isna(row['name']):
                            user_name_map[int(row['id'])] = row['name']
                
                updated_count = 0
                # 更新缺失或默认的user_name
                for idx, row in orders_df.iterrows():
                    user_id = row['user_id']
                    if pd.isna(row['user_name']) or row['user_name'] == '' or row['user_name'] == f"用户{user_id}":
                        if int(user_id) in user_name_map:
                            orders_df.at[idx, 'user_name'] = user_name_map[int(user_id)]
                            updated_count += 1
                
                if updated_count > 0:
                    app.logger.info(f"更新了{updated_count}条订单的用户名")
            
            # 确保food_name不为空
            if 'food_name' in orders_df.columns and 'food_id' in orders_df.columns:
                try:
                    # 加载菜单数据
                    menu_df = pd.read_excel('menu_data.xlsx')
                    food_name_map = {}
                    for _, row in menu_df.iterrows():
                        food_name_map[int(row['id'])] = row['name']
                    
                    # 更新缺失的food_name
                    missing_food_name_count = 0
                    for idx, row in orders_df.iterrows():
                        food_id = row['food_id']
                        if pd.isna(row['food_name']) or row['food_name'] == '':
                            if int(food_id) in food_name_map:
                                orders_df.at[idx, 'food_name'] = food_name_map[int(food_id)]
                                missing_food_name_count += 1
                    
                    if missing_food_name_count > 0:
                        app.logger.info(f"更新了{missing_food_name_count}条订单的菜品名称")
                except Exception as e:
                    app.logger.error(f"更新菜品名称时出错: {str(e)}")
            
            # 更新价格和小计
            if all(col in orders_df.columns for col in ['price', 'quantity', 'subtotal', 'food_id']):
                try:
                    # 加载菜单数据
                    menu_df = pd.read_excel('menu_data.xlsx')
                    price_map = {}
                    for _, row in menu_df.iterrows():
                        price_map[int(row['id'])] = clean_price(row['price'])
                    
                    # 更新缺失的价格和小计
                    updated_price_count = 0
                    updated_subtotal_count = 0
                    
                    for idx, row in orders_df.iterrows():
                        food_id = row['food_id']
                        quantity = row['quantity']
                        
                        # 更新价格
                        if pd.isna(row['price']) or row['price'] == 0:
                            if int(food_id) in price_map:
                                orders_df.at[idx, 'price'] = price_map[int(food_id)]
                                updated_price_count += 1
                        
                        # 确保价格是清理过的
                        current_price = orders_df.at[idx, 'price']
                        clean_price_val = clean_price(current_price)
                        if clean_price_val != current_price:
                            orders_df.at[idx, 'price'] = clean_price_val
                        
                        # 更新小计
                        if (pd.isna(row['subtotal']) or row['subtotal'] == 0) and clean_price_val > 0 and quantity > 0:
                            orders_df.at[idx, 'subtotal'] = clean_price_val * quantity
                            updated_subtotal_count += 1
                    
                    if updated_price_count > 0:
                        app.logger.info(f"更新了{updated_price_count}条订单的价格")
                    if updated_subtotal_count > 0:
                        app.logger.info(f"更新了{updated_subtotal_count}条订单的小计")
                except Exception as e:
                    app.logger.error(f"更新价格和小计时出错: {str(e)}")
            
            # 合并相同用户的相同食物订单项
            if all(col in orders_df.columns for col in ['user_id', 'food_id', 'quantity', 'price', 'subtotal']):
                try:
                    app.logger.info("开始合并相同用户的相同食物订单...")
                    # 记录合并前的订单数量
                    before_merge_count = len(orders_df)
                    
                    # 找出所有需要合并的组（相同用户ID和相同食物ID）
                    duplicated_groups = orders_df.groupby(['user_id', 'food_id']).filter(lambda x: len(x) > 1)
                    
                    if not duplicated_groups.empty:
                        # 获取需要合并的用户和食物组合
                        groups_to_merge = duplicated_groups[['user_id', 'food_id']].drop_duplicates().values.tolist()
                        app.logger.info(f"发现{len(groups_to_merge)}组需要合并的订单")
                        
                        # 对于每个需要合并的组，执行合并操作
                        for user_id, food_id in groups_to_merge:
                            # 找出属于该组的所有行
                            group_mask = (orders_df['user_id'] == user_id) & (orders_df['food_id'] == food_id)
                            group_rows = orders_df[group_mask]
                            
                            if len(group_rows) <= 1:
                                continue  # 只有一行，不需要合并
                            
                            # 提取第一行作为基准
                            base_row = group_rows.iloc[0].copy()
                            
                            # 计算总数量和总价
                            total_quantity = group_rows['quantity'].sum()
                            price = base_row['price']  # 假设价格相同
                            total_subtotal = price * total_quantity
                            
                            # 创建新的合并行
                            merged_row = base_row.copy()
                            merged_row['quantity'] = total_quantity
                            merged_row['subtotal'] = total_subtotal
                            
                            # 从原始DataFrame中删除该组的所有行
                            orders_df = orders_df[~group_mask]
                            
                            # 添加合并后的行
                            orders_df = pd.concat([orders_df, pd.DataFrame([merged_row])], ignore_index=True)
                            
                            app.logger.info(f"合并了用户{user_id}的{food_id}号食物订单，合并前{len(group_rows)}条，合并后数量为{total_quantity}")
                        
                        after_merge_count = len(orders_df)
                        app.logger.info(f"订单合并完成，订单数量从{before_merge_count}减少到{after_merge_count}")
                    else:
                        app.logger.info("没有发现需要合并的订单")
                        
                except Exception as e:
                    app.logger.error(f"合并订单时出错: {str(e)}")
            
            sheet_dict['orders'] = orders_df
        
        # 将修复后的结构保存回文件
        with pd.ExcelWriter('food_orders.xlsx', engine='openpyxl') as writer:
            for sheet_name, df in sheet_dict.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        app.logger.info("Excel文件结构已修复")
        
    except Exception as e:
        app.logger.error(f"修复Excel结构失败: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())

def initialize_app():
    """应用初始化，每次启动时加载menu_data.xlsx的内容"""
    app.logger.info("Initialisiere die Anwendung...")
    
    # 修复Excel结构
    fix_excel_structure()
    
    # 检查menu_data.xlsx是否存在
    if not os.path.exists(MENU_EXCEL_FILE):
        app.logger.warning("menu_data.xlsx nicht gefunden. Eine leere Datei wird erstellt.")
        init_menu_excel()
    else:
        app.logger.info("menu_data.xlsx gefunden. Menüdaten werden geladen.")
        try:
            # 尝试加载菜单数据，验证是否有效
            df = pd.read_excel(MENU_EXCEL_FILE, engine='openpyxl')
            
            # 检查必要字段
            required_columns = ['id', 'name', 'price', 'image']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                app.logger.error(f"Fehlende Spalten in menu_data.xlsx: {', '.join(missing_columns)}")
            else:
                app.logger.info(f"Erfolgreich {len(df)} Menüeinträge aus Excel geladen")
                
                # 如果description列不存在，添加它
                if 'description' not in df.columns:
                    app.logger.warning("Spalte 'description' fehlt in menu_data.xlsx. Es wird eine leere Spalte hinzugefügt.")
                    df['description'] = ''
                    # 保存回Excel文件
                    df.to_excel(MENU_EXCEL_FILE, index=False)
        except Exception as e:
            app.logger.error(f"Fehler beim Laden von menu_data.xlsx: {str(e)}")

def get_user_name_by_id(user_id):
    """获取用户名，首先从CSV读取，然后尝试Excel"""
    try:
        # 首先尝试从CSV读取
        users_file = 'users.csv'
        if os.path.exists(users_file):
            import csv
            with open(users_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None)  # 跳过标题行
                for row in reader:
                    if len(row) >= 2 and int(row[0]) == user_id:
                        return row[1]
        
        # 如果CSV中没找到，尝试Excel
        if os.path.exists('food_orders.xlsx'):
            users_df = pd.read_excel('food_orders.xlsx', sheet_name='users')
            user_row = users_df[users_df['id'] == user_id]
            if not user_row.empty:
                return user_row.iloc[0]['name']
    except Exception as e:
        app.logger.error(f"获取用户名失败: {str(e)}")
    
    return f"用户{user_id}"

def clean_price(price_str):
    """将各种格式的价格字符串转换为浮点数"""
    try:
        # 如果已经是数值类型，直接返回
        if isinstance(price_str, (int, float)):
            return float(price_str)
        
        # 如果是None或空值，返回0
        if price_str is None or pd.isna(price_str) or price_str == '':
            return 0.0
        
        # 转换为字符串
        price_str = str(price_str)
        
        # 移除所有非数字、小数点和逗号的字符
        cleaned = ''.join(c for c in price_str if c.isdigit() or c in '.,')
        
        # 将逗号替换为小数点（欧洲格式 -> 美式格式）
        cleaned = cleaned.replace(',', '.')
        
        # 如果处理后字符串为空，返回0
        if not cleaned:
            return 0.0
            
        return float(cleaned)
    except Exception:
        return 0.0  # 或者其他适当的默认值

if __name__ == '__main__':
    # 应用启动时初始化
    initialize_app()
    app.run(host='0.0.0.0', port=7860, debug=False)