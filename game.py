class Game:
    def __init__(self):
        self.player_hp = 100
        self.boss_hp = 200
        self.calories = 0
        self.score = 0

    def squat(self):
        # 深蹲 → 攻擊 Boss
        self.boss_hp -= 10
        self.score += 5
        self.calories += 3

    def jumping_jack(self):
        # 開合跳 → 集氣，增加分數
        self.score += 2
        self.calories += 2

    def leg_raise(self):
        # 抬腿 → 閃避，避免扣血
        self.score += 3

    def plank(self):
        # 平板撐 → 防禦，回血
        self.player_hp += 2
        self.calories += 1

    def boss_attack(self):
        # Boss 隨機攻擊玩家
        self.player_hp -= 5
