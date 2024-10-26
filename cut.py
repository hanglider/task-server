def cut_jpg(way_to_file, way_to_directory_save, split_size_gorizontal = 4, split_size_vertical = 4):
    from PIL import Image

    im = Image.open(way_to_file)
    pixels = im.load()  # список с пикселями
    x, y = im.size  # ширина (x) и высота (y) изображения

    for i in range(split_size_gorizontal):
        for j in range(split_size_vertical):
            if i != split_size_gorizontal and j != split_size_vertical:
                im.crop(box=(x/split_size_gorizontal*i, y/split_size_vertical*j, 
                             x/split_size_gorizontal*(i+1)-1, y/split_size_vertical*(j+1)-1)).\
                save('{way_to_directory_save}/image{}{}.jpg'.format(str(i+1), str(j+1)))