from PIL import Image

icoImg = Image.open("PairsStratificationIco.png")

icoImg.save(
    "PairsStratificationIco.ico",
    sizes=[
        (32,32),
        (40,40),
        (48,48),
        (64,64),
        (128,128),
        (256,256)
    ]
)

appIcoImg = Image.open("PairsStratificationAppIco.png")

appIcoImg.save(
    "PairsStratificationAppIco.ico",
    sizes=[
        (16,16),
        (20,20),
        (24,24),
        (32,32),
        (40,40),
        (48,48),
        (64,64),
        (128,128),
        (256,256)
    ]
)
