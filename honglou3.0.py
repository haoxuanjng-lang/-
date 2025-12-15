# 导入需要的库
import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from collections import Counter

# ================= 配置区 =================
TEXT_FILE = '红楼梦.txt'  # 小说文件
MASK_FILE = 'background.jpg'  # 背景图片
FONT_FILE = 'simhei.ttf'  # 字体文件(必须要有，否则中文乱码)
OUTPUT_FILE = '红楼梦词云图.png'  # 生成的图片名

# 定义你要筛选的15-20个重要角色（手动指定最准确，符合题目要求）
ROLE_NAMES = [
    "贾宝玉", "林黛玉", "薛宝钗", "王熙凤", "史湘云",
    "贾母", "贾政", "王夫人", "平儿", "袭人",
    "晴雯", "香菱", "贾探春", "贾迎春", "贾惜春",
    "秦可卿", "贾琏", "紫鹃", "妙玉", "刘姥姥"
]

# ================= 核心逻辑 =================

print("1. 正在读取小说文本...")
try:
    # encoding='utf-8' 是常见编码，如果报错可以改成 'gbk'
    with open(TEXT_FILE, 'r', encoding='utf-8') as f:
        text_content = f.read()
except UnicodeDecodeError:
    with open(TEXT_FILE, 'r', encoding='gbk') as f:
        text_content = f.read()

print("2. 正在进行分词和筛选角色...")
# 使用jieba分词
words = jieba.lcut(text_content)

# 筛选：只保留我们在 ROLE_NAMES 里定义的名字
filtered_words = []
for word in words:
    if word in ROLE_NAMES:
        filtered_words.append(word)

print(f"   筛选完成，共找到 {len(filtered_words)} 个相关人名提及。")

# 【关键改动】计算每个角色的出现频率
role_freq = Counter(filtered_words)
print(f"   找到 {len(role_freq)} 个不同的角色")
print(f"   角色频率统计：")
for role, freq in sorted(role_freq.items(), key=lambda x: x[1], reverse=True):
    print(f"      {role}: {freq}次")

# 归一化频率到更大的范围，让字体差异更明显
max_freq = max(role_freq.values())
min_freq = min(role_freq.values())
normalized_freq = {}
for role, freq in role_freq.items():
    # 将频率映射到 [1000, 10000] 范围，这样高频词会大很多倍
    normalized_freq[role] = int(1000 + (freq - min_freq) / (max_freq - min_freq) * 9000)

print(f"\n   频率范围：{min_freq} - {max_freq}")
print(f"   归一化后范围：1000 - 10000")

print("3. 正在读取背景图片...")
# 读取背景图片（保持原样，不做任何处理）
background_img = Image.open(MASK_FILE)
print(f"   背景图片大小：{background_img.size}")

# 获取背景图片的宽高
bg_width, bg_height = background_img.size

print("4. 正在生成词云...")
# 【改动】使用较小的词云尺寸，使词云更紧凑
wordcloud_width = int(bg_width * 0.6)  # 词云宽度为背景图的60%
wordcloud_height = int(bg_height * 0.6)  # 词云高度为背景图的60%

print(f"   词云尺寸：{wordcloud_width} x {wordcloud_height}")

# 创建词云对象
wc = WordCloud(
    background_color="white",  # 背景颜色为白色
    font_path=FONT_FILE,  # 字体路径
    width=wordcloud_width,  # 【改动】词云宽度缩小
    height=wordcloud_height,  # 【改动】词云高度缩小
    max_words=200,  # 最大词数（足够显示所有角色）
    min_font_size=150,  # 最小字体大小
    max_font_size=450,  # 最大字体大小
    random_state=42,  # 随机种子
    collocations=False,  # 不考虑词组搭配
    margin=1,  # 【改动】更小的边距，词更紧凑
    prefer_horizontal=0.9  # 优先水平排列
)

# 【关键改动】使用归一化后的频率字典生成词云
# 这样高频词的字体会大很多
wc.generate_from_frequencies(normalized_freq)

print("   词云生成完毕！")

print("5. 正在合成词云和背景图...")
# 获取词云图像（PIL Image对象）
wordcloud_img = wc.to_image()

# 将词云图像转换为numpy数组方便处理
wordcloud_array = np.array(wordcloud_img)

# 获取背景图像的numpy数组
background_array = np.array(background_img.convert('RGB'))

# 【关键步骤】将白色背景变为透明，只保留词云文字
# 识别白色或接近白色的像素（留一些容差，因为反锯齿会产生灰色边缘）
white_mask = (wordcloud_array[:, :, 0] >= 240) & \
             (wordcloud_array[:, :, 1] >= 240) & \
             (wordcloud_array[:, :, 2] >= 240)

# 【新增】计算词云在背景图中的中心位置
# 将词云居中放置在背景图上
offset_x = (bg_width - wordcloud_width) // 2
offset_y = (bg_height - wordcloud_height) // 2

print(f"   词云位置：({offset_x}, {offset_y})")

# 创建最终合成图像（复制背景图）
result_array = background_array.copy()

# 【改动】将词云只覆盖到中心区域
# 遍历词云的每个像素，如果不是白色，就覆盖到背景图的对应位置
for y in range(wordcloud_height):
    for x in range(wordcloud_width):
        # 词云中的像素值
        pixel = wordcloud_array[y, x]

        # 检查是否为白色（背景）
        if not ((pixel[0] >= 240) and (pixel[1] >= 240) and (pixel[2] >= 240)):
            # 计算在背景图中的位置
            bg_y = offset_y + y
            bg_x = offset_x + x

            # 确保不超出背景图边界
            if 0 <= bg_x < bg_width and 0 <= bg_y < bg_height:
                result_array[bg_y, bg_x] = pixel

# 转换为PIL Image并保存
result_img = Image.fromarray(result_array.astype('uint8'))
result_img.save(OUTPUT_FILE)

print(f"6. 成功！词云已覆盖在背景图中部，保存为 {OUTPUT_FILE}")

# 展示最终结果
plt.figure(figsize=(12, 12))
plt.imshow(result_img)
plt.axis("off")
plt.tight_layout(pad=0)
plt.show()