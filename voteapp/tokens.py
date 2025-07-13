from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six

class VoterEmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, voter, timestamp):
        return f"{voter.pk}{timestamp}{voter.is_verified}"

email_verification_token = VoterEmailVerificationTokenGenerator()
