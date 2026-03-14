class SimClock:
    def __init__(self):
        self.game_minutes = 720  # 12:00 por defecto

    def update(self, pitch_rotation):
        self.game_minutes = int(((float(pitch_rotation) - 90) % 360) * 4)

    def time_str(self):
        total = self.game_minutes % 1440
        h = total // 60
        m = total % 60
        return f"{h:02d}:{m:02d}"

    def period(self):
        h = (self.game_minutes % 1440) // 60
        if 6 <= h < 12:  return "mañana"
        if 12 <= h < 18: return "tarde"
        if 18 <= h < 22: return "noche"
        return "madrugada"

    def is_day(self):
        h = (self.game_minutes % 1440) // 60
        return 6 <= h < 20

    def to_dict(self):
        return {"game_minutes": self.game_minutes}

    @staticmethod
    def from_dict(data):
        sc = SimClock()
        sc.game_minutes = data.get("game_minutes", 720)
        return sc