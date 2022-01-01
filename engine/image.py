import PIL

class Image:

    def __init__(self, width, height, data, pil_image):
        self.width = width
        self.height = height
        self.data = data
        self.pil_image = pil_image


    @classmethod
    def from_file(cls, path_to_img):
        image = PIL.Image.open(path_to_img)
        # image = image.transpose(PIL.Image.FLIP_TOP_BOTTOM)
        # for using pil for loading in icon fow glfw, we need 3 channels
        image_data = image.convert("RGB").tobytes()
        return cls(image.width, image.height, image_data, image)
