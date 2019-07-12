# py-august [![Build Status](https://travis-ci.org/snjoetw/py-august.svg?branch=master)](https://travis-ci.org/snjoetw/py-august)
Python API for August Smart Lock and Doorbell. This is used in [Home Assistant](https://home-assistant.io) but should be generic enough that can be used elsewhere.

## Classes
### Authenticator

Authenicator is responsible for all authentication related logic, this includes authentication and verifying the account belongs to the user by sending a verification code to email or phone.

#### Constructor

| Argument                 | Description                    |
| ------------------------ | ------------------------------ |
| api                      | See Api class.                  |
| login_method             | Login method, either "phone" or "email".            |
| username                 | If you're login_method is phone, then this is your full phone# including "+" and country code; otherwise enter your email address here. |
| password                 | Password.      |
| install_id*              | ID that's generated when August app is installed. If not specified, Authenticator will auto-generate one. If an install_id is provisioned, then it's good to provide the provisioned install_id as you'll bypass verification process. |
| access_token_cache_file* | Path to access_token cache file. If specified, access_token info will be cached in the file. Subsequent authentication will utilize information in the file to determine correct authentication state.|

\* means optional

#### Methods

##### authenticate

Authenticates using specified login_method, username and password. 

Outcome of this method is an Authentication object. Use Authentication.state figure out authentication state. User is authenticated only if Authentication.state = AuthenticationState.AUTHENTICATED.

If an authenticated access_token is already in the access_token_cache_file, this method will return cached authentication.


##### send_verification_code

Sends a 6-digits verification code to phone or email depending on login_method.

##### validate_verification_code

Validates verification code. This method returns ValidationResult. Check the value to see if verification code is valid or not.


## Install

```bash
pip install py-august
```


## Usage
```python
from august.api import Api 
from august.authenticator import Authenticator, AuthenticationState

api = Api(timeout=20)
authenticator = Authenticator(api, "phone", "YOUR_USERNAME", "YOUR_PASSWORD",
                              access_token_cache_file="PATH_TO_ACCESS_TOKEN_CACHE_FILE")

authentication = authenticator.authenticate()

# State can be either REQUIRES_VALIDATION, BAD_PASSWORD or AUTHENTICATED
# You'll need to call different methods to finish authentication process, see below
state = authentication.state

# If AuthenticationState is BAD_PASSWORD, that means your login_method, username and password do not match

# If AuthenticationState is AUTHENTICATED, that means you're authenticated already. If you specify "access_token_cache_file", the authentication is cached in a file. Everytime you try to authenticate again, it'll read from that file and if you're authenticated already, Authenticator won't call August again as you have a valid access_token


# If AuthenticationState is REQUIRES_VALIDATION, then you'll need to go through verification process
# send_verification_code() will send a code to either your phone or email depending on login_method
authenticator.send_verification_code()
# Wait for your code and pass it in to validate_verification_code()
validation_result = authenticator.validate_verification_code(123456)
# If ValidationResult is INVALID_VERIFICATION_CODE, then you'll need to either enter correct one or resend by calling send_verification_code() again
# If ValidationResult is VALIDATED, then you'll need to call authenticate() again to finish authentication process
authentication = authenticator.authenticate()

# Once you have authenticated and validated you can use the access token to make API calls
locks = api.get_locks(authentication.access_token)

