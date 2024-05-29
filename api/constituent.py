class Constituent:
    def __init__(self, data: list):
        self.id, self.name = data
        self.name = self.name.strip().replace('  ', ' ')
        self.email = None
        self._status = None
        self.do_not_email = True

    def add_email(self, email, do_not_email):
        self.email = email
        self.do_not_email = do_not_email

    def status(self, status):
        self._status = status
    
    def has_email(self):
        return bool(self.email)

    def __str__(self) -> str:
        return self.name

if __name__ == "__main__":
    from test_names import names
    constits = [Constituent(i) for i in names.get('names')]
    [print(i) for i in constits]
