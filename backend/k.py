import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import pymysql

# 设置中文字体，防止图表乱码 (针对Windows系统)
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    #"password": "your_password", 
    "database": "stuportrait", 
    "port": 3306,
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}

def fetch_all_data():
    conn = pymysql.connect(**DB_CONFIG)
    try:
        # 获取所有学生的定量标签用于评估
        sql = """
            SELECT st.student_id, t.tag_name, st.tag_value
            FROM student_tag st
            JOIN tag t ON st.tag_id = t.tag_id
            WHERE t.tag_type = '定量'
        """
        with conn.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
        df = pd.DataFrame(rows)
        return df
    finally:
        conn.close()

def evaluate_k():
    print("正在获取数据...")
    df = fetch_all_data()
    
    # 数据预处理 (与业务代码一致)
    df['tag_value'] = pd.to_numeric(df['tag_value'], errors='coerce')
    df = df.dropna(subset=['tag_value'])
    df_pivot = df.pivot(index='student_id', columns='tag_name', values='tag_value')
    df_pivot = df_pivot.fillna(df_pivot.mean())
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_pivot)
    
    n_samples = len(X_scaled)
    print(f"参与评估的样本数（学生数）: {n_samples}")
    
    max_k = min(10, n_samples - 1)
    if max_k < 2:
        print("错误: 数据量过少！轮廓系数评估至少需要 3 个样本。请先在系统中导入更多学生数据并生成定量标签。")
        return

    sse = []
    silhouette_scores = []
    
    # 根据样本数量动态调整评估范围，最大不超过 K=10
    k_range = range(2, max_k + 1)
    
    print(f"正在计算不同 K 值下的指标 (K=2 到 {max_k})...")
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42)
        clusters = kmeans.fit_predict(X_scaled)
        
        # 记录 SSE (误差平方和)
        sse.append(kmeans.inertia_)
        
        # 记录轮廓系数
        score = silhouette_score(X_scaled, clusters)
        silhouette_scores.append(score)
        
    # ================= 绘制图表 =================
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # 绘制 SSE (手肘法)
    color = 'tab:blue'
    ax1.set_xlabel('聚类簇数 K', fontsize=12)
    ax1.set_ylabel('误差平方和 (SSE)', color=color, fontsize=12)
    ax1.plot(k_range, sse, marker='o', color=color, linewidth=2)
    ax1.tick_params(axis='y', labelcolor=color)

    # 实例化第二个 Y 轴，共享同一个 X 轴
    ax2 = ax1.twinx()  
    color = 'tab:orange'
    ax2.set_ylabel('平均轮廓系数', color=color, fontsize=12)  
    ax2.plot(k_range, silhouette_scores, marker='s', color=color, linewidth=2, linestyle='--')
    ax2.tick_params(axis='y', labelcolor=color)

    plt.title('K-Means 聚类 K 值评估图 (手肘法与轮廓系数)', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.6)
    
    # 保存图表，可直接用于论文
    plt.savefig('k_value_evaluation.png', dpi=300, bbox_inches='tight')
    print("评估完成！图表已保存为当前目录下的 k_value_evaluation.png")
    # plt.show() # 如果在无界面环境下运行，请注释掉此行

if __name__ == "__main__":
    evaluate_k()