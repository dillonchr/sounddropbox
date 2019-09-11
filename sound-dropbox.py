import sys
import time
import imaplib
import getpass
import email
import email.header
import datetime
import os

reload(sys)
sys.setdefaultencoding('utf8')

curr_dir='./media'

if 'EMAIL_ACCOUNT' not in os.environ:
    print "Missing EMAIL_ACCOUNT env var"
    sys.exit(1)

if 'EMAIL_PASS' not in os.environ:
    print "Missing EMAIL_PASS env var"
    sys.exit(1)

EMAIL_ACCOUNT=os.environ['EMAIL_ACCOUNT']
EMAIL_PASS=os.environ['EMAIL_PASS']
EMAIL_FOLDER = "INBOX"

def process_mailbox(M):

    rv, data = M.search(None, r'(X-GM-RAW "subject:\"media\"")')
    if rv != 'OK':
        print "No messages found!"
        return

    for num in data[0].split():
        rv, data = M.fetch(num, '(RFC822)')
        if rv != 'OK':
            print "ERROR getting message", num
            return

        print '-----'
        msg = email.message_from_string(data[0][1])
        decode = email.header.decode_header(msg['Subject'])[0]
        subject = unicode(decode[0])
        print 'Message %s: %s' % (num, subject)

        sender = msg['from'].split()[-1]
        sender = sender[1:]
        sender = sender[:-1]

        print 'Sender: ', sender
        #print 'Raw Date:', msg['Date']

        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                print part.get_payload() 

        # Now convert to local date-time
        date_tuple = email.utils.parsedate_tz(msg['Date'])
        if date_tuple:
            local_date = datetime.datetime.fromtimestamp(
                email.utils.mktime_tz(date_tuple))
            folder_name=local_date.strftime("%Y-%m-%d")
            print "Dated: ", \
                local_date.strftime("%a, %d %b %Y %H:%M:%S")

        fcount = 0
        for part in msg.walk():

            if(part.get('Content-Disposition' ) is not None ) :
                filename = folder_name + '-' + part.get_filename()
                print filename


                final_path= os.path.join(curr_dir, filename)

                if not os.path.isfile(final_path) :
                   fp = open(curr_dir+"/"+(filename), 'wb')
                   fp.write(part.get_payload(decode=True))
                   fcount += 1
                   fp.close()

        print '%d attachment(s) fetched' %fcount
        print '-----\n\n'
    try:
        print 'Sleeping for 10 min'
        time.sleep(60 * 10)
        process_mailbox(M)
    except KeyboardInterrupt as e:
        print "Caught keyboard interrupt. Canceling tasks..."
        M.close()
        M.logout()
        print "Done."



M = imaplib.IMAP4_SSL('imap.gmail.com')

try:
    rv, data = M.login(EMAIL_ACCOUNT, EMAIL_PASS)
except imaplib.IMAP4.error:
    print "LOGIN FAILED!!! "
    sys.exit(1)

print data

rv, mailboxes = M.list()
if rv == 'OK':
    print "Mailboxes located."

rv, data = M.select(EMAIL_FOLDER)

if rv == 'OK':
    print "Now processing mailbox ...\n"
    if 'media' not in os.listdir('./'):
        os.mkdir('media')
    process_mailbox(M)
else:
    print "ERROR: Unable to open mailbox ", rv

