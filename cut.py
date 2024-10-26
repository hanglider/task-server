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

def batch_cut(path_file_in, path_dir_out, count_lines=5000):
    '''Функция batch_cut разрезает файл с расширением .txt на файлы с расширением .txt c заданным количеством строк.
       
      Параметры: path_file_in : str
                 Абсолютный или относительный путь до файла с расширением .txt, который нужно разрезать.
                 path_dir_out : str
                    Абсолютный или относительный путь до папки, в которую будут помещаться нарезанные файлы.
                  count_lines :  int, default 500000
                    Количество строк, на которые разрезается исходный файл.
       Возвращаемое значение: None   
    '''
    def delete_line_feed_end(line):        
        if line[-1:] == '\n':
            return line[:-1]
        return line        
    
    path_dir_out += '\\' + path_file_in.split('\\')[-1][:-4]
    stop_iteration = count_lines - 2 
    try:
        file_number = 1  
        with open(path_file_in) as file_read:
            line = file_read.readline()                      
            while line:                
                i = 0
                batch = [delete_line_feed_end(line)]
                line = file_read.readline()
                while line and (i < stop_iteration):                    
                    batch.append(line[:-1])
                    line = file_read.readline()
                    i += 1
                if line:
                    batch.append(delete_line_feed_end(line))
                new_file_name = path_dir_out + '_' + str(file_number) + '.txt'
                with open(new_file_name, 'w') as file_write:
                    file_write.write('\n'.join(batch))                
                file_number += 1
                line = file_read.readline()
    except Exception as err:
        print('Ошибка: ', err)