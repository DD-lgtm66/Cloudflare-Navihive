import json
from bs4 import BeautifulSoup
import datetime
import sys
import os

def parse_bookmarks_html(html_file_path):
    # 读取HTML文件
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    print(f"【文件读取】内容长度: {len(html_content)} 字符")

    # 解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    print("【Soup 诊断】title:", soup.title.string if soup.title else "无 title")
    print("【Soup 诊断】所有 <A> 数量:", len(soup.find_all('a')))

    groups = []
    sites = []
    group_id_counter = [0]
    site_id_counter = [0]

    def parse_dl(dl, parent_group_id, order_num=0, current_time=None):
        if current_time is None:
            current_time = datetime.datetime.now().isoformat()

        # 强制用 recursive=True 找所有后代 DT
        children = dl.find_all('dt', recursive=True)
        print(f"【解析 DEBUG】进入 DL (parent={parent_group_id}, order={order_num}) → 找到 {len(children)} 个 DT (recursive=True)")

        if children:
            print(f"【解析 DEBUG】第一个 DT 示例: {str(children[0])[:150]}...")
        else:
            print("【解析 WARNING】这个 DL 没有找到任何 DT！检查是否选错了根 DL")

        local_order = 0
        for child in children:
            h3 = child.find('h3')
            if h3:
                group_id_counter[0] += 1
                new_group_id = group_id_counter[0]
                group_name = h3.text.strip()
                print(f"【添加 Group】ID={new_group_id}, 名称={group_name}, order={order_num + local_order}")
                groups.append({
                    "id": new_group_id,
                    "name": group_name,
                    "order_num": order_num + local_order
                })
                sub_dl = child.find('dl')
                if sub_dl:
                    parse_dl(sub_dl, new_group_id, 0, current_time)
                local_order += 1
            else:
                a = child.find('a')
                if a:
                    site_id_counter[0] += 1
                    site_name = a.text.strip()
                    site_url = a.get('href', '')
                    print(f"【添加 Site】ID={site_id_counter[0]}, 名称={site_name[:30]}, URL={site_url[:50]}...")
                    sites.append({
                        "id": site_id_counter[0],
                        "group_id": parent_group_id,
                        "name": site_name,
                        "url": site_url,
                        "icon": a.get('icon_uri') or a.get('icon', ''),
                        "description": "",
                        "notes": "",
                        "order_num": local_order,
                        "created_at": current_time,
                        "updated_at": current_time
                    })
                    local_order += 1

    # 根 DL 查找 - 超级诊断版
    all_dls = soup.find_all('dl')
    print(f"【ROOT DEBUG】HTML 中总共有 {len(all_dls)} 个 <DL>")

    root_dl = None
    selected_index = -1
    max_dt = 0

    for i, candidate in enumerate(all_dls):
        dt_count = len(candidate.find_all('dt', recursive=True))
        print(f"  DL[{i}]: 包含 {dt_count} 个 DT (recursive)")
        if dt_count > max_dt:
            max_dt = dt_count
            root_dl = candidate
            selected_index = i

    if root_dl:
        print(f"【ROOT DEBUG】最终选中 DL[{selected_index}]，它有 {max_dt} 个 DT → 这应该是内容根！")
        print("根 DL 直接子标签:", [c.name for c in root_dl.children if c.name])
        parse_dl(root_dl, 0)  # 开始递归
    else:
        print("【严重错误】没有找到任何带 DT 的 DL！")
        print("HTML 前 1000 字符预览:\n", soup.prettify()[:1000])

    # configs 和元数据（不变）
    configs = {
        "site.title": "Converted Bookmarks",
        "site.name": "Bookmarks JSON",
        "site.customCss": "",
        "site.backgroundImage": "",
        "site.backgroundOpacity": "0.84",
        "site.iconApi": "https://www.faviconextractor.com/favicon/{domain}?larger=true",
        "DB_INITIALIZED": "true"
    }
    version = "1.0"
    export_date = datetime.datetime.now().isoformat()

    output_json = {
        "groups": groups,
        "sites": sites,
        "configs": configs,
        "version": version,
        "exportDate": export_date
    }
    print(f"【最终统计】groups: {len(groups)} 个, sites: {len(sites)} 个")
    return output_json
# 主函数
if __name__ == "__main__":
    # if len(sys.argv) < 2:
    #     print("Usage: python script.py path/to/bookmarks.html")
    #     sys.exit(1)
    
    # html_file = sys.argv[1]
    html_file=r"D:\Users\DQH\Desktop\bookmarks.html"
    result = parse_bookmarks_html(html_file)
    print("当前工作目录：", os.getcwd())
    print("目标文件是否存在？", os.path.exists(html_file))
    print("文件大小（字节）：", os.path.getsize(html_file) if os.path.exists(html_file) else "不存在")
    # 输出到文件
    with open('converted_bookmarks.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    
    print("Conversion complete. Output: converted_bookmarks.json")