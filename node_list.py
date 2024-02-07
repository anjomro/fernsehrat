from typing import List, Union

import requester
from node import Node


class NodeList:
    children: List[Union[Node, "NodeList"]]