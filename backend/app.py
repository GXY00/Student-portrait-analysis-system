import random
from datetime import datetime
from flask import Flask, render_template, send_from_directory, session, make_response, request, jsonify, g
from flask_cors import CORS
from captcha_utils import CaptchaGenerator # type: ignore
import io
import base64
from flask import Response
import os
import openpyxl
import docx
import pymysql
from pymysql.cursors import DictCursor
import json
from tag_rule_engine import TagRuleEngine
from class_tag_rule_engine import ClassTagRuleEngine

base_dir = os.path.dirname(os.path.abspath(__file__))
dist_dir = os.path.join(base_dir, '../bishe/dist')
static_dir = os.path.join(dist_dir, 'static')

app = Flask(__name__, 
            static_folder=static_dir, 
            template_folder=dist_dir,
            static_url_path='/static')
app.secret_key = 'GXY040713'

# 允许跨域
CORS(app, supports_credentials=True)

# 数据库配置
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "ReDMi142GXY!MYSQl",
    "database": "stuportrait",
    "port": 3306,
    "charset": "utf8mb4",
    "cursorclass": DictCursor,
}

def test_db_connection():
    """测试数据库连接"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        print("已连接")
        connection.close()
        return True
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return False

def get_db():
    """获取数据库连接（每个请求复用一个连接）"""
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = pymysql.connect(**DB_CONFIG)
    return db

@app.teardown_appcontext
def close_db(exception):
    """请求结束后自动关闭数据库连接"""
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()
        
def query_db(sql, args=(), one=False):
    """执行SQL并返回结果"""
    cursor = get_db().cursor()
    try:
        cursor.execute(sql, args)
        result = cursor.fetchall()
        return (result[0] if result else None) if one else result
    finally:
        cursor.close()
        
def insert_log_record(sql, args=()):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(sql, args)
        db.commit()
        return (True, cursor.lastrowid)  # 成功返回标志和自增ID
    except Exception as e:
        db.rollback()
        return (False, str(e))  # 失败返回标志和错误信息
    finally:
        cursor.close()

def log_operation(username, operation_type, status, user_id=None):
    """
    使用insert_log_record函数执行SQL插入操作，记录操作日志
    :param username: 用户名
    :param operation_type: 操作类型
    :param status: 操作结果 (1-成功, 0-失败)
    :param user_id: 用户ID (可选)
    """
    insert_sql = """
    INSERT INTO operation_log (user_id, username, operation_type, status)
    VALUES (%s, %s, %s, %s)
    """
    try:
        success, msg = insert_log_record(insert_sql, (user_id, username, operation_type, status))
        if success:
            print("日志写入成功")
        else:
            print(f"写入日志失败: {msg}")   
    except Exception as e:
        print(f"写入日志失败: {e}")

@app.route('/')
def index():
    """
    当访问根路径时，返回 Vue 构建生成的 index.html
    """
    try:
        return render_template('index.html')
    except Exception as e:
        return f"错误：无法加载前端页面。请确保已在 bishe 目录下运行 'npm run build' 生成 dist 目录。<br>详情：{str(e)}"

# 用户登录接口
@app.route('/api/v1/user/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # 查询数据库中是否存在该用户
    query_sql = "SELECT * FROM user WHERE username = %s AND password = %s"
    user = query_db(query_sql, (username, password), one=True)
    
    if user:
        # 登录成功，记录日志
        user_id = user.get('user_id')
        role_id = user.get('role_id')
        role_map = {1: 'student', 2: 'teacher', 3: 'admin'}
        role_name = role_map.get(role_id, 'student')
        
        log_operation(username, "login", 1, user_id)
        print(f"登录成功: {username}, role={role_name}")
        return jsonify({"success": True, "msg": "登录成功", "role": role_name}), 200
    else:
        # 登录失败，记录日志
        log_operation(username, "login", 0)
        print("登录失败")
        return jsonify({"success": False, "msg": "用户名或密码错误"}), 401

# 用户退出登录接口
@app.route('/api/v1/user/logout_log', methods=['POST'])
def logout_log():
    data = request.get_json()
    username = data.get('username')
    status = data.get('status')
    
    user_id = None
    if username:
        try:
            with pymysql.connect(**DB_CONFIG) as connection:
                with connection.cursor() as cursor:
                    sql = "SELECT user_id FROM user WHERE username = %s"
                    cursor.execute(sql, (username,))
                    result = cursor.fetchone()
                    if result:
                        user_id = result['user_id']
        except Exception as e:
            print(f"Error fetching user_id for logout log: {e}")

    log_operation(username, '退出登录', status, user_id)
    return jsonify({"success": True}), 200

# 用户存在性检查接口
@app.route('/api/v1/user/check_exist', methods=['POST'])
def check_user_exist():
    data = request.get_json()
    username = data.get('username')
    
    query_sql = "SELECT user_id FROM user WHERE username = %s"
    user = query_db(query_sql, (username,), one=True)
    
    if user:
        return jsonify({"success": True, "exists": True, "msg": "用户存在"}), 200
    else:
        return jsonify({"success": True, "exists": False, "msg": "用户不存在"}), 200

# 用户密码重置接口
@app.route('/api/v1/user/detail', methods=['POST'])
def get_user_detail():
    data = request.get_json()
    username = data.get('username')
    
    if not username:
        return jsonify({"success": False, "msg": "用户名不能为空"}), 400
        
    # 首先获取用户的基本信息，特别是 role_id
    user_sql = "SELECT user_id, username, role_id, password FROM user WHERE username = %s"
    user = query_db(user_sql, (username,), one=True)
    
    if not user:
        return jsonify({"success": False, "msg": "用户不存在"}), 404
        
    role_id = user['role_id']
    user_info = {
        "username": user['username'],
        "role_id": role_id,
        "password": user['password'] # 实际生产环境不应返回密码，但此处前端有修改密码需求且原代码包含显示密码功能
    }
    
    if role_id == 1: # 学生
        student_sql = """
        SELECT s.stu_name as name, s.student_no as number, s.gender, s.grade, c.class_name
        FROM student s
        LEFT JOIN class c ON s.class_id = c.class_id
        WHERE s.user_id = %s
        """
        student = query_db(student_sql, (user['user_id'],), one=True)
        if student:
            user_info.update({
                "name": student['name'],
                "studentId": student['number'],
                "gender": student['gender'],
                "grade": student['grade'],
                "class": student['class_name']
            })
    elif role_id == 2: # 教师
        teacher_sql = """
        SELECT t.tea_name as name, t.teacher_no as number,t.gender as gender, t.grade, c.class_name
        FROM teacher t
        LEFT JOIN class c ON t.class_id = c.class_id
        WHERE t.user_id = %s
        """
        teacher = query_db(teacher_sql, (user['user_id'],), one=True)
        if teacher:
            user_info.update({
                "name": teacher['name'],
                "studentId": teacher['number'], # 复用字段名
                "gender": teacher['gender'],
                "grade": teacher['grade'],
                "class": teacher['class_name']
            })
    elif role_id == 3: # 管理员
        # 管理员可能没有额外信息表，直接使用 user 表信息
        # 如果有 real_name 字段
        user_detail_sql = "SELECT real_name FROM user WHERE user_id = %s"
        user_detail = query_db(user_detail_sql, (user['user_id'],), one=True)
        user_info.update({
            "name": user_detail.get('real_name', '管理员') if user_detail else '管理员',
            "studentId": "admin",
            "gender": "-",
            "grade": "-",
            "class": "-"
        })
        
    return jsonify({"success": True, "data": user_info}), 200

@app.route('/api/v1/user/update_info', methods=['POST'])
def update_user_info():
    data = request.get_json()
    # 原始 ID (username/学号/工号)
    original_id = data.get('id')
    new_id = data.get('new_id') # 新 ID
    
    # 可修改字段
    name = data.get('name')
    gender = data.get('gender')
    age = data.get('age') # 前端传来的年龄，暂不存库或存入 details
    grade = data.get('grade')
    class_name = data.get('class')
    password = data.get('password')
    role_str = data.get('role') # '学生' 或 '教师'
    
    if not original_id:
        return jsonify({"success": False, "msg": "ID不能为空"}), 400
        
    try:
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            # 1. 获取 user_id
            cursor.execute("SELECT user_id, username FROM user WHERE username = %s", (original_id,))
            user_res = cursor.fetchone()
            if not user_res:
                return jsonify({"success": False, "msg": "用户不存在"}), 404
            user_id = user_res['user_id']
            
            # 2. 更新 user 表
            user_updates = []
            user_params = []
            
            if password:
                user_updates.append("password = %s")
                user_params.append(password)
            
            if new_id:
                user_updates.append("username = %s")
                user_params.append(new_id)
                
            if name:
                user_updates.append("real_name = %s")
                user_params.append(name)
                
            # 如果修改了学号/工号或姓名，更新 create_time
            if new_id or name:
                user_updates.append("create_time = NOW()")
            
            if user_updates:
                sql = f"UPDATE user SET {', '.join(user_updates)} WHERE user_id = %s"
                user_params.append(user_id)
                cursor.execute(sql, user_params)
            
            # 3. 更新 student 或 teacher 表
            # 首先需要知道这是学生还是老师。可以通过 role_id 判断，或者通过 role_str 判断
            # 这里简单起见，尝试更新两张表，或者先查 role_id
            cursor.execute("SELECT role_id FROM user WHERE user_id = %s", (user_id,))
            role_res = cursor.fetchone()
            role_id = role_res['role_id']
            
            if role_id == 1: # 学生
                stu_updates = []
                stu_params = []
                if new_id:
                    stu_updates.append("student_no = %s")
                    stu_params.append(new_id)
                if name:
                    stu_updates.append("stu_name = %s")
                    stu_params.append(name)
                if gender:
                    stu_updates.append("gender = %s")
                    stu_params.append(gender)
                if grade:
                    stu_updates.append("grade = %s")
                    stu_params.append(grade)
                if class_name:
                    # 需要查找 class_id
                    cursor.execute("SELECT class_id FROM class WHERE class_name = %s", (class_name,))
                    class_res = cursor.fetchone()
                    if class_res:
                        stu_updates.append("class_id = %s")
                        stu_params.append(class_res['class_id'])
                
                if stu_updates:
                    sql = f"UPDATE student SET {', '.join(stu_updates)} WHERE user_id = %s"
                    stu_params.append(user_id)
                    cursor.execute(sql, stu_params)
                    
            elif role_id == 2: # 教师
                tea_updates = []
                tea_params = []
                if new_id:
                    tea_updates.append("teacher_no = %s")
                    tea_params.append(new_id)
                if name:
                    tea_updates.append("tea_name = %s")
                    tea_params.append(name)
                if gender:
                    tea_updates.append("gender = %s")
                    tea_params.append(gender)
                if grade:
                    tea_updates.append("grade = %s")
                    tea_params.append(grade)
                 # 老师也可以有班级(班主任)
                if class_name:
                    cursor.execute("SELECT class_id FROM class WHERE class_name = %s", (class_name,))
                    class_res = cursor.fetchone()
                    if class_res:
                        tea_updates.append("class_id = %s")
                        tea_params.append(class_res['class_id'])

                if tea_updates:
                    sql = f"UPDATE teacher SET {', '.join(tea_updates)} WHERE user_id = %s"
                    tea_params.append(user_id)
                    cursor.execute(sql, tea_params)
            
            connection.commit()
            
            # 记录日志
            # log_operation(original_id, "修改个人信息", 1, user_id) 
            # 注意: log_operation 需要在 app context 下运行或者重新连接数据库，这里直接用 log_operation 函数可能不行，因为它依赖 get_db()
            # 但 log_operation 使用 insert_log_record -> get_db -> g._database
            # 这里我们是在 request context 下吗？是的。
            # 但是我们自己创建了 connection。
            # 为了简单，直接手动插入日志
            cursor.execute("""
                INSERT INTO operation_log (user_id, username, operation_type, status)
                VALUES (%s, %s, %s, %s)
            """, (user_id, original_id, "修改个人信息", 1))
            connection.commit()
            
            return jsonify({"success": True, "msg": "更新成功"}), 200
            
    except Exception as e:
        print(f"Update error: {e}")
        return jsonify({"success": False, "msg": f"更新失败: {str(e)}"}), 500
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

# ===============================
# 标签生成与获取接口
# ===============================

@app.route('/api/v1/tags/generate', methods=['POST'])
def generate_tags():
    data = request.get_json()
    username = data.get('username')
    
    user_id = None
    if username:
        user = query_db("SELECT user_id FROM user WHERE username = %s", (username,), one=True)
        if user:
            user_id = user['user_id']
            
    try:
        rule_path = os.path.join(base_dir, 'stu_rule.json')
        engine = TagRuleEngine(DB_CONFIG, rule_file=rule_path)
        engine.execute_all()
        engine.close()
        log_operation(username or 'system', '生成学生标签', 1, user_id)
        return jsonify({"success": True, "msg": "标签生成成功"}), 200
    except Exception as e:
        log_operation(username or 'system', '生成学生标签', 0, user_id)
        return jsonify({"success": False, "msg": f"标签生成失败: {str(e)}"}), 500

@app.route('/api/v1/teacher/my_students', methods=['GET'])
def get_teacher_students():
    username = request.args.get('username')
    if not username:
        return jsonify({"success": False, "msg": "用户名不能为空"}), 400
    
    try:
        # 1. 获取老师信息
        user_sql = "SELECT user_id, role_id FROM user WHERE username = %s"
        user = query_db(user_sql, (username,), one=True)
        if not user or user['role_id'] != 2: # 2 is teacher
            # 如果是管理员(3)，可能也需要查看所有学生
            if user and user['role_id'] == 3:
                 # 管理员查看所有学生
                 students_sql = """
                    SELECT s.student_id, s.student_no, s.stu_name, s.gender, c.class_name
                    FROM student s
                    LEFT JOIN class c ON s.class_id = c.class_id
                    ORDER BY s.student_no
                 """
                 students = query_db(students_sql)
                 return jsonify({"success": True, "data": students}), 200
            
            return jsonify({"success": False, "msg": "用户不是教师或管理员"}), 403
            
        # 教师: 获取 class_id
        teacher_sql = "SELECT class_id FROM teacher WHERE user_id = %s"
        teacher = query_db(teacher_sql, (user['user_id'],), one=True)
        
        students = []
        if teacher and teacher['class_id']:
            # 返回该班级的学生
            students_sql = """
                SELECT s.student_id, s.student_no, s.stu_name, s.gender, c.class_name
                FROM student s
                LEFT JOIN class c ON s.class_id = c.class_id
                WHERE s.class_id = %s
                ORDER BY s.student_no
            """
            students = query_db(students_sql, (teacher['class_id'],))
        else:
            # 如果老师没有绑定班级，是否返回所有学生？或者空？
            # 暂时返回空，或者可以约定返回所有
            # 假设返回所有
            students_sql = """
                SELECT s.student_id, s.student_no, s.stu_name, s.gender, c.class_name
                FROM student s
                LEFT JOIN class c ON s.class_id = c.class_id
                ORDER BY s.student_no
            """
            students = query_db(students_sql)
            
        return jsonify({"success": True, "data": students}), 200
        
    except Exception as e:
        print(f"Error getting students: {e}")
        return jsonify({"success": False, "msg": "获取学生列表失败"}), 500

@app.route('/api/v1/tags/generate_single', methods=['POST'])
def generate_single_student_tags():
    data = request.get_json()
    student_id = data.get('student_id')
    operator_username = data.get('operator_username')
    
    if not student_id:
        return jsonify({"success": False, "msg": "学生ID不能为空"}), 400
        
    try:
        # 获取学生姓名用于日志
        stu = query_db("SELECT stu_name FROM student WHERE student_id = %s", (student_id,), one=True)
        stu_name = stu['stu_name'] if stu else str(student_id)
        
        rule_path = os.path.join(base_dir, 'stu_rule.json')
        engine = TagRuleEngine(DB_CONFIG, rule_file=rule_path)
        # 调用带 student_id 的 execute_all
        engine.execute_all(student_id=student_id)
        engine.close()
        
        # 记录日志
        log_content = f"生成学生画像: {stu_name}"
        # 获取操作者 user_id
        op_user_id = None
        if operator_username:
            u = query_db("SELECT user_id FROM user WHERE username = %s", (operator_username,), one=True)
            if u: op_user_id = u['user_id']
            
        log_operation(operator_username or 'system', log_content, 1, op_user_id)
        
        return jsonify({"success": True, "msg": f"学生 {stu_name} 画像生成成功"}), 200
    except Exception as e:
        print(f"Generate single error: {e}")
        return jsonify({"success": False, "msg": f"画像生成失败: {str(e)}"}), 500

@app.route('/api/v1/tags/student', methods=['GET'])
def get_student_tags():
    username = request.args.get('username')
    student_id_param = request.args.get('student_id')
    
    if not username and not student_id_param:
        return jsonify({"success": False, "msg": "参数缺失"}), 400
        
    try:
        target_student_id = None
        
        if student_id_param:
            target_student_id = student_id_param
        else:
            # 通过 username 查找
            user = query_db("SELECT user_id, role_id FROM user WHERE username = %s", (username,), one=True)
            if not user:
                return jsonify({"success": False, "msg": "用户不存在"}), 404
                
            if user['role_id'] == 1: # 学生
                stu = query_db("SELECT student_id FROM student WHERE user_id = %s", (user['user_id'],), one=True)
                if stu: target_student_id = stu['student_id']
            else:
                return jsonify({"success": False, "msg": "该接口仅供学生查询自己，或指定 student_id"}), 403
        
        if not target_student_id:
            return jsonify({"success": False, "msg": "未找到对应的学生信息"}), 404
            
        # 查询标签
        sql = """
            SELECT tag_name, tag_value, update_time
            FROM student_tag t
            JOIN tag tm ON t.tag_id = tm.tag_id
            WHERE t.student_id = %s
        """
        tags = query_db(sql, (target_student_id,))
        
        return jsonify({"success": True, "data": tags}), 200
        
    except Exception as e:
        return jsonify({"success": False, "msg": f"获取标签失败: {str(e)}"}), 500

# ===============================
# 班级标签接口
# ===============================



# ===============================
# 班级标签生成与获取接口
# ===============================

@app.route('/api/v1/class/list', methods=['GET'])
def get_class_list():
    """获取班级列表"""
    try:
        sql = "SELECT class_id, class_name, grade FROM class ORDER BY grade, class_name"
        classes = query_db(sql)
        return jsonify({"success": True, "data": classes}), 200
    except Exception as e:
        return jsonify({"success": False, "msg": f"获取班级列表失败: {str(e)}"}), 500

@app.route('/api/v1/tags/class/generate', methods=['POST'])
def generate_class_tags():
    """生成所有班级标签"""
    data = request.get_json()
    username = data.get('username')
    
    user_id = None
    if username:
        user = query_db("SELECT user_id FROM user WHERE username = %s", (username,), one=True)
        if user:
            user_id = user['user_id']
            
    try:
        rule_path = os.path.join(base_dir, 'class_rule.json')
        engine = ClassTagRuleEngine(DB_CONFIG, rule_file=rule_path)
        engine.execute_all()
        engine.close()
        
        log_operation(username or 'system', '生成班级标签', 1, user_id)
        return jsonify({"success": True, "msg": "班级标签生成成功"}), 200
    except Exception as e:
        log_operation(username or 'system', '生成班级标签', 0, user_id)
        return jsonify({"success": False, "msg": f"班级标签生成失败: {str(e)}"}), 500

@app.route('/api/v1/tags/class/generate_single', methods=['POST'])
def generate_single_class_tags():
    """生成单个班级标签"""
    data = request.get_json()
    class_id = data.get('class_id')
    operator_username = data.get('operator_username')
    
    if not class_id:
        return jsonify({"success": False, "msg": "班级ID不能为空"}), 400
        
    try:
        # 获取班级名称用于日志
        cls = query_db("SELECT class_name FROM class WHERE class_id = %s", (class_id,), one=True)
        class_name = cls['class_name'] if cls else str(class_id)
        
        rule_path = os.path.join(base_dir, 'class_rule.json')
        engine = ClassTagRuleEngine(DB_CONFIG, rule_file=rule_path)
        engine.execute_all(class_id=class_id)
        engine.close()
        
        # 记录日志
        log_content = f"生成班级画像: {class_name}"
        op_user_id = None
        if operator_username:
            u = query_db("SELECT user_id FROM user WHERE username = %s", (operator_username,), one=True)
            if u: op_user_id = u['user_id']
            
        log_operation(operator_username or 'system', log_content, 1, op_user_id)
        
        return jsonify({"success": True, "msg": f"班级 {class_name} 画像生成成功"}), 200
    except Exception as e:
        return jsonify({"success": False, "msg": f"画像生成失败: {str(e)}"}), 500

@app.route('/api/v1/tags/class', methods=['GET'])
def get_class_tags():
    """获取班级标签"""
    class_id = request.args.get('class_id')
    
    if not class_id:
        return jsonify({"success": False, "msg": "班级ID不能为空"}), 400
        
    try:
        # 加载规则文件获取元数据
        rule_path = os.path.join(base_dir, 'class_rule.json')
        tag_metadata = {}
        if os.path.exists(rule_path):
            try:
                with open(rule_path, 'r', encoding='utf-8') as f:
                    rules = json.load(f)
                    for tag_def in rules.get('tags', []):
                        tag_metadata[tag_def['tag_name']] = {
                            'tag_type': tag_def.get('tag_type', '数值'),
                            'description': tag_def.get('description', '')
                        }
            except Exception as e:
                print(f"加载班级规则失败: {e}")

        # 查询标签
        sql = """
            SELECT tag_name, tag_value, update_time
            FROM class_tag
            WHERE class_id = %s
        """
        tags = query_db(sql, (class_id,))
        
        # tag_value 是 JSON 格式，pymysql 可能会返回字符串或字典
        # 如果是字符串，需要解析
        if tags is None:
            tags = []
        for tag in tags:
            if isinstance(tag['tag_value'], str):
                try:
                    tag['tag_value'] = json.loads(tag['tag_value'])
                except:
                    pass
            
            # 添加元数据
            meta = tag_metadata.get(tag['tag_name'], {})
            tag['tag_type'] = meta.get('tag_type', '数值')
            tag['description'] = meta.get('description', '')
        
        return jsonify({"success": True, "data": tags}), 200
        
    except Exception as e:
        return jsonify({"success": False, "msg": f"获取班级标签失败: {str(e)}"}), 500

# 旧接口保留但被覆盖
# def get_student_tags_old():

@app.route('/api/v1/user/change_password', methods=['POST'])
def change_password():
    data = request.get_json()
    username = data.get('username')
    old_password = data.get('oldPassword')
    new_password = data.get('newPassword')
    
    # 验证原密码
    verify_sql = "SELECT * FROM user WHERE username = %s AND password = %s"
    user = query_db(verify_sql, (username, old_password), one=True)
    
    if not user:
        return jsonify({"success": False, "msg": "原密码错误"}), 400
        
    # 更新密码
    update_sql = "UPDATE user SET password = %s WHERE username = %s"
    try:
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            cursor.execute(update_sql, (new_password, username))
        connection.commit()
        connection.close()
        
        # 记录日志
        log_operation(username, "修改密码", 1, user['user_id'])
        
        return jsonify({"success": True, "msg": "密码修改成功"}), 200
    except Exception as e:
        print(f"修改密码失败: {e}")
        log_operation(username, "修改密码", 0, user['user_id'])
        return jsonify({"success": False, "msg": "服务器内部错误"}), 500

@app.route('/api/v1/user/reset_password', methods=['POST'])
def reset_password():
    data = request.get_json()
    username = data.get('username')
    new_password = data.get('new_password')
    captcha_code = data.get('captcha_code')
    
    # 验证验证码
    correct_code = session.get('captcha')
    if not correct_code or not captcha_code or captcha_code.lower() != correct_code.lower():
        return jsonify({"success": False, "msg": "验证码错误"}), 400
        
    # 更新密码
    update_sql = "UPDATE user SET password = %s WHERE username = %s"
    try:
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            cursor.execute(update_sql, (new_password, username))
        connection.commit()
        connection.close()
        
        # 记录日志
        # 获取用户ID用于日志
        user_query = "SELECT user_id FROM user WHERE username = %s"
        user_data = query_db(user_query, (username,), one=True)
        user_id = user_data['user_id'] if user_data else None
        
        log_operation(username, "重置密码", 1, user_id)
        
        return jsonify({"success": True, "msg": "密码修改成功"}), 200
    except Exception as e:
        print(f"重置密码失败: {e}")
        log_operation(username, "重置密码", 0, None)
        return jsonify({"success": False, "msg": "服务器内部错误"}), 500

# 验证码接口
@app.route('/api/v1/captcha', methods=['GET'])
def get_captcha():
    """
    生成并返回验证码图片和验证码字符
    """
    # 初始化生成器 (宽120, 高40, 字体30)
    generator = CaptchaGenerator(width=120, height=40, font_size=30)
    image, code = generator.generate_captcha()
    
    # 打印生成的验证码文本，方便调试
    print(f"Generated Captcha: {code}")
    session['captcha'] = code
    
    # 将图片转换为字节流
    img_io = io.BytesIO()
    image.save(img_io, 'PNG')
    img_io.seek(0)
    
    # 将图片转换为 base64 字符串
    img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
    
    # 返回 JSON 数据，包含验证码字符和图片
    return jsonify({
        "code": code,
        "img": f"data:image/png;base64,{img_base64}",
        "msg": "生成成功"
    })

@app.route('/api/v1/captcha/verify', methods=['POST'])
def verify_captcha():
    """
    验证前端提交的验证码
    """
    data = request.get_json()
    user_code = data.get('code')
    
    # 从 session 中获取正确的验证码
    correct_code = session.get('captcha')
    
    print(f"Verifying Captcha - User: {user_code}, Correct: {correct_code}")
    
    if not correct_code:
        return jsonify({"code": 400, "msg": "验证码已过期或未生成", "success": False}), 400
        
    if user_code and user_code.lower() == correct_code.lower():
        # 验证成功后可以选择清除 session 中的验证码，防止重放
        # session.pop('captcha', None) 
        return jsonify({"code": 200, "msg": "验证通过", "success": True}), 200
    else:
        return jsonify({"code": 400, "msg": "验证码错误", "success": False}), 200

# 处理其他静态文件（如 favicon.ico 等，如果都在 dist 根目录下）
@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join(dist_dir, path)):
        return send_from_directory(dist_dir, path)
    return "Not Found", 404

@app.route('/api/v1/import/user', methods=['POST'])
def import_user():
    data = request.get_json()
    user_list = data.get('data')
    import_type = data.get('type') # 'student' or 'teacher'
    
    if not user_list:
        return jsonify({"success": False, "msg": "数据不能为空"}), 400
    if import_type not in ['student', 'teacher']:
         return jsonify({"success": False, "msg": "未知的导入类型"}), 400
        
    success_count = 0
    fail_count = 0
    errors = []
    
    try:
        connection = pymysql.connect(**DB_CONFIG)
        # 开启事务
        connection.begin()
        
        with connection.cursor() as cursor:
            for index, item in enumerate(user_list):
                try:
                    # 1. 解析数据
                    # 通用字段
                    password = item.get('password')
                    gender = item.get('gender')
                    grade = item.get('grade')
                    class_id = item.get('class_id')
                    
                    username = ''
                    real_name = ''
                    role_id = 1
                    
                    if import_type == 'student':
                        username = item.get('student_no')
                        real_name = item.get('stu_name')
                        role_id = 1
                    elif import_type == 'teacher':
                        username = item.get('teacher_no')
                        real_name = item.get('tea_name')
                        role_id = 2
                    
                    if not username or not password:
                        fail_count += 1
                        errors.append(f"第{index+1}行: 学号/工号或密码为空")
                        continue
                        
                    # 2. 插入 user 表
                    # 检查用户是否存在
                    cursor.execute("SELECT user_id FROM user WHERE username = %s", (username,))
                    existing_user = cursor.fetchone()
                    
                    if existing_user:
                        fail_count += 1
                        errors.append(f"第{index+1}行: 用户已存在 ({username})")
                        continue
                        
                    # 插入 user
                    cursor.execute(
                        "INSERT INTO user (username, password, role_id, real_name, create_time) VALUES (%s, %s, %s, %s, NOW())",
                        (username, password, role_id, real_name)
                    )
                    user_id = cursor.lastrowid
                    
                    # 3. 插入 student/teacher 表
                    if import_type == 'student':
                        cursor.execute(
                            "INSERT INTO student (user_id, student_no, stu_name, gender, grade, class_id) VALUES (%s, %s, %s, %s, %s, %s)",
                            (user_id, username, real_name, gender, grade, class_id)
                        )
                    elif import_type == 'teacher':
                        cursor.execute(
                            "INSERT INTO teacher (user_id, teacher_no, tea_name, gender, grade, class_id) VALUES (%s, %s, %s, %s, %s, %s)",
                            (user_id, username, real_name, gender, grade, class_id)
                        )
                        
                    success_count += 1
                    
                except Exception as inner_e:
                    fail_count += 1
                    errors.append(f"第{index+1}行: 导入失败 - {str(inner_e)}")
                    # 不回滚，继续处理下一条？或者整体回滚？
                    # 这里选择继续，但前面已经 begin 事务，如果中间出错不回滚可能会有问题
                    # 如果要支持部分成功，需要每条独立事务，或者在这里不抛出异常让外层 commit
                    # 但为了保证一致性，通常批量导入要么全成功要么全失败，或者记录失败的
                    # 这里简单处理：如果有异常，记录错误，继续循环（但 pymysql 的事务是连接级的）
                    # 如果某条 SQL 失败，事务可能会进入错误状态
                    print(f"Row error: {inner_e}")
        
        connection.commit()
        return jsonify({
            "success": True, 
            "msg": f"导入完成。成功: {success_count}, 失败: {fail_count}",
            "errors": errors
        }), 200
        
    except Exception as e:
        if 'connection' in locals() and connection.open:
            connection.rollback()
        print(f"批量导入失败: {e}")
        return jsonify({"success": False, "msg": f"服务器内部错误: {str(e)}"}), 500
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

@app.route('/api/v1/survey/submit', methods=['POST'])
def submit_survey():
    data = request.get_json()
    student_no = data.get('student_no')
    answers = data.get('answers')
    semester = data.get('semester')
    questionnaire_id = data.get('questionnaire_id')

    if not student_no or not answers:
        return jsonify({"success": False, "msg": "缺少必要参数"}), 400

    try:
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            # 1. 查找学生ID
            cursor.execute("SELECT student_id, user_id FROM student WHERE student_no = %s", (student_no,))
            student_res = cursor.fetchone()
            if not student_res:
                 return jsonify({"success": False, "msg": "学生记录未找到"}), 404
            
            real_student_id = student_res['student_id']
            user_id = student_res['user_id']

            # 2. 获取或创建问卷ID
            if not questionnaire_id:
                # 兼容旧逻辑：假设问卷标题固定
                title = "学生学习行为与成长特征量化调查问卷"
                cursor.execute("SELECT questionnaire_id FROM questionnaire WHERE title = %s AND semester = %s", (title, semester))
                questionnaire = cursor.fetchone()
                
                if questionnaire:
                    questionnaire_id = questionnaire['questionnaire_id']
                else:
                    # 创建新问卷
                    cursor.execute(
                        "INSERT INTO questionnaire (title, description, create_time, semester) VALUES (%s, %s, NOW(), %s)",
                        (title, "学生画像专用优化版", semester)
                    )
                    questionnaire_id = cursor.lastrowid

            # 3. 保存答卷
            # 将 answers 转换为 JSON 字符串
            answers_json = json.dumps(answers, ensure_ascii=False)
            
            cursor.execute(
                "INSERT INTO questionnaire_record (student_id, questionnaire_id, raw_result_json, submit_time) VALUES (%s, %s, %s, NOW())",
                (real_student_id, questionnaire_id, answers_json)
            )
        
        connection.commit()
        
        # 记录日志
        log_operation(student_no, "提交问卷", 1, user_id)
        
        return jsonify({"success": True, "msg": "提交成功"}), 200

    except Exception as e:
        print(f"提交问卷失败: {e}")
        # 尝试记录失败日志
        try:
            log_operation(student_no, "提交问卷", 0)
        except:
            pass
        return jsonify({"success": False, "msg": f"服务器内部错误: {str(e)}"}), 500
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

@app.route('/api/v1/import/score', methods=['POST'])
def import_score():
    data = request.get_json()
    score_list = data.get('data')
    
    if not score_list:
        return jsonify({"success": False, "msg": "数据不能为空"}), 400
        
    success_count = 0
    fail_count = 0
    errors = []
    
    try:
        connection = pymysql.connect(**DB_CONFIG)
        connection.begin()
        
        with connection.cursor() as cursor:
            for index, item in enumerate(score_list):
                try:
                    # 1. 解析数据
                    stu_name = item.get('stu_name')
                    course_id = item.get('course_id')
                    score = item.get('score')
                    semester = item.get('semester')
                    
                    if not stu_name or course_id is None or score is None:
                        fail_count += 1
                        errors.append(f"第{index+1}行: 姓名、课程ID或成绩为空")
                        continue
                        
                    # 2. 查询 student_id
                    cursor.execute("SELECT student_id FROM student WHERE stu_name = %s", (stu_name,))
                    student_res = cursor.fetchone()
                    
                    if not student_res:
                        fail_count += 1
                        errors.append(f"第{index+1}行: 未找到姓名为 '{stu_name}' 的学生")
                        continue
                        
                    student_id = student_res['student_id']
                    
                    # 3. 类型转换
                    try:
                        course_id = int(course_id)
                        score = float(score)
                    except ValueError:
                        fail_count += 1
                        errors.append(f"第{index+1}行: 课程ID或成绩格式错误")
                        continue
                        
                    # 4. 插入 score 表
                    insert_sql = """
                    INSERT INTO score (student_id, course_id, score, semester)
                    VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(insert_sql, (student_id, course_id, score, semester))
                    success_count += 1
                    
                except Exception as row_err:
                    fail_count += 1
                    errors.append(f"第{index+1}行出错: {str(row_err)}")
                    print(f"Row error: {row_err}")
                    
        connection.commit()
        connection.close()
        
        log_operation('admin', "导入课程成绩", 1)
        
        msg = f"成功导入 {success_count} 条数据"
        if fail_count > 0:
            msg += f"，失败 {fail_count} 条"
            if errors:
                msg += f" (首个错误: {errors[0]})"
                
        return jsonify({"success": True, "msg": msg}), 200
        
    except Exception as e:
        print(f"批量导入成绩失败: {e}")
        return jsonify({"success": False, "msg": f"服务器内部错误: {str(e)}"}), 500

