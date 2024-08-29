from osgeo import gdal, osr
import requests
import geopandas as gpd
from shapely.geometry import Polygon
import math
from PIL import Image
from io import BytesIO
import numpy as np
import os
from tqdm import tqdm, trange
import time


shpPath = r"E:\programming\WMTSData\shp\aqua2.shp"
zoom = 14
output = 'aqua2'
url = "https://api.maptiler.com/tiles/satellite-v2/{z}/{x}/{y}.jpg?key=xxxxxxxxxx"


def lonlat2tile(lon, lat, zoom):
    # 将经纬度转换为瓦片坐标
    n = 2.0 ** zoom
    x_tile = int((lon + 180.0) / 360.0 * n)
    lat_rad = math.radians(lat)
    y_tile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return x_tile, y_tile


def tile2lonlat(x, y, z):
    n = 2.0 ** z
    lon_deg = x / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
    lat_deg = math.degrees(lat_rad)
    return lon_deg, lat_deg


def getRes(tile_url, i):
    response = requests.get(tile_url)
    if response.status_code != 200:
        print(f'不成功, {i}次请求')
        i = i-1
        if i == 0:
            print('算是，失败了')
            return response
        response = getRes(tile_url, i)
    return response


def singleTile(x, y, z):
    tile_url = url.format(x=x, y=y, z=z)
    response = getRes(tile_url, 5)
    # print(response.status_code)
    if response.status_code!=200:
        print(response.status_code)
    response.raise_for_status()  # 检查请求是否成功
    return Image.open(BytesIO(response.content))


def patchTile(item: Polygon, zoom, output):
    tileSize = 512
    xmin, ymin, xmax, ymax = item.bounds
    bottom_left_x, bottom_left_y = lonlat2tile(xmin, ymin, zoom)
    top_right_x, top_right_y = lonlat2tile(xmax, ymax, zoom)
    width = (top_right_x-bottom_left_x+1)*tileSize
    height = (bottom_left_y-top_right_y+1)*tileSize
    full_image = Image.new('RGB', (width, height))

    top_left_x, top_left_y = tile2lonlat(bottom_left_x, top_right_y, zoom)
    bottom_right_x, bottom_right_y = tile2lonlat(top_right_x+1, bottom_left_y+1, zoom)
    dx = (bottom_right_x-top_left_x)/width
    dy = -dx
    geotransform = [
        top_left_x, dx, 0, top_left_y, 0, dy
    ]

    for x in trange(bottom_left_x, top_right_x+1):
        for y in trange(top_right_y, bottom_left_y+1):
            tile = singleTile(x, y, zoom)
            pos_x = (x - bottom_left_x) * tileSize
            pos_y = (y - top_right_y) * tileSize
            full_image.paste(tile, (pos_x, pos_y))
            time.sleep(0.5)
    arr = np.array(full_image)
    driver = gdal.GetDriverByName('GTiff')
    ds = driver.Create(output, width, height, 3, gdal.GDT_Byte)
    ds.SetGeoTransform(geotransform)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)  # EPSG:4326 for WGS84
    ds.SetProjection(srs.ExportToWkt())
    for i in range(3):
        ds.GetRasterBand(i + 1).WriteArray(arr[:, :, i])
    ds.FlushCache()
    ds = None
    print(f"GeoTIFF saved as {output}")


def downloadProcess(shpPath, output, zoom):
    gdf = gpd.read_file(shpPath)
    for item in gdf.itertuples():
        outpath = os.path.join(output, f'FID_{item.Index}.tif')
        patchTile(item.geometry, zoom, outpath)


if __name__ == '__main__':
    downloadProcess(shpPath, output, zoom)




