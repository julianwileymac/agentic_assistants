# Chunk: bcc3c6bec4b8_13

- source: `.venv-lab/Lib/site-packages/pip/_vendor/distlib/util.py`
- lines: 1040-1132
- chunk: 14/25

```
to be removed.
        """
        subs = self._subscribers
        if event not in subs:
            raise ValueError('No subscribers: %r' % event)
        subs[event].remove(subscriber)

    def get_subscribers(self, event):
        """
        Return an iterator for the subscribers for an event.
        :param event: The event to return subscribers for.
        """
        return iter(self._subscribers.get(event, ()))

    def publish(self, event, *args, **kwargs):
        """
        Publish a event and return a list of values returned by its
        subscribers.

        :param event: The event to publish.
        :param args: The positional arguments to pass to the event's
                     subscribers.
        :param kwargs: The keyword arguments to pass to the event's
                       subscribers.
        """
        result = []
        for subscriber in self.get_subscribers(event):
            try:
                value = subscriber(event, *args, **kwargs)
            except Exception:
                logger.exception('Exception during event publication')
                value = None
            result.append(value)
        logger.debug('publish %s: args = %s, kwargs = %s, result = %s', event, args, kwargs, result)
        return result


#
# Simple sequencing
#
class Sequencer(object):

    def __init__(self):
        self._preds = {}
        self._succs = {}
        self._nodes = set()  # nodes with no preds/succs

    def add_node(self, node):
        self._nodes.add(node)

    def remove_node(self, node, edges=False):
        if node in self._nodes:
            self._nodes.remove(node)
        if edges:
            for p in set(self._preds.get(node, ())):
                self.remove(p, node)
            for s in set(self._succs.get(node, ())):
                self.remove(node, s)
            # Remove empties
            for k, v in list(self._preds.items()):
                if not v:
                    del self._preds[k]
            for k, v in list(self._succs.items()):
                if not v:
                    del self._succs[k]

    def add(self, pred, succ):
        assert pred != succ
        self._preds.setdefault(succ, set()).add(pred)
        self._succs.setdefault(pred, set()).add(succ)

    def remove(self, pred, succ):
        assert pred != succ
        try:
            preds = self._preds[succ]
            succs = self._succs[pred]
        except KeyError:  # pragma: no cover
            raise ValueError('%r not a successor of anything' % succ)
        try:
            preds.remove(pred)
            succs.remove(succ)
        except KeyError:  # pragma: no cover
            raise ValueError('%r not a successor of %r' % (succ, pred))

    def is_step(self, step):
        return (step in self._preds or step in self._succs or step in self._nodes)

    def get_steps(self, final):
        if not self.is_step(final):
            raise ValueError('Unknown: %r' % final)
        result = []
        todo = []
```