@app.route('/api/v1/questionnaire/list', methods=['GET'])
def get_questionnaire_list():
    try:
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            # 查询所有问卷，按创建时间倒序排列
            sql = "SELECT * FROM questionnaire ORDER BY create_time DESC"
            cursor.execute(sql)
            result = cursor.fetchall()
            
            # 处理 datetime 对象，转为字符串
            for item in result:
                if item.get('create_time'):
                    item['create_time'] = item['create_time'].strftime('%Y-%m-%d %H:%M:%S')
                # content_structure 是 JSON 类型，pymysql 的 DictCursor 通常会自动处理，或者是字符串
                # 如果是字符串需要解析，如果是 dict 则不用
                # 检查一下 content_structure 类型
                if item.get('content_structure') and isinstance(item['content_structure'], str):
                     try:
                         item['content_structure'] = json.loads(item['content_structure'])
                     except:
                         pass
            
            return jsonify({"success": True, "data": result}), 200
    except Exception as e:
        print(f"获取问卷列表失败: {e}")
        return jsonify({"success": False, "msg": f"服务器内部错误: {str(e)}"}), 500

@app.route('/api/v1/import/survey', methods=['POST'])
def import_survey():
    data = request.get_json()
    survey_list = data.get('data')
    
    if not survey_list:
        return jsonify({"success": False, "msg": "数据不能为空"}), 400
        
    success_count = 0
    fail_count = 0
    errors = []
    
    try:
        connection = pymysql.connect(**DB_CONFIG)
        connection.begin()
        
        with connection.cursor() as cursor:
            for index, item in enumerate(survey_list):
                try:
                    # 1. 解析数据
                    title = item.get('title')
                    description = item.get('description')
                    semester = item.get('semester')
                    
                    if not title or not semester:
                        fail_count += 1
                        errors.append(f"第{index+1}行: 问卷标题或学期为空")
                        continue
                        
                    # 2. 插入 questionnaire 表
                    insert_sql = """
                    INSERT INTO questionnaire (title, description, semester)
                    VALUES (%s, %s, %s)
                    """
                    cursor.execute(insert_sql, (title, description, semester))
                    success_count += 1
                    
                except Exception as row_err:
                    fail_count += 1
                    errors.append(f"第{index+1}行出错: {str(row_err)}")
                    print(f"Row error: {row_err}")
                    
        connection.commit()
        connection.close()
        
        log_operation('admin', "导入问卷配置", 1)
        
        msg = f"成功导入 {success_count} 条数据"
        if fail_count > 0:
            msg += f"，失败 {fail_count} 条"
            if errors:
                msg += f" (首个错误: {errors[0]})"
                
        return jsonify({"success": True, "msg": msg}), 200
        
    except Exception as e:
        print(f"批量导入问卷配置失败: {e}")
        return jsonify({"success": False, "msg": f"服务器内部错误: {str(e)}"}), 500


