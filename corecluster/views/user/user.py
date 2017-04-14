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


import time
import random
import hashlib
import datetime

from corecluster.models.core.user import User
from corecluster.utils.exception import CoreException
from corecluster.utils.decorators import register as register_decorator
from corecluster.utils import validation as v


@register_decorator(auth='guest', log=False, validate={'login': v.is_string(),
                                                       'password': v.is_string(),
                                                       'name': v.is_string(),
                                                       'surname': v.is_string(),
                                                       'email': v.is_string()})
def register(context, login, password, name, surname, email):
    """
    Register new user account with given credentials.
    :param login: User login
    :param password: Password
    :param name: First name
    :param surname: Last name
    :param email: User's email
    :return: Dictionary with user's login and password seed
    """
    if User.objects.filter(login=login).count() > 0:
        raise CoreException('user_exists')

    user = User.create()
    user.name = name
    user.surname = surname
    user.login = login
    user.email = email
    user.pw_seed = hashlib.sha1(str(random.random())).hexdigest()[:10]
    user.make_pwd(password)
    user.state = 'ok'
    user.save()
    try:
        user.save()
    except Exception as e:
        context.log.debug(0, "User.register: Adding to DB: %s" % str(e))
        raise CoreException('user_create')

    return {'login': user.login, 'pw_seed': user.pw_seed}


failed_seeds = {}

@register_decorator(auth='guest', validate={'login': v.is_string()})
def get_seed(context, login):
    """
    Get seed to generate password hash for given login
    :param login: User's login
    :return: Seed for user's password hash
    """
    time.sleep(random.random() * 3)

    try:
        user = User.objects.get(login=login)
        return {'seed': user.pw_seed}
    except Exception as e:
        # Prevent guessing login names. Without this attacker could guess which logins are valid and which are not.
        if login not in failed_seeds:
            failed_seeds[login] = hashlib.sha1(str(random.random())).hexdigest()[:10]

        return {'seed': failed_seeds[login]}


@register_decorator(auth='password', log=True, validate={'password_hash': v.is_string(),
                                                         'password_seed': v.is_string()})
def change_password(context, password_hash, password_seed):
    """
    Change user's password to new. Use sha1 of concatenated passford and seed to generate hash. The seed should be at
    least 10 characters long.
    :param password_hash: Hash generated from user's password and password_seed. To generate hash use sha1(passwd+seed)
    :param password_seed: Random seed
    """
    if len(password_seed) < 10:
        raise CoreException('seed_too_short')

    context.user.pw_hash = password_hash
    context.user.pw_seed = password_seed
    context.user.save()



@register_decorator(auth='password')
def account_info(context):
    """
    Get information about account (name, surname, email etc.)
    """
    return context.user.to_dict


@register_decorator(auth='password')
def get_quota(context):
    """
    Get information about quota (cpu, memory, storage)
    """
    return context.user.get_quota()


@register_decorator(auth='password', log=True)
def edit(context, **kwargs):
    """
    Edit account details
    """
    try:
        history = context.user.get_prop('edit_history', '')
        for f in kwargs.keys():
            history = history + '\n' + datetime.datetime.now() + ' Editing ' + f + ' from ' + getattr(context.user, f) + ' to ' + kwargs[f]
        context.user.set_prop('edit_history', history)
    except:
        pass
    context.user.edit(**kwargs)
    context.user.save()
