import pandas as pd
from pylab import mpl
import matplotlib.pyplot as plt
import numpy as np

usecols = ['小区', '价格(万元)', '行政区', '地段', '房屋户型', '楼层', '面积(m²)', '朝向', '装修情况', '电梯']
data = pd.read_csv('昆明二手房数据.csv', encoding='utf-8', usecols=usecols, na_values=['暂无数据'])

# 删除重复行
data.drop_duplicates(inplace=True)

# 去除朝向字段为装修情况的数据
renovation_list = ['毛坯', '精装', '简装', '其他']
for item in renovation_list:
    data = data[data['朝向'] != item]

# 去除地段为空值的数据
data.dropna(how='any', inplace=True)

# 去除数据中面积不包含'㎡'字符串的数据
data = data[data['面积(m²)'].str.contains('㎡')]
# 将面积后的单位去除，转换为数值型
data['面积(m²)'] = data['面积(m²)'].str.replace('㎡', '')
data['面积(m²)'] = data['面积(m²)'].astype('float')

# 去除房屋面积大于等于290m²的数据
data.drop(data[data['面积(m²)'] >= 290].index, inplace=True)

# 处理朝向数据
temp = data['朝向'].str.split(' ')
for key_values in data['朝向'].str.split(' ').items():
    data.loc[key_values[0], '朝向'] = key_values[1][0]

# 对装修情况缺失值进行填充
data['装修情况'].fillna('其他', inplace=True)

# 从楼层中提取总楼层数据
floor_total = data['楼层'].str.extract('(\d+)')
floor_total = floor_total.astype('int')
data['总楼层'] = floor_total

# 对电梯缺失值进行填充
for index, row in data[data['电梯'].isnull()].iterrows():
    if row['总楼层'] > 7:
        data.loc[index, '电梯'] = '有'
    else:
        data.loc[index, '电梯'] = '无'

# 增加房屋单价一列
data['单价(元/m²)'] = data['价格(万元)'] * 10000 / data['面积(m²)']

mpl.rcParams['font.sans-serif'] = ['FangSong']  # 指定默认字体


def pie_chart():
    # 不同行政区房源数量占比
    area_house_count = data.groupby('行政区')['行政区'].count()
    area_house_count.sort_values(ascending=False, inplace=True)  # 按照降序排列
    new_area_house_count = area_house_count[area_house_count > 100]
    # area_house_count

    # 不同户型房源数量占比
    house_type_count = data.groupby('房屋户型')['房屋户型'].count()
    house_type_count.sort_values(ascending=False, inplace=True)  # 按照降序排列
    new_house_type_count = house_type_count[house_type_count > 700]
    new_house_type_count['其它'] = house_type_count[house_type_count < 700].sum()
    # new_hourseType_count

    # 不同朝向房源数量占比()
    direction_count = data.groupby('朝向')['朝向'].count()
    new_direction_count = direction_count[direction_count > 800]
    new_direction_count['其它'] = direction_count[direction_count < 800].sum()
    new_direction_count.sort_values(ascending=False, inplace=True)

    # 不同装修
    fitment_count = data.groupby('装修情况')['装修情况'].count().sort_values(ascending=False)
    fitment_count.sort_values(ascending=False, inplace=True)

    fig = plt.figure(figsize=(10, 8), dpi=160)
    ax1 = fig.add_subplot(2, 2, 1)
    plt.title("不同行政区房源数量占比情况")
    new_area_house_count.plot.pie(shadow=True, autopct='%0.f%%', startangle=90)

    ax2 = fig.add_subplot(2, 2, 2)
    plt.title("不同户型房源数量占比情况")
    new_house_type_count.plot.pie(shadow=True, autopct='%0.f%%', startangle=90)

    ax3 = fig.add_subplot(2, 2, 3)
    plt.title("不同朝向房源数量占比情况")
    new_direction_count.plot.pie(shadow=True, autopct='%0.f%%', startangle=90)

    ax4 = fig.add_subplot(2, 2, 4)
    plt.title("不同装修类型的占比情况")
    fitment_count.plot.pie(shadow=True, autopct='%0.f%%', startangle=45)
    plt.savefig('不同行政区、户型、朝向、装修类型占比饼状图.jpg')
    plt.show()


def price_contrast():
    # 不同区的总价对比
    area_house_mean_totalprice = data.groupby('行政区')['价格(万元)'].mean()
    area_house_mean_totalprice.sort_values(ascending=False, inplace=True)

    # 不同区的单价对比
    area_house_mean_unitprice = data.groupby('行政区')['单价(元/m²)'].mean()
    area_house_mean_unitprice.sort_values(ascending=False, inplace=True)

    fig = plt.figure(figsize=(9, 5), dpi=160)
    ax1 = fig.add_subplot(1, 2, 1)
    plt.title("昆明不同地区均价对比")
    plt.ylim([30, 200])  # 设置y坐标轴的范围
    area_house_mean_totalprice.plot.bar(alpha=0.7, color='#1E90FF')
    plt.ylabel('均价')
    plt.grid(alpha=0.5, color='#CD3700', linestyle='--', axis='y')

    ax2 = fig.add_subplot(1, 2, 2)
    plt.title("昆明不同地区单价对比")
    plt.ylim([5000, 20000])
    area_house_mean_unitprice.plot.bar(alpha=0.7, color='#4876FF')
    plt.ylabel('单价(元/m$^{2}$)')
    plt.grid(alpha=0.5, color='#CD3700', linestyle='--', axis='y')
    plt.savefig('昆明不同区单价总价对比图.jpg')
    plt.show()


