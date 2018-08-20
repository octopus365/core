# -*- coding: utf-8 -*-

import os, sys, glob
sys.path.append("./modules")
import numpy as np
import pandas as pd
import email
import zipfile
import datetime
import pickle

from modules.config import parent_dir_path
from modules.config import save_dir_path


def from_mhtml_to_df(mhtml_list, current_dir_path):
    summarized_list = []
    for target_mhtml in mhtml_list:
        mhtml_list = []
        mhtml_url = "Extraction Failure"
        with open(current_dir_path + "\\" + target_mhtml) as fin:
            msg = email.message_from_file(fin)
            for tmp_sentence in msg.items():
                if tmp_sentence[0]=="Snapshot-Content-Location":
                    mhtml_url = tmp_sentence[1]
            mhtml_date = target_mhtml[0:6]
            mhtml_name = target_mhtml[7:-6]
            mhtml_name_wlink = '<a href=\"{}\">'.format(mhtml_url) + mhtml_name + '</a>'

        mhtml_list.append(mhtml_date)
        mhtml_list.append(mhtml_name_wlink)
        #mhtml_list.append(mhtml_url)
        summarized_list.append(mhtml_list)

    return pd.DataFrame(summarized_list, columns=['Date', 'Title'])

if __name__ == "__main__":
    dir_name_list = os.listdir(parent_dir_path)
    dir_name_list.remove("Tech")  # Tech has sub folders
    dir_name_list.remove("Column")
    dir_name_list.remove("__forAirg")
    if os.path.exists(save_dir_path + "\\tmp_csv\\link_num_dic.pickle"):
        with open(save_dir_path + "\\tmp_csv\\link_num_dic.pickle", mode='rb') as f:
            link_num_dic = pickle.load(f)
    else:
        link_num_dic = {}

    tech_dir_list = os.listdir(parent_dir_path + "\\Tech")
    for tech_dir_tmp in tech_dir_list:
        dir_name_list.extend(["Tech\\" + tech_dir_tmp])

    column_dir_list = os.listdir(parent_dir_path + "\\Column")
    for column_dir_tmp in column_dir_list:
        dir_name_list.extend(["Column\\" + column_dir_tmp])

    for dir_i, target_dir_tmp in enumerate(dir_name_list):
        current_dir_path = parent_dir_path + "\\" + target_dir_tmp
        mhtml_list = os.listdir(current_dir_path)
        csv_df = from_mhtml_to_df(mhtml_list, current_dir_path)
        if (target_dir_tmp in link_num_dic):
            past_link_num = link_num_dic[target_dir_tmp]
        else:
            past_link_num = 0

        if len(csv_df.index)>past_link_num:
            if target_dir_tmp[0:4] == "Tech":
                save_file_name = save_dir_path + "\\tmp_csv\\Tech_" + target_dir_tmp[5:] + ".csv"
            elif target_dir_tmp[0:6] == "Column":
                save_file_name = save_dir_path + "\\tmp_csv\\Column_" + target_dir_tmp[7:] + ".csv"
            else:
                save_file_name = save_dir_path + "\\tmp_csv\\" + target_dir_tmp + ".csv"

            csv_df.to_csv(save_file_name, index=False, encoding="utf-8")
            link_num_dic[target_dir_tmp] = len(csv_df.index)

            print(target_dir_tmp + " is created, {}/{}".format(dir_i + 1, len(dir_name_list)))
        else:
            print(target_dir_tmp + " is passed, {}/{}".format(dir_i + 1, len(dir_name_list)))


    # make zip
    today_date = datetime.date.today()
    zip_name = today_date.strftime('%Y%m%d')
    with zipfile.ZipFile(save_dir_path + "\\" + zip_name + ".zip", 'w', compression=zipfile.ZIP_STORED) as new_zip:
        ziped_file_list = os.listdir(save_dir_path + "\\tmp_csv")
        for zip_tmp in ziped_file_list:
            new_zip.write(save_dir_path + "\\tmp_csv\\" + zip_tmp)

    # save dic
    with open(save_dir_path + "\\tmp_csv\\link_num_dic.pickle", mode='wb') as f:
        pickle.dump(link_num_dic, f)

    print("all work has been finished")