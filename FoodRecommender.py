import DBHelper


MAX_SCORE = 5


class FoodRecommender:
    def __init__(self, user_id):
        self.user_id = user_id
        self.sweet_lb = 0
        self.sweet_ub = MAX_SCORE
        self.sour_lb = 0
        self.sour_ub = MAX_SCORE
        self.hot_lb = 0
        self.hot_ub = MAX_SCORE
        self.oily_lb = 0
        self.oily_ub = MAX_SCORE
        self.salty_lb = 0
        self.salty_ub = MAX_SCORE
        self.sweet, self.sour, self.hot, self.oily, self.salty = DBHelper.conn.execute(
            "SELECT ifnull(avg(score*hot),2.5),ifnull(avg(score*salty),2.5),ifnull(avg(score*sweet),2.5),"
            "ifnull(avg(score*sour),2.5),ifnull(avg(score*oily),2.5) FROM comments WHERE user_id=?;", (self.user_id,)).fetchone()
        self.except_list = []

    def get_recommend(self, num):
        res = DBHelper.conn.execute("""
    SELECT food_id,(hot-ho)*(hot-ho)+(salty-sa)*(salty-sa)+(sweet-sw)*(sweet-sw)+(sour-so)*(sour-so)+(oily-oi)*(oily-oi) as d FROM 
    (SELECT food_id, ifnull(avg(hot),2.5) as hot, ifnull(avg(salty),2.5) as salty, ifnull(avg(sweet),2.5) as sweet,
    ifnull(avg(sour),2.5) as sour, ifnull(avg(oily),2.5) as oily,
     ? as ho, ? as sa, ? as sw, ? as so, ? as oi FROM comments WHERE food_id NOT IN (%s) GROUP BY food_id)
        WHERE hot BETWEEN ? AND ?
        AND salty BETWEEN ? AND ?
        AND sweet BETWEEN ? AND ?
        AND sour BETWEEN ? AND ?
        AND oily BETWEEN ? AND ?
        ORDER BY d DESC LIMIT ?;""" % ",".join(self.except_list), (self.hot, self.salty, self.sweet, self.sour, self.oily,
                                      self.hot_lb, self.hot_ub, self.salty_lb, self.salty_ub,
                                      self.sweet_lb, self.sweet_ub, self.sour_lb, self.sour_ub,
                                      self.oily_lb, self.oily_ub, num)).fetchall()
        return res

    def too_sweet(self, food_id):
        s = DBHelper.conn.execute("SELECT ifnull(avg(sweet),-1) WHERE food_id=?", (food_id, )).fetchone()[0]
        if s == -1:
            self.except_list.append(str(food_id))
        else:
            self.sweet_ub = s
            self.sweet = (self.sweet_lb+ self.sweet_ub)/2

    def not_sweet(self, food_id):
        s = DBHelper.conn.execute("SELECT ifnull(avg(sweet),-1) WHERE food_id=?", (food_id, )).fetchone()[0]
        if s == -1:
            self.except_list.append(str(food_id))
        else:
            self.sweet_lb = s
            self.sweet = (self.sweet_lb+ self.sweet_ub)/2

    def too_sour(self, food_id):
        s = DBHelper.conn.execute("SELECT ifnull(avg(sour),-1) WHERE food_id=?", (food_id, )).fetchone()[0]
        if s == -1:
            self.except_list.append(str(food_id))
        else:
            self.sour_ub = s
            self.sour = (self.sour_lb+ self.sour_ub)/2

    def not_sour(self, food_id):
        s = DBHelper.conn.execute("SELECT ifnull(avg(sour),-1) WHERE food_id=?", (food_id, )).fetchone()[0]
        if s == -1:
            self.except_list.append(str(food_id))
        else:
            self.sour_lb = s
            self.sour = (self.sour_lb+ self.sour_ub)/2

    def tasteless(self, food_id):
        s = DBHelper.conn.execute("SELECT ifnull(avg(hot),-1), ifnull(avg(oily),-1), ifnull(avg(salty),-1) "
                                  "WHERE food_id=?", (food_id, )).fetchone()
        if min(s) == -1:
            self.except_list.append(str(food_id))
        if s[0] != -1:
            self.hot_lb = s[0]
            self.hot = (self.hot_lb+ self.hot_ub)/2
        if s[1] != -1:
            self.oily_lb = s[1]
            self.oily = (self.oily_lb+ self.oily_ub)/2
        if s[2] != -1:
            self.salty_lb = s[2]
            self.salty = (self.salty_lb+ self.salty_ub)/2

    def too_hot(self, food_id):
        s = DBHelper.conn.execute("SELECT ifnull(avg(hot),-1) WHERE food_id=?", (food_id, )).fetchone()[0]
        if s  ==  -1:
            self.except_list.append(str(food_id))
        else:
            self.hot_ub = s
            self.hot = (self.hot_lb+ self.hot_ub)/2

    def too_oily(self, food_id):
        s = DBHelper.conn.execute("SELECT ifnull(avg(oily),-1) WHERE food_id=?", (food_id, )).fetchone()[0]
        if s == -1:
            self.except_list.append(str(food_id))
        else:
            self.oily_ub = s
            self.oily = (self.oily_lb+ self.oily_ub)/2

    def too_salty(self, food_id):
        s = DBHelper.conn.execute("SELECT ifnull(avg(salty),-1) WHERE food_id=?", (food_id, )).fetchone()[0]
        if s == -1:
            self.except_list.append(str(food_id))
        else:
            self.salty_ub = s
            self.salty = (self.salty_lb+ self.salty_ub)/2

    def no_reason(self, food_id):
        self.except_list.append(str(food_id))
