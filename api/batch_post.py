try:
    from api.constituent import Constituent
except ModuleNotFoundError:
    from constituent import Constituent

class BatchPost:
    def __init__(self, data: dict):
        self.batch = data.get('batch')
        self.notif_email = data.get('email')
        self.tag = data.get('tag')
        self.tag_state = data.get('tag_state')
        constits = [(i[0], i[1]) for i in data.get('names')]
        self.constits = [Constituent(i) for i in list(set(constits))]
        self.cc = None
        self.message = None

    @property
    def has_emails(self):
        for i in self.constits:
            if i.has_email():
                return True

        return False

    def gen_message(self):
        req_type = 'tag' if self.tag_state else 'untag'
        recip = self.notif_email[0].upper() + self.notif_email[1:-12]
        success = [i for i in self.constits if i._status == 'success']
        tag_failed = [i for i in self.constits if i._status == 'tag failed']
        no_consent = [i for i in self.constits if i._status == 'no consent']
        no_email = [i for i in self.constits if i._status in ['missing', 'error']]

        errors = tag_failed or no_consent or no_email

        string = f'Hi {recip},\n\nThe following {len(success)} people were {req_type}ged {"with" if self.tag_state else "from"} \'{self.tag}\':\n'
        for i in success:
            string += f'  •  {i.name.strip()}, {i.email}\n'

        if errors:
            if tag_failed:
                string += '\nDrip tagging failed for these people:\n'
                for i in tag_failed:
                    string += f'  •  {i.name.strip()}, {i.email}\n'
            if no_consent:
                string += '\nThese people are marked as do not email:\n'
                for i in no_consent:
                    string += f'  •  {i.name.strip()}, {i.email}\n'
            if no_email:
                string += '\nAn email address was not found for these people in BB:\n'
                for i in no_email:
                    string += f'  •  {i.name.strip()}\n'
            self.cc = 'andrew@glacier.org'

        self.message = string

    def gen_resp(self) -> dict:
        req_type = 'Tagging' if self.tag_state else 'Untagging'
        success = [i for i in self.constits if i._status == 'success']
        email_success = [i.name for i in self.constits if (i._status == 'success' and not i.do_not_email)]
        email_fail = [i.name for i in self.constits if (i._status != 'success' and not i.do_not_email)]
        email_no_consent = [i.name for i in self.constits if i.do_not_email]

        message = f"{req_type} Processed for {self.batch}. {len(success)} found."
        return {'message': message, 'outcome': "Success!", 'success': email_success, 'fail': email_fail, 'noConsent': email_no_consent}

    def __str__(self) -> str:
        string = ''
        for i in self.constits:
            string += f'{i.name}, {i.email}, {i._status}\n'

        return string
