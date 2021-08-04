import math

string = "mpv videos/colors0.avi"
num_videos = 6

for i in range(1, num_videos):
    string += f" --external-file=videos/colors{i}.avi"

# number cols / number rows >= 1920/1080 (closer to ==)
# number cols * number rows >= num_videos (closer to ==)
# number cols >= number rows > 0
rows = math.ceil(math.sqrt(num_videos * 1080/1920))
cols = math.ceil(num_videos/rows)

lavfi_strings = []
for r in range(rows):
    nums = [1 + r*cols + c for c in range(cols)]
    row_string = "".join([f"[vid{n}]" for n in nums]) + f" hstack=inputs={len(nums)} [row{r+1}]"
    lavfi_strings.append(row_string)

# lavfi_strings.append()
col_string = "".join([f"[row{n}]" for n in range(1, rows+1)]) + f" vstack=inputs={rows} [vo]"
lavfi_strings.append(col_string)

string += " --lavfi-complex='" + " ; ".join(lavfi_strings) + "'"

string += " --window-maximized"

print(string)
