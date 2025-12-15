# 导入需要的库
import jieba
from wordcloud import WordCloud, ImageColorGenerator
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

# ================= 配置区 =================
TEXT_FILE = '红楼梦.txt'  # 小说文件
MASK_FILE = 'new_mask.jpg'    # 背景图片
FONT_FILE = 'simhei.ttf'        # 字体文件(必须要有，否则中文乱码)
OUTPUT_FILE = 'result_cloud.png' # 生成的图片名

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

# 将筛选后的列表拼接成一个长字符串，用空格隔开
text_for_cloud = " ".join(filtered_words)

print(f"   筛选完成，共找到 {len(filtered_words)} 个相关人名提及。")

print("3. 正在处理背景图片...")
# 1. 读取图片
img = Image.open(MASK_FILE)

# 2. 如果图片有透明背景(PNG)，把它转成白色底
if img.mode != 'RGB':
    background = Image.new("RGB", img.size, (255, 255, 255))
    if img.mode == 'RGBA':
        background.paste(img, mask=img.split()[3]) # 处理透明度
    else:
        background.paste(img)
    img = background

# 3. 转成灰度图（黑白）
img_gray = img.convert('L')
mask_image = np.array(img_gray)

# 4. 【关键步骤】二值化处理：强制把所有偏白色的地方都变成纯白(255)
# 只要像素值大于 200 (偏灰白)，就强制变成 255 (纯白背景)
# 这样只有原本黑色的荷花部分会被保留下来
mask_image[mask_image > 200] = 255

print("   图片处理完毕，正在生成词云...")

# 创建词云对象 (注意：这里我把 contour_width 加粗了一点，让形状更明显)
wc = WordCloud(
    background_color="white",
    font_path=FONT_FILE,
    mask=mask_image,          # 使用处理好的遮罩
    width=1000,
    height=1000,
    max_words=2000,
    max_font_size=150,        # 限制最大字号，防止一个大字撑满
    random_state=42,
    contour_width=2,          # 【修改】轮廓线加粗一点
    contour_color='steelblue'
)

print("4. 正在生成词云...")
# 创建词云对象
wc = WordCloud(
    background_color="white", # 背景颜色
    font_path=FONT_FILE,      # 字体路径（关键！）
    mask=mask_image,          # 设置背景形状
    width=1000,               # 图片宽度
    height=1000,              # 图片高度
    max_words=2000,           # 最大词数
    contour_width=1,          # 轮廓线宽
    contour_color='steelblue' # 轮廓颜色
)

# 根据文本生成词云
wc.generate(text_for_cloud)

# (可选) 如果你想让词云颜色跟随背景图的颜色，取消下面两行的注释
#image_colors = ImageColorGenerator(mask_image)
#wc.recolor(color_func=image_colors)

# 保存图片
wc.to_file(OUTPUT_FILE)
print(f"5. 成功！词云已保存为 {OUTPUT_FILE}")

# 展示图片
plt.imshow(wc, interpolation='bilinear')
plt.axis("off") # 不显示坐标轴
plt.show()