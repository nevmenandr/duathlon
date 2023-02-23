import os
import imageio

images = []
for filename in sorted(os.listdir('chess-gif')):
    if not filename.endswith(".png"):
        continue
    images.append(imageio.imread(os.path.join('chess-gif', filename)))
imageio.mimsave(
    '1chegoss.gif',
    images,
    format="GIF",
    duration=3,
)