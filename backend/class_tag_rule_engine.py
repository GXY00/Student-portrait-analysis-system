
import json
import pymysql
import statistics
from datetime import datetime

class ClassTagRuleEngine:
    """
    班级画像规则引擎
    支持规则类型：
    - class_aggregate
    - class_distribution
    - class_risk_ratio
    - threshold
    """

    def __init__(self, db_config, rule_file='class_rule.json'):
        self.conn = pymysql.connect(**db_config)
        self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        
        with open(rule_file, 'r', encoding='utf-8') as f:
            self.rule_config = json.load(f)

    def execute_all(self, class_id=None):
        """
        执行所有班级标签生成规则
        :param class_id: 指定班级ID，若为None则计算所有班级
        """
        execution_order = self.rule_config["execution_order"]
        tag_map = {tag["tag_name"]: tag for tag in self.rule_config["tags"]}

        # 获取需要计算的班级列表
        if class_id:
            class_ids = [class_id]
        else:
            self.cursor.execute("SELECT class_id FROM class")
            class_ids = [row['class_id'] for row in self.cursor.fetchall()]

        for cid in class_ids:
            # print(f"正在生成班级 {cid} 的标签...")
            for tag_name in execution_order:
                if tag_name not in tag_map:
                    continue
                tag = tag_map[tag_name]
                try:
                    value = self.execute_rule(tag["rule"], cid)
                    if value is not None:
                        self.save_class_tag(cid, tag_name, value)
                except Exception as e:
                    print(f"Error calculating tag {tag_name} for class {cid}: {e}")
        
        self.conn.commit()
        print("班级标签生成完成")

    def execute_rule(self, rule, class_id):
        rule_type = rule.get("type")

        if rule_type == "class_aggregate":
            return self._class_aggregate(rule, class_id)

        elif rule_type == "class_distribution":
            return self._class_distribution(rule, class_id)

        elif rule_type == "class_risk_ratio":
            return self._class_risk_ratio(rule, class_id)

        elif rule_type == "threshold":
            return self._class_threshold(rule, class_id)

        else:
            raise ValueError(f"未知班级规则类型: {rule_type}")

    # =====================================================
    # 工具：获取班级所有学生ID
    # =====================================================
    def _get_class_student_ids(self, class_id):
        sql = "SELECT student_id FROM student WHERE class_id = %s"
        self.cursor.execute(sql, (class_id,))
        return [row['student_id'] for row in self.cursor.fetchall()]

    # =====================================================
    # 工具：获取某标签的学生值列表
    # =====================================================
    def _get_student_tag_values(self, student_ids, tag_name):
        if not student_ids:
            return []
        
        # 这里的 student_tag 表是用 tag_id 关联的，所以先要获取 tag_id
        self.cursor.execute("SELECT tag_id FROM tag WHERE tag_name = %s", (tag_name,))
        tag_row = self.cursor.fetchone()
        if not tag_row:
            return []
        tag_id = tag_row['tag_id']

        format_strings = ','.join(['%s'] * len(student_ids))
        sql = f"""
            SELECT tag_value
            FROM student_tag
            WHERE student_id IN ({format_strings})
            AND tag_id = %s
        """
        params = list(student_ids) + [tag_id]
        
        self.cursor.execute(sql, params)
        result = self.cursor.fetchall()

        values = []
        for row in result:
            try:
                values.append(float(row['tag_value']))
            except (ValueError, TypeError):
                pass
        return values

    # =====================================================
    # 1️⃣ 班级聚合
    # =====================================================
    def _class_aggregate(self, rule, class_id):
        base_tag = rule["base_tag"]
        func = rule["aggregate_func"]

        student_ids = self._get_class_student_ids(class_id)
        values = self._get_student_tag_values(student_ids, base_tag)

        if not values:
            return 0

        if func == "avg":
            return round(sum(values) / len(values), 2)

        elif func == "std":
            if len(values) < 2:
                return 0
            return round(statistics.stdev(values), 2)

        elif func == "max":
            return max(values)

        elif func == "min":
            return min(values)

        else:
            raise ValueError(f"不支持的聚合函数: {func}")

    # =====================================================
    # 2️⃣ 分布统计
    # =====================================================
    def _class_distribution(self, rule, class_id):
        base_tag = rule["base_tag"]
        student_ids = self._get_class_student_ids(class_id)

        if not student_ids:
            return {}
            
        # 获取 tag_id
        self.cursor.execute("SELECT tag_id FROM tag WHERE tag_name = %s", (base_tag,))
        tag_row = self.cursor.fetchone()
        if not tag_row:
            return {}
        tag_id = tag_row['tag_id']

        format_strings = ','.join(['%s'] * len(student_ids))
        sql = f"""
            SELECT tag_value
            FROM student_tag
            WHERE student_id IN ({format_strings})
            AND tag_id = %s
        """
        params = list(student_ids) + [tag_id]
        
        self.cursor.execute(sql, params)
        result = self.cursor.fetchall()

        distribution = {}
        for row in result:
            label = row['tag_value']
            distribution[label] = distribution.get(label, 0) + 1

        return distribution

    # =====================================================
    # 3️⃣ 风险比例
    # =====================================================
    def _class_risk_ratio(self, rule, class_id):
        base_tag = rule["base_tag"]
        operator = rule["operator"]
        threshold = rule["threshold"]

        student_ids = self._get_class_student_ids(class_id)
        values = self._get_student_tag_values(student_ids, base_tag)

        if not values:
            return 0

        risk_count = 0
        for value in values:
            if operator == "<" and value < threshold:
                risk_count += 1
            elif operator == ">" and value > threshold:
                risk_count += 1
            elif operator == "<=" and value <= threshold:
                risk_count += 1
            elif operator == ">=" and value >= threshold:
                risk_count += 1
            elif operator == "==" and value == threshold:
                risk_count += 1

        ratio = risk_count / len(values)
        return round(ratio, 4)

    # =====================================================
    # 4️⃣ 班级阈值判断（等级）
    # =====================================================
    def _class_threshold(self, rule, class_id):
        base_tag = rule["base_tag"]
        rules = rule["rules"]

        # 先获取该班级的 base_tag 数值
        # 注意：这里调用的是 _get_class_tag_value，即从 class_tag 表获取
        value = self._get_class_tag_value(class_id, base_tag)

        if value is None:
            return None

        for item in rules:
            if "min" in item and value >= item["min"]:
                return item["label"] # 修正逻辑错误：只要满足一个条件就返回
            elif "max" in item and value <= item["max"]:
                return item["label"]

        return None

    # =====================================================
    # 工具：获取已计算的班级标签值
    # =====================================================
    def _get_class_tag_value(self, class_id, tag_name):
        sql = """
            SELECT tag_value
            FROM class_tag
            WHERE class_id = %s
            AND tag_name = %s
        """
        self.cursor.execute(sql, (class_id, tag_name))
        result = self.cursor.fetchone()

        if not result:
            return None

        # tag_value 在 class_tag 中是 json 类型，pymysql 如果配置了 decode_responses=True 可能会自动转，
        # 但通常这里取出的是字符串或 dict/list (如果是json字段)
        # 根据之前的 describe output, Type 是 json。
        # PyMySQL 默认可能返回字符串或 Python 对象（取决于驱动版本和配置）。
        # 我们假设它返回的是反序列化后的对象或者 json 字符串。
        val = result['tag_value']
        
        # 尝试转换为 float
        try:
            # 如果是 json 字符串，先 load
            if isinstance(val, str):
                try:
                    val = json.loads(val)
                except:
                    pass
            return float(val)
        except (ValueError, TypeError):
            return val

    # =====================================================
    # 保存 class_tag
    # =====================================================
    def save_class_tag(self, class_id, tag_name, value):
        # value 需要转换为 json 格式存储
        json_value = json.dumps(value, ensure_ascii=False)
        
        # 检查是否存在
        sql_check = "SELECT id FROM class_tag WHERE class_id=%s AND tag_name=%s"
        self.cursor.execute(sql_check, (class_id, tag_name))
        existing = self.cursor.fetchone()
        
        if existing:
            sql_update = """
                UPDATE class_tag 
                SET tag_value=%s, update_time=%s 
                WHERE id=%s
            """
            self.cursor.execute(sql_update, (json_value, datetime.now(), existing['id']))
        else:
            sql_insert = """
                INSERT INTO class_tag (class_id, tag_name, tag_value, update_time)
                VALUES (%s, %s, %s, %s)
            """
            self.cursor.execute(sql_insert, (class_id, tag_name, json_value, datetime.now()))

    def close(self):
        self.cursor.close()
        self.conn.close()
