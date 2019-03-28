class commonutils:
    def __init__(self):
        pass

    @staticmethod
    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False