def district():
    fig = plt.figure(figsize=(7, 6), dpi=160)
    position_house_mean_price = data.groupby('地段')['价格(万元)'].mean()
    position_house_mean_price.sort_values(ascending=False, inplace=True)

    # 绘图  只展示排名前十的地段
    plt.title("昆明房价排名前十的地段")
    position_house_mean_price.head(10).plot.barh(alpha=0.7,
                                                 color=['#CD3700', '#9ACD32', '#7EC0EE', 'y', 'orange', '#4876FF',
                                                        '#EEA9B8', '#EE7942', '#CD69C9', '#668B8B'])
    plt.grid(color='#DDA0DD', linestyle='--', alpha=0.5)
    plt.xlabel('均价')
    plt.savefig('昆明房价排名前十地段图.jpg')
    plt.show()


def price_10():
    fig = plt.figure(figsize=(10, 5), dpi=160)
    community_top10 = data.groupby('小区')['价格(万元)'].mean().sort_values(ascending=False).head(10)
    plt.title("昆明小区均价排名前十的小区分析")
    community_top10.plot.barh(alpha=0.7, width=0.7)
    plt.xlabel('均价')
    plt.savefig('昆明小区均价总价排名前10图.jpg')
    plt.show()


def direction():
    # 房屋朝向对房屋单价的影响
    direction_unit_price = data.groupby('朝向')['单价(元/m²)'].mean().sort_values(ascending=False)
    fig = plt.figure(figsize=(15, 5), dpi=160)
    plt.title("房屋朝向对价格的影响")
    direction_unit_price.plot.bar(alpha=0.7)
    plt.ylabel('单价(元/m$^{2}$)')
    plt.grid(color='#DDA0DD', linestyle='--', alpha=0.5, axis='y')
    plt.savefig('房屋朝向对价格影响图.jpg')
    plt.show()


def renovation():
    # 装修情况对单价的影响
    fig = plt.figure(figsize=(10, 5), dpi=160)
    fit_price = data.groupby('装修情况')['单价(元/m²)'].mean().sort_values(ascending=False)
    plt.title('不同装修和单价的关系')
    fit_price.plot.bar(color=['#FF7F50', '#00E00D', '#FFA500', '#7B68EE'])
    plt.ylabel('单价(元/m$^{2}$)')
    plt.savefig('不同装修和单价关系图.jpg')
    plt.show()


def elevator():
    # 房屋有无电梯对房屋单价的影响
    fig = plt.figure(figsize=(10, 5), dpi=160)
    fit_price = data.groupby('电梯')['单价(元/m²)'].mean().sort_values(ascending=False)
    plt.title('有无电梯和单价的关系')
    fit_price.plot.bar(color=['#FF7F50', '#00E00D'])
    plt.ylabel('单价(元/m$^{2}$)')
    plt.savefig('有无电梯和单价关系图.jpg')
    plt.show()


def size():
    # 通过密度图和散点图来分析房屋特征
    plt.rcParams['axes.unicode_minus'] = False
    fig = plt.figure(figsize=(15, 5), dpi=160)
    ax1 = fig.add_subplot(1, 2, 1)
    plt.title("房间大小分布密度分析")
    data['面积(m²)'].hist(bins=20, ax=ax1, color='#F4A460', density=True)  # 直方图  desity=True显示频率，为False显示频数
    data['面积(m²)'].plot(kind='kde', style='--', ax=ax1)  # 折线图 kind='kde'(是与直方图相关的密度图)
    plt.xlabel('面积(m$^{2}$)')
    ax2 = fig.add_subplot(1, 2, 2)
    plt.title("房间大小与房价关系分析")
    plt.scatter(data['面积(m²)'], data['价格(万元)'], s=4)
    plt.xlabel('面积(m$^{2}$)')
    plt.ylabel('均价')
    plt.savefig('房屋大小分布密度与房价关系图.jpg')
    plt.show()


def price_num():
    fig = plt.figure(figsize=(9, 6), dpi=160)
    bins_arr = np.arange(0, 300, 30)
    bins = pd.cut(data['价格(万元)'], bins_arr)
    total_price_counts = data['价格(万元)'].groupby(bins).count()
    plt.title("昆明不同总价区间内的房源数量分析")
    plt.ylabel("社区房数量")
    total_price_counts.plot.barh(alpha=0.7, width=0.7)
    plt.xlabel('数量')
    plt.ylabel('万元')
    plt.savefig('昆明不同总价区间房源数量图.jpg')
    plt.show()


if __name__ == '__main__':
    pie_chart()
    price_contrast()
    district()
    price_10()
    direction()
    renovation()
    elevator()
    size()
    price_num()
