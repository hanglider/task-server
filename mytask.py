import cv2
import asyncio

def split_image(image, num_splits):
    height, width = image.shape[:2]
    step = height // num_splits
    return [(image[i * step:(i + 1) * step, :], i * step) for i in range(num_splits)]

def load_image(image_path, num_splits):
    image = cv2.imread(image_path)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    thresholded = cv2.threshold(blurred, 100, 255, cv2.THRESH_BINARY)[1]

    image_parts = split_image(thresholded, num_splits)
    return image_parts

async def main(image_part):
    """The main async function, which will be called in TaskProcessor.
        You can edit it's body as you whant, use any arguments that you whant.

        Example usage:
            funcs = (main, main,\
            main, main) # How many subtasks do you want to split the task into, \
            in this case task is splited into 4 subtasks
            kwargs = {'image_part': image_parts[0], 'image_part': image_parts[1],\
              'image_part': image_parts[2], 'image_part': image_parts[3]} \
              #Main function arguments, must have same signature
            async with TaskProccesor(10, *funcs, **kwargs) as results:
                print("task has been processed")
                return results
    """
    await asyncio.sleep(5)
    image, offset_y = image_part
    edges = cv2.Canny(image, 100, 200)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    object_stats = []

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        object_stats.append({'coordinates': (x, y + offset_y), 'size': (w, h)})
    
    return object_stats


# This code is needed to compare the time, TODO: delete this code later

# def wo_parallel():
#     edges = cv2.Canny(thresholded, 100, 200)
#     contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#     object_stats = []

#     for contour in contours:
#         x, y, w, h = cv2.boundingRect(contour)
#         object_stats.append({'coordinates': (x, y), 'size': (w, h)})

#     return object_stats

# s_time = time.time()
# wo_parallel()
# print(f"{time.time() - s_time:.2f}")