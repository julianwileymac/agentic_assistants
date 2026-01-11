# Chunk: 3ccf96faba39_0

- source: `.venv-lab/Lib/site-packages/jedi/api/completion.py`
- lines: 1-84
- chunk: 1/11

```
import re
from textwrap import dedent
from inspect import Parameter

from parso.python.token import PythonTokenTypes
from parso.python import tree
from parso.tree import search_ancestor, Leaf
from parso import split_lines

from jedi import debug
from jedi import settings
from jedi.api import classes
from jedi.api import helpers
from jedi.api import keywords
from jedi.api.strings import complete_dict
from jedi.api.file_name import complete_file_name
from jedi.inference import imports
from jedi.inference.base_value import ValueSet
from jedi.inference.helpers import infer_call_of_leaf, parse_dotted_names
from jedi.inference.context import get_global_filters
from jedi.inference.value import TreeInstance
from jedi.inference.docstring_utils import DocstringModule
from jedi.inference.names import ParamNameWrapper, SubModuleName
from jedi.inference.gradual.conversion import convert_values, convert_names
from jedi.parser_utils import cut_value_at_position
from jedi.plugins import plugin_manager


class ParamNameWithEquals(ParamNameWrapper):
    def get_public_name(self):
        return self.string_name + '='


def _get_signature_param_names(signatures, positional_count, used_kwargs):
    # Add named params
    for call_sig in signatures:
        for i, p in enumerate(call_sig.params):
            kind = p.kind
            if i < positional_count and kind == Parameter.POSITIONAL_OR_KEYWORD:
                continue
            if kind in (Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY) \
                    and p.name not in used_kwargs:
                yield ParamNameWithEquals(p._name)


def _must_be_kwarg(signatures, positional_count, used_kwargs):
    if used_kwargs:
        return True

    must_be_kwarg = True
    for signature in signatures:
        for i, p in enumerate(signature.params):
            kind = p.kind
            if kind is Parameter.VAR_POSITIONAL:
                # In case there were not already kwargs, the next param can
                # always be a normal argument.
                return False

            if i >= positional_count and kind in (Parameter.POSITIONAL_OR_KEYWORD,
                                                  Parameter.POSITIONAL_ONLY):
                must_be_kwarg = False
                break
        if not must_be_kwarg:
            break
    return must_be_kwarg


def filter_names(inference_state, completion_names, stack, like_name, fuzzy,
                 imported_names, cached_name):
    comp_dct = set()
    if settings.case_insensitive_completion:
        like_name = like_name.lower()
    for name in completion_names:
        string = name.string_name
        if string in imported_names and string != like_name:
            continue
        if settings.case_insensitive_completion:
            string = string.lower()
        if helpers.match(string, like_name, fuzzy=fuzzy):
            new = classes.Completion(
                inference_state,
                name,
                stack,
```
