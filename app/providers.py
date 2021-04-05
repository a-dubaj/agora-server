# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# The [[agora]] models search as an open market of providers (who bid content for each query) and users (who are interested in media of any type which is relevant within a given [[context]], which maps to a query).

from collections import namedtuple
from dataclasses import dataclass
from enum import Enum
from flask import current_app, redirect, url_for
from typing import Sequence

from . import util

class FloatEnum(float, Enum):
    pass

class Confidence(FloatEnum):
    # intended to be a float 0 .. 1
    null = 0.0
    low = 0.1
    default = 0.5
    high = 0.9
    inf = 1.0

@dataclass(order=True)
class Bid:
    confidence: Confidence = Confidence.null
    proposal: callable = False
    message: str = ''

def get_bids(q: str, tokens: Sequence[str] = []) -> Sequence[Bid]:

    # conceptually a list of tuples (confidence, proposal), but actually a list of data classes currently. unsure if this is idiomatic.
    bids = []
    for provider in PROVIDERS:
        bids.append(provider(q, tokens))
    return bids # unranked; sort to rank

def go(q, tokens):
    if tokens[0] == 'go' and len(tokens) > 1:
        return Bid(
                Confidence.high, 
                lambda: redirect(url_for('agora.go', node=util.slugify(" ".join(tokens[1:]))))
                )
    else:
        return Bid(Confidence.low, lambda: False)
    # add logic for:
    #    if there is indeed a go link in the destination
    #        return (0.9, )
    #    if there is not:
    #        return (False, 0.0)


def node(q, tokens):
    # In case nothing else beats it, bid to show a plain [[agora]] node. 
    # This also serves as a "constructive 404".
    return Bid(
            Confidence.default, 
            lambda: redirect(url_for('agora.node', node=util.slugify(q))))

PROVIDERS = [
        node, 
        go
        ]


