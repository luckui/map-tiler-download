# 说明
支持输入shp文件，下载shp范围内的每个要素范围的切片影像。
目前支持maptiler的api，请注册后获得key之后替换url里的key。

## 更新
* 更新了下载函数 patchTile.py，推荐使用该方法，支持将请求到的图片分切片下载，即使中途头一个切片没有请求到，也不影响下一次请求。

## 参数
示例输入参数以下：
```
shpPath = r"E:\GISprogram\investigate2\SurveyArea\surveyArea.shp"
zoom = 15
output = 'test'

url = "https://api.maptiler.com/tiles/satellite-v2/{z}/{x}/{y}.jpg?key=xxxxxxxxxx"
```
