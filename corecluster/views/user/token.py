"""
Copyright (C) 2014-2017 cloudover.io ltd.
This file is part of the CloudOver.org project

Licensee holding a valid commercial license for this software may
use it in accordance with the terms of the license agreement
between cloudover.io ltd. and the licensee.

Alternatively you may use this software under following terms of
GNU Affero GPL v3 license:

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version. For details contact
with the cloudover.io company: https://cloudover.io/


This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.


You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import hashlib
import datetime
import random

from corecluster.utils import validation as v
from corecluster.utils.decorators import register
from corecluster.models.core.token import Token


@register(auth='password', validate={'name': v.is_string(empty=True, none=True),
                                     'token_valid_to': v.is_string(empty=False, none=True)})
def create(context, name='', token_valid_to=None):
    """
    Create new token
    :param name: Name of token
    :param token_valid_to: How long token should be valid (datetime string)
    :return: Dictionary with token's info
    """
    token = Token()
    token.user_id = context.user_id
    token.token = hashlib.sha1(str(random.random())).hexdigest()
    token.creation_date = datetime.datetime.now()
    token.name = name
    token.ignore_permissions = True
    if token_valid_to is not None:
        token.valid_to = token_valid_to
    else:
        token.valid_to = datetime.datetime.now()+datetime.timedelta(weeks=1)

    token.save()

    return token.to_dict


@register(auth='password', validate={'name': v.is_string(empty=True, none=True)})
def get_list(context, name=''):
    """
    Get list of tokens (optionaly filtered by name)
    :param name: Name of token(s) to list
    :return: List with tokens' dictionaries
    """

    tokens = []
    if name == '':
        tokens = Token.objects.filter(user=context.user_id).all()
    else:
        tokens = Token.objects.filter(user=context.user_id).filter(name=name).all()
    return [t.to_dict for t in tokens]


@register(auth='password', validate={'token_id': v.is_id()})
def get(context, token_id):
    """
    Obsolete. Get token by ID
    :param token_id: Token id
    :return: Dictionary with token
    """

    return Token.get(context.user_id, token_id).to_dict


@register(auth='password', validate={'token_id': v.is_id()})
def get_by_id(context, token_id):
    """
    Get one token by id
    :param token_id: Token id
    :return: Dictionary with token
    """

    return Token.get(context.user_id, token_id).to_dict


@register(auth='password', validate={'token_id': v.is_id()})
def delete(context, token_id):
    """
    Delete token
    :param token_id: Token id to be deleted
    """
    token = Token.get(context.user_id, token_id)
    token.remove(context)


@register(auth='password', validate={'token_id': v.is_id()})
def edit(context, token_id, **kwargs):
    """ Edit token properties """
    token = Token.get(context.user_id, token_id)
    token.edit(context, **kwargs)
    token.save()