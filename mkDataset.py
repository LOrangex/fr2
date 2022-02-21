import os
import numpy as np
import cv2

#type取值
TYPE_TRAIN = 'train'
TYPE_TEST = 'test'
#图片储存地址
PATH_FACE_SAVE = "D:\\bruce\\face-id\\practice\data\\face"
#数据集储存地址
PATH_DATASET_SAVE = "D:\\bruce\\face-id\\practice\data\\dataset"
#调整图片大小时扩充的地方填充的颜色
RESIZE_FILL_COLOR = (0,0,0)
#人脸图片的大小
FACE_SIZE = 64


def resizeImage(image, height, width):
    '''按照指定图像大小调整尺寸'''
    top, bottom, left, right = (0, 0, 0, 0)
    # 获取图像尺寸
    h, w, _ = image.shape
    # 对于长宽不相等的图片，找到最长的一边
    longest_edge = max(h, w)
    # 计算短边需要增加多上像素宽度使其与长边等长
    if h < longest_edge:
        dh = longest_edge - h
        top = dh // 2
        bottom = dh - top
    elif w < longest_edge:
        dw = longest_edge - w
        left = dw // 2
        right = dw - left
    else:
        pass
    # 给图像增加边界，是图片长、宽等长，cv2.BORDER_CONSTANT指定边界颜色由value指定
    constant = cv2.copyMakeBorder(image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=RESIZE_FILL_COLOR)
    # 调整图像大小并返回
    return cv2.resize(constant, (height, width))

def readFace(path):
    '''
    读取人脸
    '''
    print(path)
    image = cv2.imread(path)
    image = resizeImage(image, FACE_SIZE, FACE_SIZE)
    # 放开这个代码，可以看到resize_image()函数的实际调用效果
    # cv2.imwrite('{}.jpg'.format(1), image)
    return image

def readFacesAndLabels(dir, label, images=[], labels=[]):
    '''
    读取脸部图片，返回图片数组和标签数组
    '''
    for face in os.listdir(dir):
        path = '{}/{}'.format(dir, face)
        #读取成图片
        image = readFace(path)
        images.append(image)
        labels.append(label)
    return images, labels

def getFaceDir(name):
    '''
    获取目标文件夹的训练/测试数据目录
    '''
    train_dir = '{}/{}/{}'.format(PATH_FACE_SAVE, name, TYPE_TRAIN)
    test_dir = '{}/{}/{}'.format(PATH_FACE_SAVE, name, TYPE_TEST)
    return train_dir, test_dir

def getNameList():
    '''
    获取名称列表
    '''
    names = [];
    for dir_item in os.listdir(PATH_FACE_SAVE):
        names.append(dir_item)
    return names

def loadDataset(type):
    '''
    读取数据集
    '''
    dir = PATH_DATASET_SAVE
    images = np.load('{}/{}_images.npy'.format(dir, type))
    labels = np.load('{}/{}_labels.npy'.format(dir, type))
    names_map = loadDict('{}/{}_names_map.npy'.format(dir, type))
    return images, labels, names_map

def saveDataset(images, labels, names_map, type):
    '''
    保存数据集
    '''
    dir = PATH_DATASET_SAVE
    if os.path.isdir(dir)==False:
        os.mkdir(dir)
    np.save('{}/{}_images.npy'.format(dir, type), images)
    np.save('{}/{}_labels.npy'.format(dir, type), labels)
    saveDict('{}/{}_names_map.npy'.format(dir, type), names_map)

def saveDict(path, dict):
    '''
    保存字典
    '''
    f = open(path, 'w')
    f.write(str(dict))
    f.close()

def loadDict(path):
    '''
    读取字典
    '''
    f = open(path, 'r')
    a = f.read()
    dict = eval(a)
    f.close()
    return dict

def mkDataset(type):
    '''
    制作数据集
    '''
    images, labels = ([], [])
    names = getNameList()
    #读取所有名字的所有人脸图片数据
    for name in names:
        #读取该名字下的具体人脸目录
        train_dir, test_dir = getFaceDir(name)
        #将目录下的所有人脸读进images，并同步记录labels
        if type==TYPE_TRAIN:
            images, labels = readFacesAndLabels(train_dir, name, images, labels)
        else:
            images, labels = readFacesAndLabels(test_dir, name, images, labels)
    # 将输入的所有图片转成四维矩阵（数组），方便计算，尺寸为(图片数量*FACE_SIZE*FACE_SIZE*3)
    # 两个人共1200张图片，IMAGE_SIZE为64，故对我来说尺寸为1200 * 64 * 64 * 3
    # 图片为64 * 64像素,一个像素3个颜色值(RGB)
    images = np.array(images)
    # 名字用数字对应
    names_map = {};
    for i in range(len(names)):
        names_map[names[i]] = i
    #将名称字典打印出来，以便后面进行对照
    print(names_map);
    labels = np.array([names_map[label] for label in labels])
    #将标签转为one-hot形式
    labels = ((np.arange(len(names))==labels[:,None]).astype(np.integer))
    return images, labels, names_map

if __name__ == '__main__':
    # 制作训练集
    images, labels, names_map = mkDataset(TYPE_TRAIN)
    saveDataset(images, labels, names_map, TYPE_TRAIN)
    # 制作测试集
    images, labels, names_map = mkDataset(TYPE_TEST)
    saveDataset(images, labels, names_map, TYPE_TEST)