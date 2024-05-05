import os
import requests
import json
import csv
import time


def crawl_product_id():
    product_list = []
    i = 1
    while True:
        print("Crawl page: ", i)
        print(laptop_page_url.format(i))
        response = requests.get(laptop_page_url.format(i), headers=headers)

        if response.status_code != 200:
            break

        products = json.loads(response.text)["data"]

        if len(products) == 0:
            break

        for product in products:
            product_id = str(product["id"])
            print("Product ID: ", product_id)
            product_list.append(product_id)

        i += 1

    print("No. Page: ", i)
    print("No. Product ID: ", len(product_list))

    return product_list, i


def save_product_id(product_list):
    file = open(product_id_file, "w+")
    str = "\n".join(product_list)
    file.write(str)
    file.close()
    print("Save file: ", product_id_file)


def crawl_product(product_list):
    if product_list is None:
        with open(product_id_file, 'r') as f:
            product_list = f.readlines()
            product_list = [x[:-1] for x in product_list]

    f = open(product_data_file, "w+", encoding="utf-8")
    retry_list = []
    try:
        for product_id in product_list:
            response = requests.get(product_url.format(product_id), headers=headers)
            if response.status_code == 200:
                k = response.text
                if k.startswith('{') and k.endswith('}'):
                    print(f"Crawl product: {product_id} - Success")
                    f.write(k + '\n')
                else:
                    print(f"Crawl product: {product_id} - To retry list (1)")
                    retry_list.append(product_id)
                    time.sleep(10)
            else:
                print(f"Crawl product: {product_id} - To retry list (2)")
                retry_list.append(product_id)
                time.sleep(10)

        for product_id in retry_list:
            for count in range(3):
                response = requests.get(product_url.format(product_id), headers=headers)
                if response.status_code == 200:
                    k = response.text
                    if k.startswith('{') and k.endswith('}'):
                        print(f"Crawl product: {product_id} - Success")
                        f.write(k + '\n')
                        break
                    else:
                        count += 1
                        print(f"Crawl product: {product_id} - Retry {count}")
                        time.sleep(10)
                else:
                    count += 1
                    print(f"Crawl product: {product_id} - Retry {count}")
                    time.sleep(10)
    except Exception as e:
        print(e)

    f.close()

    print("Save file: ", product_data_file)


def filter_product_data():
    with open(product_data_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    with open(product_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Product Name', 'Brand', 'Release Year', 'Operating System', 'Screen Size (inch)', 'Battery (mAh)',
                         'Main Camera (MP)', 'RAM (GB)', 'Internal Storage (GB)', 'Chip Set', 'CPU speed', 'GPU', 'Price'])
        for line in lines:
            data = json.loads(line[:-1])
            name = data['name']
            brand = data['brand']['name']
            price = data['price']
            released_year = ''
            p_os = 'iOS' if 'iphone' in name.lower() else 'Android'
            screen_size = ''
            battery = ''
            camera = ''
            ram = ''
            rom = ''
            chip_set = ''
            cpu_speed = ''
            gpu = ''
            specifications = data['specifications']
            for obj in specifications:
                if obj['name'] == 'Content':
                    attributes = obj['attributes']
                    for item in attributes:
                        if item['code'] == 'battery_capacity':
                            battery = item['value']
                        if item['code'] == 'screen_size':
                            screen_size = item['value']
                        if item['code'] == 'camera_truoc':
                            camera = item['value']
                        if item['code'] == 'camera_truoc':
                            camera = item['value']
                        if item['code'] == 'camera':
                            camera = item['value']
                        if item['code'] == 'ram':
                            ram = item['value']
                        if item['code'] == 'rom':
                            rom = item['value']
                        if item['code'] == 'chip_set':
                            chip_set = item['value']
                        if item['code'] == 'cpu_speed':
                            cpu_speed = item['value']
                        if item['code'] == 'chip_do_hoa':
                            gpu = item['value']
            writer.writerow([name, brand, released_year, p_os, screen_size, battery, camera, ram, rom, chip_set,
                             cpu_speed, gpu, price])


if __name__ == '__main__':
    laptop_page_url = "https://tiki.vn/api/v2/products?limit=48&category=1795&page={}&urlKey=dien-thoai-smartphone"
    product_url = "https://tiki.vn/api/v2/products/{}"

    product_id_file = "./data/product-id.txt"
    product_data_file = "./data/product.txt"
    product_file = "./data/product.csv"

    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36"
    }

    # init data folder
    if not os.path.exists('./data'):
        os.mkdir('./data')

    # crawl product id
    product_list, page = crawl_product_id()

    # save product id for backup
    save_product_id(product_list)

    # crawl detail for each product id
    crawl_product(product_list)

    # filter and map data to csv file
    filter_product_data()
