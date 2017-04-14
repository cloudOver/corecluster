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


class TaskBaseException(Exception):
    """
    This is base class for all Task exceptions. Don't use it directly. Instead of it, use TashError, TaskFatalError
    or TaskNotReady exceptions
    """
    comment = ''
    exception = None

    def __init__(self, comment='', exception=None):
        self.comment = comment
        self.exception = exception

    def __unicode__(self):
        return self.comment

    def __str__(self):
        return self.comment


class TaskFatalError(TaskBaseException):
    """
    This exception should be raised when fatal error occurs and it is possible, that cloud resources are broken (storage
    or node)
    """
    pass


class TaskError(TaskBaseException):
    """
    This exception should be raised when error is related to task. This will block all tasks related with this object
    """
    pass


class TaskNotReady(TaskBaseException):
    """
    This exception should be raised only when resources are not ready and task should be delayed. It blocks next tasks,
    but agent will try to execute it in next attempt. For example, vm is still running and agent should wait until vm is
    stopped (by another agent)
    """
    pass