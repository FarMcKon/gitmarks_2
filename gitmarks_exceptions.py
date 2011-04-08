# encoding: utf-8

"""Gitmarks exception classes"""


class GitmarksException(Exception):
    """Base exception class"""
    pass


class InputError(GitmarksException):
    """Exception raised for errors in user input."""
    pass


class SettingsError(GitmarksException):
    """Exception raised for problems with settings files"""
    pass


class GitError(GitmarksException):
    """Exception raised for problems with git setup"""
    pass
