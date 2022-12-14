import logging
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, SupportsFloat

from sortedcontainers import SortedList


@dataclass
class Pair:
    up_to_key: SupportsFloat
    value: Any = None


class SliceMap:
    def __init__(
        self,
        include: str = "start",
    ):
        """
        SliceMap is like dict that allows setting values for whole slices of keys.

        It is efficient, having O(log(n)) insertion and querying time complexity.
        Under the hood, it uses SortedList and bisect search to find the correct
        place for a key to insert.

        Parameters
        ----------
        include
            Either "start" or "end". If "start", the key on the threshold between
            two slices will belong to the second slice. If "end" it will belong to
            the first slice.
        """
        assert include in ("start", "end"), "Possible `include` values: start | end"

        self.data = SortedList(key=lambda x: x.up_to_key)
        self.data.add(Pair(up_to_key=float("inf"), value=None))
        self.include = include

    def copy(self):
        """Returns a deepcopy of itself."""
        return deepcopy(self)

    def export(self):
        """Export SliceMap as list of tuples.

        This allows using SliceMap's final slices in other parts of your program.
        """
        return [(-float("inf"), self.data[0].up_to_key, self.data[0].value)] + [
            (p1.up_to_key, p2.up_to_key, p2.value) for p1, p2 in zip(self.data, self.data[1:])
        ]

    def __setitem__(self, slice_key: slice, value: Any):
        """Add a new slice to SliceMap. All values in slice key will map to the value.

        When adding new slice, a binary search will take place. This operation will
        have ``O(log(n))`` time complexity.

        Parameters
        ----------
        slice_key
            Slice of numerical values. If already exists in SliceMap, overlapping
            values will be overwritten. If, as a result of adding new slice, an
            existing slice will be 100% covered, it'll be removed.
        value
            Any python object can be a value.
        """
        assert isinstance(slice_key, slice)
        assert slice_key.step == 1 or slice_key.step is None

        start = slice_key.start if slice_key.start is not None else -float("inf")
        stop = slice_key.stop if slice_key.stop is not None else float("inf")

        logging.debug("Inserting value %s between keys %s:%s", value, start, stop)
        if start >= stop:
            logging.debug("Empty slice")
            return

        start_key_idx = self.data.bisect_left(Pair(up_to_key=start))
        end_key_idx = self.data.bisect_right(Pair(up_to_key=stop))
        if start_key_idx < len(self.data):
            old_value_to_keep = self.data[start_key_idx].value
        else:
            old_value_to_keep = None
        num_el_to_remove = end_key_idx - start_key_idx

        logging.debug("Will remove %s values", num_el_to_remove)

        for _ in range(num_el_to_remove):
            logging.debug(
                "Removing value %s up to key %s",
                self.data[start_key_idx].value,
                self.data[start_key_idx].up_to_key,
            )
            self.data.pop(start_key_idx)

        logging.debug("Inserting value %s up to key %s", old_value_to_keep, start)
        logging.debug("Inserting value %s up to key %s", value, stop)
        if start > -float("inf"):
            self.data.add(Pair(up_to_key=start, value=old_value_to_keep))
        self.data.add(Pair(up_to_key=stop, value=value))

    def __getitem__(self, key: SupportsFloat):
        """Check the value under the given key. If there's none, None will be returned.

        Parameters
        ----------
        key
            A numerical value.

        Returns
        -------
        Any
            Value of the key or None (if key is not present in SliceMap).

        """
        if key == float("inf"):
            return self.data[-1].value
        if key == -float("inf"):
            return self.data[0].value

        if self.include == "start":
            search_op = self.data.bisect_right
        else:
            search_op = self.data.bisect_left

        if isinstance(key, slice):
            idx1 = search_op(Pair(up_to_key=key.start))
            idx2 = search_op(Pair(up_to_key=key.stop))
            return tuple(self.data[i].value for i in range(idx1, idx2 + 1))
        else:
            idx = search_op(Pair(up_to_key=key))
            return self.data[idx].value

    def __len__(self):
        """Return the number of slices in SliceMap.

        If a slice becomes redundant because other slices are covering it 100%,
        it is removed from the SliceMap, and length might decrease.

        Returns
        -------
        int
            The number of slices in SliceMap.
        """
        return len(self.data) - 1

    def __repr__(self):
        start_bracket = "[" if self.include == "start" else "("
        end_bracket = ")" if self.include == "start" else "]"

        values = []

        p = self.data[0]
        values.append(f"(-inf,{p.up_to_key}{end_bracket}: {p.value}")

        for p1, p2 in zip(self.data, self.data[1:]):
            values.append(f"{start_bracket}{p1.up_to_key},{p2.up_to_key}" f"{end_bracket}: {p2.value}")

        return "{" + ", ".join(values) + "}"

    def plot(self):
        """If values are numerical and matplotlib is installed: plots SliceMap."""
        try:
            from slicemap import plot_slicemap

            return plot_slicemap(self) if len(self) > 0 else None
        except ImportError:
            logging.error("SliceMap.plot requires matplotlib to be installed!")