@app.route('/api/v1/questionnaire/save', methods=['POST'])
def save_questionnaire():
    try:
        title = request.form.get('title')
        description = request.form.get('description')
        semester = request.form.get('semester')
        file = request.files.get('file')
        questionnaire_id = request.form.get('questionnaire_id')

        if not title or not semester:
             return jsonify({"success": False, "msg": "标题和学期不能为空"}), 400

        connection = pymysql.connect(**DB_CONFIG)
        try:
            with connection.cursor() as cursor:
                # 检查同名问卷
                if questionnaire_id:
                    # 更新时，检查除了当前ID之外是否有同名
                    check_sql = "SELECT count(*) as count FROM questionnaire WHERE title = %s AND questionnaire_id != %s"
                    cursor.execute(check_sql, (title, questionnaire_id))
                else:
                    # 新增时，检查是否有同名
                    check_sql = "SELECT count(*) as count FROM questionnaire WHERE title = %s"
                    cursor.execute(check_sql, (title,))
                
                if cursor.fetchone()['count'] > 0:
                    return jsonify({"success": False, "msg": "问卷名称已存在，请使用其他名称"}), 400
        finally:
            connection.close()

        content_structure = None
        if file:
            filename = file.filename.lower() if file.filename else ''
            try:
                if filename.endswith('.xlsx') or filename.endswith('.xls'):
                    # Parse Excel
                    wb = openpyxl.load_workbook(file) # type: ignore
                    sheet = wb.active
                    rows = list(sheet.iter_rows(values_only=True)) # type: ignore
                    
                    if not rows:
                         return jsonify({"success": False, "msg": "Excel文件为空"}), 400
                         
                    # Find headers
                    header = rows[0]
                    # Clean headers (strip spaces)
                    header = [str(h).strip() if h else '' for h in header]
                    
                    try:
                        # Try to find exact matches or partial matches if needed
                        # Assuming exact match based on user description
                        idx_id = -1
                        idx_text = -1
                        idx_type = -1
                        
                        for i, h in enumerate(header):
                            if '题目编号' in h:
                                idx_id = i
                            elif '题目类型' in h:
                                idx_type = i
                            elif '题目' in h: # Check this last as '题目' is substring of others
                                idx_text = i
                        
                        if idx_id == -1 or idx_text == -1 or idx_type == -1:
                             return jsonify({"success": False, "msg": "Excel表头缺失，需包含：题目编号、题目、题目类型"}), 400
                             
                        parsed_data = []
                        for row in rows[1:]:
                            # Skip if row is shorter than max index
                            max_idx = max(idx_id, idx_text, idx_type)
                            if len(row) <= max_idx:
                                continue
                                
                            q_id = row[idx_id]
                            q_text = row[idx_text]
                            q_type = row[idx_type]
                            
                            if not q_text: # Skip if question text is empty
                                continue
                                
                            parsed_data.append({
                                'id': str(q_id) if q_id is not None else '',
                                'question': str(q_text) if q_text is not None else '',
                                'type': str(q_type).strip() if q_type is not None else ''
                            })
                            
                        content_structure = json.dumps(parsed_data, ensure_ascii=False)
                        
                    except Exception as e:
                        print(f"Excel parsing logic error: {e}")
                        return jsonify({"success": False, "msg": f"解析Excel逻辑错误: {str(e)}"}), 400
                        
                elif filename.endswith('.docx'):
                    # Parse Word
                    doc = docx.Document(file) # type: ignore
                    paragraphs = []
                    for para in doc.paragraphs:
                        text = para.text.strip()
                        if text:
                            paragraphs.append(text)
                    content_structure = json.dumps(paragraphs, ensure_ascii=False)
                else:
                    return jsonify({"success": False, "msg": "不支持的文件格式"}), 400
            except Exception as e:
                return jsonify({"success": False, "msg": f"文件解析失败: {str(e)}"}), 400
        
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            if questionnaire_id:
                # Update
                update_sql = "UPDATE questionnaire SET title=%s, description=%s, semester=%s"
                params = [title, description, semester]
                if content_structure:
                    update_sql += ", content_structure=%s"
                    params.append(content_structure)
                update_sql += " WHERE questionnaire_id=%s"
                params.append(questionnaire_id)
                cursor.execute(update_sql, params)
            else:
                # Insert
                if content_structure is None:
                    content_structure = '[]'
                
                insert_sql = "INSERT INTO questionnaire (title, description, semester, content_structure, create_time) VALUES (%s, %s, %s, %s, NOW())"
                cursor.execute(insert_sql, (title, description, semester, content_structure))
        
        connection.commit()
        connection.close()
        
        op_type = "更新问卷" if questionnaire_id else "新增问卷"
        log_operation('admin', op_type, 1) # Assuming admin user
        
        return jsonify({"success": True, "msg": "保存成功"}), 200

    except Exception as e:
        print(f"保存问卷失败: {e}")
        return jsonify({"success": False, "msg": f"服务器内部错误: {str(e)}"}), 500

