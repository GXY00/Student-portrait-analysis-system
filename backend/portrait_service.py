import os
from tag_rule_engine import TagRuleEngine
from class_tag_rule_engine import ClassTagRuleEngine

class PortraitService:
    @staticmethod
    def generate_student_portrait(student_id, db_config, base_dir):
        """
        Generates portrait (tags) for a single student.
        :param student_id: Student ID
        :param db_config: Database configuration dictionary
        :param base_dir: Base directory to locate rule file
        """
        try:
            rule_path = os.path.join(base_dir, 'stu_rule.json')
            if not os.path.exists(rule_path):
                 return False, f"Rule file not found: {rule_path}"

            engine = TagRuleEngine(db_config, rule_file=rule_path)
            
            # Execute rule engine for specific student
            engine.execute_all(target_student_id=student_id)
            
            engine.close()
            return True, "画像生成成功"
        except Exception as e:
            print(f"Error generating portrait for student {student_id}: {e}")
            return False, str(e)

    @staticmethod
    def generate_class_portrait(class_id, db_config, base_dir):
        """
        Generates portrait (tags) for a single class.
        :param class_id: Class ID
        :param db_config: Database configuration dictionary
        :param base_dir: Base directory to locate rule file
        """
        try:
            rule_path = os.path.join(base_dir, 'class_rule.json')
            if not os.path.exists(rule_path):
                 return False, f"Rule file not found: {rule_path}"

            engine = ClassTagRuleEngine(db_config, rule_file=rule_path)
            
            # Execute rule engine for specific class
            engine.execute_all(class_id=class_id)
            
            engine.close()
            return True, "班级画像生成成功"
        except Exception as e:
            print(f"Error generating portrait for class {class_id}: {e}")
            return False, str(e)
