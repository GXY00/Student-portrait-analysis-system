import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import pymysql
import json

class ClusterAnalyzer:
    def __init__(self, db_config):
        self.db_config = db_config

    def get_connection(self):
        return pymysql.connect(**self.db_config)

    def perform_clustering(self, task_desc, feature_tags, k_value=4):
        """
        执行聚类分析
        :param task_desc: 任务描述
        :param feature_tags: 参与聚类的标签名称列表
        :param k_value: 聚类簇数
        """
        # 1. 创建任务记录
        task_id = self._create_task(task_desc, feature_tags, k_value)

        # 2. 获取数据
        df = self._fetch_data(feature_tags)
        if df.empty:
            return {"status": "error", "message": "未找到指定标签的数据"}

        # 3. 数据预处理
        # 透视表: index=student_id, columns=tag_name, values=tag_value
        # 注意: tag_value 是 VARCHAR，需要转换为 float
        try:
            # 过滤掉非数值的值
            df['tag_value'] = pd.to_numeric(df['tag_value'], errors='coerce')
            df = df.dropna(subset=['tag_value'])
            
            df_pivot = df.pivot(index='student_id', columns='tag_name', values='tag_value')
        except Exception as e:
             return {"status": "error", "message": f"数据转换失败: {str(e)}"}
        
        # 填充缺失值 (使用均值填充)
        df_pivot = df_pivot.fillna(df_pivot.mean())
        
        # 如果列数少于请求的特征数，说明某些标签没有数据
        if len(df_pivot.columns) < len(feature_tags):
            missing = set(feature_tags) - set(df_pivot.columns)
            # 可以选择报错或者继续，这里选择继续但记录警告
            print(f"Warning: Missing data for tags: {missing}")

        # 标准化
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(df_pivot)

        # 4. 执行聚类
        kmeans = KMeans(n_clusters=k_value, random_state=42)
        clusters = kmeans.fit_predict(X_scaled)
        
        # 5. 保存结果
        self._save_results(task_id, df_pivot.index, clusters)
        
        # 6. 结果分析 (计算簇中心)
        # 将聚类结果加回 DataFrame
        df_pivot['cluster'] = clusters
        
        # 计算每个簇的中心点（原始值，便于理解）
        centroids = df_pivot.groupby('cluster').mean()
        
        # 计算每个簇的学生数量
        counts = df_pivot['cluster'].value_counts().sort_index()
        
        # 7. PCA 降维用于可视化 (2D)
        # 如果特征数大于2才需要降维，否则直接用
        if X_scaled.shape[1] > 2:
            pca = PCA(n_components=2)
            coords = pca.fit_transform(X_scaled)
        else:
            # 如果特征本身就是2维或1维，直接使用（或者补0）
            coords = X_scaled[:, :2] if X_scaled.shape[1] >= 2 else np.hstack((X_scaled, np.zeros((X_scaled.shape[0], 1))))

        # 准备返回结果
        result = {
            "task_id": task_id,
            "features": feature_tags,
            "k_value": k_value,
            "clusters_info": [],
            "points": []
        }
        
        # 组装簇信息
        for cluster_id in centroids.index:
            result["clusters_info"].append({
                "cluster_id": int(cluster_id),
                "count": int(counts.get(cluster_id, 0)),
                "features": centroids.loc[cluster_id].to_dict()
            })
        
        # 组装散点图数据
        for i, student_id in enumerate(df_pivot.index):
            result["points"].append({
                "student_id": int(student_id),
                "x": float(coords[i, 0]),
                "y": float(coords[i, 1]),
                "cluster": int(clusters[i])
            })
            
        return {"status": "success", "data": result}

    def _create_task(self, desc, features, k):
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "INSERT INTO cluster_task (task_desc, feature_desc, k_value) VALUES (%s, %s, %s)"
                cursor.execute(sql, (desc, ",".join(features), k))
                conn.commit()
                return cursor.lastrowid
        finally:
            conn.close()

    def _fetch_data(self, tags):
        conn = self.get_connection()
        try:
            # 需要 join student_tag 和 tag 表
            placeholders = ','.join(['%s'] * len(tags))
            sql = f"""
                SELECT st.student_id, t.tag_name, st.tag_value
                FROM student_tag st
                JOIN tag t ON st.tag_id = t.tag_id
                WHERE t.tag_name IN ({placeholders})
            """
            return pd.read_sql(sql, conn, params=tags) # type: ignore
        finally:
            conn.close()

    def _save_results(self, task_id, student_ids, clusters):
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                values = []
                for sid, cluster in zip(student_ids, clusters):
                    values.append((task_id, sid, int(cluster)))
                
                sql = "INSERT INTO cluster_result (task_id, student_id, cluster_label) VALUES (%s, %s, %s)"
                cursor.executemany(sql, values)
                conn.commit()
        finally:
            conn.close()
