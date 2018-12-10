import sqlite3
import time

conn = sqlite3.connect("eatingtoday.db")


def create_user(nickname, password):
    if conn.execute("SELECT count(*) FROM user WHERE nickname=?", (nickname, )).fetchone()[0] != 0:
        return None  # 注册失败
    conn.execute("INSERT INTO user SELECT ifnull(max(user_id),0)+1,?,? FROM user", (nickname, password))
    conn.commit()
    uid = conn.execute("SELECT user_id FROM user WHERE nickname=? AND password=?", (nickname, password)).fetchone()[0]
    return uid  # 返回user_id


def user_verification(name, psw):
    uid = conn.execute("SELECT user_id FROM user WHERE nickname=? AND password=?", (name, psw)).fetchone()
    if uid:
        return uid[0]   # 验证成功，返回user_id
    else:
        return None     # 验证失败


def new_food(food_name):
    if conn.execute("SELECT count(*) FROM foods WHERE food_name=?", (food_name, )).fetchone()[0] != 0:
        return None  # 失败
    conn.execute("INSERT INTO foods SELECT ifnull(max(food_id),0)+1,? FROM foods", (food_name, ))
    conn.commit()
    fid = conn.execute("SELECT food_id FROM foods WHERE food_name=?", (food_name, )).fetchone()[0]
    return fid  # 返回food_id


def new_history(user_id, food_id):
    conn.execute("INSERT INTO history VALUES(?,?,?)", (user_id, food_id, time.time()))
    conn.commit()


def edit_comment(user_id, food_id,  # 不可空，若存在评论则修改，若不存在则新建
                 score, hot, salty, sweet, sour, oily,   # 各项评分（可空）
                 comment, loc_lng, loc_lat):    # 评论，图片路径，经纬度（可空）
    c = conn.execute("SELECT count(*) FROM comments WHERE user_id=? AND food_id=?", (user_id, food_id)).fetchone()[0]
    if c == 0:
        conn.execute("INSERT INTO "
                     "comments(user_id, food_id, score, hot, salty, sweet, sour, oily, comment, loc_lng, loc_lat) "
                     "VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                     (user_id, food_id, score, hot, salty, sweet, sour, oily, comment, loc_lng, loc_lat))
    else:
        conn.execute("UPDATE comments SET score=?, hot=?, salty=?, sweet=?, sour=?, oily=?,"
                     "comment=?, loc_lng=?, loc_lat=? WHERE user_id=? AND food_id=?",
                     (score, hot, salty, sweet, sour, oily, comment, loc_lng, loc_lat, user_id, food_id))
    conn.commit()


def picture_path(user_id, food_id, pic_path):   # 将图片路径注册到评论中
    c = conn.execute("SELECT count(*) FROM comments WHERE user_id=? AND food_id=?", (user_id, food_id)).fetchone()[0]
    if c == 0:
        conn.execute("INSERT INTO comments(user_id, food_id, img) VALUES (?,?,?)", (user_id, food_id, pic_path))
    else:
        conn.execute("UPDATE comments SET img=? WHERE user_id=? AND food_id=?", (pic_path, user_id, food_id))
    conn.commit()
