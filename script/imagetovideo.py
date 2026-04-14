import cv2
import os

current_dir = os.getcwd()

frames = sorted([
    f for f in os.listdir(current_dir)
    if f.startswith("frame_") and f.endswith(".png")
])

if not frames:
    raise Exception("No frames found in current directory")

first = cv2.imread(os.path.join(current_dir, frames[0]))
height, width, _ = first.shape

output_video = os.path.join(current_dir, "output.mp4")

video = cv2.VideoWriter(
    output_video,
    cv2.VideoWriter_fourcc(*"mp4v"),
    24,
    (width, height)
)

for f in frames:
    path = os.path.join(current_dir, f)
    frame = cv2.imread(path)
    video.write(frame)

video.release()

print("Video created at:", output_video)