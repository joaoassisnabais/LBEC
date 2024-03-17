class Dto:
    def to_json(self) -> str:
        raise NotImplementedError()

class TokenDto(Dto):
    def __init__(self, token, exp) -> None:
        self.token = token
        self.exp = exp

    def to_json(self) -> str:
        return {"token": self.token, "exp": str(self.exp)}