from PIL import Image, ImageOps
import torchvision.transforms as transforms
import torch
import os
from model.train import ModelInference


image_size = 224

classes = [
    "Full front view",
    "Back view",
    "Interior",
    "Wheel",
    "Headlight",
    "Trunk",
    "Side view",
    "Engine",
]

trained_model = ModelInference.load_from_checkpoint(
    "./Assets/image_classification_model.pt"
)

test_transforms = transforms.Compose(
    [
        transforms.Resize(image_size),
        transforms.CenterCrop(image_size),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ]
)


def padding(img, expected_size):
    desired_size = expected_size
    delta_width = desired_size - img.size[0]
    delta_height = desired_size - img.size[1]
    pad_width = delta_width // 2
    pad_height = delta_height // 2
    padding = (
        pad_width,
        pad_height,
        delta_width - pad_width,
        delta_height - pad_height,
    )
    return ImageOps.expand(img, padding)


def resize_with_padding(img, expected_size):
    # img.thumbnail((expected_size[0], expected_size[1]))
    # print(img.size)
    delta_width = expected_size[0] - img.size[0]
    delta_height = expected_size[1] - img.size[1]
    pad_width = delta_width // 2
    pad_height = delta_height // 2
    padding = (
        pad_width,
        pad_height,
        delta_width - pad_width,
        delta_height - pad_height,
    )
    return ImageOps.expand(img, padding)


def predict_label(img):
    # Note: img is now an Image object, not a path
    width, height = img.size
    ratio = width / height
    if ratio >= 1:
        img = img.resize((image_size, int(image_size / ratio)))
    elif ratio < 1:
        img = img.resize((int(image_size * ratio), image_size))
    img = ImageOps.pad(img, (image_size, image_size))
    img_tensor = test_transforms(img)
    img_tensor = img_tensor.unsqueeze(0)  # Add batch dimension
    with torch.no_grad():
        trained_model.eval()
        out = trained_model(img_tensor)[0]
        ps = torch.exp(out)
        result = classes[torch.argmax(ps)]
    return result


def process_images(image_paths):
    # Constant folder for saving processed images
    destination_folder = "./images/car parts"
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    for img_path in image_paths:
        test_image = Image.open(img_path).convert("RGB")
        predicted_class = predict_label(test_image)

        # Construct the new file name with class prefix
        image_file = os.path.basename(img_path)
        new_file_name = "{}_{}".format(predicted_class, image_file)
        destination_path = os.path.join(destination_folder, new_file_name)

        # Save the file to the "images" folder with the new name
        test_image.save(destination_path)
