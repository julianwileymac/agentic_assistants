# Chunk: 4e9bd49cabbf_22

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 1697-1815
- chunk: 23/64

```
):
        """
        Removes the API hook from the given process and module.

        @warning: Do not call from an API hook callback.

        @type  debug: L{Debug}
        @param debug: Debug object.

        @type  pid: int
        @param pid: Process ID.
        """
        try:
            hook = self.__hook[pid]
        except KeyError:
            return
        label = "%s!%s" % (self.__modName, self.__procName)
        hook.unhook(debug, pid, label)
        del self.__hook[pid]


# ==============================================================================


class BufferWatch(object):
    """
    Returned by L{Debug.watch_buffer}.

    This object uniquely references a buffer being watched, even if there are
    multiple watches set on the exact memory region.

    @type pid: int
    @ivar pid: Process ID.

    @type start: int
    @ivar start: Memory address of the start of the buffer.

    @type end: int
    @ivar end: Memory address of the end of the buffer.

    @type action: callable
    @ivar action: Action callback.

    @type oneshot: bool
    @ivar oneshot: C{True} for one shot breakpoints, C{False} otherwise.
    """

    def __init__(self, pid, start, end, action=None, oneshot=False):
        self.__pid = pid
        self.__start = start
        self.__end = end
        self.__action = action
        self.__oneshot = oneshot

    @property
    def pid(self):
        return self.__pid

    @property
    def start(self):
        return self.__start

    @property
    def end(self):
        return self.__end

    @property
    def action(self):
        return self.__action

    @property
    def oneshot(self):
        return self.__oneshot

    def match(self, address):
        """
        Determine if the given memory address lies within the watched buffer.

        @rtype: bool
        @return: C{True} if the given memory address lies within the watched
            buffer, C{False} otherwise.
        """
        return self.__start <= address < self.__end


# ==============================================================================


class _BufferWatchCondition(object):
    """
    Used by L{Debug.watch_buffer}.

    This class acts as a condition callback for page breakpoints.
    It emulates page breakpoints that can overlap and/or take up less
    than a page's size.
    """

    def __init__(self):
        self.__ranges = list()  # list of BufferWatch in definition order

    def add(self, bw):
        """
        Adds a buffer watch identifier.

        @type  bw: L{BufferWatch}
        @param bw:
            Buffer watch identifier.
        """
        self.__ranges.append(bw)

    def remove(self, bw):
        """
        Removes a buffer watch identifier.

        @type  bw: L{BufferWatch}
        @param bw:
            Buffer watch identifier.

```
