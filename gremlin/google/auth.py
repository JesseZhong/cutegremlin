#!/usr/bin/env python3
from google.auth.transport import requests
from google.oauth2 import id_token


def generatePolicy(principal: str, idInformation: {}, effect: str, methodArn) -> {}:
    """
        Generates a policy based off of the user's information.
    """
    authResponse: {} = {}
    authResponse['principalId'] = principal

    if effect and methodArn:
        authResponse['policyDocument'] = {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Sid': 'FirstStatement',
                    'Action': 'execute-api:Invoke',
                    'Effect': effect,
                    'Resource': methodArn
                }
            ]
        }

        context: {} = {}
        if 'name' in idInformation:
            context['name'] = idInformation['name']

        if 'picture' in idInformation:
            context['picture'] = idInformation['picture']

        if 'locale' in idInformation:
            context['locale'] = idInformation['locale']

        authResponse['context'] = context

    return authResponse


def verify(token: str, clientID: str) -> {}:
    idInformation: {}

    try:
        # Verify and get information from id_token.
        idInformation = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            f'{clientID}.apps.googleusercontent.com'
        )

        # Deny access if the account is not a Google account.
        if idInformation['iss'] not in [
            'accounts.google.com',
            'https://accounts.google.com'
        ]:
            return None

    except ValueError as e:
        print(e)

        # Deny access if the token is invalid
        return None

    return idInformation
