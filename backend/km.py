import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import pymysql

# 设置中文字体
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

def get_cluster_profiles():
    conn = pymysql.connect(**DB_CONFIG)
    try:
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
    finally:
        conn.close()

    if df.empty or len(df['student_id'].unique()) < 4:
        print("错误：数据量不足。需要至少 4 个学生的定量标签数据！")
        return

    # 数据预处理
    df['tag_value'] = pd.to_numeric(df['tag_value'], errors='coerce')
    df = df.dropna()
    df_pivot = df.pivot(index='student_id', columns='tag_name', values='tag_value')
    df_pivot = df_pivot.fillna(df_pivot.mean())

    # 标准化并聚类 (固定 K=4)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_pivot)
    kmeans = KMeans(n_clusters=4, random_state=42)
    clusters = kmeans.fit_predict(X_scaled)

    # 将聚类结果加回原始数据，计算原始均值（为了论文表格好看）
    df_pivot['Cluster'] = clusters
    
    # 计算每个簇的特征均值 (保留2位小数)
    centroids = df_pivot.groupby('Cluster').mean().round(2)
    # 计算每个簇的人数
    counts = df_pivot['Cluster'].value_counts().sort_index()
    centroids['学生人数'] = counts

    print("\n================ 论文用表：各学习风格聚类簇特征均值 ================\n")
    # 打印 Markdown 格式的表格，直接可以贴进论文或者转成 Word 表格
    print(centroids.to_markdown())
    print("\n====================================================================\n")

    # 绘制雷达图
    features = [col for col in centroids.columns if col != '学生人数']
    N = len(features)
    
    # 准备雷达图的角度
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1] # 闭合多边形

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    # 定义四种颜色
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    labels = ['类型 0', '类型 1', '类型 2', '类型 3']

    # 为了让不同量纲的数据在雷达图上好看，我们在绘图时对均值进行 Min-Max 归一化 (仅用于绘图展示)
    # 如果你的数据量纲差不多（比如都是 0-100），可以注释掉这一段，直接用原始值画
    plot_data = centroids[features].copy()
    for col in plot_data.columns:
        min_val = plot_data[col].min()
        max_val = plot_data[col].max()
        if max_val != min_val:
            plot_data[col] = (plot_data[col] - min_val) / (max_val - min_val) * 100 # 映射到 0-100 方便看
        else:
            plot_data[col] = 50

    for i in range(4):
        values = plot_data.iloc[i].tolist()
        values += values[:1] # 闭合
        
        ax.plot(angles, values, linewidth=2, linestyle='solid', label=labels[i], color=colors[i])
        ax.fill(angles, values, color=colors[i], alpha=0.1)

    # 替换 x 轴的标签为特征名
    plt.xticks(angles[:-1], features, color='black', size=11)
    
    # 隐藏 y 轴的刻度（因为我们做了归一化，看形状更重要）
    ax.set_yticklabels([])

    plt.title('四类学习风格群体特征画像雷达图', size=16, y=1.05)
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    
    plt.savefig('cluster_radar_chart.png', dpi=300, bbox_inches='tight')
    print("雷达图已生成并保存为：cluster_radar_chart.png")
    # plt.show()

if __name__ == "__main__":
    get_cluster_profiles()