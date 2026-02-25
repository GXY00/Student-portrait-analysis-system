import json
import pymysql
from datetime import datetime

class TagRuleEngine:

    def __init__(self, db_config, rule_file='stu_rule.json'):
        self.conn = pymysql.connect(**db_config)
        self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)

        with open(rule_file, 'r', encoding='utf-8') as f:
            self.rule_config = json.load(f)

    # ===============================
    # 主入口
    # ===============================
    def execute_all(self, student_id=None):
        self.sync_tags()
        execution_order = self.rule_config["execution_order"]
        tag_map = {tag["tag_name"]: tag for tag in self.rule_config["tags"]}

        for tag_name in execution_order:
            tag = tag_map[tag_name]
            # print(f"正在生成标签: {tag_name}")
            self.execute_tag(tag, student_id)

        print("全部标签生成完成")
        self.conn.commit()

    # ===============================
    # 同步标签定义到 tag 表
    # ===============================
    def sync_tags(self):
        tags = self.rule_config["tags"]
        for tag in tags:
            tag_name = tag["tag_name"]
            tag_type = tag["tag_type"]
            tag_level = tag["tag_level"]
            description = tag["description"]

            # 检查标签是否存在
            self.cursor.execute("SELECT tag_id FROM tag WHERE tag_name=%s", (tag_name,))
            existing = self.cursor.fetchone()

            if existing:
                # 更新
                self.cursor.execute("""
                    UPDATE tag 
                    SET tag_type=%s, tag_level=%s, description=%s 
                    WHERE tag_name=%s
                """, (tag_type, tag_level, description, tag_name))
            else:
                # 插入
                self.cursor.execute("""
                    INSERT INTO tag (tag_name, tag_type, tag_level, description)
                    VALUES (%s, %s, %s, %s)
                """, (tag_name, tag_type, tag_level, description))
        self.conn.commit()

    # ===============================
    # 执行单个标签
    # ===============================
    def execute_tag(self, tag, student_id=None):
        rule = tag["rule"]
        rule_type = rule["type"]

        if rule_type == "aggregate":
            self.handle_aggregate(tag, rule, student_id)

        elif rule_type == "formula":
            self.handle_formula(tag, rule, student_id)

        elif rule_type == "threshold":
            self.handle_threshold(tag, rule, student_id)
            
        elif rule_type == "questionnaire_score":
            self.handle_questionnaire_score(tag, rule, student_id)
            
        elif rule_type == "questionnaire_score_with_numeric":
            self.handle_questionnaire_score_with_numeric(tag, rule, student_id)
            
        elif rule_type == "questionnaire_preference":
            self.handle_questionnaire_preference(tag, rule, student_id)
            
        elif rule_type == "questionnaire_numeric":
            self.handle_questionnaire_numeric(tag, rule, student_id)

    # ===============================
    # 问卷评分类型 (questionnaire_score)
    # ===============================
    def handle_questionnaire_score(self, tag, rule, student_id=None):
        title = rule["questionnaire_title"]
        questions = rule["questions"]
        
        # 获取问卷记录
        records = self.get_questionnaire_records(title, student_id)
        
        for s_id, raw_json in records.items():
            total_score = 0
            count = 0
            
            # 解析结果
            try:
                result_map = json.loads(raw_json) if isinstance(raw_json, str) else raw_json
                if not result_map:
                    continue
                    
                for q in questions:
                    key = q["key"]
                    val = result_map.get(key)
                    if val is not None:
                        # 尝试转为数字
                        try:
                            score = float(val)
                            # 处理反向计分 (假设5分制: 1->5, 5->1 => 6-val)
                            if q.get("reverse", False):
                                score = 6 - score
                            total_score += score
                            count += 1
                        except ValueError:
                            pass
                
                if count > 0:
                    avg_score = total_score / count
                    self.save_student_tag(s_id, tag["tag_name"], avg_score)
                    
            except Exception as e:
                print(f"Error parsing record for student {s_id}: {e}")

    # ===============================
    # 问卷评分+数值类型 (questionnaire_score_with_numeric)
    # ===============================
    def handle_questionnaire_score_with_numeric(self, tag, rule, student_id=None):
        title = rule["questionnaire_title"]
        likert_keys = rule["likert_questions"]
        numeric_keys = rule["numeric_fields"]
        weights = rule["weights"]
        
        records = self.get_questionnaire_records(title, student_id)
        
        for s_id, raw_json in records.items():
            try:
                result_map = json.loads(raw_json) if isinstance(raw_json, str) else raw_json
                if not result_map:
                    continue
                
                # 计算量表题均分
                likert_sum = 0
                likert_count = 0
                for key in likert_keys:
                    val = result_map.get(key)
                    if val is not None:
                        try:
                            likert_sum += float(val)
                            likert_count += 1
                        except ValueError:
                            pass
                
                likert_avg = (likert_sum / likert_count) if likert_count > 0 else 0
                
                # 计算数值题均分
                numeric_sum = 0
                numeric_count = 0
                for key in numeric_keys:
                    val = result_map.get(key)
                    if val is not None:
                        try:
                            numeric_sum += float(val)
                            numeric_count += 1
                        except ValueError:
                            pass
                            
                numeric_avg = (numeric_sum / numeric_count) if numeric_count > 0 else 0
                
                # 加权计算
                final_score = (likert_avg * weights.get("likert", 0.6)) + (numeric_avg * weights.get("numeric", 0.4))
                self.save_student_tag(s_id, tag["tag_name"], final_score)
                
            except Exception as e:
                print(f"Error parsing record for student {s_id}: {e}")

    # ===============================
    # 问卷偏好类型 (questionnaire_preference)
    # ===============================
    def handle_questionnaire_preference(self, tag, rule, student_id=None):
        title = rule["questionnaire_title"]
        mapping = rule["mapping"] # {"Q8": "独立学习型", ...}
        
        records = self.get_questionnaire_records(title, student_id)
        
        for s_id, raw_json in records.items():
            try:
                result_map = json.loads(raw_json) if isinstance(raw_json, str) else raw_json
                if not result_map:
                    continue
                
                # 找出得分最高的选项
                max_score = -1
                best_label = None
                
                for key, label in mapping.items():
                    val = result_map.get(key)
                    if val is not None:
                        try:
                            score = float(val)
                            if score > max_score:
                                max_score = score
                                best_label = label
                        except ValueError:
                            pass
                
                if best_label:
                    self.save_student_tag(s_id, tag["tag_name"], best_label)
                    
            except Exception as e:
                print(f"Error parsing record for student {s_id}: {e}")

    # ===============================
    # 问卷数值直接提取 (questionnaire_numeric)
    # ===============================
    def handle_questionnaire_numeric(self, tag, rule, student_id=None):
        title = rule["questionnaire_title"]
        field = rule["field"]
        
        records = self.get_questionnaire_records(title, student_id)
        
        for s_id, raw_json in records.items():
            try:
                result_map = json.loads(raw_json) if isinstance(raw_json, str) else raw_json
                if not result_map:
                    continue
                
                val = result_map.get(field)
                if val is not None:
                    # 尝试转为数字，确保存储为数值形式
                    try:
                        num_val = float(val)
                        self.save_student_tag(s_id, tag["tag_name"], num_val)
                    except ValueError:
                        self.save_student_tag(s_id, tag["tag_name"], val)
                        
            except Exception as e:
                print(f"Error parsing record for student {s_id}: {e}")

    # ===============================
    # 辅助方法：获取问卷记录
    # ===============================
    def get_questionnaire_records(self, title, student_id=None):
        # 1. 查找问卷ID
        self.cursor.execute("SELECT questionnaire_id FROM questionnaire WHERE title=%s", (title,))
        q_row = self.cursor.fetchone()
        if not q_row:
            print(f"Warning: Questionnaire '{title}' not found.")
            return {}
            
        qid = q_row["questionnaire_id"]
        
        # 2. 获取所有记录
        sql = """
            SELECT student_id, raw_result_json 
            FROM questionnaire_record 
            WHERE questionnaire_id=%s
        """
        params = [qid]
        if student_id:
            sql += " AND student_id=%s"
            params.append(student_id)
        
        sql += " ORDER BY submit_time ASC"
        
        self.cursor.execute(sql, params)
        rows = self.cursor.fetchall()
        
        # 使用字典覆盖，保留最新的提交
        records = {}
        for row in rows:
            records[row["student_id"]] = row["raw_result_json"]
            
        return records


    # ===============================
    # aggregate 类型
    # ===============================
    def handle_aggregate(self, tag, rule, student_id=None):
        where_clause = ""
        params = []
        if student_id:
            where_clause = "WHERE student_id = %s"
            params.append(student_id)

        sql = f"""
            SELECT student_id, {rule['aggregate_func'].upper()}({rule['field']}) as value
            FROM {rule['source_table']}
            {where_clause}
            GROUP BY student_id
        """

        self.cursor.execute(sql, params)
        results = self.cursor.fetchall()

        for row in results:
            self.save_student_tag(row["student_id"], tag["tag_name"], row["value"])

    # ===============================
    # formula 类型
    # ===============================
    def handle_formula(self, tag, rule, student_id=None):
        operations = rule["operations"]
        operator = rule["operator"]

        sql_parts = []
        for op in operations:
            sql_parts.append(f"{op['func'].upper()}({op['field']})")
        
        where_clause = ""
        params = []
        if student_id:
            where_clause = "WHERE student_id = %s"
            params.append(student_id)

        sql = f"""
            SELECT student_id, 
            ({sql_parts[0]} {operator} {sql_parts[1]}) as value
            FROM {rule['source_table']}
            {where_clause}
            GROUP BY student_id
        """

        self.cursor.execute(sql, params)
        results = self.cursor.fetchall()

        for row in results:
            self.save_student_tag(row["student_id"], tag["tag_name"], row["value"])

    # ===============================
    # threshold 类型
    # ===============================
    def handle_threshold(self, tag, rule, student_id=None):
        base_tag = rule["base_tag"]

        # 获取tag_id
        self.cursor.execute("SELECT tag_id FROM tag WHERE tag_name=%s", (base_tag,))
        base_tag_row = self.cursor.fetchone()
        if not base_tag_row:
            return

        base_tag_id = base_tag_row["tag_id"]

        # 获取学生原始值
        sql = """
            SELECT student_id, tag_value
            FROM student_tag
            WHERE tag_id=%s
        """
        params = [base_tag_id]
        if student_id:
            sql += " AND student_id=%s"
            params.append(student_id)

        self.cursor.execute(sql, params)
        students = self.cursor.fetchall()

        for stu in students:
            value = float(stu["tag_value"])
            label = self.match_threshold(value, rule["rules"])
            self.save_student_tag(stu["student_id"], tag["tag_name"], label)

    # ===============================
    # 匹配阈值规则
    # ===============================
    def match_threshold(self, value, rules):
        for r in rules:
            if "min" in r and value >= r["min"]:
                return r["label"]
            if "max" in r and value <= r["max"]:
                return r["label"]
        return None

    # ===============================
    # 保存 student_tag
    # ===============================
    def save_student_tag(self, student_id, tag_name, value):
        # 获取tag_id
        self.cursor.execute("SELECT tag_id FROM tag WHERE tag_name=%s", (tag_name,))
        tag_row = self.cursor.fetchone()
        if not tag_row:
            return

        tag_id = tag_row["tag_id"]

        # 插入或更新
        self.cursor.execute("""
            INSERT INTO student_tag (student_id, tag_id, tag_value, update_time)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            tag_value=VALUES(tag_value),
            update_time=VALUES(update_time)
        """, (student_id, tag_id, str(value), datetime.now()))

    # ===============================
    # 关闭连接
    # ===============================
    def close(self):
        self.cursor.close()
        self.conn.close()
