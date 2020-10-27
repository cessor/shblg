import imaplib
import email
import email.utils
from email.header import decode_header
from typing import Type, TypeVar, List
import pgpy  # type: ignore

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from django.db.models.manager import Manager

from blog.models import Article, Author  # type: ignore


# https://stackoverflow.com/questions/44640479/mypy-annotation-for-classmethod-returning-instance
T = TypeVar('T', bound='MultipartMessage')


class VerificationFailed(Exception):
    pass


class Mismatch(VerificationFailed):
    def _message(self):
        raise NotImplementedError()

    def __init__(self, actual: str, expected: str):
        self._actual = actual
        self._expected = expected
        super().__init__(self._message())


class NotMultipart(VerificationFailed):
    def __init__(self, sender: str):
        super().__init__(
            f"An email by {sender} was found, but it is not a multipart "
            f"message. Did the author forget to sign it? "
            f"This email will be rejected."
        )


class AuthorUnknown(VerificationFailed):
    def __init__(self, sender: str):
        super().__init__(
            f"An email by {sender} was found, but this author is unknown. "
            f"This email will be rejected."
        )


class AuthorNotVerifyable(VerificationFailed):
    def __init__(self, sender: str):
        super().__init__(
            f"Author {sender} has not provided a PGP key and "
            f"therefore their emails can't be verfied. "
            f"This email will be rejected."
        )


class NoSignature(VerificationFailed):
    def __init__(self, message: email.message.Message):
        super().__init__(
            "This email was not signed. The sender's identity can't be "
            "verified. This email will be rejected."
        )


class SignatureMismatch(Mismatch):
    def _message(self):
        return (
            f'The provided signature was created by a key with the fingerprint '
            f'{self.actual} and did not match the authors configured public key '
            f'{self.expected}. This email was likely sent by someone else who '
            f'is not the author and will therefore be rejected.'
        )


class PublicKeyMismatch(Mismatch):
    def _message(self):
        return (
            f'The attached public key {self.actual} did not match the '
            f'authors configured public key {self.expected}. '
            f'This email was likely sent by someone else who '
            f'is not the author and will therefore be rejected.'
        )


class VerifiedMessage:
    def __init__(self, subject: str, body: str, author: Author):
        self._subject = subject
        self.body = body
        self.author = author

    @property
    def subject(self):
        text, encoding = decode_header(self._subject)[0]
        return text.decode(encoding)


class MultipartMessage:
    def __init__(self, message: email.message.Message):
        # I am assuming that all messages are sent as pgp-signed
        self._message = message
        self._body = None
        self._signature = None
        self._public_key = None
        if not message.is_multipart():
            raise NotMultipart(sender=self.sender_address)
        self._parse()

    @classmethod
    def from_bytes(cls: Type[T], message: bytes) -> T:
        # Convert from raw data
        return cls(email.message_from_bytes(message))

    @property
    def sender_address(self) -> str:
        sender = self._message.get('from')
        name, email_address = email.utils.parseaddr(sender)
        return email_address

    def verify(self, authors: Manager) -> VerifiedMessage:
        try:
            author = authors.get(email=self.sender_address)
        except ObjectDoesNotExist:
            raise AuthorUnknown(self.sender_address)
        if not author.pgp_public_key:
            raise AuthorNotVerifyable(author)

        expected_public_key = pgpy.PGPKey()
        expected_public_key.parse(author.pgp_public_key)

        # Mandatory: Verify Signature
        if not self._signature:
            raise NoSignature(self)

        attached_signature = pgpy.PGPSignature()
        attached_signature.parse(self._signature)

        # Verify signature
        if not (attached_signature.signer_fingerprint == expected_public_key.fingerprint):
            raise SignatureMismatch(
                expected_public_key.fingerprint,
                attached_signature.signer_fingerprint
            )

        # Optional: If a public key was attached, verify it for good measure
        if self._public_key:
            attached_pub_key = pgpy.PGPKey()
            attached_pub_key.parse(self._public_key)

            # Verify public Key
            if not expected_public_key.fingerprint == attached_pub_key.fingerprint:
                raise PublicKeyMismatch(
                    expected_public_key,
                    attached_pub_key
                )

        return VerifiedMessage(
            subject=self._message.get('subject'),
            body=self._body,
            author=author
        )

    def _parse(self):
        for part in self._message.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            # Actual Content
            if (content_type == "text/plain"
                    and "attachment" not in content_disposition):
                self._body = part.get_payload(decode=True).decode()

            # PGP Signature
            if (content_type == "application/pgp-signature"
                    and 'attachment' in content_disposition):
                self._signature = part.get_payload(decode=True).decode('ascii')

            # Attached PGP Public key
            if (content_type == "application/pgp-keys"
                    and 'attachment' in content_disposition):
                self._public_key = part.get_payload(
                    decode=True).decode('ascii')


class ImapError(Exception):
    def __init__(self, error_message: List[bytes]):
        super().__init__(message[0])


class Command(BaseCommand):
    LIMIT = 1024

    help = 'Fetches emails from the configured IMAP postbox'

    def _move_email(self, imap, mail_id, postbox):
        status, message = imap.copy(mail_id, postbox)
        if not status == 'OK':
            raise ImapError(message)

        # https://docs.python.org/3/library/imaplib.html#imaplib.IMAP4.store
        status, message = imap.store(mail_id, '+FLAGS', '\\Deleted')
        if not status == 'OK':
            raise ImapError(message)

    def handle(self, *args, **options):
        with imaplib.IMAP4_SSL(
            host=settings.IMAP_HOST,
            port=settings.IMAP_PORT,
            # certfile=settings.IMAP_CERT_FILE
        ) as imap:
            imap.login(settings.IMAP_USERNAME, settings.IMAP_PASSWORD)

            # Select default postbox
            imap.select()

            # Fetch ids of ALL mails
            status, mails = imap.search(None, 'ALL')
            assert status == 'OK'

            # Split ids from response
            mail_ids = mails[0].split()

            # Sort and limit
            mail_ids = list(reversed(mail_ids))[:self.LIMIT]

            for mail_id in mail_ids:
                # Fetch actual mail
                status, response = imap.fetch(mail_id, '(RFC822)')
                (flags, message_bytes), _ = response

                try:
                    # Verify Message
                    message = (
                        MultipartMessage
                        .from_bytes(message_bytes)
                        .verify(Author.objects)
                    )
                except VerificationFailed as e:
                    self.stdout.write(
                        self.style.ERROR(
                            '%s' % e
                        )
                    )
                    self._move_email(
                        imap, mail_id, settings.IMAP_BOX_DEADLETTER
                    )
                else:
                    try:
                        article = Article.objects.create(
                            title=message.subject,
                            content=message.body,
                        )
                        article.authors.add(message.author)
                        article.save()

                    except IntegrityError:
                        self.stdout.write(
                            self.style.ERROR(
                                'It looks like this article already exists: "%s"' % message.subject
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.SUCCESS(
                                'Successfully created article: "%s"' % article.title
                            )
                        )

                    self._move_email(
                        imap, mail_id, settings.IMAP_BOX_PUBLISHED
                    )

            imap.expunge()
