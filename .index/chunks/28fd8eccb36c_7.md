# Chunk: 28fd8eccb36c_7

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_trace_dispatch_regular.py`
- lines: 446-500
- chunk: 8/9

```
G: print('skipped: trace_dispatch', abs_path_canonical_path_and_base[2], frame.f_lineno, event, frame.f_code.co_name, file_type)
                    cache_skips[frame_cache_key] = 1
                    return None if event == "call" else NO_FTRACE

            if py_db.is_files_filter_enabled:
                if py_db.apply_files_filter(frame, abs_path_canonical_path_and_base[0], False):
                    cache_skips[frame_cache_key] = 1

                    if (
                        is_stepping
                        and additional_info.pydev_original_step_cmd in (CMD_STEP_INTO, CMD_STEP_INTO_MY_CODE)
                        and not _global_notify_skipped_step_in
                    ):
                        notify_skipped_step_in_because_of_filters(py_db, frame)

                    # A little gotcha, sometimes when we're stepping in we have to stop in a
                    # return event showing the back frame as the current frame, so, we need
                    # to check not only the current frame but the back frame too.
                    back_frame = frame.f_back
                    if back_frame is not None and pydev_step_cmd in (
                        CMD_STEP_INTO,
                        CMD_STEP_INTO_MY_CODE,
                        CMD_STEP_RETURN,
                        CMD_STEP_RETURN_MY_CODE,
                    ):
                        if py_db.apply_files_filter(back_frame, back_frame.f_code.co_filename, False):
                            back_frame_cache_key = back_frame.f_code
                            cache_skips[back_frame_cache_key] = 1
                            # if DEBUG: print('skipped: trace_dispatch (filtered out: 1)', frame_cache_key, frame.f_lineno, event, frame.f_code.co_name)
                            return None if event == "call" else NO_FTRACE
                    else:
                        # if DEBUG: print('skipped: trace_dispatch (filtered out: 2)', frame_cache_key, frame.f_lineno, event, frame.f_code.co_name)
                        return None if event == "call" else NO_FTRACE

            # if DEBUG: print('trace_dispatch', filename, frame.f_lineno, event, frame.f_code.co_name, file_type)

            # Just create PyDBFrame directly (removed support for Python versions < 2.5, which required keeping a weak
            # reference to the frame).
            ret = PyDBFrame(
                (
                    py_db,
                    abs_path_canonical_path_and_base,
                    additional_info,
                    t,
                    frame_skips_cache,
                    frame_cache_key,
                )
            ).trace_dispatch(frame, event, arg)
            if ret is None:
                # 1 means skipped because of filters.
                # 2 means skipped because no breakpoints were hit.
                cache_skips[frame_cache_key] = 2
                return None if event == "call" else NO_FTRACE

```
