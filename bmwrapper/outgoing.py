import asyncore
from smtpd import SMTPServer
import email.parser
import email.header
import logging

import bminterface


class OutgoingServer(SMTPServer):
    address_label = u'bmwrapper'

    def __init__(self, local_address, remote_address):
        SMTPServer.__init__(self, local_address, remote_address)  # Why are we using old-style classes

        logging.info("SMTP: {0}".format(bminterface.client_status_summary()))

        addresses = bminterface.list_my_addresses()
        logging.debug("Address list: {0}".format(addresses))

        if not addresses:
            logging.debug("No send addresses found. Creating a random address..")
            address = bminterface.create_random_address(OutgoingServer.address_label)
        else:
            addresses_with_label = [address for address in addresses if
                                    address[u'label'] == OutgoingServer.address_label]
            if len(addresses_with_label) >= 1:
                address = addresses_with_label[0][u'address']
            else:
                logging.info("Label {0} not found in Bitmessage addresses.".format(OutgoingServer.address_label))
                address = addresses[0][u'address']

        logging.info("SMTP: First BM-address: {0}".format(address))

    def process_message(self, peer, mailfrom, rcpttos, data):
        parser = email.parser.FeedParser()
        parser.feed(data)
        msg = parser.close()

        to_address = msg['To']
        from_address = msg['From']
        subject = u' '.join(unicode(t[0], t[1] or 'UTF-8') for t in email.header.decode_header(msg['Subject'])).encode(
            'UTF-8')
        body = self._bmformat(msg)

        # Make sure we don't send an actually blank subject or body--this can cause problems.
        if not subject:
            subject = ' '
        if not body:
            body = ' '

        if bminterface.send(to_address, from_address, subject, body):
            logging.info("Message queued for sending...")
        else:
            logging.warn("There was an error trying to send the message...")

        return 0

    def _bmformat(self, msg):
        disclaimer = ""
        image_notice = ""
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            disclaimer = "\n" \
                         "<!-- Email sent from bmwrapper -->\n" \
                         "<!-- Thanks Arceliar, https://github.com/Arceliar/bmwrapper -->\n"
            image_notice = "<!-- Note: An image is attached below -->\n"
        if not msg.is_multipart():
            # This is a single part message, so there's nothing to do.
            # Will still parse, just to get rid of awkward quote '>' everywhere.
            my_text, old_text = self._parse_quote_text(msg.get_payload())
            return my_text + old_text
        else:
            # This is a multipart message.
            # Unfortunately, now we have to actually do work.
            my_text, old_text, image = self._recurse_parse(msg)
            return image_notice + my_text + old_text + disclaimer + image

    def _recurse_parse(self, msg):
        text = ''
        image = ''
        for item in msg.get_payload():
            if 'text/plain' in item['Content-Type']:
                text += item.get_payload()
            elif 'image' in item['Content-Type']:
                [filetype, name] = item['Content-Type'].rstrip().split('\n')
                name = name.replace('name', 'alt')
                imageraw = item.get_payload().rstrip().split('\n')
                imagedata = ''
                for line in imageraw:
                    if not line[0] == '-':
                        imagedata += line
                image += '<img ' + name + ' src="data:' + filetype + 'base64,' + imagedata + '" />'
            elif 'multipart' in item['Content-Type']:
                first_text_new, text_new, image_new = self._recurse_parse(item)
                text += first_text_new + text_new
                image += image_new
            else:
                # Note that there's a chance we may die horribly if nothing returns.
                pass
        first_text, text = self._parse_quote_text(text)
        return first_text, text, image

    @staticmethod
    def _parse_quote_text(text):
        raw_text = text.split('\n')
        temp_text = []
        text = ''
        first_text = ''
        n = 0
        while len(raw_text):
            for line in range(len(raw_text)):
                if raw_text[line]:
                    if raw_text[line][0] == '>':  # and raw_text[line].strip('>')[0] == ' '):
                        raw_text[line] = raw_text[line][1:]
                        if raw_text[line] and raw_text[line][0] == ' ':
                            raw_text[line] = raw_text[line][1:]
                        temp_text.append(raw_text[line])
                    else:
                        if n == 0:
                            first_text += raw_text[line] + '\n'
                        else:
                            text += raw_text[line] + '\n'
                else:
                    if n == 0:
                        first_text += '\n'
                    else:
                        text += '\n'
            if len(temp_text):
                text += '\n\n------------------------------------------------------\n'
            raw_text = temp_text
            temp_text = []
            n += 1
        text = text.rstrip('\n')
        first_text = first_text.rstrip('\n')
        return first_text, text


def run():
    OutgoingServer(('localhost', 12345), None)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    run()
