import json
import os
import time

from xhs.help import get_imgs_url_from_note, get_video_url_from_note, get_valid_path_name, download_file

from plus.sql_utils import SQL_UTILS
from xhs import XhsClient, Note, NoteType


class XhsClientPLUS(XhsClient):

    def get_follow_user_list(self):
        uri = "/api/sns/v2/user/followings/self"
        # "cursor": ,
        params = {"order": 2}
        return self.get(uri, params)

    def contains_chinese(self, input_str):
        for char in input_str:
            if '\u4e00' <= char <= '\u9fff':
                return True
        return False

    def get_user_all_note_ids(self, user_id: str):
        has_more = True
        cursor = ""
        result = []
        while has_more:
            res = self.get_user_notes(user_id, cursor)
            has_more = res["has_more"]
            cursor = res["cursor"]
            note_ids = map(lambda item: item["note_id"], res["notes"])
            result+=note_ids
            if (result.__len__() == 0): break
            last = result[result.__len__()-1]
            # if SQL_UTILS.contains(last, SQL_UTILS.LOCAL):
            #     break
        return result

    def create_image_note_by_path(self, path):
        for root, dirs, files in os.walk(path):
            try:

                if (files.__len__() > 0):
                    title = root.split("\\")[-1]
                    images = []
                    video_path = None
                    desc = ""
                    for file in files:
                        if file.endswith(".mp4"):
                            video_path = root + "/" + file
                        if file.endswith(".png"):
                            images.append(root + "/" + file)
                        if file.endswith(".md"):
                            title = file.split(".")[0]
                            with open(root + "/" + file, 'r', encoding="utf8") as f:
                                desc = f.read().split("----------------------------------")[0]
                                desc = desc.split("![")[0]
                    if not self.contains_chinese(title): title = "开心消消乐"+ str(time.time())
                    if SQL_UTILS.contains(title, SQL_UTILS.ADD): continue
                    print(title)
                    if (video_path is not None):
                        continue
                        # data = self.create_video_note(title=title.encode('unicode-escape').decode('utf-8'), video_path=video_path, desc=desc,
                        #                   is_private=False)
                    else:
                        data = self.create_image_note(title, desc, images, is_private=False)
                    SQL_UTILS.insert_data(title, json.dumps(data), SQL_UTILS.ADD)
            except Exception as e:
                SQL_UTILS.insert_data(title, "", SQL_UTILS.ADD)
                print(f"Error: {e}")
                break

    def save_search_notes(self, key:str, dir_path: str, crawl_interval: int = 1, page: int = 1,
                          page_size: int = 5):
        data = self.get_note_by_keyword(keyword =key)
        for item in data["items"]:
            try:
                if SQL_UTILS.contains(item["id"], SQL_UTILS.LOCAL): continue
                note = self.get_note_by_id(item["id"])
                if not os.path.exists(dir_path+"/"+key):
                    os.mkdir(dir_path+"/"+key)
                note = self.c_note(note)
                self.save_note_by_id(note.note_id, dir_path+"/"+key)
                SQL_UTILS.insert_data( note.note_id, json.dumps(note), SQL_UTILS.LOCAL)
            except Exception as e:
                print(e)
    def c_note(self, note):
        interact_info = note["interact_info"]
        note_info = Note(
            note_id=note["note_id"],
            title=note["title"],
            desc=note["desc"],
            type=note["type"],
            user=note["user"],
            img_urls=get_imgs_url_from_note(note),
            video_url=get_video_url_from_note(note),
            tag_list=note["tag_list"],
            at_user_list=note["at_user_list"],
            collected_count=interact_info["collected_count"],
            comment_count=interact_info["comment_count"],
            liked_count=interact_info["liked_count"],
            share_count=interact_info["share_count"],
            time=note["time"],
            last_update_time=note["last_update_time"],
        )
        return note_info
    def checkName(self, name):
        return name.replace("\\", "").replace("/", "").replace(":", "").replace("*", "").replace("?", "").replace("\"", "").replace("<", "").replace(">", "").replace("|", "").replace("\r", "").replace("\n", "")
    def save_user_all_notes(self, user_id: str, dir_path: str, crawl_interval: int = 1, is_video=False):
        nickName = self.checkName(self.get_user_info(user_id)["basic_info"]["nickname"])
        note_id_list = self.get_user_all_note_ids(user_id)
        note_id_list.reverse()
        print(note_id_list.__len__())
        for id in note_id_list:
            if not os.path.exists(dir_path+"/"+nickName):
                os.mkdir(dir_path+"/"+nickName)
            try:
                print(id)
                if SQL_UTILS.contains(id, SQL_UTILS.LOCAL): continue
                note = self.save_note_by_id(id, dir_path+"/"+nickName, is_video = is_video)
                SQL_UTILS.insert_data( id, json.dumps(note), SQL_UTILS.LOCAL)
            except Exception as e:
                print(e)
    def save_note_by_id(self, note_id: str, dir_path: str, note=None, is_video=False):
        if note is None:
            note = self.get_note_by_id(note_id)

        title = self.checkName(get_valid_path_name(note["title"]))
        content = note["title"]
        if note["desc"]:
            content += "\n" + note["desc"] + "\n"+"----------------------------------"+"\n"
        if not title:
            title = note_id


        # new_dir_path = os.path.join(dir_path, title)
        new_dir_path = dir_path
        if not os.path.exists(new_dir_path):
            os.mkdir(new_dir_path)

        if note["type"] == NoteType.VIDEO.value:
            video_url = get_video_url_from_note(note)
            video_filename = os.path.join(new_dir_path, f"{title}.mp4")
            download_file(video_url, video_filename)
            # content += f"\n![](11.mp4)"
            # with open(os.path.join(new_dir_path, f"{title}.md"), "w", encoding="utf-8") as f:
            #     f.write(content)
        elif (not is_video):
            img_urls = get_imgs_url_from_note(note)
            for index, img_url in enumerate(img_urls):
                filename = f"{index}.png"
                img_file_name = os.path.join(new_dir_path, f"{index}.png")
                download_file(img_url, img_file_name)
                content += f"\n![](./{filename})"
            with open(os.path.join(new_dir_path, f"{title}.md"), "w", encoding="utf-8") as f:
                f.write(content)
        return note
