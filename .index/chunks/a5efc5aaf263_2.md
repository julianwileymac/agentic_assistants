# Chunk: a5efc5aaf263_2

- source: `.venv-lab/Lib/site-packages/zmq/log/handlers.py`
- lines: 160-233
- chunk: 3/3

```
table_ to a str
        try:
            topic, msg = str(record.msg).split(TOPIC_DELIM, 1)
        except ValueError:
            topic = ""
        else:
            # copy to avoid mutating LogRecord in-place
            record = copy(record)
            record.msg = msg

        try:
            bmsg = self.format(record).encode("utf8")
        except Exception:
            self.handleError(record)
            return

        topic_list = []

        if self.root_topic:
            topic_list.append(self.root_topic)

        topic_list.append(record.levelname)

        if topic:
            topic_list.append(topic)

        btopic = '.'.join(topic_list).encode("utf8", "replace")

        self.socket.send_multipart([btopic, bmsg])


class TopicLogger(logging.Logger):
    """A simple wrapper that takes an additional argument to log methods.

    All the regular methods exist, but instead of one msg argument, two
    arguments: topic, msg are passed.

    That is::

        logger.debug('msg')

    Would become::

        logger.debug('topic.sub', 'msg')
    """

    def log(self, level, topic, msg, *args, **kwargs):
        """Log 'msg % args' with level and topic.

        To pass exception information, use the keyword argument exc_info
        with a True value::

            logger.log(level, "zmq.fun", "We have a %s",
                    "mysterious problem", exc_info=1)
        """
        logging.Logger.log(self, level, f'{topic}{TOPIC_DELIM}{msg}', *args, **kwargs)


# Generate the methods of TopicLogger, since they are just adding a
# topic prefix to a message.
for name in "debug warn warning error critical fatal".split():
    try:
        meth = getattr(logging.Logger, name)
    except AttributeError:
        # some methods are missing, e.g. Logger.warn was removed from Python 3.13
        continue
    setattr(
        TopicLogger,
        name,
        lambda self, level, topic, msg, *args, **kwargs: meth(
            self, level, topic + TOPIC_DELIM + msg, *args, **kwargs
        ),
    )
```
