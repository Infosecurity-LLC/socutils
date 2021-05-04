#!/usr/bin/python3
import logging
import mimetypes
import smtplib
import os
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from .exceptions import MailException

logger = logging.getLogger('socutils.mail')


def get_mails_string(mails):
    if isinstance(mails, list):
        return ', '.join(mails)
    elif isinstance(mails, str):
        return mails
    else:
        raise TypeError('mails list should be a string or list of strings')


def _create_message(sender, recipients, subj, html_text, from_=None, rt=None,
                    cc=None):
    """ Создание письма. """
    msg = MIMEMultipart('related')
    msg_alternative = MIMEMultipart('alternative')
    msg.attach(msg_alternative)
    html_part = MIMEText(html_text, 'html', "utf-8")

    msg['Subject'] = subj
    if from_:
        msg['From'] = from_
    else:
        msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    if rt:
        msg['reply-to'] = rt
    if cc:
        msg['Cc'] = get_mails_string(cc)
    msg_alternative.attach(html_part)
    # msg.attach(html_part)
    return msg


def _add_attachment(message, attachment):
    """ Добавление вложения atachement к письму message. """
    if not os.path.isfile(attachment):
        logger.error('File not exist: {}'.format(attachment))
        return None

    ctype, encoding = mimetypes.guess_type(attachment)
    if ctype is None or encoding is not None:
        # No guess could be made, or the file is encoded (compressed), so
        # use a generic bag-of-bits type.
        ctype = 'application/octet-stream'
    maintype, subtype = ctype.split('/', 1)
    """    if maintype == 'text':
        with open(attachment) as fp:
            part = MIMEText(fp.read(), _subtype=subtype)
    else:"""
    with open(attachment, 'rb') as fp:
        part = MIMEBase(maintype, subtype, name=os.path.basename(attachment))
        part.set_payload(fp.read())
        encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'inline',
                    filename=os.path.basename(attachment))
    part.add_header('Content-ID', '<{}>'.format(os.path.basename(attachment)))
    part.add_header('Content-Description', '{}'.format(os.path.basename(attachment)))
    part.add_header('Content-Transfer-Encoding', 'base64')
    message.attach(part)


class MailSender:
    """ Содержит настройки для подключения к SMTP серверу. """

    def __init__(self, server, port, username=None, passwd=None, ssl=False,
                 login=True):
        self._server = server
        self._port = port
        self._username = username
        self._passwd = passwd
        self._ssl = ssl
        self._login = login

    def send_msg(self, sender, recipients, subject, email_text,
                 attachments=None, from_=None, rt=None, cc=None):
        """ Создание и отправка письма указанным получателям. """
        if not recipients:
            raise MailException('No recipients')
        if not isinstance(recipients, list):
            recipients = [recipients]

        with smtplib.SMTP(self._server, self._port) as smtp:
            # smtp.ehlo()
            if self._ssl:
                smtp.starttls()
                # smtp.ehlo()
            if self._username and self._passwd and self._login:
                smtp.login(self._username, self._passwd)
            msg = _create_message(sender, recipients, subject, email_text,
                                  from_, rt, cc)
            for attachment in attachments or []:
                _add_attachment(msg, attachment)
            try:
                smtp.sendmail(sender, recipients, msg.as_string())
            except smtplib.SMTPException as err:
                raise MailException(err)

    def send_separate(self, sender, recipients, subject, email_text,
                      attachments=None, from_=None, rt=None, cc=None):
        if not recipients:
            raise MailException('No recipients')
        if not isinstance(recipients, list):
            recipients = [recipients]
        for recipient in recipients:
            self.send_msg(sender, recipient, subject, email_text, attachments,
                          from_, rt, cc)


if __name__ == '__main__':
    pass
