#!/usr/bin/python
# -*- coding: utf-8 -*-



from pyscada.models import Mail, MailRecipient

from django.core.mail import send_mail
from django.conf import settings

from time import time


class Handler:
    def __init__(self):
        '''
        init the handler
        '''
        self.dt_set = 5;
        if settings.PYSCADA.has_key('mail_count_limit'):
            self.mail_count_limit        = float(settings.PYSCADA['mail_count_limit'])
        else:
            self.mail_count_limit        = 200 # only send 200 Mails per 24h per user
        

    def run(self):
        '''
        check for events and trigger action
        '''
        # Mail limitation ()
        
        blocked_recipient = []
    
        for mail in Mail.objects.filter(done=False,send_fail_count__lte=3):
            # limit number of mails in 24 h  
            for recipient in mail.mail_recipients.exclude(to_email__in=blocked_recipient):
                if recipient.mailqueue_set.filter(timestamp__gt=time()-(60*60*24)).count() > self.mail_count_limit:
                    blocked_recipient.append(recipient.pk)
            # send mails
            if mail.recipients_list(exclude_list=blocked_recipient):
                if send_mail(mail.subject,mail.message,mail.mail_from,mail.recipients_list(),fail_silently=True) >= 1:
                    mail.done       = True
                    mail.timestamp  = time()
                    mail.save()
                else:
                    mail.send_fail_count = mail.send_fail_count + 1
                    mail.timestamp  = time()
                    mail.save()
            else:
                mail.done       = True
                mail.timestamp  = time()
                mail.save()
