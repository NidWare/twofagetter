import time
import pyotp

class AuthenticatorModule:
    @staticmethod
    def generate_totp(secret):
        """
        Generate the current TOTP (Time-based One-Time Password) using the secret key.

        :param secret: Secret key used to generate the TOTP.
        :return: Current TOTP.
        """
        totp = pyotp.TOTP(secret)
        return totp.now()

    @staticmethod
    def get_fresh_totp(secret):
        """
        Get a fresh TOTP, ensuring it's not close to expiration.

        :param secret: Secret key used to generate the TOTP.
        :return: Fresh TOTP and time remaining.
        """
        totp = pyotp.TOTP(secret)

        while True:
            current_otp = totp.now()
            time_remaining = totp.interval - (time.time() % totp.interval)

            if time_remaining > totp.interval / 2:
                return current_otp, time_remaining

            time.sleep(time_remaining + 1)
