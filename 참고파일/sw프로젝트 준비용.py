from PIL import Image

# 색상 매핑 (0~15번)
color_mapping = {
    (0, 0, 0): 0,          # BLACK
    (0, 0, 139): 1,        # DARK_BLUE
    (0, 100, 0): 2,        # DARK_GREEN
    (0, 139, 139): 3,      # DARK_SKYBLUE
    (139, 0, 0): 4,        # DARK_RED
    (148, 0, 211): 5,      # DARK_VIOLET
    (139, 139, 0): 6,      # DAKR_YELLOW
    (169, 169, 169): 7,    # GRAY
    (128, 128, 128): 8,    # DARK_GRAY
    (0, 0, 255): 9,        # BLUE
    (0, 255, 0): 10,       # GREEN
    (135, 206, 250): 11,   # SKYBLUE
    (255, 0, 0): 12,       # RED
    (238, 130, 238): 13,   # VIOLET
    (255, 255, 0): 14,     # YELLOW
    (255, 255, 255): 15    # WHITE
}

def closest_color(rgb):
    min_distance = float('inf')
    closest = 0
    for color, index in color_mapping.items():
        distance = sum((comp1 - comp2) ** 2 for comp1, comp2 in zip(color, rgb))
        if distance < min_distance:
            min_distance = distance
            closest = index
    return closest

def image_to_data(image_path, output_width):
    img = Image.open(image_path)
    img = img.resize((output_width, int(img.height * output_width / img.width)))  # 비율 유지
    img = img.convert("RGB")  # RGB로 변환
    
    data = []
    for y in range(img.height):
        line = []
        for x in range(img.width):
            rgb = img.getpixel((x, y))
            color_index = closest_color(rgb)
            line.append(color_index)  # 색상 인덱스를 추가
        data.append(line)
    
    return data, img.width, img.height

def format_data_to_c_array(data):
    formatted_data = []
    for line in data:
        formatted_line = "{" + ", ".join(map(str, line)) + "}"
        formatted_data.append(formatted_line)
    return "int Data[{}][{}] = {{\n    {}\n}};".format(len(data), len(data[0]), ",\n    ".join(formatted_data))

# 사용 예시
if __name__ == "__main__":
    # 고정 경로
    base_path = r"C:\Users\bongm\OneDrive\바탕 화면\sw준비용\\"
    
    # 사용자 입력 파일 이름
    file_name = input("이미지 파일 이름: ").strip()
    
    # 결합된 경로
    input_image = base_path + file_name
    
    # 가로 크기 입력
    output_width = int(input("텍스트 출력의 가로 크기: "))
    
    data, width, height = image_to_data(input_image, output_width)
    
    # C 스타일 데이터 포맷
    c_array = format_data_to_c_array(data)
    
    # 결과 출력
    with open(r"C:\Users\bongm\OneDrive\바탕 화면\sw준비용\\output.txt", "w") as f:
        f.write(c_array)
    
    print("파일에 저장되었습니다")