@app.route('/api/v1/questionnaire/delete', methods=['POST'])
def delete_questionnaire():
    try:
        data = request.get_json()
        ids = data.get('ids')
        
        if not ids or not isinstance(ids, list):
            return jsonify({"success": False, "msg": "参数错误，请选择要删除的问卷"}), 400
            
        # Convert ids to list of strings to prevent SQL injection if they were weird types, 
        # though pymysql handles list with IN clause well if parameterized.
        # But pymysql doesn't support list directly in %s for IN clause in a simple way 
        # without building the string manually or using specific execute_many which is for multiple queries.
        # Standard way: construct placeholder string
        
        placeholders = ', '.join(['%s'] * len(ids))
        sql = f"DELETE FROM questionnaire WHERE questionnaire_id IN ({placeholders})"
        
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            cursor.execute(sql, ids)
            
        connection.commit()
        connection.close()
        
        log_operation('admin', "批量删除问卷", 1)
        
        return jsonify({"success": True, "msg": "删除成功"}), 200
        
    except Exception as e:
        print(f"删除问卷失败: {e}")
        return jsonify({"success": False, "msg": f"服务器内部错误: {str(e)}"}), 500

@app.route('/api/v1/user/list', methods=['GET'])
def get_user_list():
    try:
        users_list = []
        
        # 1. 获取所有学生
        student_sql = """
        SELECT s.student_no as id, s.stu_name as name, s.gender, s.grade, c.class_name, u.password
        FROM student s
        LEFT JOIN class c ON s.class_id = c.class_id
        LEFT JOIN user u ON s.user_id = u.user_id
        """
        students = query_db(student_sql)
        if students:
            for s in students:
                # 计算学生年龄
                age = 16 # 默认高一
                if s['grade'] == '高二':
                    age = 17
                elif s['grade'] == '高三':
                    age = 18
                
                users_list.append({
                    "id": s['id'],
                    "name": s['name'],
                    "gender": s['gender'],
                    "age": age,
                    "grade": s['grade'],
                    "class": s['class_name'],
                    "role": "student", # 前端筛选用
                    "password": s['password']
                })

        # 2. 获取所有教师
        teacher_sql = """
        SELECT t.teacher_no as id, t.tea_name as name, t.gender, t.grade, c.class_name, u.password
        FROM teacher t
        LEFT JOIN class c ON t.class_id = c.class_id
        LEFT JOIN user u ON t.user_id = u.user_id
        """
        teachers = query_db(teacher_sql)
        if teachers:
            for t in teachers:
                # 计算教师年龄 [22, 65)
                age = random.randint(22, 64)
                
                users_list.append({
                    "id": t['id'],
                    "name": t['name'],
                    "gender": t['gender'],
                    "age": age,
                    "grade": t['grade'],
                    "class": t['class_name'],
                    "role": "teacher", # 前端筛选用
                    "password": t['password']
                })
                
        return jsonify({"success": True, "data": users_list}), 200
        
    except Exception as e:
        print(f"获取用户列表失败: {e}")
        return jsonify({"success": False, "msg": "服务器内部错误"}), 500

if __name__ == '__main__':
    print(f"前端静态资源目录: {static_dir}")
    print(f"前端模板目录: {dist_dir}")

    # 测试数据库连接
    test_db_connection()
    
    app.run(host='0.0.0.0', port=5000, debug=True)
