import zipfile
import os
import xml.dom.minidom
import xlrd, xlwt, xlutils

def unzip(src, dst):
    print("unzip %s to %s" % (src, dst))
    zip_file = src
    z = zipfile.ZipFile(zip_file, 'r')
    z.extractall(dst)
    z.close()

def search_ipa(src):
    file_names = os.listdir(src)

    file_paths = []
    for file_name in file_names:
        if file_name[-3:] == "ipa":
            file_paths.append(os.path.join(src, file_name))
    return file_paths


def parse_info_plist_xml(src):
    plist_file = search_file(src, "Info.plist")
    print(plist_file)
    dom_tree = xml.dom.minidom.parse(plist_file)
    plist_object = dom_tree.documentElement
    return plist_object, plist_file


def search_file(src, file_name):
    if not os.path.isdir(src):
        return ""
    files = os.listdir(src)
    if file_name in files:
        return os.path.join(src, file_name)
    else:
        for file in files:
            new_src = os.path.join(src, file)
            if os.path.isdir(new_src):
                return search_file(new_src, file_name)
        return ""



def read_info_plist(src, key):
    plist_object, plist_file = parse_info_plist_xml(src)
    return get_xml_value(plist_object, key)



def get_xml_value(plist, key):
    for element in plist.childNodes:
        if element.localName == 'dict':
            return __get_common_xml_value(element, key)
    return None, None


def __get_common_xml_value(element, key):
    count = element.childNodes.length
    i = 0
    while i < count:
        node = element.childNodes[i]
        if node.localName == 'key':
            i = i + 2

            if node.firstChild and node.firstChild.data == key:
                new_node = element.childNodes[i]
                return __format_xml_node(new_node)
        i = i + 1
    return None


def __format_xml_node(element):
    if element.localName == "string":
        return __format_string_node(element)
    if element.localName == "array":
        return __format_array_node(element)


def __format_string_node(element):
    if element is None:
        return ""
    if element.firstChild is None:
        return ""
    return element.firstChild.data


def __format_array_node(element):
    child_nodes = element.childNodes
    child_array = []
    for child in child_nodes:
        if child.localName == "dict":
            child_array.append(__format_dict_node(child))
        if child.localName == "string":
            child_array.append(__format_string_node(child))
    return child_array

def __format_dict_node(element):
    child_nodes = element.childNodes
    child_dict = {}
    last_key = ""
    for child in child_nodes:
        if child.localName == "key":
            last_key = __format_string_node(child)
        if child.localName == "string":
            if last_key != "":
                child_dict[last_key] = __format_string_node(child)
        if child.localName == "array":
            if last_key != "":
                child_dict[last_key] = __format_array_node(child)
    return child_dict


def create_excel():
    book = xlwt.Workbook()
    sheet_new = book.add_sheet("sheet")
    return sheet_new, book


def write_excel(sheet, name, bundle_id, schemes, index):
    sheet.write(index, 0, name)
    sheet.write(index, 1, bundle_id)
    sheet.write(index, 2, schemes)


def rmdir_recure(path):
    if not os.path.isdir(path):
        os.remove(path)

    targets = os.listdir(path)

    for target in targets:
        newpath = os.path.join(path, target)

        if os.path.isfile(newpath):
            os.remove(newpath)
        else:
            rmdir_recure(newpath)

    os.rmdir(path)


def main(src, dst):
    file_paths = search_ipa(src)

    excel_file = os.path.join(dst, "output.xlsx")
    if os.path.exists(excel_file):
        os.remove(excel_file)
    sheet, book = create_excel()
    temp_dir = os.path.join(dst, "temp")

    errors = []
    index = 0
    for file_path in file_paths:
        try:
            unzip(file_path, temp_dir)
            url_types = read_info_plist(temp_dir, "CFBundleURLTypes")
            display_name = read_info_plist(temp_dir, "CFBundleDisplayName")
            bundle_id = read_info_plist(temp_dir, "CFBundleIdentifier")
            schemes = []
            if url_types is not None:
                for url_type in url_types:
                    if url_type.get("CFBundleURLSchemes"):
                        schemes = schemes + url_type.get("CFBundleURLSchemes")
            write_excel(sheet, display_name, bundle_id, ",".join(schemes), index)
            book.save(excel_file)

        except Exception as e:
            print(index, e)
            errors.append(e)
        finally:
            index = index + 1
            rmdir_recure(temp_dir)
# main("/Volumes/disk/apps", "/Users/daiyichao/Downloads/export")


def plist_make(path):

    out_put = ''
    with open(path, 'rb') as f:
        content = f.read()
        array = content.splitlines()
        for item in array:
            item_array = ("%s" % item).split(',')
            scheme = item_array[2]
            out_put = out_put + "<string>"+scheme+"</string>\r\n"

    print(out_put)


plist_make("/Users/daiyichao/Downloads/applist_sec.csv")

