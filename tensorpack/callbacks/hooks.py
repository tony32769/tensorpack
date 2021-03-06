# -*- coding: utf-8 -*-
# File: hooks.py


""" Compatible layers between tf.train.SessionRunHook and Callback"""

import tensorflow as tf

from ..tfutils.common import tfv1
from .base import Callback

__all__ = ['CallbackToHook', 'HookToCallback']


class CallbackToHook(tfv1.train.SessionRunHook):
    """
    Hooks are less powerful than callbacks so the conversion is incomplete.
    It only converts the `before_run/after_run` calls.

    This is only for internal implementation of
    before_run/after_run callbacks.
    You shouldn't need to use this.
    """

    def __init__(self, cb):
        self._cb = cb

    def before_run(self, ctx):
        return self._cb.before_run(ctx)

    def after_run(self, ctx, vals):
        self._cb.after_run(ctx, vals)


class HookToCallback(Callback):
    """
    Make a ``tf.train.SessionRunHook`` into a callback.
    Note that when `SessionRunHook.after_create_session` is called, the `coord` argument will be None.
    """

    _chief_only = False

    def __init__(self, hook):
        """
        Args:
            hook (tf.train.SessionRunHook):
        """
        self._hook = hook

    def _setup_graph(self):
        with tf.name_scope(None):   # jump out of the name scope
            self._hook.begin()

    def _before_train(self):
        sess = tf.get_default_session()
        # coord is set to None when converting
        self._hook.after_create_session(sess, None)

    def _before_run(self, ctx):
        return self._hook.before_run(ctx)

    def _after_run(self, ctx, run_values):
        self._hook.after_run(ctx, run_values)

    def _after_train(self):
        self._hook.end(self.trainer.sess)
